"""
Orin.LAB · Telegram Bot Handlers
"""

import os
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

ANTHROPIC_CLIENT = None
CHAT_HISTORY: dict[int, list[dict]] = {}
MAX_HISTORY = 20

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
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("🌐 Website", url="https://orinlab.xyz"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Welcome to Orin.LAB*\n\n"
        "I'm Orin — your AI crypto research assistant.\n\n"
        "Ask me anything about the market, or use:\n"
        "/signal `$SOL` — get a trading signal\n"
        "/analyze `$SOL` — deep market analysis\n"
        "/help — see all commands",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Orin.LAB Commands*\n\n"
        "/signal `$TOKEN` — generate BUY/SELL/HOLD signal\n"
        "/analyze `$TOKEN` — deep AI market analysis\n"
        "/start — show welcome menu\n"
        "/help — show this message\n\n"
        "_Or just chat with me naturally — I understand crypto questions._",
        parse_mode="Markdown",
    )


async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = " ".join(context.args) if context.args else "SOL"
    token = token.upper().replace("$", "")

    await update.message.reply_text(f"🔍 Analyzing `${token}`...", parse_mode="Markdown")

    try:
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
        await update.message.reply_text(
            f"📊 *Signal: ${token}*\n\n{signal_text}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error generating signal: {e}")


async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = " ".join(context.args) if context.args else "SOL"
    token = token.upper().replace("$", "")

    await update.message.reply_text(f"🧪 Running deep analysis on `${token}`...", parse_mode="Markdown")

    try:
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
        await update.message.reply_text(
            f"🔬 *Analysis: ${token}*\n\n{analysis}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in CHAT_HISTORY:
        CHAT_HISTORY[user_id] = []

    CHAT_HISTORY[user_id].append({"role": "user", "content": text})
    if len(CHAT_HISTORY[user_id]) > MAX_HISTORY:
        CHAT_HISTORY[user_id] = CHAT_HISTORY[user_id][-MAX_HISTORY:]

    try:
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
    elif query.data == "help":
        await handle_help(update, context)
