"""
reports.py — Daily inventory report generation for the Brain Image Library.

This module builds summary DataFrames across all BIL datasets (metadata
versions 1.0 and 2.0).  Reports are cached under ``/tmp/``, ``reports/``,
and ``/bil/data/inventory/daily/`` when those paths are available.

Public functions
----------------
daily(option, overwrite)
    Return today's inventory report as a :class:`pandas.DataFrame`.
get_all_bildids()
    Return all unique dataset IDs across metadata versions 1.0 and 2.0.

Private helpers (not part of the public API)
---------------------------------------------
_get_did(bildid)
    Fetch combined metadata + inventory data for a single dataset.
_create_daily_report(overwrite)
    Build the daily report locally when the remote download fails.
"""

import logging
import requests
from typing import Optional

from .retrieve import by_id, by_version
from .inventory import get as inventory_get
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

logger = logging.getLogger(__name__)

__all__ = ["daily", "get_all_bildids"]


def _get_did(bildid: str) -> dict:
    """
    Retrieves detailed metadata for a dataset by its ID.

    Args:
        bildid (str): The unique identifier of the dataset.

    Returns:
        dict: A dictionary containing the dataset metadata, including:
            - `metadata_version`: Version of the metadata.
            - `bildid`: The dataset ID.
            - `bildate`: The submission date of the dataset.
            - `contributor`: Name of the primary contributor.
            - `affiliation`: Affiliation of the primary contributor.
            - `award_number`: Award number associated with the funding.
            - `project`: Name of the project.
            - `consortium`: Name of the consortium.
            - `bildirectory`: Directory path of the dataset.
            - `generalmodality`: General modality of the dataset.
            - `technique`: Technique used in the dataset.
            - `species`: Species in the dataset.
            - `taxonomy`: NCBI taxonomy ID of the species.
            - `genotype`: Genotype information of the specimen.
            - `samplelocalid`: Local ID of the specimen sample.
    """

    def safe_get(data, keys, default=None):
        """Helper function to safely retrieve nested dictionary values."""
        try:
            for key in keys:
                data = data[key]
            return data
        except (KeyError, IndexError, TypeError):
            return default

    metadata = by_id(bildid=bildid)
    metadata = metadata.get("retjson", [{}])[0]

    inv = inventory_get(bildid=bildid)

    return {
        "metadata_version": safe_get(metadata, ["Submission", "metadata"]),
        "bildid": bildid,
        "bildate": safe_get(metadata, ["Submission", "bildate"]),
        "contributor": safe_get(metadata, ["Contributors", 0, "contributorname"]),
        "affiliation": safe_get(metadata, ["Contributors", 0, "affiliation"]),
        "award_number": safe_get(metadata, ["Funders", 0, "award_number"]),
        "project": safe_get(metadata, ["Submission", "project"]),
        "consortium": safe_get(metadata, ["Submission", "consortium"]),
        "bildirectory": safe_get(metadata, ["Dataset", 0, "bildirectory"]),
        "generalmodality": safe_get(metadata, ["Dataset", 0, "generalmodality"]),
        "technique": safe_get(metadata, ["Dataset", 0, "technique"]),
        "species": safe_get(metadata, ["Specimen", 0, "species"]),
        "taxonomy": safe_get(metadata, ["Specimen", 0, "ncbitaxonomy"]),
        "genotype": safe_get(metadata, ["Specimen", 0, "genotype"]),
        "samplelocalid": safe_get(metadata, ["Specimen", 0, "samplelocalid"]),
        "number_of_files": inv.get("number_of_files") if inv else None,
        "size": inv.get("size") if inv else None,
        "file_types": inv.get("file_types") if inv else None,
        "frequencies": inv.get("frequencies") if inv else None,
        "mime_types": inv.get("mime_types") if inv else None,
    }


