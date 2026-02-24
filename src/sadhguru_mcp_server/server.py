"""FastMCP server instance and resource registration."""

from __future__ import annotations

import json
from datetime import date as date_module

import httpx
from fastmcp import FastMCP

from sadhguru_mcp_server.cache import QuoteCache
from sadhguru_mcp_server.scraper import fetch_quote

mcp = FastMCP(name="SadhguruServer")
_cache = QuoteCache()


def _iso_to_source_date(iso_date: str) -> str:
    """Convert ISO 8601 date to source website format.

    Example: '2026-02-22' -> 'february-22-2026'
    """
    d = date_module.fromisoformat(iso_date)
    month = d.strftime("%B").lower()
    return f"{month}-{d.day}-{d.year}"


@mcp.resource(
    "sadhguru://daily-quote/today",
    name="TodaysQuote",
    description="Sadhguru's daily quote for today.",
    mime_type="application/json",
)
async def get_todays_quote() -> str:
    """Retrieve today's daily quote."""
    today_iso = date_module.today().isoformat()
    return await _get_quote_json(today_iso)


@mcp.resource(
    "sadhguru://daily-quote/{date}",
    name="QuoteByDate",
    description=(
        "Sadhguru's daily quote for a specific date (ISO 8601 format: yyyy-mm-dd)."
    ),
    mime_type="application/json",
)
async def get_quote_by_date(date: str) -> str:
    """Retrieve a daily quote for the given ISO 8601 date."""
    _validate_iso_date(date)
    return await _get_quote_json(date)


@mcp.tool()
async def get_daily_quote(date: str = "") -> str:
    """Get Sadhguru's daily quote.

    Args:
        date: ISO 8601 date (e.g. 2026-02-24). Defaults to today.
    """
    if not date:
        date = date_module.today().isoformat()
    _validate_iso_date(date)
    return await _get_quote_json(date)


def _validate_iso_date(iso_date: str) -> None:
    """Validate that the given string is a valid ISO 8601 date (yyyy-mm-dd)."""
    try:
        date_module.fromisoformat(iso_date)
    except ValueError:
        msg = (
            f"Invalid date format: '{iso_date}'."
            " Expected ISO 8601 format: yyyy-mm-dd"
            " (e.g., 2026-02-22)"
        )
        raise ValueError(msg) from None


async def _get_quote_json(iso_date: str) -> str:
    """Shared logic: check cache, fetch on miss, return JSON string."""
    cached = _cache.get(iso_date)
    if cached is not None:
        return json.dumps(cached)

    source_date = _iso_to_source_date(iso_date)

    try:
        raw = await fetch_quote(source_date)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            msg = f"No quote available for date: {iso_date}"
            raise ValueError(msg) from None
        msg = (
            f"Upstream error (HTTP {e.response.status_code})"
            f" while fetching quote for {iso_date}"
        )
        raise ValueError(msg) from None
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        msg = (
            "Upstream unavailable: could not reach"
            f" isha.sadhguru.org ({type(e).__name__})"
        )
        raise ValueError(msg) from None

    quote_data = {
        "quote": raw["quote"],
        "date": iso_date,
        "source_url": raw["source_url"],
    }

    _cache.set(iso_date, quote_data)
    return json.dumps(quote_data)
