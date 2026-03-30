"""
Orin.LAB · Market Analyst
Deep AI-powered market analysis using Claude.
"""

import anthropic
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

SYSTEM_PROMPT = """You are Orin, chief market analyst at Orin.LAB — an AI research lab for crypto markets.

You provide deep, structured market analysis covering:
1. Price action and technical levels
2. On-chain metrics interpretation
3. Ecosystem and narrative analysis
4. Risk assessment
5. Short and medium term outlook

Style: professional, data-driven, concise. No hype. Frame everything as probabilities, not certainties."""


def fetch_coingecko_data(token_id: str) -> dict:
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
        params = {"localization": "false", "tickers": "false", "community_data": "false"}
        resp = httpx.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        market = data.get("market_data", {})
        return {
            "name": data.get("name"),
            "symbol": data.get("symbol", "").upper(),
            "price": market.get("current_price", {}).get("usd", 0),
            "change_24h": market.get("price_change_percentage_24h", 0),
            "change_7d": market.get("price_change_percentage_7d", 0),
            "market_cap": market.get("market_cap", {}).get("usd", 0),
            "volume_24h": market.get("total_volume", {}).get("usd", 0),
            "high_24h": market.get("high_24h", {}).get("usd", 0),
            "low_24h": market.get("low_24h", {}).get("usd", 0),
            "ath": market.get("ath", {}).get("usd", 0),
            "ath_change": market.get("ath_change_percentage", {}).get("usd", 0),
        }
    except Exception:
        return {}


def analyze(token: str, data: dict) -> str:
    client = anthropic.Anthropic()

    if data:
        context = f"""
Token: {data.get('name')} (${data.get('symbol')})
Current Price: ${data.get('price', 0):,.4f}
24h Change: {data.get('change_24h', 0):.2f}%
7d Change: {data.get('change_7d', 0):.2f}%
24h High: ${data.get('high_24h', 0):,.4f}
24h Low: ${data.get('low_24h', 0):,.4f}
Market Cap: ${data.get('market_cap', 0):,.0f}
24h Volume: ${data.get('volume_24h', 0):,.0f}
ATH: ${data.get('ath', 0):,.4f} ({data.get('ath_change', 0):.1f}% from ATH)
"""
    else:
        context = f"Token: {token}\n(Live data unavailable — use general knowledge)"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Provide a comprehensive market analysis:\n{context}"
        }]
    )
    return response.content[0].text


COINGECKO_IDS = {
    "SOL": "solana",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "JUP": "jupiter-exchange-solana",
    "BONK": "bonk",
    "WIF": "dogwifcoin",
}


def run():
    console.print(Panel.fit(
        "[bold cyan]Orin.LAB[/bold cyan] · [magenta]Market Analyst[/magenta]\n"
        "[dim]Deep AI market analysis[/dim]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold]Token:[/bold] ", end="")
        token = Prompt.ask("Enter token (e.g. SOL) or [dim]q[/dim] to quit").upper()

        if token == "Q":
            break

        cg_id = COINGECKO_IDS.get(token, token.lower())

        with console.status("[dim]Fetching market data...[/dim]", spinner="dots"):
            data = fetch_coingecko_data(cg_id)

        with console.status("[dim]Running deep analysis with Claude...[/dim]", spinner="dots"):
            result = analyze(token, data)

        console.print(Panel(
            f"[white]{result}[/white]",
            title=f"[bold cyan]Orin.LAB Analysis: ${token}[/bold cyan]",
            border_style="magenta",
            box=box.ROUNDED,
        ))
