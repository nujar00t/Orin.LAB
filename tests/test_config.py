"""
Tests for utils/config.py
"""

import os
import pytest
from unittest.mock import patch
from utils.config import Config


class TestConfig:
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = Config()
            assert cfg.claude_model == "claude-haiku-4-5-20251001"
            assert cfg.solana_rpc_url == "https://api.mainnet-beta.solana.com"
            assert cfg.signal_interval_seconds == 300
            assert cfg.signal_confidence_threshold == 70
            assert cfg.rate_limit_calls == 10

    def test_loads_from_env(self):
        env = {
            "ANTHROPIC_API_KEY": "sk-test",
            "TELEGRAM_BOT_TOKEN": "bot123",
            "CLAUDE_MODEL": "claude-opus-4-6",
            "SIGNAL_INTERVAL": "60",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = Config()
            assert cfg.anthropic_api_key == "sk-test"
            assert cfg.telegram_bot_token == "bot123"
            assert cfg.claude_model == "claude-opus-4-6"
            assert cfg.signal_interval_seconds == 60

    def test_allowed_users_parsing(self):
        with patch.dict(os.environ, {"TELEGRAM_ALLOWED_USERS": "111,222,333"}):
            cfg = Config()
            assert cfg.telegram_allowed_users == [111, 222, 333]

    def test_allowed_users_empty(self):
        with patch.dict(os.environ, {"TELEGRAM_ALLOWED_USERS": ""}):
            cfg = Config()
            assert cfg.telegram_allowed_users == []

    def test_validate_missing_keys(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = Config()
            missing = cfg.validate()
            assert "ANTHROPIC_API_KEY" in missing
            assert "TELEGRAM_BOT_TOKEN" in missing

    def test_validate_passes_when_set(self):
        env = {
            "ANTHROPIC_API_KEY": "sk-test",
            "TELEGRAM_BOT_TOKEN": "bot123",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = Config()
            assert cfg.validate() == []