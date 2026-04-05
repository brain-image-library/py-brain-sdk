from .retrieve import *
import uuid
import requests
import pandas as pd
import gzip
import io
import json
import ast
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def summary(dataset_id=None):
    """
    Summarizes dataset metadata.

    This function retrieves metadata for a dataset and computes summary
    statistics, including file sizes, counts, and types.

    Args:
        dataset_id (str, optional): The unique identifier of the dataset. Defaults to None.

    Returns:
        dict: A dictionary containing the following keys:
            - `pretty_size` (str): Human-readable size of the dataset.
            - `size` (int): Total size of the dataset in bytes.
            - `number_of_files` (int): Number of files in the dataset.
            - `files` (dict): Detailed file information, including:
                - `frequencies` (dict): Frequency of file extensions.
                - `types` (list): Types of files in the dataset.
                - `sizes` (dict): Size of files grouped by extension.
    """
    metadata = get(dataset_id=dataset_id)
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


def __generate_dataset_uuid(directory):
    """
    Generates a UUID for a dataset based on its directory path.

    This function computes a consistent UUID for a dataset using the
    directory path as the seed. The UUID is generated using the UUIDv5
    algorithm with the DNS namespace.

    Args:
        directory (str): The absolute or relative path to the dataset directory.

    Returns:
        str: A string representation of the generated UUID.
    """
    if directory[-1] == "/":
        directory = directory[:-1]

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, directory))


class DatasetInventory(dict):
    """A dict subclass returned by get() that supports method chaining."""

    def __init__(self, data, dataset_id):
        super().__init__(data)
        self._dataset_id = dataset_id

    def to_manifest(self, checksum="md5"):
        """
        Writes a manifest file for this dataset.

        Writes a tab-separated file named ``<dataset_id>.manifest`` with
        columns ``URL`` and the selected checksum column.

        Args:
            checksum (str): Checksum column to include. One of 'md5', 'sha256',
                'xxh64', or 'b2sum'. Defaults to 'md5'.

        Returns:
            str | None: Path to the written manifest file, or None on failure.
        """
        valid_checksums = ("md5", "sha256", "xxh64", "b2sum")
        if checksum not in valid_checksums:
            print(f"Error: checksum must be one of {valid_checksums}, got '{checksum}'.")
            return None

        manifest = self.get("manifest", [])
        if not manifest:
            print(f"Error: no manifest entries found for dataset '{self._dataset_id}'.")
            return None

        df = pd.DataFrame(manifest)
        if checksum not in df.columns:
            df[checksum] = ""

        df = df[["download_url", checksum]].rename(columns={"download_url": "URL"})
        output_path = f"{self._dataset_id}.manifest"
        df.to_csv(output_path, sep="\t", index=False)
        return output_path

    def download(self, n=2):
        """
        Downloads all files in this dataset's manifest to a local folder.

        Files are saved under ``<dataset_id>/`` preserving the path structure
        from the download URL. Files that already exist on disk are skipped.
        Partial downloads (``.part`` files) are resumed automatically using
        HTTP range requests when the server supports it.

        Args:
            n (int): Number of concurrent downloads. Defaults to 2.

        Returns:
            str: Path to the download folder.
        """
        manifest = self.get("manifest", [])
        if not manifest:
            print(f"Error: no manifest entries found for dataset '{self._dataset_id}'.")
            return None

        folder = self._dataset_id
        os.makedirs(folder, exist_ok=True)

        urls = [entry.get("download_url") for entry in manifest if entry.get("download_url")]
        if not urls:
            print(f"Error: no download URLs found for dataset '{self._dataset_id}'.")
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
                print(f"\nWarning: failed to download {url}: {e}")
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

        print(
            f"\nDownload complete: {results['ok']} downloaded, "
            f"{results['skipped']} skipped, {results['failed']} failed."
        )
        return folder


def to_manifest(dataset_id=None, checksum="md5"):
    """
    Retrieves a dataset inventory and writes a manifest file.

    Calls get() for the given dataset_id and writes a tab-separated file
    named ``<dataset_id>.manifest`` with columns ``URL`` and the selected
    checksum column.

    Args:
        dataset_id (str, optional): The unique identifier for the dataset. Defaults to None.
        checksum (str): Checksum column to include. One of 'md5', 'sha256',
            'xxh64', or 'b2sum'. Defaults to 'md5'.

    Returns:
        str | None: Path to the written manifest file, or None on failure.
    """
    if dataset_id is None:
        print("Error: dataset_id must be provided.")
        return None

    data = get(dataset_id=dataset_id)
    if data is None:
        return None

    return data.to_manifest(checksum=checksum)


def get(dataset_id=None):
    """
    Retrieves metadata for a dataset by its ID from a compressed JSON (.json.gz).

    Args:
        dataset_id (str, optional): The unique identifier for the dataset. Defaults to None.

    Returns:
        dict | None: Dataset metadata if successful, otherwise None.
    """
    if dataset_id is None:
        print("Error: dataset_id must be provided.")
        return None

    filename = f"{dataset_id}.json.gz"
    url = f"https://download.brainimagelibrary.org/inventory/datasets/JSON/{filename}"

    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"Error: received status code {resp.status_code} for {url}")
            return None

        try:
            with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as gz:
                raw = gz.read()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = ast.literal_eval(raw.decode("utf-8"))
            return DatasetInventory(data, dataset_id)
        except gzip.BadGzipFile:
            print("Error: Response is not a valid gzip file.")
            return None
        except (ValueError, SyntaxError) as e:
            print(f"Error: Decompressed content could not be parsed: {e}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
