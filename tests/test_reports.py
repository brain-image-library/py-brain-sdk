import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
import requests

from brainimagelibrary import reports


SAMPLE_DF = pd.DataFrame([
    {"bildid": "act-bag", "metadata_version": "2.0", "contributor": "Alice",
     "affiliation": "CMU", "species": "Mus musculus", "generalmodality": "LM",
     "number_of_files": 10, "size": 1024},
    {"bildid": "xyz-abc", "metadata_version": "1.0", "contributor": "Bob",
     "affiliation": "Pitt", "species": "Homo sapiens", "generalmodality": "EM",
     "number_of_files": 5, "size": 512},
])


def make_mock_response(content=b"", status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.content = content
    return mock


# --- get_all_bildids ---

def test_get_all_bildids_returns_combined_deduplicated_list():
    v1_ids = ["aaa-bbb", "ccc-ddd"]
    v2_ids = ["ccc-ddd", "eee-fff"]  # ccc-ddd is a duplicate
    with patch("brainimagelibrary.reports.by_version") as mock_bv:
        mock_bv.side_effect = lambda version: v1_ids if version == "1.0" else v2_ids
        result = reports.get_all_bildids()
    assert result == ["aaa-bbb", "ccc-ddd", "eee-fff"]
    assert len(result) == 3


def test_get_all_bildids_preserves_order():
    v1_ids = ["zzz", "aaa"]
    v2_ids = ["bbb"]
    with patch("brainimagelibrary.reports.by_version") as mock_bv:
        mock_bv.side_effect = lambda version: v1_ids if version == "1.0" else v2_ids
        result = reports.get_all_bildids()
    assert result[0] == "zzz"
    assert result[1] == "aaa"
    assert result[2] == "bbb"


def test_get_all_bildids_handles_empty_versions():
    with patch("brainimagelibrary.reports.by_version") as mock_bv:
        mock_bv.return_value = []
        result = reports.get_all_bildids()
    assert result == []


# --- daily ---

def test_daily_raises_value_error_for_invalid_option():
    with pytest.raises(ValueError, match="Invalid option"):
        reports.daily(option="invalid")


def test_daily_loads_from_local_json_when_exists():
    with patch("brainimagelibrary.reports.Path.exists", return_value=True), \
         patch("brainimagelibrary.reports.pd.read_json", return_value=SAMPLE_DF) as mock_read:
        result = reports.daily(option="simple", overwrite=False)
    mock_read.assert_called_once()
    assert isinstance(result, pd.DataFrame)


def test_daily_skips_local_json_when_overwrite_true():
    tsv_content = SAMPLE_DF.to_csv(sep="\t", index=False).encode()
    mock_resp = make_mock_response(content=tsv_content, status_code=200)
    with patch("brainimagelibrary.reports.Path.exists", return_value=True), \
         patch("brainimagelibrary.reports.requests.get", return_value=mock_resp), \
         patch("builtins.open", mock_open()), \
         patch("brainimagelibrary.reports.pd.read_csv", return_value=SAMPLE_DF):
        result = reports.daily(option="simple", overwrite=True)
    assert isinstance(result, pd.DataFrame)


def test_daily_downloads_simple_report_on_success():
    tsv_content = SAMPLE_DF.to_csv(sep="\t", index=False).encode()
    mock_resp = make_mock_response(content=tsv_content, status_code=200)
    with patch("brainimagelibrary.reports.Path.exists", return_value=False), \
         patch("brainimagelibrary.reports.requests.get", return_value=mock_resp), \
         patch("builtins.open", mock_open()), \
         patch("brainimagelibrary.reports.pd.read_csv", return_value=SAMPLE_DF) as mock_read:
        result = reports.daily(option="simple")
    mock_read.assert_called_once()
    assert isinstance(result, pd.DataFrame)


def test_daily_downloads_detailed_report_on_success():
    tsv_content = SAMPLE_DF.to_csv(sep="\t", index=False).encode()
    mock_resp = make_mock_response(content=tsv_content, status_code=200)
    with patch("brainimagelibrary.reports.Path.exists", return_value=False), \
         patch("brainimagelibrary.reports.requests.get", return_value=mock_resp) as mock_get, \
         patch("builtins.open", mock_open()), \
         patch("brainimagelibrary.reports.pd.read_csv", return_value=SAMPLE_DF) as mock_read:
        result = reports.daily(option="detailed")
    mock_read.assert_called_once()
    assert isinstance(result, pd.DataFrame)
    called_url = mock_get.call_args[0][0]
    assert "today.tsv" in called_url


def test_daily_falls_back_to_build_when_download_fails():
    mock_resp = make_mock_response(status_code=404)
    with patch("brainimagelibrary.reports.Path.exists", return_value=False), \
         patch("brainimagelibrary.reports.requests.get", return_value=mock_resp), \
         patch("brainimagelibrary.reports._create_daily_report", return_value=SAMPLE_DF) as mock_build:
        result = reports.daily(option="simple")
    mock_build.assert_called_once()
    assert isinstance(result, pd.DataFrame)


def test_daily_falls_back_to_build_on_request_exception():
    with patch("brainimagelibrary.reports.Path.exists", return_value=False), \
         patch("brainimagelibrary.reports.requests.get",
               side_effect=requests.exceptions.RequestException("timeout")), \
         patch("brainimagelibrary.reports._create_daily_report", return_value=SAMPLE_DF) as mock_build:
        result = reports.daily(option="simple")
    mock_build.assert_called_once()
    assert isinstance(result, pd.DataFrame)
