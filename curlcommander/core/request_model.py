from dataclasses import dataclass, field


@dataclass
class RequestConfig:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)
    body: str = ""
    body_type: str = "none"   # "json" | "form" | "raw" | "none"
    auth_type: str = "none"   # "none" | "bearer" | "basic" | "apikey"
    auth_value: str = ""      # token | user:pass | "Header: Value"
    follow_redirects: bool = True
    verify_ssl: bool = True
    timeout: float = 30.0


@dataclass
class ResponseResult:
    status_code: int | None
    reason: str
    headers: dict[str, str]
    body: str
    content_type: str
    duration_ms: float
    size_bytes: int
    error: str | None


@dataclass
class HistoryEntry:
    id: int
    timestamp: str
    request: RequestConfig
    status_code: int | None
    duration_ms: float
    curl_cmd: str
