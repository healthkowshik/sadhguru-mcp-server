"""In-memory cache with lazy midnight expiry."""

from __future__ import annotations

from datetime import date


class QuoteCache:
    """Cache that expires all entries when the calendar day rolls over.

    Not persistent across restarts. Not thread-safe (asyncio is single-threaded).
    """

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self._date_key: str = date.today().isoformat()

    def _expire_if_stale(self) -> None:
        """Clear the cache if the date has rolled over."""
        today = date.today().isoformat()
        if self._date_key != today:
            self._store.clear()
            self._date_key = today

    def get(self, key: str) -> dict | None:
        self._expire_if_stale()
        return self._store.get(key)

    def set(self, key: str, value: dict) -> None:
        self._expire_if_stale()
        self._store[key] = value
