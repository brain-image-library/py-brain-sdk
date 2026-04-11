import pytest
from unittest.mock import patch, MagicMock
import requests

import brainimagelibrary.query as query


VALID_RESPONSE = {"retjson": [{"bildid": "act-bag", "title": "Test Dataset"}]}
NOT_FOUND_RESPONSE = {"message": "GET failure, no entry found"}

# Patch target: requests.get lives in _api after the refactor
_PATCH = "brainimagelibrary._api.requests.get"


def make_mock_response(json_data, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


# --- by_id ---

def test_by_id_returns_empty_dict_when_no_bildid():
    assert query.by_id() == {}
    assert query.by_id(bildid=None) == {}


def test_by_id_returns_metadata_on_success():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        result = query.by_id(bildid="act-bag")
    assert result == VALID_RESPONSE
    assert "bildid=act-bag" in mock_get.call_args[0][0]
    assert "/query?" in mock_get.call_args[0][0]


def test_by_id_returns_empty_dict_when_not_found():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(NOT_FOUND_RESPONSE)
        result = query.by_id(bildid="nonexistent")
    assert result == {}


def test_by_id_returns_none_on_request_exception():
    with patch(_PATCH) as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("network error")
        result = query.by_id(bildid="act-bag")
    assert result is None


# --- by_directory ---

def test_by_directory_returns_empty_dict_when_no_directory():
    assert query.by_directory() == {}


def test_by_directory_returns_metadata_on_success():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        result = query.by_directory(directory="/bil/data/2019/02/13/H19.28.012")
    assert result == VALID_RESPONSE
    assert "bildirectory=" in mock_get.call_args[0][0]
    assert "/query?" in mock_get.call_args[0][0]


def test_by_directory_returns_empty_dict_when_not_found():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(NOT_FOUND_RESPONSE)
        result = query.by_directory(directory="/bil/data/missing")
    assert result == {}


def test_by_directory_returns_none_on_request_exception():
    with patch(_PATCH) as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("timeout")
        result = query.by_directory(directory="/bil/data/2019/02/13/H19.28.012")
    assert result is None


# --- by_url ---

def test_by_url_returns_empty_dict_when_no_url():
    assert query.by_url() == {}


def test_by_url_delegates_to_by_directory():
    url = "https://download.brainimagelibrary.org/2019/02/13/H19.28.012"
    expected_directory = "/bil/data/2019/02/13/H19.28.012"
    with patch("brainimagelibrary.query.by_directory") as mock_by_dir:
        mock_by_dir.return_value = VALID_RESPONSE
        result = query.by_url(url=url)
    mock_by_dir.assert_called_once_with(directory=expected_directory)
    assert result == VALID_RESPONSE


# --- by_affiliation ---

def test_by_affiliation_uses_query_endpoint():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        query.by_affiliation("Carnegie Mellon University")
    assert "/query?" in mock_get.call_args[0][0]
    assert "affiliation=" in mock_get.call_args[0][0]


def test_by_affiliation_returns_empty_dict_when_not_found():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(NOT_FOUND_RESPONSE)
        result = query.by_affiliation("Unknown University")
    assert result == {}


def test_by_affiliation_returns_none_on_request_exception():
    with patch(_PATCH) as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("timeout")
        result = query.by_affiliation("Carnegie Mellon University")
    assert result is None


# --- by_text ---

def test_by_text_hits_fulltext_endpoint():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        query.by_text("mouse cortex")
    called_url = mock_get.call_args[0][0]
    assert "/query/fulltext?" in called_url
    assert "text=" in called_url


def test_by_text_returns_results_on_success():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(VALID_RESPONSE)
        result = query.by_text("mouse cortex")
    assert result == VALID_RESPONSE


def test_by_text_returns_empty_dict_when_not_found():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(NOT_FOUND_RESPONSE)
        result = query.by_text("xyzzy nothing matches")
    assert result == {}


def test_by_text_returns_none_on_request_exception():
    with patch(_PATCH) as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("timeout")
        result = query.by_text("mouse cortex")
    assert result is None


# --- by_version ---

def test_by_version_uses_query_endpoint():
    api_response = {"bildids": ["act-bag"]}
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(api_response)
        query.by_version()
    assert "/query?" in mock_get.call_args[0][0]
    assert "metadata=2.0" in mock_get.call_args[0][0]


def test_by_version_returns_list_of_ids():
    api_response = {"bildids": ["act-bag", "xyz-abc"]}
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(api_response)
        result = query.by_version(version="1.0")
    assert result == ["act-bag", "xyz-abc"]


def test_by_version_returns_empty_dict_when_not_found():
    with patch(_PATCH) as mock_get:
        mock_get.return_value = make_mock_response(NOT_FOUND_RESPONSE)
        result = query.by_version(version="99.0")
    assert result == {}


def test_by_version_returns_none_on_request_exception():
    with patch(_PATCH) as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("timeout")
        result = query.by_version()
    assert result is None
