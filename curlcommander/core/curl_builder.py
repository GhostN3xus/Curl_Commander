import shlex
from urllib.parse import urlencode

from curlcommander.core.auth_handler import resolve_auth
from curlcommander.core.request_model import RequestConfig


def build_curl(config: RequestConfig) -> str:
    """Generate a curl command string from a RequestConfig.

    Always includes -L -s -i. Uses shlex.quote on all parts for safe escaping.
    Auth is resolved into headers before building. URL goes last.
    """
    resolved = resolve_auth(config)

    parts: list[str] = ["curl", "-L", "-s", "-i"]

    if resolved.http2:
        parts.append("--http2")

    if resolved.compressed:
        parts.append("--compressed")

    if resolved.proxy:
        parts += ["-x", resolved.proxy]

    if resolved.max_retries > 0:
        parts += ["--retry", str(resolved.max_retries)]
        if resolved.retry_delay > 0:
            parts += ["--retry-delay", str(resolved.retry_delay)]

    if not resolved.verify_ssl:
        parts.append("-k")

    parts += ["-X", resolved.method]

    effective_headers = dict(resolved.headers)
    if resolved.body_type == "json" and "Content-Type" not in effective_headers:
        effective_headers["Content-Type"] = "application/json"
    elif resolved.body_type == "form" and "Content-Type" not in effective_headers:
        effective_headers["Content-Type"] = "application/x-www-form-urlencoded"

    for key, value in effective_headers.items():
        parts += ["-H", f"{key}: {value}"]

    if resolved.body:
        parts += ["--data-raw", resolved.body]

    if resolved.output_path:
        parts += ["-o", resolved.output_path]

    url = resolved.url
    if resolved.params:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{urlencode(resolved.params)}"

    parts.append(url)

    return " ".join(shlex.quote(p) for p in parts)
