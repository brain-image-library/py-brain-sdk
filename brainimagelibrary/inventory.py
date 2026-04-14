"""Inventory retrieval and download utilities for Brain Image Library datasets."""

import logging
import requests
import pandas as pd
import gzip
import io
import json
import ast
import os
from typing import Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

logger = logging.getLogger(__name__)

__all__ = ["summary", "DatasetInventory", "to_manifest", "exists", "has", "get"]


def summary(bildid: Optional[str] = None) -> Optional[dict]:
    """
    Summarizes inventory information for a dataset.

    Retrieves inventory information for a dataset and computes summary
    statistics, including file sizes, counts, and types.

    Args:
        bildid (str, optional): The unique identifier of the dataset. Defaults to None.

    Returns:
        dict or None: A dictionary containing the following keys, or None if the
            dataset cannot be retrieved:

            - ``pretty_size`` (str): Human-readable size of the dataset.
            - ``size`` (int): Total size of the dataset in bytes.
            - ``number_of_files`` (int): Number of files in the dataset.
            - ``files`` (dict): Detailed file information with keys
              ``frequencies`` (dict of extension counts), ``types`` (list of
              file types), and ``sizes`` (dict of total size per extension).

    Example:
        >>> from brainimagelibrary import inventory
        >>> info = inventory.summary(bildid="act-bag")
        >>> print(info["pretty_size"])
        '1.2 GB'
        >>> print(info["number_of_files"])
        42
        >>> print(list(info["files"].keys()))
        ['frequencies', 'types', 'sizes']
    """
    metadata = get(bildid=bildid)
    manifest = metadata["manifest"]
    df = pd.DataFrame(manifest)

    data = {}
    data["pretty_size"] = metadata["pretty_size"]
    data["size"] = metadata["size"]
    data["number_of_files"] = metadata["number_of_files"]

    grouped_data = df.groupby("extension")["size"].sum()
    data["files"] = {
        "frequencies": metadata["frequencies"],
        "types": metadata["file_types"],
        "sizes": grouped_data.to_dict(),
    }

    return data


