"""
Orin.LAB · Rate Limiter
Token-bucket rate limiter for API calls and signal generation.
"""

import time
import threading
from collections import deque
from functools import wraps
from typing import Callable, Optional


class RateLimiter:
    """
    Sliding-window rate limiter.
    Allows `max_calls` calls per `period` seconds.
    Thread-safe.
    """

    def __init__(self, max_calls: int = 10, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self._calls: deque[float] = deque()
        self._lock = threading.Lock()

    def _cleanup(self, now: float) -> None:
        cutoff = now - self.period
        while self._calls and self._calls[0] < cutoff:
            self._calls.popleft()

    def is_allowed(self) -> bool:
        now = time.monotonic()
        with self._lock:
            self._cleanup(now)
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            return False

    def wait_and_acquire(self) -> None:
        """Block until a call slot is available."""
        while True:
            now = time.monotonic()
            with self._lock:
                self._cleanup(now)
                if len(self._calls) < self.max_calls:
                    self._calls.append(now)
                    return
                oldest = self._calls[0]
                wait = self.period - (now - oldest) + 0.01
            time.sleep(max(wait, 0.01))

    def remaining(self) -> int:
        now = time.monotonic()
        with self._lock:
            self._cleanup(now)
            return max(0, self.max_calls - len(self._calls))

    def __call__(self, fn: Callable) -> Callable:
        """Use as a decorator to rate-limit a function."""
        @wraps(fn)
        def wrapper(*args, **kwargs):
            self.wait_and_acquire()
            return fn(*args, **kwargs)
        return wrapper


# Pre-built limiters for common services
anthropic_limiter = RateLimiter(max_calls=10, period=60)
jupiter_limiter = RateLimiter(max_calls=30, period=60)
twitter_limiter = RateLimiter(max_calls=5, period=60)