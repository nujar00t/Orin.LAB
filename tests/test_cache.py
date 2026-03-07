"""
Tests for utils/cache.py
"""

import time
import pytest
from utils.cache import TTLCache


class TestTTLCache:
    def test_set_and_get(self):
        cache = TTLCache(default_ttl=60)
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_miss_returns_none(self):
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_expiry(self):
        cache = TTLCache(default_ttl=0.1)
        cache.set("key", "value")
        time.sleep(0.15)
        assert cache.get("key") is None

    def test_custom_ttl(self):
        cache = TTLCache(default_ttl=60)
        cache.set("key", "value", ttl=0.1)
        time.sleep(0.15)
        assert cache.get("key") is None

    def test_delete(self):
        cache = TTLCache()
        cache.set("key", "value")
        cache.delete("key")
        assert cache.get("key") is None

    def test_clear(self):
        cache = TTLCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert len(cache) == 0

    def test_contains(self):
        cache = TTLCache()
        cache.set("key", "value")
        assert "key" in cache
        assert "other" not in cache

    def test_len(self):
        cache = TTLCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert len(cache) == 2

    def test_len_excludes_expired(self):
        cache = TTLCache(default_ttl=0.1)
        cache.set("a", 1)
        cache.set("b", 2, ttl=60)
        time.sleep(0.15)
        assert len(cache) == 1

    def test_overwrite(self):
        cache = TTLCache()
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"