class DatasetInventory(dict):
    """
    A dict subclass representing a dataset's inventory, returned by :func:`get`.

    Provides convenient methods for exporting and downloading dataset files
    without needing to call module-level functions separately.
    """

    def __init__(self, data: dict, bildid: str) -> None:
        super().__init__(data)
        self._bildid = bildid

    def to_manifest(self, checksum: str = "md5") -> Optional[str]:
        """
        Writes a manifest file for this dataset.

        Writes a tab-separated file named ``<bildid>.manifest`` with
        columns ``URL`` and the selected checksum column.

        Args:
            checksum (str): Checksum column to include. One of 'md5', 'sha256',
                'xxh64', or 'b2sum'. Defaults to 'md5'.

        Returns:
            str | None: Path to the written manifest file, or None on failure.

        Example:
            >>> from brainimagelibrary import inventory
            >>> dataset = inventory.get(bildid="act-bag")
            >>> path = dataset.to_manifest(checksum="md5")
            >>> print(path)
            'act-bag.manifest'
        """
        valid_checksums = ("md5", "sha256", "xxh64", "b2sum")
        if checksum not in valid_checksums:
            logger.error(
                "checksum must be one of %s, got '%s'.", valid_checksums, checksum
            )
            return None

        manifest = self.get("manifest", [])
        if not manifest:
            logger.error("No manifest entries found for dataset '%s'.", self._bildid)
            return None

        df = pd.DataFrame(manifest)
        if checksum not in df.columns:
            df[checksum] = ""

        df = df[["download_url", checksum]].rename(columns={"download_url": "URL"})
        output_path = f"{self._bildid}.manifest"
        df.to_csv(output_path, sep="\t", index=False)
        return output_path

    def rename(self, new_name: str) -> Optional[str]:
        """
        Renames the local download folder for this dataset.

        If the folder ``<bildid>/`` exists on disk it is renamed to
        ``<new_name>/``.  The internal identifier is updated so that
        subsequent calls to :meth:`download` and :meth:`to_manifest` use
        the new name.

        Args:
            new_name (str): The new folder name.

        Returns:
            str | None: The new folder path on success, or None on failure.

        Example:
            >>> from brainimagelibrary import inventory
            >>> dataset = inventory.get(bildid="act-bag")
            >>> new_path = dataset.rename("act-bag-renamed")
            >>> print(new_path)
            'act-bag-renamed'
        """
        if not new_name:
            logger.error("new_name must be a non-empty string.")
            return None

        old_folder = self._bildid
        if os.path.exists(old_folder):
            try:
                os.rename(old_folder, new_name)
            except OSError as e:
                logger.error("Failed to rename '%s' to '%s': %s", old_folder, new_name, e)
                return None

        self._bildid = new_name
        return new_name

    def download(
        self,
        n: int = 2,
        extensions: Optional[Union[str, list]] = None,
    ) -> Optional[str]:
        """
        Downloads files in this dataset's manifest to a local folder.

        Files are saved under ``<bildid>/`` preserving the path structure
        from the download URL. Files that already exist on disk are skipped.
        Partial downloads (``.part`` files) are resumed automatically using
        HTTP range requests when the server supports it.

        Args:
            n (int): Number of concurrent downloads. Defaults to 2.
            extensions (list | str | None): File extension(s) to filter downloads,
                e.g. ``'png'`` or ``['png', 'tif']``. If None, all files are downloaded.

        Returns:
            str: Path to the download folder.

        Example:
            >>> from brainimagelibrary import inventory
            >>> dataset = inventory.get(bildid="act-bag")
            >>> folder = dataset.download(n=4)
            >>> print(folder)
            'act-bag'
            >>> folder = dataset.download(n=4, extensions='png')
            >>> folder = dataset.download(n=4, extensions=['png', 'tif'])
        """
        manifest = self.get("manifest", [])
        if not manifest:
            logger.error("No manifest entries found for dataset '%s'.", self._bildid)
            return None

        folder = self._bildid
        os.makedirs(folder, exist_ok=True)

        if extensions is not None:
            if isinstance(extensions, str):
                extensions = [extensions]
            extensions = {ext.lstrip(".").lower() for ext in extensions}

        urls = [
            entry.get("download_url")
            for entry in manifest
            if entry.get("download_url")
            and (
                extensions is None
                or os.path.splitext(entry.get("download_url", ""))[1]
                .lstrip(".")
                .lower()
                in extensions
            )
        ]
        if not urls:
            logger.error("No download URLs found for dataset '%s'.", self._bildid)
            return folder

        results = {"ok": 0, "skipped": 0, "failed": 0}

        def _download_one(url):
            path_part = url.split("://", 1)[-1].split("/", 1)[-1]
            dest = os.path.join(folder, path_part)
            part = dest + ".part"

            if os.path.exists(dest):
                return "skipped", url

            os.makedirs(os.path.dirname(dest), exist_ok=True)

            # Determine resume offset from an existing .part file
            resume_offset = os.path.getsize(part) if os.path.exists(part) else 0
            headers = {"Range": f"bytes={resume_offset}-"} if resume_offset else {}

            try:
                resp = requests.get(url, stream=True, timeout=60, headers=headers)

                # 416 = range not satisfiable → server thinks file is complete
                if resp.status_code == 416:
                    os.rename(part, dest)
                    return "ok", url

                if resp.status_code not in (200, 206):
                    return "failed", url

                resuming = resp.status_code == 206
                total = int(resp.headers.get("Content-Length", 0))
                if resuming:
                    total += resume_offset

                mode = "ab" if resuming else "wb"
                label = os.path.basename(dest)
                with tqdm(
                    total=total if total else None,
                    initial=resume_offset if resuming else 0,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=label,
                    leave=False,
                ) as pbar:
                    with open(part, mode) as f:
                        for chunk in resp.iter_content(chunk_size=1024 * 1024):
                            f.write(chunk)
                            pbar.update(len(chunk))

                os.rename(part, dest)
                return "ok", url

            except requests.exceptions.RequestException as e:
                logger.warning("Failed to download %s: %s", url, e)
                return "failed", url

        with tqdm(total=len(urls), desc="Overall", unit="file") as overall:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {executor.submit(_download_one, url): url for url in urls}
                for future in as_completed(futures):
                    status, url = future.result()
                    results[status] += 1
                    overall.set_postfix(
                        ok=results["ok"],
                        skipped=results["skipped"],
                        failed=results["failed"],
                    )
                    overall.update(1)

        logger.info(
            "Download complete: %d downloaded, %d skipped, %d failed.",
            results["ok"],
            results["skipped"],
            results["failed"],
        )
        return folder


