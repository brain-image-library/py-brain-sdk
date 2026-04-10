import pytest
from unittest.mock import patch, MagicMock, call
import requests

from brainimagelibrary import dois


DATACITE_RESPONSE = {
    "data": {
        "id": "10.35077/act-bag",
        "attributes": {
            "titles": [{"title": "Test Dataset Title"}],
            "citationCount": 5,
            "relatedIdentifiers": [
                {
                    "relatedIdentifier": "https://download.brainimagelibrary.org/act/bag",
                    "relatedIdentifierType": "URL",
                }
            ],
        },
    }
}


def make_mock_response(json_data=None, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    return mock


# --- _doi_exists ---

def test_doi_exists_returns_true_on_200():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=200)
        assert dois._doi_exists(bildid="act-bag") is True


def test_doi_exists_returns_false_on_404():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        assert dois._doi_exists(bildid="nonexistent") is False


def test_doi_exists_returns_false_on_exception():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("timeout")
        assert dois._doi_exists(bildid="act-bag") is False


# --- _get_datacite_metadata ---

def test_get_datacite_metadata_returns_dict_on_200():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(DATACITE_RESPONSE, status_code=200)
        result = dois._get_datacite_metadata(bildid="act-bag")
    assert result == DATACITE_RESPONSE
    assert "data" in result


def test_get_datacite_metadata_returns_none_on_404():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        result = dois._get_datacite_metadata(bildid="nonexistent")
    assert result is None


# --- Dataset.get ---

def test_dataset_get_returns_metadata():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(DATACITE_RESPONSE, status_code=200)
        result = dois.dataset.get(bildid="act-bag")
    assert result == DATACITE_RESPONSE


# --- Dataset.exists ---

def test_dataset_exists_returns_true():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=200)
        assert dois.dataset.exists(bildid="act-bag") is True


def test_dataset_exists_returns_false():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        assert dois.dataset.exists(bildid="nonexistent") is False


# --- Dataset.get_number_of_citations ---

def test_get_number_of_citations_returns_none_keys_when_doi_missing():
    with patch("brainimagelibrary.dois._doi_exists", return_value=False):
        result = dois.dataset.get_number_of_citations(bildid="nonexistent")
    assert result == {
        "datacite": None,
        "opencitations": None,
        "crossref": None,
        "semanticscholar": None,
    }


def test_get_number_of_citations_returns_dict_with_expected_keys():
    with patch("brainimagelibrary.dois._doi_exists", return_value=True), \
         patch("brainimagelibrary.dois._get_number_of_citations_from_datacite", return_value=5), \
         patch("brainimagelibrary.dois._get_number_of_citations_from_opencitations", return_value=3), \
         patch("brainimagelibrary.dois._get_number_of_citations_from_crossref", return_value=2), \
         patch("brainimagelibrary.dois._get_number_of_citations_from_semanticscholar", return_value=1):
        result = dois.dataset.get_number_of_citations(bildid="act-bag")
    assert set(result.keys()) == {"datacite", "opencitations", "crossref", "semanticscholar"}
    assert result["datacite"] == 5
    assert result["opencitations"] == 3


# --- Dataset.get_datacite_citations ---

def test_get_datacite_citations_returns_none_keys_when_doi_missing():
    with patch("brainimagelibrary.dois._doi_exists", return_value=False):
        result = dois.dataset.get_datacite_citations(bildid="nonexistent")
    assert result == {
        "datacite": None,
        "opencitations": None,
        "crossref": None,
        "semanticscholar": None,
    }


def test_get_datacite_citations_returns_dict_with_expected_keys():
    with patch("brainimagelibrary.dois._doi_exists", return_value=True), \
         patch("brainimagelibrary.dois._get_citations_from_datacite", return_value=[]), \
         patch("brainimagelibrary.dois._get_citations_from_opencitations", return_value=[]), \
         patch("brainimagelibrary.dois._get_citations_from_crossref", return_value=None), \
         patch("brainimagelibrary.dois._get_citations_from_semanticscholar", return_value=None):
        result = dois.dataset.get_datacite_citations(bildid="act-bag")
    assert set(result.keys()) == {"datacite", "opencitations", "crossref", "semanticscholar"}


# --- Collection.exists ---

def test_collection_exists_returns_true():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=200)
        assert dois.collection.exists(bildid="act-bag") is True


def test_collection_exists_returns_false():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        assert dois.collection.exists(bildid="nonexistent") is False


