"""
Orin.LAB · Config
Typed configuration loader from environment variables with validation.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    # Anthropic
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    claude_model: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"))

    # Telegram
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_allowed_users: list[int] = field(default_factory=list)

    # Twitter / X
    twitter_api_key: str = field(default_factory=lambda: os.getenv("TWITTER_API_KEY", ""))
    twitter_api_secret: str = field(default_factory=lambda: os.getenv("TWITTER_API_SECRET", ""))
    twitter_access_token: str = field(default_factory=lambda: os.getenv("TWITTER_ACCESS_TOKEN", ""))
    twitter_access_secret: str = field(default_factory=lambda: os.getenv("TWITTER_ACCESS_SECRET", ""))

    # Solana
    solana_rpc_url: str = field(default_factory=lambda: os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"))
    solana_wallet_address: Optional[str] = field(default_factory=lambda: os.getenv("SOLANA_WALLET_ADDRESS"))

    # Signal Engine
    signal_interval_seconds: int = field(default_factory=lambda: int(os.getenv("SIGNAL_INTERVAL", "300")))
    signal_confidence_threshold: int = field(default_factory=lambda: int(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "70")))

    # Rate Limiting
    rate_limit_calls: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_CALLS", "10")))
    rate_limit_period: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PERIOD", "60")))

    def __post_init__(self):
        raw = os.getenv("TELEGRAM_ALLOWED_USERS", "")
        if raw:
            self.telegram_allowed_users = [int(uid.strip()) for uid in raw.split(",") if uid.strip().isdigit()]

    def validate(self) -> list[str]:
        """Return a list of missing required config keys."""
        errors = []
        if not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY")
        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN")
        return errors

    @classmethod
    def load(cls) -> "Config":
        cfg = cls()
        missing = cfg.validate()
        if missing:
            raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")
        return cfg


# Singleton
_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config