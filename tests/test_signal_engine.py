"""
Unit tests for Orin.LAB Signal Engine.
"""

import pytest
from unittest.mock import patch, MagicMock
from agents.signal_engine import fetch_price, generate_signal, TOKENS


class TestFetchPrice:
    @patch("agents.signal_engine.httpx.get")
    def test_returns_price(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {"fake_mint": {"price": 142.5}}
        }
        mock_get.return_value = mock_resp
        price = fetch_price("fake_mint")
        assert price == 142.5

    @patch("agents.signal_engine.httpx.get")
    def test_returns_zero_on_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        price = fetch_price("fake_mint")
        assert price == 0.0

    @patch("agents.signal_engine.httpx.get")
    def test_returns_zero_on_missing_mint(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {}}
        mock_get.return_value = mock_resp
        price = fetch_price("nonexistent_mint")
        assert price == 0.0


class TestGenerateSignal:
    @patch("agents.signal_engine.anthropic.Anthropic")
    def test_returns_string(self, mock_anthropic):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="SIGNAL: BUY\nConfidence: 80/100")]
        )
        mock_anthropic.return_value = mock_client
        result = generate_signal("SOL", 142.5)
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("agents.signal_engine.anthropic.Anthropic")
    def test_called_with_price(self, mock_anthropic):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="SIGNAL: HOLD")]
        )
        mock_anthropic.return_value = mock_client
        generate_signal("SOL", 142.5)
        call_args = mock_client.messages.create.call_args
        assert "142.5" in str(call_args)


class TestTokens:
    def test_sol_exists(self):
        assert "SOL" in TOKENS

    def test_all_mints_are_strings(self):
        for symbol, mint in TOKENS.items():
            assert isinstance(mint, str)
            assert len(mint) > 10
