import time

import httpx

from curlcommander.core.auth_handler import resolve_auth
from curlcommander.core.request_model import RequestConfig, ResponseResult


async def send(config: RequestConfig) -> ResponseResult:
    resolved = resolve_auth(config)

    auth: tuple[str, str] | None = None
    if config.auth_type == "basic" and ":" in config.auth_value:
        username, password = config.auth_value.split(":", 1)
        auth = (username, password)

    content: bytes | None = None
    if resolved.body:
        content = resolved.body.encode()
        if resolved.body_type == "json" and "Content-Type" not in resolved.headers:
            resolved.headers["Content-Type"] = "application/json"
        elif resolved.body_type == "form" and "Content-Type" not in resolved.headers:
            resolved.headers["Content-Type"] = "application/x-www-form-urlencoded"

    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            verify=resolved.verify_ssl,
            follow_redirects=resolved.follow_redirects,
            timeout=resolved.timeout,
        ) as client:
            response = await client.request(
                method=resolved.method,
                url=resolved.url,
                headers=resolved.headers,
                params=resolved.params,
                content=content,
                auth=auth,
            )

        elapsed_ms = (time.perf_counter() - start) * 1000

        return ResponseResult(
            status_code=response.status_code,
            reason=response.reason_phrase,
            headers=dict(response.headers),
            body=response.text,
            content_type=response.headers.get("content-type", ""),
            duration_ms=elapsed_ms,
            size_bytes=len(response.content),
            error=None,
        )

    except httpx.RequestError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ResponseResult(
            status_code=None,
            reason="",
            headers={},
            body="",
            content_type="",
            duration_ms=elapsed_ms,
            size_bytes=0,
            error=str(exc),
        )