def daily(option: str = "simple", overwrite: bool = False) -> pd.DataFrame:
    """
    Retrieve the daily inventory report from the Brain Image Library.

    The function follows a three-step fallback strategy:

    1. Load ``/bil/data/inventory/daily/reports/today.json`` from the BIL
       shared filesystem if it exists (and ``overwrite`` is ``False``).
    2. If the local file is absent, download the report from the web
       (URL depends on ``option``).
    3. If the download also fails, log a warning and fall back to
       :func:`__create_daily_report` to build the report locally.

    Args:
        option (str, optional): The type of daily report to fetch when falling
            back to a web download.  Options are:

            - ``"simple"`` *(default)*: Fetches the simple daily inventory TSV
              from ``download.brainimagelibrary.org/inventory/daily/<YYYYMMDD>.tsv``.
            - ``"detailed"``: Fetches the pre-built detailed report from
              ``download.brainimagelibrary.org/inventory/daily/reports/today.tsv``.

        overwrite (bool, optional): When ``True``, skip any cached file on disk
            and force a fresh download or regeneration.  Defaults to ``False``.

    Returns:
        pd.DataFrame: A DataFrame containing the inventory data.

    Raises:
        ValueError: If ``option`` is not ``"simple"`` or ``"detailed"``.

    Example:
        >>> from brainimagelibrary import reports
        >>> df = reports.daily(option="simple")
        >>> print(df.columns.tolist())
        ['bildid', 'contributor', 'affiliation', 'species', 'generalmodality', ...]
        >>> print(len(df))
        1500
        >>> df_detail = reports.daily(option="detailed", overwrite=True)
        >>> print(type(df_detail))
        <class 'pandas.core.frame.DataFrame'>
    """

    def fetch_and_load_csv(url, file_path):
        """Helper function to download and load a TSV file as a DataFrame."""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
                return pd.read_csv(file_path, sep="\t")
            else:
                return None
        except requests.exceptions.RequestException as e:
            logger.error("Error fetching URL %s: %s", url, e)
            return None

    if option not in ("simple", "detailed"):
        raise ValueError(f"Invalid option '{option}'. Choose 'simple' or 'detailed'.")

    # Step 1: try local BIL filesystem JSON cache
    local_json = Path("/bil/data/inventory/daily/reports/today.json")
    if not overwrite and local_json.exists():
        logger.info("Loading daily report from %s.", local_json)
        try:
            return pd.read_json(local_json)
        except ValueError:
            logger.warning(
                "%s is empty or corrupt, falling back to download.", local_json
            )

    # Step 2: attempt web download
    if option == "simple":
        base_url = "https://download.brainimagelibrary.org/inventory/daily"
        today = datetime.today().strftime("%Y%m%d")
        url = f"{base_url}/{today}.tsv"
        file_path = f"/tmp/{today}.tsv"
    else:
        url = "https://download.brainimagelibrary.org/inventory/daily/reports/today.tsv"
        file_path = "/tmp/today.tsv"

    df = fetch_and_load_csv(url, file_path)

    # Step 3: build from scratch if download failed
    if df is None:
        logger.warning(
            "Cannot download daily report from %s. Building report from scratch...", url
        )
        df = _create_daily_report(overwrite)

    return df


def _create_daily_report(overwrite: bool = False) -> pd.DataFrame:
    """
    Create or load the daily inventory report from local storage.

    Checks for an existing report (``<YYYYMMDD>.tsv``) in the following
    locations, in order:

    1. ``/bil/data/inventory/daily/`` — BIL shared filesystem (preferred).
    2. ``reports/`` — local working-directory fallback.

    If no cached file is found (or ``overwrite`` is ``True`` for the BIL path
    check), the report is generated by iterating over all datasets in metadata
    versions 1.0 and 2.0 via :func:`__get_did`, deduplicating on ``bildid``,
    and saving the result as a tab-separated file to both ``reports/`` and, if
    the path exists, ``/bil/data/inventory/daily/``.

    Args:
        overwrite (bool, optional): When ``True``, skip the BIL filesystem
            cache check and regenerate the report from scratch.
            Defaults to ``False``.

    Returns:
        pd.DataFrame: The daily inventory report as a DataFrame.

    Side Effects:
        - Reads ``<YYYYMMDD>.tsv`` from disk when a cached copy exists.
        - Creates the ``reports/`` directory if it does not already exist.
        - Writes ``reports/<YYYYMMDD>.tsv`` after generating a new report.
        - Writes ``/bil/data/inventory/daily/<YYYYMMDD>.tsv`` when that
          directory is available on the BIL shared filesystem.
    """
    today = datetime.today().strftime("%Y%m%d")

    if not overwrite:
        bil_path = Path(f"/bil/data/inventory/daily/{today}.tsv")
        if bil_path.exists():
            logger.info("Daily report %s found on disk.", bil_path)
            return pd.read_csv(bil_path, sep="\t")

        local_path = Path(f"reports/{today}.tsv")
        if local_path.exists():
            logger.info("Daily report %s found on disk.", local_path)
            return pd.read_csv(local_path, sep="\t")

    all_datasets = get_all_bildids()

    logger.info("Processing %d unique datasets in parallel.", len(all_datasets))
    data = []
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_get_did, dataset): dataset for dataset in all_datasets
        }
        for future in tqdm(as_completed(futures), total=len(futures)):
            try:
                result = future.result()
                if result is not None:
                    data.append(result)
            except Exception as e:
                bildid = futures[future]
                logger.warning("Failed to fetch dataset %s: %s", bildid, e)

    df = pd.DataFrame(data).drop_duplicates(subset=["bildid"])

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    df.to_csv(reports_dir / f"{today}.tsv", sep="\t", index=False)

    # save to BIL shared filesystem
    bil_dir = Path("/bil/data/inventory/daily")
    if bil_dir.exists():
        df.to_csv(bil_dir / f"{today}.tsv", sep="\t", index=False)

    return df


def get_all_bildids() -> list:
    """
    Retrieve all dataset IDs from the Brain Image Library across metadata versions.

    Fetches dataset ID lists for metadata versions 1.0 and 2.0 in parallel,
    then returns the combined deduplicated list.

    Returns:
        list[str]: All unique BIL dataset IDs across v1.0 and v2.0 metadata.

    Example:
        >>> from brainimagelibrary import reports
        >>> ids = reports.get_all_bildids()
        >>> print(type(ids))
        <class 'list'>
        >>> print(ids[:3])
        ['act-bag', 'another-id', 'third-id']
        >>> print(len(ids) > 0)
        True
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_v1 = executor.submit(lambda: list(by_version(version="1.0")))
        future_v2 = executor.submit(lambda: list(by_version(version="2.0")))
        datasets_v1 = future_v1.result()
        datasets_v2 = future_v2.result()

    return list(dict.fromkeys(datasets_v1 + datasets_v2))
