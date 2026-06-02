from curlcommander.core.request_model import HistoryEntry, RequestConfig, ResponseResult


def test_request_config_defaults():
    config = RequestConfig(method="GET", url="https://example.com")
    assert config.headers == {}
    assert config.params == {}
    assert config.body == ""
    assert config.body_type == "none"
    assert config.auth_type == "none"
    assert config.auth_value == ""
    assert config.follow_redirects is True
    assert config.verify_ssl is True
    assert config.timeout == 30.0


def test_request_config_custom():
    config = RequestConfig(
        method="POST",
        url="https://api.example.com",
        headers={"X-Custom": "value"},
        body='{"key": "val"}',
        body_type="json",
        auth_type="bearer",
        auth_value="tok",
        verify_ssl=False,
        timeout=10.0,
    )
    assert config.method == "POST"
    assert config.headers["X-Custom"] == "value"
    assert config.verify_ssl is False
    assert config.timeout == 10.0


def test_response_result_ok():
    result = ResponseResult(
        status_code=200,
        reason="OK",
        headers={"content-type": "application/json"},
        body='{"a": 1}',
        content_type="application/json",
        duration_ms=42.0,
        size_bytes=8,
        error=None,
    )
    assert result.status_code == 200
    assert result.error is None


def test_response_result_error():
    result = ResponseResult(
        status_code=None,
        reason="",
        headers={},
        body="",
        content_type="",
        duration_ms=0.0,
        size_bytes=0,
        error="Connection refused",
    )
    assert result.status_code is None
    assert result.error == "Connection refused"


def test_history_entry():
    config = RequestConfig(method="GET", url="https://example.com")
    entry = HistoryEntry(
        id=1,
        timestamp="2024-01-01T00:00:00",
        request=config,
        status_code=200,
        duration_ms=55.0,
        curl_cmd="curl -L -s -i -X GET 'https://example.com'",
    )
    assert entry.id == 1
    assert entry.request.url == "https://example.com"
