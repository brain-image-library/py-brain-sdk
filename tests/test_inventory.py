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


@pytest.fixture(autouse=True)
def local_json_dir(tmp_path, monkeypatch):
    """Point the local inventory directory at an empty temp dir by default."""
    monkeypatch.setattr(inventory, "LOCAL_JSON_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture(autouse=True)
def fresh_inventory_state(monkeypatch):
    """Start every test with an empty cache and no retry delays."""
    monkeypatch.setattr(inventory, "RETRY_BACKOFF", 0)
    inventory.clear_cache()
    yield
    inventory.clear_cache()


def write_local_gzip(directory, bildid, data):
    with gzip.open(directory / f"{bildid}.json.gz", "wb") as gz:
        gz.write(json.dumps(data).encode("utf-8"))


def make_mock_response(status_code=200, content=b""):
    mock = MagicMock()
    mock.status_code = status_code
    mock.content = content
    return mock


# --- exists() ---

def test_has_returns_false_when_no_bildid():
    assert inventory.exists(bildid=None) is False
    assert inventory.exists() is False


def test_has_returns_true_when_head_200():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        mock_head.return_value = MagicMock(status_code=200)
        assert inventory.exists(bildid="act-bag") is True


def test_has_returns_false_when_head_404():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        mock_head.return_value = MagicMock(status_code=404)
        assert inventory.exists(bildid="nonexistent") is False


def test_has_returns_false_on_request_exception():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        mock_head.side_effect = requests.exceptions.RequestException("timeout")
        assert inventory.exists(bildid="act-bag") is False


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



def test_get_uses_local_file_without_downloading(local_json_dir):
    write_local_gzip(local_json_dir, "act-bag", SAMPLE_INVENTORY)
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        result = inventory.get(bildid="act-bag")
    mock_get.assert_not_called()
    assert isinstance(result, DatasetInventory)
    assert result["number_of_files"] == 3


def test_get_downloads_when_local_gzip_is_bad(local_json_dir):
    (local_json_dir / "act-bag.json.gz").write_bytes(b"not gzip data")
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        result = inventory.get(bildid="act-bag")
    mock_get.assert_called_once()
    assert result["number_of_files"] == 3


def test_get_downloads_when_local_gzip_is_truncated(local_json_dir):
    write_local_gzip(local_json_dir, "act-bag", SAMPLE_INVENTORY)
    path = local_json_dir / "act-bag.json.gz"
    path.write_bytes(path.read_bytes()[:-20])
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        result = inventory.get(bildid="act-bag")
    mock_get.assert_called_once()
    assert result["number_of_files"] == 3


def test_get_downloads_when_local_file_unreadable(local_json_dir):
    write_local_gzip(local_json_dir, "act-bag", SAMPLE_INVENTORY)
    with patch("brainimagelibrary.inventory.open", side_effect=PermissionError("denied"), create=True), \
         patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        result = inventory.get(bildid="act-bag")
    mock_get.assert_called_once()
    assert result["number_of_files"] == 3


def test_get_returns_none_on_truncated_download():
    truncated = make_gzip_response(SAMPLE_INVENTORY)
    truncated.content = truncated.content[:-20]
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = truncated
        result = inventory.get(bildid="act-bag")
    assert result is None


def test_exists_uses_local_file_without_request(local_json_dir):
    write_local_gzip(local_json_dir, "act-bag", SAMPLE_INVENTORY)
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        assert inventory.exists(bildid="act-bag") is True
    mock_head.assert_not_called()


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


# --- unreachable BIL ---

from brainimagelibrary._api import UNREACHABLE_MESSAGE


def test_get_prints_unreachable_on_timeout(capsys):
    with patch("brainimagelibrary.inventory.requests.get",
               side_effect=requests.exceptions.Timeout("timed out")):
        assert inventory.get(bildid="act-bag") is None
    assert UNREACHABLE_MESSAGE in capsys.readouterr().out


def test_get_prints_unreachable_on_server_error(capsys):
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_mock_response(status_code=503)):
        assert inventory.get(bildid="act-bag") is None
    assert UNREACHABLE_MESSAGE in capsys.readouterr().out


def test_get_does_not_print_unreachable_on_404(capsys):
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_mock_response(status_code=404)):
        assert inventory.get(bildid="act-bag") is None
    assert UNREACHABLE_MESSAGE not in capsys.readouterr().out


def test_exists_prints_unreachable_on_connection_error(capsys):
    with patch("brainimagelibrary.inventory.requests.head",
               side_effect=requests.exceptions.ConnectionError("refused")):
        assert inventory.exists(bildid="act-bag") is False
    assert UNREACHABLE_MESSAGE in capsys.readouterr().out


