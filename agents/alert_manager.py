"""
Orin.LAB · Alert Manager
Watches signal confidence and fires alerts when thresholds are crossed.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Callable, Awaitable, Optional
from utils.logger import get_logger
from utils.cache import signal_cache
from utils.helpers import extract_confidence, extract_signal_type, format_price

logger = get_logger("alert_manager")


@dataclass
class Alert:
    symbol: str
    signal_type: str          # BUY | SELL | HOLD
    confidence: int
    price: float
    message: str


AlertHandler = Callable[[Alert], Awaitable[None]]


class AlertManager:
    """
    Polls cached signals and fires registered handlers when a signal
    meets the configured confidence threshold.
    """

    def __init__(self, confidence_threshold: int = 70, poll_interval: float = 60.0):
        self.confidence_threshold = confidence_threshold
        self.poll_interval = poll_interval
        self._handlers: list[AlertHandler] = []
        self._seen: set[str] = set()          # deduplicate within a run
        self._running = False

    def register(self, handler: AlertHandler) -> None:
        """Register an async callback to be called when an alert fires."""
        self._handlers.append(handler)

    async def _fire(self, alert: Alert) -> None:
        for handler in self._handlers:
            try:
                await handler(alert)
            except Exception as exc:
                logger.error(f"Alert handler error: {exc}")

    async def check_once(self, symbols: list[str], prices: dict[str, float]) -> list[Alert]:
        """Check current signals and return any new alerts."""
        fired: list[Alert] = []
        for symbol in symbols:
            cache_key = f"signal:{symbol}"
            signal_text = signal_cache.get(cache_key)
            if not signal_text:
                continue

            sig_type = extract_signal_type(signal_text)
            confidence = extract_confidence(signal_text)
            if sig_type is None or confidence is None:
                continue
            if confidence < self.confidence_threshold:
                continue

            dedup_key = f"{symbol}:{sig_type}:{confidence}"
            if dedup_key in self._seen:
                continue

            self._seen.add(dedup_key)
            price = prices.get(symbol, 0.0)
            alert = Alert(
                symbol=symbol,
                signal_type=sig_type,
                confidence=confidence,
                price=price,
                message=(
                    f"🚨 {sig_type} signal on {symbol} "
                    f"@ {format_price(price)} | "
                    f"Confidence: {confidence}/100"
                ),
            )
            await self._fire(alert)
            fired.append(alert)
            logger.info(f"Alert fired: {alert.message}")

        return fired

    async def run(self, symbols: list[str], price_fetcher: Callable[[str], Awaitable[float]]) -> None:
        """Start the alert polling loop."""
        self._running = True
        logger.info(f"AlertManager started (threshold={self.confidence_threshold}%)")
        while self._running:
            prices = {}
            for sym in symbols:
                prices[sym] = await price_fetcher(sym)
            await self.check_once(symbols, prices)
            await asyncio.sleep(self.poll_interval)

    def stop(self) -> None:
        self._running = False