def to_manifest(bildid: Optional[str] = None, checksum: str = "md5") -> Optional[str]:
    """
    Writes a manifest file for a dataset.

    Retrieves inventory information for the given ``bildid`` and writes a
    tab-separated file named ``<bildid>.manifest`` with columns ``URL`` and
    the selected checksum column.

    Args:
        bildid (str, optional): The unique identifier for the dataset. Defaults to None.
        checksum (str): Checksum column to include. One of ``'md5'``, ``'sha256'``,
            ``'xxh64'``, or ``'b2sum'``. Defaults to ``'md5'``.

    Returns:
        str | None: Path to the written manifest file, or None on failure.

    Example:
        >>> from brainimagelibrary import inventory
        >>> path = inventory.to_manifest(bildid="act-bag", checksum="md5")
        >>> print(path)
        'act-bag.manifest'
        >>> path_sha = inventory.to_manifest(bildid="act-bag", checksum="sha256")
        >>> print(path_sha)
        'act-bag.manifest'
    """
    if bildid is None:
        logger.error("bildid must be provided.")
        return None

    data = get(bildid=bildid)
    if data is None:
        return None

    return data.to_manifest(checksum=checksum)


def exists(bildid: Optional[str] = None) -> bool:
    """
    Checks whether the inventory file for a dataset exists and is accessible.

    Args:
        bildid (str, optional): The unique identifier for the dataset. Defaults to None.

    Returns:
        bool: True if the compressed JSON file exists and is accessible, False otherwise.

    Example:
        >>> from brainimagelibrary import inventory
        >>> inventory.exists(bildid="act-bag")
        True
        >>> inventory.exists(bildid="nonexistent-id")
        False
    """
    if bildid is None:
        return False

    url = f"https://download.brainimagelibrary.org/inventory/datasets/JSON/{bildid}.json.gz"

    try:
        resp = requests.head(url, timeout=30)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def has(bildid: Optional[str] = None, option: Optional[str] = None) -> Optional[bool]:
    """
    Checks whether a dataset contains files of a given type.

    First verifies the dataset exists via :func:`exists`, then retrieves its
    inventory and checks whether ``option`` appears in the ``file_types``
    field. If ``option`` is ``'cell_by_gene'``, returns True if any manifest
    entry has ``is_cell_by_gene`` set to True.

    Args:
        bildid (str, optional): The unique identifier for the dataset. Defaults to None.
        option (str, optional): The file type/extension to look for, or
            ``'cell_by_gene'`` to check for cell-by-gene files. Defaults to None.

    Returns:
        bool | None: True if the condition is met, False if not, or None if the
            dataset does not exist.

    Example:
        >>> from brainimagelibrary import inventory
        >>> inventory.has(bildid="act-bag", option="tif")
        True
        >>> inventory.has(bildid="act-bag", option="xyz")
        False
        >>> inventory.has(bildid="nonexistent", option="tif")
        None
    """
    if not exists(bildid=bildid):
        return None

    data = get(bildid=bildid)
    if data is None:
        return False

    if option == "cell_by_gene":
        manifest = data.get("manifest", [])
        return any(entry.get("is_cell_by_gene") is True for entry in manifest)

    file_types = data.get("file_types", {})
    return option in file_types


def get(bildid: Optional[str] = None) -> Optional["DatasetInventory"]:
    """
    Retrieves inventory information for a dataset by its ID from a compressed JSON (.json.gz).

    Args:
        bildid (str, optional): The unique identifier for the dataset. Defaults to None.

    Returns:
        dict | None: Dataset inventory information if successful, otherwise None.

    Example:
        >>> from brainimagelibrary import inventory
        >>> data = inventory.get(bildid="act-bag")
        >>> print(data["number_of_files"])
        42
        >>> print(data["pretty_size"])
        '1.2 GB'
        >>> print(list(data.keys()))
        ['number_of_files', 'size', 'pretty_size', 'manifest', 'file_types', 'frequencies', 'mime_types']
    """
    if bildid is None:
        logger.error("bildid must be provided.")
        return None

    filename = f"{bildid}.json.gz"
    url = f"https://download.brainimagelibrary.org/inventory/datasets/JSON/{filename}"

    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            logger.error("Received status code %d for %s.", resp.status_code, url)
            return None

        try:
            with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as gz:
                raw = gz.read()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = ast.literal_eval(raw.decode("utf-8"))
            return DatasetInventory(data, bildid)
        except gzip.BadGzipFile:
            logger.error("Response is not a valid gzip file.")
            return None
        except (ValueError, SyntaxError) as e:
            logger.error("Decompressed content could not be parsed: %s", e)
            return None

    except requests.exceptions.RequestException as e:
        logger.error("Error making API request: %s", e)
        return None
