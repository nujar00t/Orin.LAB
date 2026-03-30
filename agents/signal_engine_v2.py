"""
Orin.LAB · Signal Engine v2
Rate-limited, cached version of the signal engine.
Replaces direct API calls with rate_limiter + TTL cache.
"""

from __future__ import annotations

import httpx
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

from utils.rate_limiter import anthropic_limiter, jupiter_limiter
from utils.cache import price_cache, signal_cache
from utils.logger import get_logger
from utils.helpers import extract_signal_type, extract_confidence, format_price

console = Console()
logger = get_logger("signal_engine")

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


@jupiter_limiter
def fetch_price(mint: str) -> float:
    cache_key = f"price:{mint}"
    cached = price_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = httpx.get(f"{JUPITER_PRICE_API}?ids={mint}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        price = float(data["data"].get(mint, {}).get("price", 0))
        price_cache.set(cache_key, price, ttl=30)
        return price
    except Exception as exc:
        logger.warning(f"Price fetch failed for {mint}: {exc}")
        return 0.0


@anthropic_limiter
def generate_signal(symbol: str, price: float) -> str:
    cache_key = f"signal:{symbol}"
    cached = signal_cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Signal cache hit: {symbol}")
        return cached

    if price == 0:
        return "Unable to fetch price data."

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Generate signal for {symbol} at current price {format_price(price)}",
        }],
    )
    result = response.content[0].text
    signal_cache.set(cache_key, result, ttl=300)
    logger.info(f"Signal generated: {symbol} → {extract_signal_type(result)} ({extract_confidence(result)}/100)")
    return result