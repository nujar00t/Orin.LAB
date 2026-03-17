"""
Orin.LAB · Telegram Bot Handlers
"""

import os
import base64
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import get_logger
from utils.rate_limiter import anthropic_limiter
from agents.signal_history import SignalHistory

logger = get_logger("bot.handlers")

ANTHROPIC_CLIENT = None
CHAT_HISTORY: dict[int, list[dict]] = {}
MAX_HISTORY = 20

signal_history = SignalHistory()

SYSTEM_PROMPT = """You are Orin, an expert AI crypto market analyst from Orin.LAB.
You specialize in Solana ecosystem, DeFi, and crypto market analysis.

Your style:
- Direct and concise
- Data-driven, not hype-driven
- Always mention risk when giving signals
- Use technical terms naturally but explain when needed
- Never give guaranteed predictions — frame as probabilities

When asked for signals, always output:
SIGNAL: BUY / SELL / HOLD
Confidence: X/100
Reasoning: (2-3 sentences)
Risk: (1 sentence)"""

CHART_PROMPT = """You are Orin, an expert crypto chart analyst from Orin.LAB.
Analyze this chart image and provide:

1. **Trend** — current trend direction and strength
2. **Key Levels** — support and resistance levels visible
3. **Pattern** — any chart patterns (head & shoulders, triangle, etc.)
4. **Signal** — BUY / SELL / HOLD with confidence score
5. **Target** — price target if signal is BUY/SELL
6. **Stop Loss** — recommended stop loss level
7. **Risk** — LOW / MEDIUM / HIGH

Be specific with price levels if visible. Keep it concise and actionable."""


def _get_client() -> anthropic.Anthropic:
    global ANTHROPIC_CLIENT
    if ANTHROPIC_CLIENT is None:
        ANTHROPIC_CLIENT = anthropic.Anthropic()
    return ANTHROPIC_CLIENT


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📊 Signal", callback_data="signal"),
            InlineKeyboardButton("🔍 Analyze", callback_data="analyze"),
        ],
        [
            InlineKeyboardButton("📈 History", callback_data="history"),
            InlineKeyboardButton("🐋 Whales", callback_data="whales"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Welcome to Orin.LAB*\n\n"
        "I'm Orin — your AI crypto research assistant.\n\n"
        "📊 Ask me anything about the market, or use:\n"
        "/signal `$SOL` — trading signal\n"
        "/analyze `$TOKEN` — deep analysis\n"
        "/history — recent signal history\n"
        "/help — all commands\n\n"
        "📸 *Send a chart photo* for instant AI analysis!",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Orin.LAB Commands*\n\n"
        "/signal `$TOKEN` — BUY/SELL/HOLD signal with confidence\n"
        "/analyze `$TOKEN` — deep AI market analysis\n"
        "/history — last 10 signals generated\n"
        "/start — show welcome menu\n"
        "/help — show this message\n\n"
        "📸 *Send any chart image* → instant AI chart analysis\n"
        "_Or just chat — I understand crypto questions naturally._",
        parse_mode="Markdown",
    )


async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = " ".join(context.args) if context.args else "SOL"
    token = token.upper().replace("$", "")

    msg = update.message or update.callback_query.message
    await msg.reply_text(f"🔍 Analyzing `${token}`...", parse_mode="Markdown")

    try:
        anthropic_limiter.wait_and_acquire()
        client = _get_client()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Generate a trading signal for ${token} based on current market conditions."
            }]
        )
        signal_text = response.content[0].text
        signal_history.add(token, signal_text)

        await msg.reply_text(
            f"📊 *Signal: ${token}*\n\n{signal_text}",
            parse_mode="Markdown",
        )
        logger.info(f"Signal generated: {token}")
    except Exception as e:
        logger.error(f"Signal error: {e}")
        await msg.reply_text(f"⚠️ Error generating signal: {e}")


async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = " ".join(context.args) if context.args else "SOL"
    token = token.upper().replace("$", "")

    msg = update.message or update.callback_query.message
    await msg.reply_text(f"🧪 Running deep analysis on `${token}`...", parse_mode="Markdown")

    try:
        anthropic_limiter.wait_and_acquire()
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"Provide a comprehensive market analysis for ${token}. "
                    "Cover: price action, key levels, ecosystem news, risks, and outlook."
                )
            }]
        )
        analysis = response.content[0].text
        await msg.reply_text(
            f"🔬 *Analysis: ${token}*\n\n{analysis}",
            parse_mode="Markdown",
        )
        logger.info(f"Analysis generated: {token}")
    except Exception as e:
        logger.error(f"Analyze error: {e}")
        await msg.reply_text(f"⚠️ Error: {e}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze a chart image sent to the bot."""
    caption = (update.message.caption or "").strip().lower()

    await update.message.reply_text(
        "📸 *Chart received — analyzing...*",
        parse_mode="Markdown",
    )

    try:
        # Download the highest resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()
        image_b64 = base64.standard_b64encode(bytes(image_bytes)).decode("utf-8")

        anthropic_limiter.wait_and_acquire()
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": CHART_PROMPT + (f"\n\nUser note: {caption}" if caption else ""),
                    },
                ],
            }]
        )

        analysis = response.content[0].text
        await update.message.reply_text(
            f"📈 *Chart Analysis*\n\n{analysis}",
            parse_mode="Markdown",
        )
        logger.info("Chart analysis completed")
    except Exception as e:
        logger.error(f"Photo analysis error: {e}")
        await update.message.reply_text(f"⚠️ Could not analyze chart: {e}")


async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    records = signal_history.get_recent(10)

    if not records:
        await msg.reply_text("📭 No signal history yet. Try `/signal $SOL`!", parse_mode="Markdown")
        return

    lines = ["📋 *Recent Signals*\n"]
    for r in records:
        lines.append(f"`{r['time']}` *{r['token']}* — {r['signal']} ({r['confidence']})")

    await msg.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in CHAT_HISTORY:
        CHAT_HISTORY[user_id] = []

    CHAT_HISTORY[user_id].append({"role": "user", "content": text})
    if len(CHAT_HISTORY[user_id]) > MAX_HISTORY:
        CHAT_HISTORY[user_id] = CHAT_HISTORY[user_id][-MAX_HISTORY:]

    try:
        anthropic_limiter.wait_and_acquire()
        client = _get_client()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=CHAT_HISTORY[user_id],
        )
        reply = response.content[0].text
        CHAT_HISTORY[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await update.message.reply_text(f"⚠️ {e}")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signal":
        context.args = ["SOL"]
        await handle_signal(update, context)
    elif query.data == "analyze":
        context.args = ["SOL"]
        await handle_analyze(update, context)
    elif query.data == "history":
        await handle_history(update, context)
    elif query.data == "help":
        await handle_help(update, context)
    elif query.data == "whales":
        await query.message.reply_text(
            "🐋 *Whale Tracker*\n\n"
            "Use `/whales add <address>` to watch a wallet.\n"
            "Alerts fire automatically when large moves are detected.",
            parse_mode="Markdown",
        )