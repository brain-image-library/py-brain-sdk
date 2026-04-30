"""Query dataset metadata from the Brain Image Library /query endpoint."""

import logging
from typing import Optional

from ._api import BIL_API_BASE, DOWNLOAD_BASE, _fetch

logger = logging.getLogger(__name__)

__all__ = ["by_id", "by_directory", "by_url", "by_affiliation", "by_text", "by_version"]

_ENDPOINT = f"{BIL_API_BASE}/query"


def by_id(
    bildid: Optional[str] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Optional[dict]:
    """
    Retrieves metadata for a dataset by its Brain Image Library ID.

    This function sends a GET request to the Brain Image Library API to fetch
    metadata for a specified dataset using its unique `bildid`.

    Args:
        bildid (str, optional): The unique identifier for the dataset. If not provided,
            the function returns an empty dictionary.
        params (dict, optional): Query parameters to include in the API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request. Defaults to None.

    Returns:
        dict: The metadata for the dataset if the request is successful.
        dict: An empty dictionary if the dataset ID is invalid or not found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.

    Example:
        >>> from brainimagelibrary import query
        >>> metadata = query.by_id(bildid="act-bag")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("retjson" in metadata)
        True
    """
    if not bildid:
        return {}
    return _fetch(f"{_ENDPOINT}?bildid={bildid}", params=params, headers=headers)


def by_directory(
    directory: Optional[str] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Optional[dict]:
    """
    Retrieves metadata for a dataset by its directory path.

    This function sends a GET request to the Brain Image Library API to fetch
    metadata for a specified dataset using its directory path.

    Args:
        directory (str, optional): The directory path of the dataset. If not provided,
            the function returns an empty dictionary.
        params (dict, optional): Query parameters to include in the API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request. Defaults to None.

    Returns:
        dict: The metadata for the dataset if the request is successful.
        dict: An empty dictionary if the directory path is invalid or not found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.

    Example:
        >>> from brainimagelibrary import query
        >>> metadata = query.by_directory(directory="/bil/data/2019/02/13/H19.28.012.MITU.01.05")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("retjson" in metadata)
        True
    """
    if not directory:
        return {}
    return _fetch(f"{_ENDPOINT}?bildirectory={directory}", params=params, headers=headers)


def by_url(url: Optional[str] = None) -> Optional[dict]:
    """
    Retrieves metadata for a dataset by its download URL.

    Converts a ``download.brainimagelibrary.org`` URL to its corresponding
    BIL filesystem path and delegates to :func:`by_directory`.

    Args:
        url (str, optional): The download URL of the dataset
            (e.g. ``"https://download.brainimagelibrary.org/2019/02/13/H19.28.012.MITU.01.05"``).
            If not provided, returns an empty dictionary.

    Returns:
        dict: The metadata for the dataset if the request is successful.
        dict: An empty dictionary if the URL is not provided or no entry is found.
        None: If the request fails or encounters an exception.

    Example:
        >>> from brainimagelibrary import query
        >>> metadata = query.by_url("https://download.brainimagelibrary.org/2019/02/13/H19.28.012.MITU.01.05")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("retjson" in metadata)
        True
    """
    if not url:
        return {}
    directory = url.replace(DOWNLOAD_BASE, "/bil/data")
    return by_directory(directory=directory)


def by_affiliation(
    affiliation: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Optional[dict]:
    """
    Retrieves datasets associated with a contributor's affiliation.

    Queries the Brain Image Library API for datasets whose contributors
    belong to the specified affiliation.

    Args:
        affiliation (str): The affiliation name to search for (e.g. a university
            or research institute).
        params (dict, optional): Additional query parameters to include in the
            API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request.
            Defaults to None.

    Returns:
        dict: The API response containing matching contributor/dataset records.
        dict: An empty dictionary if no records are found for the affiliation.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the
            API request.

    Example:
        >>> from brainimagelibrary import query
        >>> results = query.by_affiliation("Carnegie Mellon University")
        >>> print(type(results))
        <class 'dict'>
        >>> print(len(results) > 0)
        True
    """
    return _fetch(f"{_ENDPOINT}?affiliation={affiliation}", params=params, headers=headers)


def by_text(
    text: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Optional[dict]:
    """
    Performs a full-text search across Brain Image Library datasets.

    Sends a GET request to the Brain Image Library full-text search endpoint
    and returns all matching records.

    Args:
        text (str): The search string to query against the BIL index.
        params (dict, optional): Additional query parameters to include in the
            API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request.
            Defaults to None.

    Returns:
        dict: The API response containing matching dataset records.
        dict: An empty dictionary if no results are found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the
            API request.

    Example:
        >>> from brainimagelibrary import query
        >>> results = query.by_text("mouse cortex")
        >>> print(type(results))
        <class 'dict'>
        >>> print(len(results) > 0)
        True
    """
    return _fetch(f"{_ENDPOINT}/fulltext?text={text}", params=params, headers=headers)


def by_version(version: str = "2.0") -> Optional[list]:
    """
    Retrieves dataset IDs based on metadata version.

    This function sends a GET request to the Brain Image Library API to fetch
    dataset IDs associated with a specific metadata version.

    Args:
        version (str, optional): The metadata version to query. Defaults to "2.0".

    Returns:
        list: A list of dataset IDs (`bildids`) if the request is successful.
        dict: An empty dictionary if no datasets are found for the specified version.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.

    Example:
        >>> from brainimagelibrary import query
        >>> ids = query.by_version(version="1.0")
        >>> print(type(ids))
        <class 'list'>
        >>> print(len(ids) > 0)
        True
    """
    data = _fetch(f"{_ENDPOINT}/submission?metadata={version}")
    if not data:
        return data  # None (request failed) or {} (not found)
    return data.get("bildids")
