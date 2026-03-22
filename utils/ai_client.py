"""
Orin.LAB · AI Client
Unified provider adapter — supports Anthropic and any OpenAI-compatible API
(DeepInfra, Together, Groq, OpenRouter, etc.)

Set AI_PROVIDER in .env:
  AI_PROVIDER=anthropic   → uses ANTHROPIC_API_KEY
  AI_PROVIDER=deepinfra   → uses DEEPINFRA_API_KEY + DEEPINFRA_MODEL
  AI_PROVIDER=openai      → uses OPENAI_API_KEY + OPENAI_MODEL
"""

from __future__ import annotations

import os
from typing import Optional
from utils.logger import get_logger

logger = get_logger("ai_client")

AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").lower()

# DeepInfra / OpenAI-compatible defaults
DEEPINFRA_BASE_URL = "https://api.deepinfra.com/v1/openai"
DEEPINFRA_MODEL    = os.getenv("DEEPINFRA_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct")
OPENAI_BASE_URL    = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL       = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _make_openai_client(base_url: str, api_key: str):
    try:
        from openai import OpenAI
        return OpenAI(base_url=base_url, api_key=api_key)
    except ImportError:
        raise ImportError(
            "openai package not installed. Run: pip install openai"
        )


def chat(
    messages: list[dict],
    system: str = "",
    max_tokens: int = 400,
    model: Optional[str] = None,
) -> str:
    """
    Unified chat call — works with Anthropic or any OpenAI-compatible API.

    Args:
        messages:   List of {"role": ..., "content": ...} dicts
        system:     System prompt string
        max_tokens: Max tokens in response
        model:      Override model (optional)

    Returns:
        Response text as string
    """
    provider = AI_PROVIDER

    # ── ANTHROPIC ──────────────────────────────────────────────────────────────
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        use_model = model or os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
        response = client.messages.create(
            model=use_model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text

    # ── DEEPINFRA ──────────────────────────────────────────────────────────────
    if provider == "deepinfra":
        api_key = os.getenv("DEEPINFRA_API_KEY", "")
        if not api_key:
            raise EnvironmentError("DEEPINFRA_API_KEY not set in .env")
        client = _make_openai_client(DEEPINFRA_BASE_URL, api_key)
        use_model = model or DEEPINFRA_MODEL
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        response = client.chat.completions.create(
            model=use_model,
            messages=full_messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    # ── OPENAI-COMPATIBLE (openrouter, together, groq, etc.) ───────────────────
    if provider in ("openai", "openrouter", "together", "groq", "custom"):
        api_key   = os.getenv("OPENAI_API_KEY", "")
        base_url  = os.getenv("OPENAI_BASE_URL", OPENAI_BASE_URL)
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not set in .env")
        client = _make_openai_client(base_url, api_key)
        use_model = model or OPENAI_MODEL
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        response = client.chat.completions.create(
            model=use_model,
            messages=full_messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    raise ValueError(
        f"Unknown AI_PROVIDER '{provider}'. "
        "Choose: anthropic | deepinfra | openai"
    )


def chat_with_image(image_b64: str, prompt: str, system: str = "", max_tokens: int = 600) -> str:
    """
    Vision call — sends a base64 image + text prompt.
    Anthropic: native vision support.
    OpenAI-compatible: uses vision message format.
    """
    provider = AI_PROVIDER

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return response.content[0].text

    # OpenAI-compatible vision
    if provider == "deepinfra":
        api_key  = os.getenv("DEEPINFRA_API_KEY", "")
        client   = _make_openai_client(DEEPINFRA_BASE_URL, api_key)
        use_model = os.getenv("DEEPINFRA_VISION_MODEL", "meta-llama/Llama-3.2-90B-Vision-Instruct")
    else:
        api_key  = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", OPENAI_BASE_URL)
        client   = _make_openai_client(base_url, api_key)
        use_model = os.getenv("OPENAI_MODEL", "gpt-4o")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            {"type": "text", "text": prompt},
        ],
    })
    response = client.chat.completions.create(model=use_model, messages=messages, max_tokens=max_tokens)
    return response.choices[0].message.content
