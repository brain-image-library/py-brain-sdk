"""Shared low-level API utilities for the brainimagelibrary package."""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BIL_API_BASE = "https://api.brainimagelibrary.org"
DOWNLOAD_BASE = "https://download.brainimagelibrary.org"

_NOT_FOUND_MESSAGE = "GET failure, no entry found"

UNREACHABLE_MESSAGE = (
    "Brain Image Library is unreachable at the moment. Please check "
    "https://www.brainimagelibrary.org/datacentermove.html for more information"
)


def _is_server_error(status_code: int) -> bool:
    """Return True when *status_code* means the server could not serve the request."""
    return status_code >= 500


def _report_unreachable(url: str, reason: object) -> None:
    """Log why *url* could not be retrieved and tell the user BIL is unreachable."""
    logger.error("Could not retrieve %s: %s", url, reason)
    print(UNREACHABLE_MESSAGE)


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
