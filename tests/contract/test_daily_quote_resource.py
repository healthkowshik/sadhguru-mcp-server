"""Contract tests for MCP daily quote resources."""

import json
from datetime import date
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastmcp.client import Client
from mcp.shared.exceptions import McpError

from sadhguru_mcp_server.server import mcp

FETCH_QUOTE = "sadhguru_mcp_server.server.fetch_quote"


@pytest.fixture
def sample_quote():
    """A sample quote dict as returned by the scraper."""
    return {
        "quote": ("Meditation is not a conquest or achievement – it is a homecoming."),
        "date": "february-24-2026",
        "source_url": (
            "https://isha.sadhguru.org/en/wisdom/quotes/date/february-24-2026"
        ),
    }


# ──────────────────────────────────────────────────────────
# US1: sadhguru://daily-quote/today
# ──────────────────────────────────────────────────────────


class TestTodayResource:
    """Contract tests for sadhguru://daily-quote/today."""

    @pytest.mark.asyncio
    async def test_today_response_has_required_fields(self, sample_quote):
        """Response must contain quote, date, source_url."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote,
        ):
            async with Client(mcp) as client:
                result = await client.read_resource("sadhguru://daily-quote/today")
                data = json.loads(result[0].text)

                assert "quote" in data
                assert "date" in data
                assert "source_url" in data
                assert isinstance(data["quote"], str)
                assert data["quote"]
                assert isinstance(data["date"], str)
                assert data["date"]
                assert isinstance(data["source_url"], str)
                assert data["source_url"]

    @pytest.mark.asyncio
    async def test_today_date_matches_iso_today(self, sample_quote):
        """The date field must be today in ISO 8601."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote,
        ):
            async with Client(mcp) as client:
                result = await client.read_resource("sadhguru://daily-quote/today")
                data = json.loads(result[0].text)
                assert data["date"] == date.today().isoformat()

    @pytest.mark.asyncio
    async def test_today_source_url_contains_isha_domain(self, sample_quote):
        """source_url must point to isha.sadhguru.org."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote,
        ):
            async with Client(mcp) as client:
                result = await client.read_resource("sadhguru://daily-quote/today")
                data = json.loads(result[0].text)
                prefix = "https://isha.sadhguru.org/en/wisdom/quotes/date/"
                assert data["source_url"].startswith(prefix)

    @pytest.mark.asyncio
    async def test_today_idempotent_response(self, sample_quote):
        """Two reads should return identical content."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote,
        ):
            async with Client(mcp) as client:
                r1 = await client.read_resource("sadhguru://daily-quote/today")
                r2 = await client.read_resource("sadhguru://daily-quote/today")
                assert json.loads(r1[0].text) == json.loads(r2[0].text)


# ──────────────────────────────────────────────────────────
# US2: sadhguru://daily-quote/{date}
# ──────────────────────────────────────────────────────────


@pytest.fixture
def sample_quote_for_date():
    """A sample quote dict for a specific date."""
    return {
        "quote": ("The mind is like a puzzle with too many pieces missing."),
        "date": "february-22-2026",
        "source_url": (
            "https://isha.sadhguru.org/en/wisdom/quotes/date/february-22-2026"
        ),
    }


DATE_URI = "sadhguru://daily-quote/2026-02-22"


class TestDateResource:
    """Contract tests for sadhguru://daily-quote/{date}."""

    @pytest.mark.asyncio
    async def test_date_response_has_required_fields(self, sample_quote_for_date):
        """Response must contain quote, date, source_url."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote_for_date,
        ):
            async with Client(mcp) as client:
                result = await client.read_resource(DATE_URI)
                data = json.loads(result[0].text)

                assert "quote" in data
                assert "date" in data
                assert "source_url" in data
                assert isinstance(data["quote"], str)
                assert data["quote"]
                assert isinstance(data["date"], str)
                assert data["date"]
                assert isinstance(data["source_url"], str)
                assert data["source_url"]

    @pytest.mark.asyncio
    async def test_date_matches_requested_date(self, sample_quote_for_date):
        """The date field must match the requested date."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote_for_date,
        ):
            async with Client(mcp) as client:
                result = await client.read_resource(DATE_URI)
                data = json.loads(result[0].text)
                assert data["date"] == "2026-02-22"

    @pytest.mark.asyncio
    async def test_date_source_url_is_correct(self, sample_quote_for_date):
        """source_url must match the correct date."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote_for_date,
        ):
            async with Client(mcp) as client:
                result = await client.read_resource(DATE_URI)
                data = json.loads(result[0].text)
                expected = (
                    "https://isha.sadhguru.org/en/wisdom/quotes/date/february-22-2026"
                )
                assert data["source_url"] == expected

    @pytest.mark.asyncio
    async def test_date_cached_response_matches_first(self, sample_quote_for_date):
        """Cached response must match the first response."""
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            return_value=sample_quote_for_date,
        ):
            async with Client(mcp) as client:
                r1 = await client.read_resource(DATE_URI)
                r2 = await client.read_resource(DATE_URI)
                assert json.loads(r1[0].text) == json.loads(r2[0].text)


# ──────────────────────────────────────────────────────────
# US3: Error handling
# ──────────────────────────────────────────────────────────


class TestInvalidDateFormat:
    """Contract tests for invalid date format errors."""

    @pytest.mark.asyncio
    async def test_invalid_date_not_a_date(self):
        """'not-a-date' must mention ISO 8601 format."""
        async with Client(mcp) as client:
            with pytest.raises(McpError, match="ISO 8601"):
                await client.read_resource("sadhguru://daily-quote/not-a-date")

    @pytest.mark.asyncio
    async def test_invalid_date_wrong_format(self):
        """'22-02-2026' must mention ISO 8601 format."""
        async with Client(mcp) as client:
            with pytest.raises(McpError, match="ISO 8601"):
                await client.read_resource("sadhguru://daily-quote/22-02-2026")


class TestUnavailableDate:
    """Contract tests for unavailable date errors."""

    @pytest.mark.asyncio
    async def test_future_date_returns_error(self):
        """Future date must indicate no quote available."""
        url = "https://isha.sadhguru.org/en/wisdom/quotes/date/january-1-2030"
        mock_response = httpx.Response(
            404,
            request=httpx.Request("GET", url),
        )
        error = httpx.HTTPStatusError(
            "Not Found",
            request=mock_response.request,
            response=mock_response,
        )
        with patch(
            FETCH_QUOTE,
            new_callable=AsyncMock,
            side_effect=error,
        ):
            async with Client(mcp) as client:
                with pytest.raises(McpError, match="[Nn]o quote"):
                    await client.read_resource("sadhguru://daily-quote/2030-01-01")
