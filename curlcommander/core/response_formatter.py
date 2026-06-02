import json


def format_body(body: str, content_type: str) -> str:
    """Return body string formatted for display based on content-type."""
    ct = content_type.lower()

    if "json" in ct:
        try:
            parsed = json.loads(body)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            return body

    return body


def get_lexer(content_type: str) -> str:
    """Return a pygments/rich lexer name for the given content-type."""
    ct = content_type.lower()
    if "json" in ct:
        return "json"
    if "html" in ct:
        return "html"
    if "xml" in ct:
        return "xml"
    return "text"
