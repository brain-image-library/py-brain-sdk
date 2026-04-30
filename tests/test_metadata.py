import pytest
from unittest.mock import patch, MagicMock
import requests

from brainimagelibrary import metadata


VALID_RESPONSE = {"retjson": [{"bildid": "act-bag", "title": "Test Dataset"}]}
NOT_FOUND_RESPONSE = {"message": "GET failure, no entry found"}


def make_mock_response(json_data, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


# --- get ---

def test_get_returns_empty_dict_when_no_bildid():
    assert metadata.get() == {}
    assert metadata.get(bildid=None) == {}
    assert metadata.get(bildid="") == {}


def test_get_returns_metadata_on_success():
    with patch("brainimagelibrary.metadata.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        result = metadata.get(bildid="act-bag")
    assert result == VALID_RESPONSE
    mock_get.assert_called_once()


def test_get_uses_retrieve_endpoint():
    with patch("brainimagelibrary.metadata.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        metadata.get(bildid="act-bag")
    called_url = mock_get.call_args[0][0]
    assert "/retrieve?" in called_url
    assert "bildid=act-bag" in called_url


def test_get_returns_empty_dict_when_not_found():
    with patch("brainimagelibrary.metadata.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(NOT_FOUND_RESPONSE)
        result = metadata.get(bildid="nonexistent")
    assert result == {}


def test_get_returns_none_on_request_exception():
    with patch("brainimagelibrary.metadata.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("network error")
        result = metadata.get(bildid="act-bag")
    assert result is None


def test_get_passes_params_and_headers():
    with patch("brainimagelibrary.metadata.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        metadata.get(bildid="act-bag", params={"foo": "bar"}, headers={"X-Test": "1"})
    _, kwargs = mock_get.call_args
    assert kwargs.get("params") == {"foo": "bar"}
    assert kwargs.get("headers") == {"X-Test": "1"}
