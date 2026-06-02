import argparse


def build_request_parser() -> argparse.ArgumentParser:
    """Parser used when no subcommand is detected (request / wizard mode)."""
    parser = argparse.ArgumentParser(
        prog="curlcmd",
        description="CurlCommander — visual HTTP request builder and curl generator",
    )
    parser.add_argument("url", nargs="?", help="Target URL")
    parser.add_argument("-X", "--method", default="GET", metavar="METHOD", help="HTTP method (default: GET)")
    parser.add_argument("-H", "--header", action="append", dest="headers", default=[], metavar="Key: Value", help="Header (repeatable)")
    parser.add_argument("-p", "--param", action="append", dest="params", default=[], metavar="key=value", help="Query param (repeatable)")
    parser.add_argument("-b", "--body", default="", help="Request body as string")
    parser.add_argument("--body-file", metavar="PATH", help="Read request body from file")
    parser.add_argument("--json", dest="json_body", metavar="JSON", help="JSON body (sets Content-Type automatically)")
    parser.add_argument("--form", dest="form_body", metavar="DATA", help="Form-urlencoded body")
    parser.add_argument("--auth-bearer", metavar="TOKEN", help="Bearer token")
    parser.add_argument("--auth-basic", metavar="USER:PASS", help="Basic auth credentials")
    parser.add_argument("--auth-apikey", metavar="'Header: Value'", help="API key auth")
    parser.add_argument("--no-redirect", action="store_true", help="Do not follow redirects")
    parser.add_argument("--no-verify", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("--timeout", type=float, default=30.0, metavar="SECONDS", help="Request timeout (default: 30)")
    parser.add_argument("--curl-only", action="store_true", help="Print curl command without sending")
    parser.add_argument("--save", action="store_true", help="Save to history even with --curl-only")
    parser.add_argument("--gui", action="store_true", help="Launch the Textual TUI")
    return parser


def build_subcommand_parser() -> argparse.ArgumentParser:
    """Parser used when a subcommand (history, replay, curl, clear-history) is detected."""
    parser = argparse.ArgumentParser(
        prog="curlcmd",
        description="CurlCommander — subcommands",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    subparsers.add_parser("history", help="List request history")

    replay_p = subparsers.add_parser("replay", help="Replay a history entry by ID")
    replay_p.add_argument("id", type=int, help="History entry ID")

    curl_p = subparsers.add_parser("curl", help="Print curl command for a history entry")
    curl_p.add_argument("id", type=int, help="History entry ID")

    export_p = subparsers.add_parser("export-history", help="Export history to JSON")
    export_p.add_argument("-o", "--output", default="history.json", metavar="PATH", help="Output JSON file path")

    subparsers.add_parser("clear-history", help="Clear all history")

    return parser


SUBCOMMANDS: frozenset[str] = frozenset({"history", "replay", "curl", "export-history", "clear-history"})
