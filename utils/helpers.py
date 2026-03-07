"""
Orin.LAB · Helpers
Formatting, parsing, and misc utility functions.
"""

from __future__ import annotations
import re
from typing import Optional


def format_price(price: float, decimals: int = 4) -> str:
    """Format a price with appropriate decimal places and $ prefix."""
    if price >= 1_000:
        return f"${price:,.2f}"
    if price >= 1:
        return f"${price:.2f}"
    return f"${price:.{decimals}f}"


def format_pct(value: float, decimals: int = 2) -> str:
    """Format a percentage value with sign."""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def format_signal_badge(signal_line: str) -> str:
    """Return an emoji badge for a signal line."""
    upper = signal_line.upper()
    if "BUY" in upper:
        return "🟢 BUY"
    if "SELL" in upper:
        return "🔴 SELL"
    return "🟡 HOLD"


def truncate(text: str, max_len: int = 280, suffix: str = "…") -> str:
    """Truncate text to max_len characters."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def extract_confidence(signal_text: str) -> Optional[int]:
    """Parse confidence score from signal output."""
    match = re.search(r"Confidence:\s*(\d+)", signal_text)
    if match:
        return int(match.group(1))
    return None


def extract_signal_type(signal_text: str) -> Optional[str]:
    """Parse BUY/SELL/HOLD from signal output."""
    match = re.search(r"SIGNAL:\s*(BUY|SELL|HOLD)", signal_text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def sol_explorer_url(address: str) -> str:
    """Return Solscan URL for a wallet or token address."""
    return f"https://solscan.io/account/{address}"


def shorten_address(address: str, chars: int = 4) -> str:
    """Shorten a Solana address to first and last N chars."""
    if len(address) <= chars * 2 + 3:
        return address
    return f"{address[:chars]}...{address[-chars:]}"