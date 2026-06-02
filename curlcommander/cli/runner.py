import asyncio
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from curlcommander.config import DB_PATH
from curlcommander.core.curl_builder import build_curl
from curlcommander.core.http_client import send
from curlcommander.core.request_model import HistoryEntry, RequestConfig
from curlcommander.core.response_formatter import format_body, get_lexer
from curlcommander.storage.history_repo import HistoryRepo

_console = Console()


def run_cli(args) -> None:
    repo = HistoryRepo(DB_PATH)

    match args.subcommand:
        case "history":
            _show_history(repo)
        case "replay":
            _replay(repo, args.id)
        case "curl":
            _show_curl_from_history(repo, args.id)
        case "export-history":
            _export_history(repo, args.output)
        case "clear-history":
            repo.clear()
            _console.print("[green]History cleared.[/green]")
        case _:
            _run_request(args, repo)


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def _show_history(repo: HistoryRepo) -> None:
    entries = repo.load()
    if not entries:
        _console.print("[dim]No history entries.[/dim]")
        return

    table = Table(title="Request History", show_lines=False)
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Timestamp")
    table.add_column("Method")
    table.add_column("URL", no_wrap=True, max_width=50)
    table.add_column("Status", justify="center")
    table.add_column("ms", justify="right")

    for entry in entries:
        style = _status_style(entry.status_code)
        table.add_row(
            str(entry.id),
            entry.timestamp,
            entry.request.method,
            entry.request.url,
            f"[{style}]{entry.status_code or 'ERR'}[/{style}]",
            f"{entry.duration_ms:.0f}",
        )

    _console.print(table)


def _replay(repo: HistoryRepo, id: int) -> None:
    entry = repo.get_by_id(id)
    if entry is None:
        _console.print(f"[red]No history entry with ID {id}.[/red]")
        return

    _console.print(f"[dim]Replaying #{id}…[/dim]")
    _execute_request(entry.request, repo)


def _show_curl_from_history(repo: HistoryRepo, id: int) -> None:
    entry = repo.get_by_id(id)
    if entry is None:
        _console.print(f"[red]No history entry with ID {id}.[/red]")
        return

    _print_curl(entry.curl_cmd)


def _export_history(repo: HistoryRepo, output: str) -> None:
    repo.export_json(output)
    _console.print(f"[green]History exported to[/green] [bold]{output}[/bold]")


# ---------------------------------------------------------------------------
# Request execution
# ---------------------------------------------------------------------------

def _run_request(args, repo: HistoryRepo) -> None:
    if not args.url:
        from curlcommander.cli.wizard import run_wizard
        config = run_wizard()
        if config is None:
            return
    else:
        config = _build_config(args)

    if args.curl_only:
        curl_cmd = build_curl(config)
        _print_curl(curl_cmd)
        if args.save:
            _persist(config, None, 0.0, curl_cmd, repo)
        return

    _execute_request(config, repo)


def _execute_request(config: RequestConfig, repo: HistoryRepo) -> None:
    curl_cmd = build_curl(config)
    _console.print(f"[dim]→ {config.method} {config.url}[/dim]")

    result = asyncio.run(send(config))

    if result.error:
        _console.print(f"[red bold]Error:[/red bold] {result.error}")
        _persist(config, None, result.duration_ms, curl_cmd, repo)
        return

    style = _status_style(result.status_code)
    status_line = Text()
    status_line.append(f"{result.status_code} {result.reason}", style=f"bold {style}")
    status_line.append(f"  {result.duration_ms:.0f} ms  {result.size_bytes} B", style="dim")
    _console.print(status_line)

    header_table = Table(show_header=True, header_style="bold dim", box=None, padding=(0, 1))
    header_table.add_column("Header", style="cyan")
    header_table.add_column("Value")
    for k, v in result.headers.items():
        header_table.add_row(k, v)
    _console.print(header_table)

    if result.body:
        formatted = format_body(result.body, result.content_type)
        _console.print(Syntax(formatted, get_lexer(result.content_type), theme="monokai", word_wrap=True))

    _persist(config, result.status_code, result.duration_ms, curl_cmd, repo)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_config(args) -> RequestConfig:
    headers: dict[str, str] = {}
    for h in args.headers:
        if ": " in h:
            k, v = h.split(": ", 1)
            headers[k.strip()] = v.strip()

    params: dict[str, str] = {}
    for p in args.params:
        if "=" in p:
            k, v = p.split("=", 1)
            params[k.strip()] = v.strip()

    body = ""
    body_type = "none"

    if args.json_body:
        body, body_type = args.json_body, "json"
    elif args.form_body:
        body, body_type = args.form_body, "form"
    elif args.body_file:
        body, body_type = Path(args.body_file).read_text(encoding="utf-8"), "raw"
    elif args.body:
        body, body_type = args.body, "raw"

    auth_type, auth_value = "none", ""
    if args.auth_bearer:
        auth_type, auth_value = "bearer", args.auth_bearer
    elif args.auth_basic:
        auth_type, auth_value = "basic", args.auth_basic
    elif args.auth_apikey:
        auth_type, auth_value = "apikey", args.auth_apikey

    return RequestConfig(
        method=args.method.upper(),
        url=args.url,
        headers=headers,
        params=params,
        body=body,
        body_type=body_type,
        auth_type=auth_type,
        auth_value=auth_value,
        follow_redirects=not args.no_redirect,
        verify_ssl=not args.no_verify,
        timeout=args.timeout,
    )


def _persist(
    config: RequestConfig,
    status_code: int | None,
    duration_ms: float,
    curl_cmd: str,
    repo: HistoryRepo,
) -> None:
    entry = HistoryEntry(
        id=0,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        request=config,
        status_code=status_code,
        duration_ms=duration_ms,
        curl_cmd=curl_cmd,
    )
    repo.save(entry)


def _print_curl(curl_cmd: str) -> None:
    _console.print(Syntax(curl_cmd, "bash", theme="monokai", word_wrap=True))


def _status_style(status_code: int | None) -> str:
    if status_code is None:
        return "red"
    if status_code < 300:
        return "green"
    if status_code < 400:
        return "yellow"
    return "red"
