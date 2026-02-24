"""Fetch and parse Sadhguru daily quotes from the Isha Foundation website."""

from __future__ import annotations

import json

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://isha.sadhguru.org/en/wisdom/quotes/date"


async def fetch_quote(source_date: str) -> dict:
    """Fetch a quote for the given date in source format (e.g., 'february-22-2026').

    Returns a dict with 'quote', 'date', and 'source_url' keys.
    """
    source_url = f"{BASE_URL}/{source_date}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            source_url,
            timeout=httpx.Timeout(10.0),
            follow_redirects=True,
        )
        response.raise_for_status()

    quote_text = _parse_quote(response.text)

    return {
        "quote": quote_text,
        "date": source_date,
        "source_url": source_url,
    }


def _parse_quote(html: str) -> str:
    """Extract quote text from __NEXT_DATA__ JSON in the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")

    if not script_tag or not script_tag.string:
        msg = "Unable to parse quote: __NEXT_DATA__ script tag not found"
        raise ValueError(msg)

    data = json.loads(script_tag.string)
    try:
        quote_text = data["props"]["pageProps"]["pageDataDetail"]["summary"][0]["value"]
    except (KeyError, IndexError, TypeError) as e:
        msg = "Unable to parse quote: unexpected page structure"
        raise ValueError(msg) from e

    if not quote_text or not quote_text.strip():
        msg = "Unable to parse quote: quote text is empty"
        raise ValueError(msg)

    return quote_text.strip()
