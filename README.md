# sadhguru-mcp-server

> Namaskaram Sadhguru! 🙏

An MCP server that serves Sadhguru's daily quotes from [isha.sadhguru.org](https://isha.sadhguru.org/en/wisdom/quotes).

## Resources

| Resource URI | Description |
|---|---|
| `sadhguru://daily-quote/today` | Today's quote |
| `sadhguru://daily-quote/{date}` | Quote for a specific date (ISO 8601: `yyyy-mm-dd`) |

Both resources return JSON with three fields:

```json
{
  "quote": "Meditation is not a conquest or achievement – it is a homecoming.",
  "date": "2026-02-24",
  "source_url": "https://isha.sadhguru.org/en/wisdom/quotes/date/february-24-2026"
}
```

## Quickstart

**Requirements**: Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
# Clone and install
git clone https://github.com/healthkowshik/sadhguru-mcp-server.git
cd sadhguru-mcp-server
uv sync
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sadhguru": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/sadhguru-mcp-server", "python", "-m", "sadhguru_mcp_server"]
    }
  }
}
```

### Run directly

```bash
uv run python -m sadhguru_mcp_server
```

## Development

```bash
# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format --check .
```

## How it works

The server scrapes quotes from the Isha Foundation website by parsing the `__NEXT_DATA__` JSON embedded in each page. Responses are cached in-memory per date and expire at midnight.

## License

MIT
