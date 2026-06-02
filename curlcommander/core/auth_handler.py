import copy

from curlcommander.core.request_model import RequestConfig


def resolve_auth(config: RequestConfig) -> RequestConfig:
    """Returns a deep copy of config with auth credentials injected into headers."""
    resolved = copy.deepcopy(config)

    match resolved.auth_type:
        case "bearer":
            resolved.headers["Authorization"] = f"Bearer {resolved.auth_value}"
        case "apikey":
            if ": " in resolved.auth_value:
                header_name, header_value = resolved.auth_value.split(": ", 1)
                resolved.headers[header_name.strip()] = header_value.strip()
        case "basic" | "none":
            pass  # basic auth is handled directly by httpx, not as a header

    return resolved
