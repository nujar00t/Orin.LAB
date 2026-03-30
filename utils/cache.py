"""
Orin.LAB · Cache
Simple in-memory TTL cache for price data and signals.
"""

import time
import threading
from typing import Any, Optional


class TTLCache:
    """
    Thread-safe in-memory cache with per-entry TTL (time-to-live).
    Entries expire after `default_ttl` seconds unless overridden per set().
    """

    def __init__(self, default_ttl: float = 60.0):
        self.default_ttl = default_ttl
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        expires_at = time.monotonic() + (ttl if ttl is not None else self.default_ttl)
        with self._lock:
            self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __len__(self) -> int:
        now = time.monotonic()
        with self._lock:
            return sum(1 for _, (_, exp) in self._store.items() if exp > now)


# Shared caches
price_cache = TTLCache(default_ttl=30)       # price data: 30s TTL
signal_cache = TTLCache(default_ttl=300)     # signals: 5min TTL