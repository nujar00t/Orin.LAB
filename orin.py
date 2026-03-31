#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║         O R I N . L A B                 ║
║   AI Research Lab for Crypto Markets     ║
║   $ORNL · Built on Solana               ║
╚══════════════════════════════════════════╝
"""

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

BANNER = """[bold cyan]
 ██████╗ ██████╗ ██╗███╗   ██╗   ██╗      █████╗ ██████╗
██╔═══██╗██╔══██╗██║████╗  ██║   ██║     ██╔══██╗██╔══██╗
██║   ██║██████╔╝██║██╔██╗ ██║   ██║     ███████║██████╔╝
██║   ██║██╔══██╗██║██║╚██╗██║   ██║     ██╔══██║██╔══██╗
╚██████╔╝██║  ██║██║██║ ╚████║   ███████╗██║  ██║██████╔╝
 ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚══════╝╚═╝  ╚═╝╚═════╝
[/bold cyan]
[dim]AI Research Lab for Crypto Markets · [bold]$ORNL[/bold] · Built on Solana[/dim]"""


@click.group()
def cli():
    """Orin.LAB — AI Research Lab for Crypto Markets · $ORNL"""
    console.print(BANNER)


@cli.command()
def bot():
    """Launch Telegram AI Bot"""
    from bot.telegram_bot import run
    console.print(Panel.fit(
        "[bold cyan]Starting Telegram Bot...[/bold cyan]",
        border_style="cyan"
    ))
    run()


@cli.command()
def signal():
    """Launch Signal Engine — generate market signals"""
    from agents.signal_engine import run
    console.print(Panel.fit(
        "[bold cyan]Starting Signal Engine...[/bold cyan]",
        border_style="cyan"
    ))
    run()


@cli.command()
def analyst():
    """Launch Market Analyst — deep AI market analysis"""
    from agents.market_analyst import run
    console.print(Panel.fit(
        "[bold cyan]Starting Market Analyst...[/bold cyan]",
        border_style="cyan"
    ))
    run()


@cli.command()
def onchain():
    """Launch On-chain Agent — Solana wallet and transaction monitoring"""
    from agents.onchain_agent import run
    console.print(Panel.fit(
        "[bold cyan]Starting On-chain Agent...[/bold cyan]",
        border_style="cyan"
    ))
    run()


@cli.command()
@click.argument("tokens", nargs=-1)
def posts(tokens):
    """Preview natural human-style posts for given tokens (default: SOL BTC ETH)"""
    from agents.technical_analysis import analyze
    from agents.post_writer import preview_all

    symbols = list(tokens) if tokens else ["SOL", "BTC", "ETH"]
    console.print(Panel.fit(
        f"[bold cyan]Generating posts for {', '.join(f'${s}' for s in symbols)}...[/bold cyan]",
        border_style="cyan"
    ))
    results = []
    for sym in symbols:
        with console.status(f"[dim]Analyzing ${sym}...[/dim]", spinner="dots"):
            results.append(analyze(sym))
    preview_all(results)


if __name__ == "__main__":
    cli()