def test_download_prints_unreachable_once_on_timeouts(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    dataset = DatasetInventory(SAMPLE_INVENTORY, "act-bag")
    with patch("brainimagelibrary.inventory.requests.get",
               side_effect=requests.exceptions.Timeout("timed out")):
        assert dataset.download(n=2) == "act-bag"
    assert capsys.readouterr().out.count(UNREACHABLE_MESSAGE) == 1


# --- retries ---

def test_get_retries_server_error_then_succeeds():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.side_effect = [
            make_mock_response(status_code=503),
            requests.exceptions.ConnectionError("reset"),
            make_gzip_response(SAMPLE_INVENTORY),
        ]
        result = inventory.get(bildid="act-bag")
    assert mock_get.call_count == 3
    assert result["number_of_files"] == 3


def test_get_gives_up_after_max_attempts(capsys):
    with patch("brainimagelibrary.inventory.requests.get",
               side_effect=requests.exceptions.Timeout("timed out")) as mock_get:
        assert inventory.get(bildid="act-bag") is None
    assert mock_get.call_count == inventory.MAX_ATTEMPTS
    assert capsys.readouterr().out.count(UNREACHABLE_MESSAGE) == 1


def test_get_does_not_retry_404():
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_mock_response(status_code=404)) as mock_get:
        assert inventory.get(bildid="act-bag") is None
    mock_get.assert_called_once()


# --- raise_errors ---

@pytest.mark.parametrize("response, error", [
    (make_mock_response(status_code=404), inventory.DatasetNotFound),
    (make_mock_response(status_code=503), inventory.InventoryUnavailable),
    (make_mock_response(status_code=403), inventory.InventoryError),
    (make_mock_response(status_code=200, content=b"not gzip"), inventory.InvalidInventory),
])
def test_get_raise_errors_raises_specific_exception(response, error):
    with patch("brainimagelibrary.inventory.requests.get", return_value=response):
        with pytest.raises(error):
            inventory.get(bildid="act-bag", raise_errors=True)


def test_get_raise_errors_on_connection_error():
    with patch("brainimagelibrary.inventory.requests.get",
               side_effect=requests.exceptions.ConnectionError("refused")):
        with pytest.raises(inventory.InventoryUnavailable):
            inventory.get(bildid="act-bag", raise_errors=True)


# --- bildid validation ---

@pytest.mark.parametrize("bildid", ["", "../etc", "a/b", "..", ".hidden", "act bag"])
def test_get_rejects_invalid_bildid_without_request(bildid):
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        assert inventory.get(bildid=bildid) is None
        with pytest.raises(inventory.InvalidBildid):
            inventory.get(bildid=bildid, raise_errors=True)
    mock_get.assert_not_called()


def test_exists_rejects_invalid_bildid_without_request():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head:
        assert inventory.exists(bildid="../etc") is False
    mock_head.assert_not_called()


# --- content validation ---

def test_get_returns_none_when_inventory_is_not_an_object():
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_gzip_response([1, 2, 3])):
        assert inventory.get(bildid="act-bag") is None


def test_get_returns_none_on_deeply_nested_literal():
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(b"(" * 100000 + b")" * 100000)
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_mock_response(status_code=200, content=buf.getvalue())):
        assert inventory.get(bildid="act-bag") is None


# --- caching ---

def test_get_caches_successful_lookups():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        inventory.get(bildid="act-bag")
        inventory.get(bildid="act-bag")
    mock_get.assert_called_once()


def test_get_does_not_cache_failures():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.side_effect = [
            make_mock_response(status_code=404),
            make_gzip_response(SAMPLE_INVENTORY),
        ]
        assert inventory.get(bildid="act-bag") is None
        assert inventory.get(bildid="act-bag")["number_of_files"] == 3


def test_get_returns_independent_copies():
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_gzip_response(SAMPLE_INVENTORY)):
        first = inventory.get(bildid="act-bag")
        first["manifest"].clear()
        first.rename("other")
        second = inventory.get(bildid="act-bag")
    assert len(second["manifest"]) == 3
    assert second._bildid == "act-bag"


def test_clear_cache_forces_reload():
    with patch("brainimagelibrary.inventory.requests.get") as mock_get:
        mock_get.return_value = make_gzip_response(SAMPLE_INVENTORY)
        inventory.get(bildid="act-bag")
        inventory.clear_cache()
        inventory.get(bildid="act-bag")
    assert mock_get.call_count == 2


# --- has() / summary() ---

def test_has_does_not_send_head_request():
    with patch("brainimagelibrary.inventory.requests.head") as mock_head, \
         patch("brainimagelibrary.inventory.requests.get",
               return_value=make_gzip_response(SAMPLE_INVENTORY)):
        assert inventory.has(bildid="act-bag", option="tif") is True
        assert inventory.has(bildid="act-bag", option="xyz") is False
    mock_head.assert_not_called()


def test_has_returns_none_when_dataset_missing():
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_mock_response(status_code=404)):
        assert inventory.has(bildid="nonexistent", option="tif") is None


def test_has_returns_false_when_inventory_corrupt():
    with patch("brainimagelibrary.inventory.requests.get",
               return_value=make_mock_response(status_code=200, content=b"not gzip")):
        assert inventory.has(bildid="act-bag", option="tif") is False


def test_summary_returns_none_when_get_fails():
    with patch("brainimagelibrary.inventory.get", return_value=None):
        assert inventory.summary(bildid="act-bag") is None
