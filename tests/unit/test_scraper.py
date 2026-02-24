"""Unit tests for scraper — parse HTML, extract quote."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from sadhguru_mcp_server.scraper import fetch_quote
from tests.conftest import SAMPLE_QUOTE_TEXT

MOCK_CLIENT = "sadhguru_mcp_server.scraper.httpx.AsyncClient"
EXAMPLE_URL = "https://example.com"


def _mock_httpx_response(html: str) -> httpx.Response:
    """Create a mock httpx 200 response with the given HTML."""
    return httpx.Response(
        200,
        text=html,
        request=httpx.Request("GET", EXAMPLE_URL),
    )


def _setup_mock_client(mock_cls, *, response=None, side_effect=None):
    """Wire up an AsyncMock httpx client."""
    mock_client = AsyncMock()
    if side_effect:
        mock_client.get.side_effect = side_effect
    else:
        mock_client.get.return_value = response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_cls.return_value = mock_client


@pytest.mark.asyncio
async def test_fetch_quote_extracts_quote_from_next_data(
    mock_quote_html,
):
    """fetch_quote should parse __NEXT_DATA__ and extract text."""
    response = _mock_httpx_response(mock_quote_html)

    with patch(MOCK_CLIENT) as mock_cls:
        _setup_mock_client(mock_cls, response=response)
        result = await fetch_quote("february-22-2026")

    assert result["quote"] == SAMPLE_QUOTE_TEXT


@pytest.mark.asyncio
async def test_fetch_quote_returns_correct_source_url(
    mock_quote_html,
):
    """fetch_quote should return the source URL."""
    response = _mock_httpx_response(mock_quote_html)

    with patch(MOCK_CLIENT) as mock_cls:
        _setup_mock_client(mock_cls, response=response)
        result = await fetch_quote("february-22-2026")

    expected = "https://isha.sadhguru.org/en/wisdom/quotes/date/february-22-2026"
    assert result["source_url"] == expected


@pytest.mark.asyncio
async def test_fetch_quote_returns_date_in_source_format(
    mock_quote_html,
):
    """fetch_quote should return the date as provided."""
    response = _mock_httpx_response(mock_quote_html)

    with patch(MOCK_CLIENT) as mock_cls:
        _setup_mock_client(mock_cls, response=response)
        result = await fetch_quote("february-22-2026")

    assert result["date"] == "february-22-2026"


@pytest.mark.asyncio
async def test_fetch_quote_raises_on_timeout():
    """fetch_quote should raise on network timeout."""
    with patch(MOCK_CLIENT) as mock_cls:
        _setup_mock_client(
            mock_cls,
            side_effect=httpx.TimeoutException("timed out"),
        )
        with pytest.raises(httpx.TimeoutException):
            await fetch_quote("february-22-2026")


@pytest.mark.asyncio
async def test_fetch_quote_raises_on_connection_error():
    """fetch_quote should raise on connection refused."""
    with patch(MOCK_CLIENT) as mock_cls:
        _setup_mock_client(
            mock_cls,
            side_effect=httpx.ConnectError("refused"),
        )
        with pytest.raises(httpx.ConnectError):
            await fetch_quote("february-22-2026")
