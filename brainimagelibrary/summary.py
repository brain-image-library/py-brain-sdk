"""Summary utilities for Brain Image Library daily inventory reports."""

import logging
import requests
import pandas as pd
from pathlib import Path
from typing import Optional

from . import reports

logger = logging.getLogger(__name__)

__all__ = ["load", "daily"]


def load(date: str) -> Optional[pd.DataFrame]:
    """
    Load a daily inventory report for a specific date as a DataFrame.

    Follows a two-step lookup strategy:

    1. Read ``/bil/data/inventory/daily/<date>.tsv`` from the BIL shared
       filesystem if it exists.
    2. Otherwise download the file from
       ``https://download.brainimagelibrary.org/inventory/daily/<date>.tsv``
       and cache it under ``/tmp/``.

    If neither source is available, a warning is logged and ``None`` is returned.

    Args:
        date (str): Date in ``YYYYMMDD`` format (e.g. ``"20240101"``).

    Returns:
        pd.DataFrame | None: The inventory report as a DataFrame, or ``None``
        when data for the requested date cannot be found or downloaded.

    Example:
        >>> from brainimagelibrary import summary
        >>> df = summary.load("20240101")
        >>> if df is not None:
        ...     print(type(df))
        ...     print(len(df) > 0)
        <class 'pandas.core.frame.DataFrame'>
        True
        >>> df_missing = summary.load("19000101")
        Data for 19000101 is unavailable.
    """
    bil_path = Path(f"/bil/data/inventory/daily/{date}.tsv")
    if bil_path.exists():
        return pd.read_csv(bil_path, sep="\t")

    url = f"https://download.brainimagelibrary.org/inventory/daily/{date}.tsv"
    tmp_path = f"/tmp/{date}.tsv"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(tmp_path, "wb") as f:
                f.write(response.content)
            return pd.read_csv(tmp_path, sep="\t")
        else:
            logger.warning("Data for %s is unavailable.", date)
            return None
    except requests.exceptions.RequestException:
        logger.warning("Data for %s is unavailable.", date)
        return None


def daily(option: str = "simple", overwrite: bool = False) -> dict:
    """
    Returns a summary of the daily Brain Image Library inventory report.

    Args:
        option (str, optional): Type of daily report to fetch. Options are:
            - ``"simple"``: Fetches the simple daily inventory (default).
            - ``"detailed"``: Fetches the detailed daily report.
        overwrite (bool, optional): If True, forces regeneration of the report
            even if a cached version exists. Defaults to False.

    Returns:
        dict: A dictionary with the following keys:
            - ``metadata_version``: Value counts of metadata versions.
            - ``number_of_datasets``: Total number of datasets (int).
            - ``number_of_unique_contributors``: Count of unique contributors (int).
            - ``contributors``: Value counts of contributor names.
            - ``number_of_unique_affiliations``: Count of unique affiliations (int).
            - ``affiliations``: Value counts of contributor affiliations.
            - ``number_of_unique_species``: Count of unique species (int).
            - ``species``: Value counts of species.
            - ``number_of_files``: Total number of files across all datasets (int or long int).

    Example:
        >>> from brainimagelibrary import summary
        >>> report = summary.daily(option="simple")
        >>> print(type(report))
        <class 'dict'>
        >>> print(list(report.keys()))
        ['metadata_version', 'number_of_datasets', 'number_of_unique_contributors', 'contributors', 'number_of_unique_affiliations', 'affiliations', 'number_of_unique_species', 'species', 'number_of_files']
        >>> print(report["number_of_datasets"] > 0)
        True
        >>> print(report["number_of_unique_contributors"] > 0)
        True
        >>> print(report["number_of_unique_affiliations"] > 0)
        True
        >>> print(report["number_of_unique_species"] > 0)
        True
        >>> print(report["number_of_files"] > 0)
        True
    """
    report = reports.daily(option=option, overwrite=overwrite)
    return {
        "metadata_version": report["metadata_version"].value_counts(),
        "number_of_datasets": len(report),
        "number_of_unique_contributors": report["contributor"].nunique(),
        "number_of_unique_affiliations": report["affiliation"].nunique(),
        "number_of_unique_species": report["species"].nunique(),
        "number_of_files": int(report["number_of_files"].sum()),
    }
