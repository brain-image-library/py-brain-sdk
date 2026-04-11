"""Metadata retrieval for Brain Image Library datasets."""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

__all__ = ["get"]


def get(
    bildid: Optional[str] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Optional[dict]:
    """
    Retrieves metadata for a dataset by its Brain Image Library ID.

    Args:
        bildid (str, optional): The unique identifier for the dataset. If not provided,
            the function returns an empty dictionary.
        params (dict, optional): Additional query parameters to include in the
            API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request.
            Defaults to None.

    Returns:
        dict: The metadata for the dataset if the request is successful.
        dict: An empty dictionary if the dataset ID is invalid or not found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the
            API request.

    Example:
        >>> import brainimagelibrary
        >>> result = brainimagelibrary.metadata.get(bildid="act-bag")
        >>> print(type(result))
        <class 'dict'>
    """
    if not bildid:
        return {}

    api_url = f"https://api.brainimagelibrary.org/retrieve?bildid={bildid}"

    try:
        response = requests.get(api_url, params=params, headers=headers)
        response = response.json()
        if (
            "message" in response.keys()
            and response["message"] == "GET failure, no entry found"
        ):
            return {}
        else:
            return response

    except requests.exceptions.RequestException as e:
        logger.error("Error making API request: %s", e)
        return None
