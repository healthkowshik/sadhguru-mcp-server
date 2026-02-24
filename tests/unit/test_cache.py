"""Unit tests for QuoteCache — get, set, and midnight expiry."""

from datetime import date
from unittest.mock import patch

from sadhguru_mcp_server.cache import QuoteCache


def test_get_returns_none_for_missing_key():
    cache = QuoteCache()
    assert cache.get("2026-02-22") is None


def test_set_and_get_returns_stored_value():
    cache = QuoteCache()
    quote = {
        "quote": "Test quote",
        "date": "2026-02-22",
        "source_url": "https://example.com",
    }
    cache.set("2026-02-22", quote)
    assert cache.get("2026-02-22") == quote


def test_get_returns_none_for_different_key():
    cache = QuoteCache()
    quote = {
        "quote": "Test quote",
        "date": "2026-02-22",
        "source_url": "https://example.com",
    }
    cache.set("2026-02-22", quote)
    assert cache.get("2026-02-23") is None


def test_cache_clears_on_day_rollover():
    quote = {
        "quote": "Test quote",
        "date": "2026-02-22",
        "source_url": "https://example.com",
    }

    # Set a value "today" (Feb 22)
    with patch("sadhguru_mcp_server.cache.date") as mock_date:
        mock_date.today.return_value = date(2026, 2, 22)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        cache = QuoteCache()
        cache.set("2026-02-22", quote)
        assert cache.get("2026-02-22") == quote

    # Next day (Feb 23) — cache should be cleared
    with patch("sadhguru_mcp_server.cache.date") as mock_date:
        mock_date.today.return_value = date(2026, 2, 23)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        assert cache.get("2026-02-22") is None


def test_cache_set_on_new_day_clears_old_entries():
    old_quote = {
        "quote": "Old",
        "date": "2026-02-22",
        "source_url": "https://example.com",
    }
    new_quote = {
        "quote": "New",
        "date": "2026-02-23",
        "source_url": "https://example.com",
    }

    with patch("sadhguru_mcp_server.cache.date") as mock_date:
        mock_date.today.return_value = date(2026, 2, 22)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        cache = QuoteCache()
        cache.set("2026-02-22", old_quote)

    with patch("sadhguru_mcp_server.cache.date") as mock_date:
        mock_date.today.return_value = date(2026, 2, 23)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        cache.set("2026-02-23", new_quote)
        assert cache.get("2026-02-23") == new_quote
        assert cache.get("2026-02-22") is None  # Old entry cleared
