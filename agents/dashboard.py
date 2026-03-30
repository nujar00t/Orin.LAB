"""
Orin.LAB · Terminal Dashboard
Live Rich dashboard showing token prices, signals, and portfolio summary.
"""

from __future__ import annotations

import time
import httpx
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from utils.helpers import format_price, format_pct, format_signal_badge
from utils.cache import price_cache, signal_cache

console = Console()

JUPITER_PRICE_API = "https://price.jup.ag/v6/price"

TOKENS = {
    "SOL":  "So11111111111111111111111111111111111111112",
    "JUP":  "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF":  "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
}


def fetch_prices() -> dict[str, float]:
    ids = ",".join(TOKENS.values())
    try:
        resp = httpx.get(f"{JUPITER_PRICE_API}?ids={ids}", timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {sym: float(data.get(mint, {}).get("price", 0)) for sym, mint in TOKENS.items()}
    except Exception:
        return {sym: price_cache.get(f"price:{sym}") or 0.0 for sym in TOKENS}


def build_price_table(prices: dict[str, float]) -> Table:
    table = Table(
        title="[bold cyan]Live Prices[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        show_footer=False,
    )
    table.add_column("Token", style="bold white", width=8)
    table.add_column("Price", justify="right", width=14)
    table.add_column("Signal", justify="center", width=12)
    table.add_column("Confidence", justify="right", width=12)

    for symbol, price in prices.items():
        sig_text = signal_cache.get(f"signal:{symbol}") or ""
        badge = format_signal_badge(sig_text) if sig_text else "[dim]–[/dim]"
        conf_raw = ""
        if sig_text:
            import re
            m = re.search(r"Confidence:\s*(\d+)", sig_text)
            conf_raw = f"{m.group(1)}/100" if m else "–"

        color = "green" if price > 0 else "red"
        table.add_row(
            f"[bold]{symbol}[/bold]",
            f"[{color}]{format_price(price)}[/{color}]",
            badge,
            conf_raw or "[dim]–[/dim]",
        )

    return table


def build_header() -> Panel:
    text = Text.assemble(
        ("Orin", "bold cyan"),
        (".", "white"),
        ("LAB", "bold yellow"),
        ("  ·  Terminal Dashboard", "dim"),
    )
    return Panel(text, border_style="cyan", padding=(0, 2))


def run():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=1),
    )

    with Live(layout, console=console, refresh_per_second=0.5, screen=True):
        while True:
            prices = fetch_prices()
            for sym, price in prices.items():
                price_cache.set(f"price:{sym}", price, ttl=30)

            layout["header"].update(build_header())
            layout["body"].update(Panel(build_price_table(prices), border_style="dim"))
            layout["footer"].update(
                Panel(
                    f"[dim]Updated: {time.strftime('%H:%M:%S')}  ·  Press Ctrl+C to exit[/dim]",
                    border_style="dim",
                    padding=0,
                )
            )
            time.sleep(15)


if __name__ == "__main__":
    run()