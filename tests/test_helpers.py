"""
Tests for utils/helpers.py
"""

import pytest
from utils.helpers import (
    format_price,
    format_pct,
    format_signal_badge,
    truncate,
    extract_confidence,
    extract_signal_type,
    shorten_address,
    sol_explorer_url,
)


class TestFormatPrice:
    def test_large_price(self):
        assert format_price(65000.0) == "$65,000.00"

    def test_mid_price(self):
        assert format_price(1.5) == "$1.50"

    def test_small_price(self):
        assert format_price(0.00012345) == "$0.0001"

    def test_custom_decimals(self):
        assert format_price(0.00012345, decimals=6) == "$0.000123"


class TestFormatPct:
    def test_positive(self):
        assert format_pct(3.5) == "+3.50%"

    def test_negative(self):
        assert format_pct(-2.1) == "-2.10%"

    def test_zero(self):
        assert format_pct(0.0) == "+0.00%"


class TestFormatSignalBadge:
    def test_buy(self):
        assert format_signal_badge("SIGNAL: BUY") == "🟢 BUY"

    def test_sell(self):
        assert format_signal_badge("SIGNAL: SELL") == "🔴 SELL"

    def test_hold(self):
        assert format_signal_badge("SIGNAL: HOLD") == "🟡 HOLD"

    def test_case_insensitive(self):
        assert format_signal_badge("signal: buy") == "🟢 BUY"


class TestTruncate:
    def test_short_text(self):
        assert truncate("hello", 280) == "hello"

    def test_long_text(self):
        text = "a" * 300
        result = truncate(text, 280)
        assert len(result) == 280
        assert result.endswith("…")

    def test_exact_length(self):
        text = "a" * 280
        assert truncate(text, 280) == text


class TestExtractConfidence:
    def test_valid(self):
        assert extract_confidence("Confidence: 85/100") == 85

    def test_missing(self):
        assert extract_confidence("No confidence here") is None

    def test_multiple_spaces(self):
        assert extract_confidence("Confidence:  72/100") == 72


class TestExtractSignalType:
    def test_buy(self):
        assert extract_signal_type("SIGNAL: BUY\nConfidence: 80") == "BUY"

    def test_sell(self):
        assert extract_signal_type("SIGNAL: sell") == "SELL"

    def test_hold(self):
        assert extract_signal_type("SIGNAL: HOLD") == "HOLD"

    def test_missing(self):
        assert extract_signal_type("nothing here") is None


class TestShortenAddress:
    def test_long_address(self):
        addr = "So11111111111111111111111111111111111111112"
        result = shorten_address(addr, chars=4)
        assert result == "So11...1112"

    def test_short_address(self):
        addr = "abc"
        assert shorten_address(addr) == "abc"


class TestSolExplorerUrl:
    def test_returns_solscan_url(self):
        addr = "So11111111111111111111111111111111111111112"
        url = sol_explorer_url(addr)
        assert "solscan.io" in url
        assert addr in url