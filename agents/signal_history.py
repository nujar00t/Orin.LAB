"""
Orin.LAB · Signal History
Persist generated signals to a local JSON file for tracking and review.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from utils.helpers import extract_signal_type, extract_confidence
from utils.logger import get_logger

logger = get_logger("signal_history")

DEFAULT_PATH = Path(os.getenv("SIGNAL_HISTORY_PATH", "data/signal_history.json"))
MAX_RECORDS = 500


class SignalHistory:
    """
    Append-only signal log stored as a JSON array on disk.
    Thread-safe for single-process use.
    """

    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self, records: list[dict]) -> None:
        self.path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, token: str, signal_text: str) -> dict:
        """Append a new signal record and return it."""
        sig_type = extract_signal_type(signal_text) or "UNKNOWN"
        confidence = extract_confidence(signal_text)

        record = {
            "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "token": token.upper(),
            "signal": sig_type,
            "confidence": f"{confidence}/100" if confidence else "–",
            "raw": signal_text,
        }

        records = self._load()
        records.append(record)

        # Keep only the most recent MAX_RECORDS
        if len(records) > MAX_RECORDS:
            records = records[-MAX_RECORDS:]

        self._save(records)
        logger.debug(f"Signal saved: {token} → {sig_type}")
        return record

    def get_recent(self, n: int = 10) -> list[dict]:
        """Return the last N signals, newest first."""
        records = self._load()
        return list(reversed(records[-n:]))

    def get_by_token(self, token: str, n: int = 10) -> list[dict]:
        """Return last N signals for a specific token."""
        records = self._load()
        filtered = [r for r in records if r["token"] == token.upper()]
        return list(reversed(filtered[-n:]))

    def stats(self) -> dict:
        """Return summary stats across all recorded signals."""
        records = self._load()
        if not records:
            return {"total": 0}

        from collections import Counter
        signals = [r["signal"] for r in records]
        counts = Counter(signals)
        tokens = Counter(r["token"] for r in records)

        return {
            "total": len(records),
            "buy": counts.get("BUY", 0),
            "sell": counts.get("SELL", 0),
            "hold": counts.get("HOLD", 0),
            "top_tokens": tokens.most_common(5),
            "first": records[0]["time"] if records else None,
            "last": records[-1]["time"] if records else None,
        }

    def clear(self) -> None:
        self._save([])
        logger.info("Signal history cleared")