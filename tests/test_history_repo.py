import pytest

from curlcommander.core.request_model import HistoryEntry, RequestConfig
from curlcommander.storage.history_repo import HistoryRepo


@pytest.fixture
def repo():
    return HistoryRepo(db_path=":memory:")


def _make_entry(method: str = "GET", url: str = "https://example.com", status: int = 200) -> HistoryEntry:
    return HistoryEntry(
        id=0,
        timestamp="2024-01-01T12:00:00",
        request=RequestConfig(method=method, url=url),
        status_code=status,
        duration_ms=42.0,
        curl_cmd=f"curl -L -s -i -X {method} '{url}'",
    )


def test_save_returns_positive_id(repo):
    id_ = repo.save(_make_entry())
    assert id_ > 0


def test_load_returns_saved_entry(repo):
    repo.save(_make_entry(url="https://example.com"))
    entries = repo.load()
    assert len(entries) == 1
    assert entries[0].request.url == "https://example.com"


def test_load_ordered_newest_first(repo):
    repo.save(_make_entry(url="https://first.com"))
    repo.save(_make_entry(url="https://second.com"))
    entries = repo.load()
    assert entries[0].request.url == "https://second.com"
    assert entries[1].request.url == "https://first.com"


def test_load_respects_limit(repo):
    for i in range(5):
        repo.save(_make_entry(url=f"https://example.com/{i}"))
    entries = repo.load(limit=3)
    assert len(entries) == 3


def test_get_by_id(repo):
    id_ = repo.save(_make_entry(method="POST", url="https://api.com"))
    entry = repo.get_by_id(id_)
    assert entry is not None
    assert entry.id == id_
    assert entry.request.method == "POST"
    assert entry.request.url == "https://api.com"


def test_get_by_id_missing_returns_none(repo):
    assert repo.get_by_id(9999) is None


def test_clear_removes_all(repo):
    repo.save(_make_entry())
    repo.save(_make_entry())
    repo.clear()
    assert repo.load() == []


def test_headers_and_params_round_trip(repo):
    config = RequestConfig(
        method="GET",
        url="https://example.com",
        headers={"Authorization": "Bearer tok", "Accept": "application/json"},
        params={"page": "1", "limit": "10"},
    )
    entry = HistoryEntry(
        id=0,
        timestamp="2024-06-01T00:00:00",
        request=config,
        status_code=200,
        duration_ms=100.0,
        curl_cmd="",
    )
    id_ = repo.save(entry)
    fetched = repo.get_by_id(id_)
    assert fetched is not None
    assert fetched.request.headers["Authorization"] == "Bearer tok"
    assert fetched.request.params["page"] == "1"


def test_delete_by_id(repo):
    id_ = repo.save(_make_entry())
    repo.delete_by_id(id_)
    assert repo.get_by_id(id_) is None
    assert repo.load() == []


def test_null_status_preserved(repo):
    entry = _make_entry(status=None)
    id_ = repo.save(entry)
    fetched = repo.get_by_id(id_)
    assert fetched.status_code is None
