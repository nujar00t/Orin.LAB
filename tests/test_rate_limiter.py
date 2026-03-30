"""
Tests for utils/rate_limiter.py
"""

import time
import threading
import pytest
from utils.rate_limiter import RateLimiter


class TestRateLimiter:
    def test_allows_calls_within_limit(self):
        limiter = RateLimiter(max_calls=5, period=60)
        for _ in range(5):
            assert limiter.is_allowed() is True

    def test_blocks_calls_over_limit(self):
        limiter = RateLimiter(max_calls=3, period=60)
        for _ in range(3):
            limiter.is_allowed()
        assert limiter.is_allowed() is False

    def test_remaining_decrements(self):
        limiter = RateLimiter(max_calls=5, period=60)
        assert limiter.remaining() == 5
        limiter.is_allowed()
        assert limiter.remaining() == 4

    def test_window_slides(self):
        limiter = RateLimiter(max_calls=2, period=0.2)
        limiter.is_allowed()
        limiter.is_allowed()
        assert limiter.is_allowed() is False
        time.sleep(0.25)
        assert limiter.is_allowed() is True

    def test_thread_safety(self):
        limiter = RateLimiter(max_calls=10, period=60)
        results = []
        lock = threading.Lock()

        def call():
            allowed = limiter.is_allowed()
            with lock:
                results.append(allowed)

        threads = [threading.Thread(target=call) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert results.count(True) == 10
        assert results.count(False) == 10

    def test_decorator(self):
        limiter = RateLimiter(max_calls=100, period=60)
        call_count = 0

        @limiter
        def my_func():
            nonlocal call_count
            call_count += 1

        for _ in range(5):
            my_func()

        assert call_count == 5