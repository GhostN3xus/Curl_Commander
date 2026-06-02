from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widget import Widget
from textual.widgets import Label, Static
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from curlcommander.core.request_model import ResponseResult
from curlcommander.core.response_formatter import format_body, get_lexer


class ResponsePanel(Widget):
    DEFAULT_CSS = """
    ResponsePanel {
        height: 2fr;
        border: round $success;
        padding: 0 1;
        overflow-y: auto;
    }
    ResponsePanel Label {
        text-style: bold;
        color: $text-muted;
    }
    #response-body-scroll {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Response")
        yield Static("", id="response-status")
        yield Static("", id="response-headers")
        with ScrollableContainer(id="response-body-scroll"):
            yield Static("", id="response-body")

    def show_result(self, result: ResponseResult) -> None:
        if result.error:
            self.query_one("#response-status", Static).update(
                Text(f"Error: {result.error}", style="bold red")
            )
            self.query_one("#response-headers", Static).update("")
            self.query_one("#response-body", Static).update("")
            return

        style = _status_style(result.status_code)
        status_text = Text()
        status_text.append(f"{result.status_code} {result.reason}", style=f"bold {style}")
        status_text.append(f"   {result.duration_ms:.0f} ms  {result.size_bytes} B", style="dim")
        self.query_one("#response-status", Static).update(status_text)

        header_table = Table(show_header=True, header_style="bold dim", box=None, padding=(0, 1))
        header_table.add_column("Header", style="cyan", no_wrap=True)
        header_table.add_column("Value")
        for k, v in result.headers.items():
            header_table.add_row(k, v)
        self.query_one("#response-headers", Static).update(header_table)

        if result.body:
            formatted = format_body(result.body, result.content_type)
            lexer = get_lexer(result.content_type)
            self.query_one("#response-body", Static).update(
                Syntax(formatted, lexer, theme="monokai", word_wrap=True)
            )
        else:
            self.query_one("#response-body", Static).update("")

    def clear(self) -> None:
        for id_ in ("#response-status", "#response-headers", "#response-body"):
            self.query_one(id_, Static).update("")


def _status_style(status_code: int | None) -> str:
    if status_code is None:
        return "red"
    if status_code < 300:
        return "green"
    if status_code < 400:
        return "yellow"
    return "red"
