import sys
from rich.console import Console

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

console = Console(legacy_windows=False)


def color(text: str, col: str) -> str:
    return f"[{col}]{text}[/{col}]"


def bold(text: str) -> str:
    return f"[bold]{text}[/bold]"


class Indicators:
    SUCCESS = "[green]SUCCESS ✓[/green]"
    FAIL    = "[red]FAIL ✗[/red]"
    WARNING = "[yellow]WARNING ⚠[/yellow]"


status_as_text = {
    True:  Indicators.SUCCESS,
    False: Indicators.FAIL,
}
