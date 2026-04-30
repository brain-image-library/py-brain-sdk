"""Shared low-level API utilities for the brainimagelibrary package."""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BIL_API_BASE = "https://api.brainimagelibrary.org"
DOWNLOAD_BASE = "https://download.brainimagelibrary.org"

_NOT_FOUND_MESSAGE = "GET failure, no entry found"


def _fetch(
    url: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Optional[dict]:
    """
    Send a GET request to *url* and return the parsed JSON body.

    Returns:
        dict: Parsed JSON on success.
        dict: An empty dict when the API reports no matching entry.
        None: When the HTTP request itself fails.
    """
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data.get("message") == _NOT_FOUND_MESSAGE:
            return {}
        return data
    except requests.exceptions.RequestException as exc:
        logger.error("API request failed (%s): %s", url, exc)
        return None