# --- Collection.get ---

def test_collection_get_returns_none_when_doi_missing():
    with patch("brainimagelibrary.dois._doi_exists", return_value=False):
        result = dois.collection.get(bildid="nonexistent")
    assert result is None


def test_collection_get_returns_metadata_when_doi_exists():
    with patch("brainimagelibrary.dois._doi_exists", return_value=True), \
         patch("brainimagelibrary.dois._get_datacite_metadata", return_value=DATACITE_RESPONSE):
        result = dois.collection.get(bildid="act-bag")
    assert result == DATACITE_RESPONSE


# --- Collection.get_datasets ---

def test_collection_get_datasets_returns_empty_list_when_no_metadata():
    with patch("brainimagelibrary.dois._get_datacite_metadata", return_value=None):
        result = dois.collection.get_datasets(bildid="nonexistent")
    assert result == []


def test_collection_get_datasets_returns_empty_list_when_no_download_urls():
    metadata_no_urls = {
        "data": {
            "attributes": {
                "relatedIdentifiers": [
                    {"relatedIdentifier": "https://example.com/other", "relatedIdentifierType": "URL"}
                ]
            }
        }
    }
    with patch("brainimagelibrary.dois._get_datacite_metadata", return_value=metadata_no_urls):
        result = dois.collection.get_datasets(bildid="act-bag")
    assert result == []


# --- module-level convenience functions ---

def test_module_get_datacite_metadata_delegates():
    with patch("brainimagelibrary.dois._get_datacite_metadata", return_value=DATACITE_RESPONSE) as mock_fn:
        result = dois.get_datacite_metadata(bildid="act-bag")
    assert result == DATACITE_RESPONSE


def test_module_get_number_of_citations_delegates():
    expected = {"datacite": 5, "opencitations": 3, "crossref": 2, "semanticscholar": 1}
    with patch.object(dois.dataset, "get_number_of_citations", return_value=expected) as mock_fn:
        result = dois.get_number_of_citations(bildid="act-bag")
    assert result == expected
    mock_fn.assert_called_once_with(bildid="act-bag")


def test_module_get_datacite_citations_delegates():
    expected = {"datacite": [], "opencitations": [], "crossref": None, "semanticscholar": None}
    with patch.object(dois.dataset, "get_datacite_citations", return_value=expected) as mock_fn:
        result = dois.get_datacite_citations(bildid="act-bag")
    assert result == expected
    mock_fn.assert_called_once_with(bildid="act-bag")


# --- private citation helpers ---

def test_get_number_of_citations_from_datacite_parses_count():
    with patch("brainimagelibrary.dois._get_datacite_metadata", return_value=DATACITE_RESPONSE):
        result = dois._get_number_of_citations_from_datacite(bildid="act-bag")
    assert result == 5


def test_get_number_of_citations_from_datacite_returns_none_when_no_metadata():
    with patch("brainimagelibrary.dois._get_datacite_metadata", return_value=None):
        result = dois._get_number_of_citations_from_datacite(bildid="nonexistent")
    assert result is None


def test_get_number_of_citations_from_opencitations_parses_count():
    api_response = [{"count": "7"}]
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(api_response, status_code=200)
        result = dois._get_number_of_citations_from_opencitations(bildid="act-bag")
    assert result == 7


def test_get_number_of_citations_from_opencitations_returns_none_on_404():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        result = dois._get_number_of_citations_from_opencitations(bildid="act-bag")
    assert result is None


def test_get_number_of_citations_from_crossref_parses_count():
    api_response = {"message": {"is-referenced-by-count": 12}}
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(api_response, status_code=200)
        result = dois._get_number_of_citations_from_crossref(bildid="act-bag")
    assert result == 12


def test_get_number_of_citations_from_crossref_returns_none_on_404():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        result = dois._get_number_of_citations_from_crossref(bildid="act-bag")
    assert result is None


def test_get_number_of_citations_from_semanticscholar_parses_count():
    api_response = {"citationCount": 9}
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(api_response, status_code=200)
        result = dois._get_number_of_citations_from_semanticscholar(bildid="act-bag")
    assert result == 9


def test_get_number_of_citations_from_semanticscholar_returns_none_on_404():
    with patch("brainimagelibrary.dois.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        result = dois._get_number_of_citations_from_semanticscholar(bildid="act-bag")
    assert result is None
