# Quickstart: Daily Quote Resource

**Date**: 2026-02-24 | **Branch**: `001-daily-quote`

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Astral package manager)

## Setup

```bash
# Clone and enter the project
cd sadhguru-mcp-server

# Install dependencies
uv sync

# Run the MCP server
uv run python -m sadhguru_mcp_server
```

## Project Structure

```text
src/
└── sadhguru_mcp_server/
    ├── __init__.py
    ├── __main__.py        # Entry point: creates and runs the MCP server
    ├── server.py          # FastMCP server instance and resource registration
    ├── scraper.py         # Fetch and parse quotes from Isha Foundation
    └── cache.py           # In-memory cache with midnight expiry

tests/
├── conftest.py            # Shared fixtures
├── contract/
│   └── test_daily_quote_resource.py  # MCP resource contract tests
├── unit/
│   ├── test_scraper.py    # Scraping and parsing tests
│   └── test_cache.py      # Cache behavior tests
└── integration/
    └── test_daily_quote_e2e.py       # End-to-end with real HTTP
```

## Usage

### With an MCP client

Configure your MCP client to connect to the server. The server
exposes two resources:

- **`sadhguru://daily-quote/today`** — today's quote
- **`sadhguru://daily-quote/{date}`** — quote for a specific date
  (e.g., `sadhguru://daily-quote/february-22-2026`)

### Running tests

```bash
# Run all tests
uv run pytest

# Run only contract tests
uv run pytest tests/contract/

# Run only unit tests
uv run pytest tests/unit/
```

### Linting

```bash
uv run ruff check .
uv run ruff format .
```
