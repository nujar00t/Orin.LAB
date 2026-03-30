"""
Orin.LAB · Signal Engine
Generate BUY/SELL/HOLD signals from on-chain data + sentiment analysis.
"""

import os
import httpx
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()

JUPITER_PRICE_API = "https://price.jup.ag/v6/price"

TOKENS = {
    "SOL":  "So11111111111111111111111111111111111111112",
    "BTC":  "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
    "ETH":  "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
    "JUP":  "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF":  "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
}

SYSTEM_PROMPT = """You are Orin, the signal engine for Orin.LAB.
Generate precise trading signals based on price data.

Always respond in this exact format:
SIGNAL: [BUY/SELL/HOLD]
Confidence: [0-100]/100
Target: $[price]
Stop Loss: $[price]
Reasoning: [2 sentences max]
Risk Level: [LOW/MEDIUM/HIGH]"""


def fetch_price(mint: str) -> float:
    try:
        resp = httpx.get(f"{JUPITER_PRICE_API}?ids={mint}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return float(data["data"].get(mint, {}).get("price", 0))
    except Exception:
        return 0.0


def generate_signal(symbol: str, price: float) -> str:
    if price == 0:
        return "Unable to fetch price data."
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Generate signal for {symbol} at current price ${price:.4f}"
        }]
    )
    return response.content[0].text


def run():
    console.print(Panel.fit(
        "[bold cyan]Orin.LAB[/bold cyan] · [yellow]Signal Engine[/yellow]\n"
        "[dim]On-chain + AI powered trading signals[/dim]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold]Options:[/bold]")
        console.print("  [cyan]1[/cyan] Generate signal for a token")
        console.print("  [cyan]2[/cyan] Scan all tokens")
        console.print("  [cyan]q[/cyan] Quit")

        choice = Prompt.ask("\nChoose", choices=["1", "2", "q"])

        if choice == "q":
            break

        elif choice == "1":
            symbol = Prompt.ask("Token (e.g. SOL)").upper()
            mint = TOKENS.get(symbol)
            if not mint:
                mint = Prompt.ask(f"Mint address for {symbol}")

            with console.status(f"[dim]Fetching {symbol} price...[/dim]", spinner="dots"):
                price = fetch_price(mint)

            with console.status("[dim]Generating signal with AI...[/dim]", spinner="dots"):
                signal = generate_signal(symbol, price)

            console.print(Panel(
                f"[bold white]{signal}[/bold white]",
                title=f"[bold cyan]Orin.LAB Signal: ${symbol}[/bold cyan]",
                border_style="yellow",
                box=box.ROUNDED,
            ))

        elif choice == "2":
            table = Table(title="Token Scan", border_style="cyan", box=box.ROUNDED)
            table.add_column("Token", style="cyan")
            table.add_column("Price", justify="right")
            table.add_column("Signal", justify="center")

            for symbol, mint in TOKENS.items():
                with console.status(f"[dim]Scanning {symbol}...[/dim]", spinner="dots"):
                    price = fetch_price(mint)
                    if price > 0:
                        sig = generate_signal(symbol, price)
                        sig_line = sig.split("\n")[0] if sig else "N/A"
                        color = "green" if "BUY" in sig_line else "red" if "SELL" in sig_line else "yellow"
                        table.add_row(symbol, f"${price:.4f}", f"[{color}]{sig_line}[/{color}]")

            console.print(table)
