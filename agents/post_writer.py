"""
Orin.LAB · Post Writer
Generate natural, human-sounding crypto posts from TA results.
Varied templates, casual tone, no robotic repetition.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from agents.technical_analysis import TAResult
from utils.helpers import format_price, format_pct


# ──────────────────────────────────────────────────────────────────────────────
# Template pools — randomly selected to avoid repetition
# ──────────────────────────────────────────────────────────────────────────────

BUY_OPENERS = [
    "been watching {token} for a while and this setup is clean",
    "not gonna lie, {token} is looking interesting right now",
    "quietly accumulating {token} at these levels",
    "{token} just hit a level I've had circled for weeks",
    "the {token} chart is giving me confidence",
    "zoomed out on {token} and the structure is solid",
    "{token} dip buyers have been right every time this cycle",
    "RSI on {token} just flashed a level I don't ignore",
]

SELL_OPENERS = [
    "think {token} needs to breathe here tbh",
    "took some {token} off the table, no shame in that",
    "{token} hitting resistance I've had marked for a while",
    "overbought on multiple timeframes for {token} rn",
    "scaling out of {token} — risk management over everything",
    "{token} showing classic signs of exhaustion imo",
    "the {token} move was real but this area deserves caution",
    "rotating out of {token} for now, will revisit lower",
]

HOLD_OPENERS = [
    "watching {token} closely — not the time to chase",
    "{token} in no man's land right now, patience pays",
    "holding {token} steady, waiting for a cleaner setup",
    "nothing wrong with doing nothing on {token} here",
    "{token} consolidating — let it cook",
    "zoomed in too much on {token}? zoom out, it's fine",
    "not adding or trimming {token}, just watching",
    "sometimes the best trade on {token} is no trade",
]

CONTEXT_LINES = {
    "BUY": [
        "RSI was sitting in oversold territory — textbook.",
        "MACD crossed bullish and volume picked up. That combo works.",
        "Price bounced clean off the EMA. Structure intact.",
        "Bollinger squeeze resolving upward. Been waiting for this.",
        "Volume confirms the move. Not just price action noise.",
        "Strong support held multiple times. Market respects this level.",
        "EMA alignment is bullish across timeframes.",
    ],
    "SELL": [
        "RSI stretched. Markets don't go up forever.",
        "MACD rolling over at the top — seen this before.",
        "Price touched the upper Bollinger and got rejected. Classic.",
        "Volume diverging while price pushes higher. Caution.",
        "EMA stack starting to compress. Momentum slowing.",
        "Key resistance overhead, reward/risk not great from here.",
        "Sentiment running hot. Good time to trim, not add.",
    ],
    "HOLD": [
        "Volume dried up. No edge in either direction right now.",
        "MACD flat, RSI neutral — textbook indecision zone.",
        "Waiting for a breakout or breakdown to confirm direction.",
        "Price inside a range. Trade the edges, not the middle.",
        "No conviction in either direction from the indicators.",
        "Consolidation is healthy. Don't read too much into it.",
        "Let the setup develop. Forcing trades here is how you lose.",
    ],
}

CLOSERS = [
    "not financial advice — do your own research",
    "DYOR always, never size up more than you can afford to lose",
    "manage your risk, this is not financial advice",
    "as always, NFA. trade safe.",
    "position sizing and risk management over everything",
    "NFA. stay humble, the market humbles everyone eventually",
    "your portfolio, your rules. NFA.",
]

HASHTAG_POOLS = {
    "SOL":  ["#Solana", "#SOL", "#Crypto", "#DeFi", "#Web3"],
    "BTC":  ["#Bitcoin", "#BTC", "#Crypto", "#DigitalGold"],
    "ETH":  ["#Ethereum", "#ETH", "#DeFi", "#Crypto"],
    "JUP":  ["#Jupiter", "#JUP", "#Solana", "#DeFi"],
    "BONK": ["#BONK", "#Solana", "#Memecoin", "#Crypto"],
    "WIF":  ["#WIF", "#dogwifhat", "#Solana", "#Memecoin"],
}

DEFAULT_TAGS = ["#Crypto", "#Trading", "#DeFi"]


def _pick(pool: list[str]) -> str:
    return random.choice(pool)


def _tags(symbol: str, n: int = 3) -> str:
    pool = HASHTAG_POOLS.get(symbol.upper(), DEFAULT_TAGS)
    chosen = random.sample(pool, min(n, len(pool)))
    return " ".join(chosen)


# ──────────────────────────────────────────────────────────────────────────────
# Post builders
# ──────────────────────────────────────────────────────────────────────────────

def build_signal_post(result: TAResult) -> str:
    """Build a natural single-tweet signal post from a TAResult."""
    sig  = result.signal
    token = result.symbol
    price = result.price

    opener_pool = {"BUY": BUY_OPENERS, "SELL": SELL_OPENERS, "HOLD": HOLD_OPENERS}[sig]
    opener  = _pick(opener_pool).format(token=f"${token}")
    context = _pick(CONTEXT_LINES[sig])
    closer  = _pick(CLOSERS)
    tags    = _tags(token)

    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}[sig]

    # Build RSI line if available
    indicator_line = ""
    if result.rsi is not None:
        indicator_line = f"RSI: {result.rsi:.0f}"
    if result.macd_histogram is not None:
        hist_str = f"+{result.macd_histogram:.4f}" if result.macd_histogram > 0 else f"{result.macd_histogram:.4f}"
        indicator_line += f" | MACD hist: {hist_str}" if indicator_line else f"MACD hist: {hist_str}"

    lines = [
        f"{emoji} {opener}",
        "",
        f"${token} at {format_price(price)} — {sig} signal ({result.confidence}/100)",
        context,
    ]

    if indicator_line:
        lines.append(f"[ {indicator_line} ]")

    lines += ["", f"{closer}", "", tags]

    return "\n".join(lines)


def build_market_update_post(results: list[TAResult]) -> str:
    """Build a multi-token market scan post (thread-style)."""
    lines = ["📊 quick market scan from orin.lab\n"]

    for r in results:
        emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(r.signal, "⚪")
        rsi_str = f" | RSI {r.rsi:.0f}" if r.rsi else ""
        lines.append(
            f"{emoji} ${r.symbol} {format_price(r.price)} — {r.signal} {r.confidence}/100{rsi_str}"
        )

    lines += [
        "",
        "all based on RSI, MACD, Bollinger Bands + EMA alignment",
        "not financial advice, do your own research",
        "",
        "#Crypto #Solana #DeFi #Trading",
    ]
    return "\n".join(lines)


def build_whale_alert_post(symbol: str, sol_amount: float, usd_value: float,
                            direction: str, label: str) -> str:
    """Build a natural whale alert post."""
    dir_word = "moved in" if direction == "IN" else "moved out"
    dir_emoji = "📥" if direction == "IN" else "📤"

    openers = [
        f"{dir_emoji} whale just {dir_word} — worth watching",
        f"big money {dir_word} on {symbol}. keeping an eye on this.",
        f"on-chain picked up a large move. {dir_word}.",
        f"whale alert — {sol_amount:,.0f} SOL {dir_word}",
    ]

    return "\n".join([
        _pick(openers),
        "",
        f"🐋 {label}",
        f"Amount: {sol_amount:,.1f} SOL (~{format_price(usd_value, 0)})",
        f"Direction: {direction}",
        "",
        "not necessarily bullish/bearish — context matters",
        "DYOR | #Solana #Crypto #OnChain",
    ])


def build_ta_thread(result: TAResult) -> list[str]:
    """
    Build a Twitter thread (list of tweets) for a full TA breakdown.
    Each item in the list is one tweet.
    """
    token = f"${result.symbol}"
    price = format_price(result.price)
    sig_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(result.signal, "⚪")

    tweet1 = "\n".join([
        f"been running the charts on {token} — here's what I'm seeing 🧵",
        "",
        f"price: {price}",
        f"signal: {sig_emoji} {result.signal} ({result.confidence}/100)",
        "",
        "thread below 👇",
    ])

    tweet2_lines = [f"📐 RSI & Momentum — {token}"]
    if result.rsi is not None:
        zone = "oversold 🔥" if result.rsi < 30 else "overbought ⚠️" if result.rsi > 70 else "neutral"
        tweet2_lines.append(f"RSI(14): {result.rsi:.1f} — {zone}")
    if result.macd is not None:
        direction = "above" if result.macd > 0 else "below"
        tweet2_lines.append(f"MACD {direction} signal line — momentum is {'bullish' if result.macd > 0 else 'bearish'}")
    tweet2 = "\n".join(tweet2_lines)

    tweet3_lines = [f"📊 Structure — {token}"]
    if result.bb_upper and result.bb_lower:
        tweet3_lines.append(f"Bollinger Bands: {format_price(result.bb_lower)} — {format_price(result.bb_upper)}")
        if result.bb_pct is not None:
            pct_desc = "near lower band" if result.bb_pct < 0.3 else "near upper band" if result.bb_pct > 0.7 else "mid-range"
            tweet3_lines.append(f"price is {pct_desc} (%B: {result.bb_pct:.2f})")
    if result.ema_9 and result.ema_21:
        trend = "above" if result.price > result.ema_21 else "below"
        tweet3_lines.append(f"price is {trend} EMA(21) — {'bullish' if result.price > result.ema_21 else 'bearish'} structure")
    tweet3 = "\n".join(tweet3_lines)

    tweet4_lines = [f"🎯 My take on {token}"]
    for r in result.reasons[:3]:
        tweet4_lines.append(f"• {r}")
    tweet4_lines += ["", "NFA. manage your risk. DYOR always.", "#Crypto #Trading #Solana"]
    tweet4 = "\n".join(tweet4_lines)

    return [tweet1, tweet2, tweet3, tweet4]


# ──────────────────────────────────────────────────────────────────────────────
# CLI runner — preview posts in terminal
# ──────────────────────────────────────────────────────────────────────────────

def preview_all(results: list[TAResult]) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich import box

    console = Console()

    console.print("\n[bold cyan]━━━ SINGLE SIGNAL POSTS ━━━[/bold cyan]\n")
    for r in results:
        post = build_signal_post(r)
        console.print(Panel(post, title=f"[bold]${r.symbol}[/bold]", border_style="cyan", box=box.ROUNDED))

    console.print("\n[bold yellow]━━━ MARKET SCAN POST ━━━[/bold yellow]\n")
    console.print(Panel(build_market_update_post(results), border_style="yellow", box=box.ROUNDED))

    console.print("\n[bold green]━━━ TA THREAD (SOL) ━━━[/bold green]\n")
    if results:
        for i, tweet in enumerate(build_ta_thread(results[0]), 1):
            console.print(Panel(tweet, title=f"[dim]Tweet {i}/4[/dim]", border_style="green", box=box.ROUNDED))
