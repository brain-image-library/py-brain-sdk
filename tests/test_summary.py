import io
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
import requests

from brainimagelibrary import summary


SAMPLE_TSV_CONTENT = (
    "bildid\tcontributor\taffiliation\tspecies\tmetadata_version\tnumber_of_files\n"
    "act-bag\tJohn Doe\tCMU\tMus musculus\t2.0\t42\n"
    "xyz-abc\tJane Smith\tPitt\tMus musculus\t1.0\t10\n"
)

SAMPLE_DF = pd.read_csv(io.StringIO(SAMPLE_TSV_CONTENT), sep="\t")


def make_mock_response(content=b"", status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.content = content
    return mock


# --- load() ---

def test_load_reads_from_bil_path_when_exists(tmp_path):
    tsv_file = tmp_path / "20240101.tsv"
    tsv_file.write_text(SAMPLE_TSV_CONTENT)
    with patch("brainimagelibrary.summary.Path") as mock_path_cls:
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_cls.return_value = mock_path_instance
        with patch("brainimagelibrary.summary.pd.read_csv", return_value=SAMPLE_DF) as mock_read:
            result = summary.load("20240101")
    assert result is not None
    mock_read.assert_called_once()


def test_load_downloads_when_bil_path_missing(tmp_path):
    with patch("brainimagelibrary.summary.Path") as mock_path_cls, \
         patch("brainimagelibrary.summary.requests.get") as mock_get, \
         patch("builtins.open", mock_open()), \
         patch("brainimagelibrary.summary.pd.read_csv", return_value=SAMPLE_DF):
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_cls.return_value = mock_path_instance
        mock_get.return_value = make_mock_response(
            content=SAMPLE_TSV_CONTENT.encode(), status_code=200
        )
        result = summary.load("20240101")
    assert result is not None


def test_load_returns_none_when_download_fails(caplog):
    import logging
    with patch("brainimagelibrary.summary.Path") as mock_path_cls, \
         patch("brainimagelibrary.summary.requests.get") as mock_get, \
         caplog.at_level(logging.WARNING, logger="brainimagelibrary.summary"):
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_cls.return_value = mock_path_instance
        mock_get.return_value = make_mock_response(status_code=404)
        result = summary.load("19000101")
    assert result is None
    assert "unavailable" in caplog.text


def test_load_returns_none_on_request_exception(caplog):
    import logging
    with patch("brainimagelibrary.summary.Path") as mock_path_cls, \
         patch("brainimagelibrary.summary.requests.get") as mock_get, \
         caplog.at_level(logging.WARNING, logger="brainimagelibrary.summary"):
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_cls.return_value = mock_path_instance
        mock_get.side_effect = requests.exceptions.RequestException("timeout")
        result = summary.load("20240101")
    assert result is None
    assert "unavailable" in caplog.text


# --- daily() ---

def test_daily_returns_dict_with_expected_keys():
    with patch("brainimagelibrary.summary.reports.daily", return_value=SAMPLE_DF):
        result = summary.daily(option="simple")
    expected_keys = {
        "metadata_version",
        "number_of_datasets",
        "number_of_unique_contributors",
        "number_of_unique_affiliations",
        "number_of_unique_species",
        "number_of_files",
    }
    assert set(result.keys()) == expected_keys


def test_daily_counts_datasets():
    with patch("brainimagelibrary.summary.reports.daily", return_value=SAMPLE_DF):
        result = summary.daily()
    assert result["number_of_datasets"] == 2


def test_daily_counts_unique_contributors():
    with patch("brainimagelibrary.summary.reports.daily", return_value=SAMPLE_DF):
        result = summary.daily()
    assert result["number_of_unique_contributors"] == 2


def test_daily_counts_unique_affiliations():
    with patch("brainimagelibrary.summary.reports.daily", return_value=SAMPLE_DF):
        result = summary.daily()
    assert result["number_of_unique_affiliations"] == 2


def test_daily_counts_unique_species():
    with patch("brainimagelibrary.summary.reports.daily", return_value=SAMPLE_DF):
        result = summary.daily()
    assert result["number_of_unique_species"] == 1  # both rows are Mus musculus


def test_daily_sums_number_of_files():
    with patch("brainimagelibrary.summary.reports.daily", return_value=SAMPLE_DF):
        result = summary.daily()
    assert result["number_of_files"] == 52  # 42 + 10


def test_daily_passes_option_and_overwrite_to_reports():
    with patch("brainimagelibrary.summary.reports.daily", return_value=SAMPLE_DF) as mock_daily:
        summary.daily(option="detailed", overwrite=True)
    mock_daily.assert_called_once_with(option="detailed", overwrite=True)
