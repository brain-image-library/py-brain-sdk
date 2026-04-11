import gzip
import io
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
import requests

from brainimagelibrary import inventory
from brainimagelibrary.inventory import DatasetInventory


SAMPLE_INVENTORY = {
    "number_of_files": 3,
    "size": 1024,
    "pretty_size": "1.0 KB",
    "manifest": [
        {"extension": "tif", "size": 512, "download_url": "https://download.brainimagelibrary.org/act-bag/file1.tif", "md5": "abc123", "sha256": "def456", "xxh64": "ghi789", "b2sum": "jkl012"},
        {"extension": "tif", "size": 256, "download_url": "https://download.brainimagelibrary.org/act-bag/file2.tif", "md5": "bcd234", "sha256": "efg567", "xxh64": "hij890", "b2sum": "klm123"},
        {"extension": "json", "size": 256, "download_url": "https://download.brainimagelibrary.org/act-bag/meta.json", "md5": "cde345", "sha256": "fgh678", "xxh64": "ijk901", "b2sum": "lmn234"},
    ],
    "file_types": ["tif", "json"],
    "frequencies": {"tif": 2, "json": 1},
    "mime_types": {"image/tiff": 2, "application/json": 1},
}


def make_gzip_response(data):
    """Return a mock response whose .content is a valid gzip JSON payload."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json.dumps(data).encode("utf-8"))
    mock = MagicMock()
    mock.status_code = 200
    mock.content = buf.getvalue()
    return mock


def make_mock_response(status_code=200, content=b""):
    mock = MagicMock()
    mock.status_code = status_code
    mock.content = content
    return mock


# --- has() ---

def test_has_returns_false_when_no_bildid():
    assert inventory.has(bildid=None) is False
    assert inventory.has() is False


def test_has_returns_true_when_head_200():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        mock_head.return_value = MagicMock(status_code=200)
        assert inventory.has(bildid="act-bag") is True


def test_has_returns_false_when_head_404():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        mock_head.return_value = MagicMock(status_code=404)
        assert inventory.has(bildid="nonexistent") is False


def test_has_returns_false_on_request_exception():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        mock_head.side_effect = requests.exceptions.RequestException("timeout")
        assert inventory.has(bildid="act-bag") is False


# --- get() ---

def test_get_returns_none_when_no_bildid(capsys):
    assert inventory.get(bildid=None) is None
    assert inventory.get() is None


def test_get_returns_dataset_inventory_on_success():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        result = inventory.get(bildid="act-bag")
    assert isinstance(result, DatasetInventory)
    assert result["number_of_files"] == 3
    assert result["pretty_size"] == "1.0 KB"
    assert len(result["manifest"]) == 3


def test_get_returns_none_on_non_200():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=404)
        result = inventory.get(bildid="nonexistent")
    assert result is None


def test_get_returns_none_on_bad_gzip():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(status_code=200, content=b"not gzip data")
        result = inventory.get(bildid="act-bag")
    assert result is None


def test_get_returns_none_on_request_exception():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("timeout")
        result = inventory.get(bildid="act-bag")
    assert result is None


def test_get_requests_correct_url():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        inventory.get(bildid="act-bag")
    url = mock_get.call_args[0][0]
    assert "act-bag.json.gz" in url
    assert "download.brainimagelibrary.org" in url


# --- to_manifest() (module-level) ---

def test_to_manifest_returns_none_when_no_bildid(capsys):
    assert inventory.to_manifest(bildid=None) is None


def test_to_manifest_writes_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        path = inventory.to_manifest(bildid="act-bag", checksum="md5")
    assert path == "act-bag.manifest"
    manifest_file = tmp_path / "act-bag.manifest"
    assert manifest_file.exists()
    content = manifest_file.read_text()
    assert "URL" in content
    assert "md5" in content


# --- DatasetInventory.to_manifest() ---

def test_dataset_inventory_to_manifest_invalid_checksum(caplog):
    import logging
    di = DatasetInventory(SAMPLE_INVENTORY, "act-bag")
    with caplog.at_level(logging.ERROR, logger="brainimagelibrary.inventory"):
        result = di.to_manifest(checksum="crc32")
    assert result is None
    assert "checksum must be one of" in caplog.text


def test_dataset_inventory_to_manifest_valid_checksums(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    di = DatasetInventory(SAMPLE_INVENTORY, "act-bag")
    for checksum in ("md5", "sha256", "xxh64", "b2sum"):
        path = di.to_manifest(checksum=checksum)
        assert path == "act-bag.manifest"


def test_dataset_inventory_to_manifest_empty_manifest(caplog):
    import logging
    data = dict(SAMPLE_INVENTORY)
    data["manifest"] = []
    di = DatasetInventory(data, "act-bag")
    with caplog.at_level(logging.ERROR, logger="brainimagelibrary.inventory"):
        result = di.to_manifest()
    assert result is None
    assert "no manifest entries" in caplog.text.lower()


# --- summary() ---

def test_summary_returns_dict_with_expected_keys():
    with patch("brainimagelibrary.inventory.get") as mock_get:
        mock_get.return_value = DatasetInventory(SAMPLE_INVENTORY, "act-bag")
        result = inventory.summary(bildid="act-bag")
    assert result["pretty_size"] == "1.0 KB"
    assert result["size"] == 1024
    assert result["number_of_files"] == 3
    assert "frequencies" in result["files"]
    assert "types" in result["files"]
    assert "sizes" in result["files"]


def test_summary_aggregates_sizes_by_extension():
    with patch("brainimagelibrary.inventory.get") as mock_get:
        mock_get.return_value = DatasetInventory(SAMPLE_INVENTORY, "act-bag")
        result = inventory.summary(bildid="act-bag")
    sizes = result["files"]["sizes"]
    assert sizes["tif"] == 768   # 512 + 256
    assert sizes["json"] == 256
