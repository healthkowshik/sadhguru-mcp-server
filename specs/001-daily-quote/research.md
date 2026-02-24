# Research: Daily Quote Resource

**Date**: 2026-02-24 | **Branch**: `001-daily-quote`

## Decision 1: HTTP Client

**Decision**: httpx (async)
**Rationale**: httpx is the standard async HTTP client for Python. It
supports `async with` context management, configurable timeouts, and
mirrors the familiar `requests` API. Since FastMCP resource handlers
support `async def`, using httpx's `AsyncClient` avoids blocking the
event loop during upstream fetches.
**Alternatives considered**:
- `aiohttp`: More mature async library but heavier API surface. httpx
  is simpler and aligns with modern Python conventions.
- `urllib3` / `requests`: Synchronous only. Would require threadpool
  offloading, adding unnecessary complexity.

## Decision 2: HTML Parsing Strategy

**Decision**: Parse `__NEXT_DATA__` JSON from the `<script>` tag using
beautifulsoup4 to locate the tag, then `json.loads()` to extract the
quote from structured data.

**Rationale**: The source page is a Next.js SSR application. The HTML
contains a `<script id="__NEXT_DATA__" type="application/json">` tag
with the full page data as JSON. The quote text lives at:

```
props.pageProps.pageDataDetail.summary[0].value
```

This is far more stable than CSS class selectors (`css-1cw0rco`) which
are Emotion/CSS-in-JS hashes that can change with any rebuild.

**Fallback**: If `__NEXT_DATA__` is missing, extract the quote from the
`<meta property="og:description" content="...">` tag. This is a
standard meta tag unlikely to be removed.

**Alternatives considered**:
- CSS class selectors (`div.css-1cw0rco`): Unstable. Emotion generates
  hashed class names that change on rebuild. Rejected.
- Regex-only (no beautifulsoup4): Fragile for HTML edge cases.
  beautifulsoup4 with `html.parser` is robust and requires no C deps.
- `lxml`: Faster but requires C library. Overkill for parsing a single
  page. `html.parser` (stdlib) is sufficient.

## Decision 3: beautifulsoup4 Parser

**Decision**: `html.parser` (Python stdlib)
**Rationale**: No C dependency required. Performance is irrelevant since
we parse a single page per cache miss. Keeps the dependency footprint
minimal.
**Alternatives considered**:
- `lxml`: Requires `libxml2`. Unnecessary for this use case.
- `html5lib`: Slowest option. No benefit for well-formed HTML.

## Decision 4: Caching Strategy

**Decision**: In-memory `dict` with lazy midnight expiry.
**Rationale**: The spec requires per-date caching that expires at
midnight. A plain dict keyed by date string is the simplest correct
approach. Staleness is checked lazily on each `get`/`set` call by
comparing a stored date marker against `date.today()`. No background
tasks, no timers, no external libraries.

asyncio is single-threaded, so no locking is needed. The cache is not
persistent across restarts, which matches the spec requirement.

**Alternatives considered**:
- `cachetools.TTLCache`: External dependency for a trivial use case.
  Violates YAGNI.
- `functools.lru_cache`: TTL-based expiry is awkward. Midnight-aligned
  expiry is not a natural fit.
- Per-entry TTL with timestamps: More complex than needed. A single
  date marker that clears the entire cache on day rollover is simpler
  and correct since old-day entries are stale anyway.

## Decision 5: FastMCP Tool & Resource Registration

**Decision**: One `@mcp.tool()` and two `@mcp.resource()` registrations,
all sharing the same scraper/cache logic.

```python
@mcp.tool()
async def get_daily_quote(date: str = "") -> str:
    """Get Sadhguru's daily quote."""
    # date is ISO 8601 (e.g., "2026-02-22"), defaults to today
    ...

@mcp.resource("sadhguru://daily-quote/{date}", mime_type="application/json")
async def get_quote_by_date(date: str) -> str:
    ...

@mcp.resource("sadhguru://daily-quote/today", mime_type="application/json")
async def get_todays_quote() -> str:
    ...
```

**Rationale**: MCP resources are *application-controlled* — the client
application decides when to attach them, and the model cannot discover
or invoke them autonomously. Most MCP clients (Claude Desktop,
VS Code/Copilot, Cursor) only let the model auto-discover tools.
A server with only resources appears invisible to the model.

The `get_daily_quote` tool provides model-controlled access to the same
functionality, ensuring cross-client compatibility. The resources remain
for clients that support application-controlled attachment (e.g.,
Claude Code `@`-mentions, MCP Inspector manual triggers).

FastMCP distinguishes templates (with `{param}` in URI) from fixed
resources (concrete URI) automatically. The `today` resource is
matched before the template, so there is no routing conflict.

Return type is `str` with `json.dumps()` and `mime_type="application/json"`.
FastMCP does not support returning dicts directly.

## Decision 6: Error Handling

**Decision**: Raise `ValueError` with descriptive messages for:
- Invalid date format (not matching `month-day-year` pattern)
- HTTP 404 from upstream (no quote for that date)
- Network errors (connection timeout, DNS failure)
- Missing quote in parsed HTML (page exists but structure changed)

**Rationale**: The spec requires descriptive errors for all failure
modes (FR-007, FR-008). Clear error messages help MCP clients display
meaningful feedback.

## Source Page Findings

**URL pattern**: `https://isha.sadhguru.org/en/wisdom/quotes/date/{month}-{day}-{year}`
- Month: lowercase full name (e.g., `february`)
- Day: no zero-padding (e.g., `3` not `03`)
- Year: four digits

**Date conversion**: The MCP resource accepts ISO 8601 dates
(`yyyy-mm-dd`, e.g., `2026-02-22`). The server converts to the source
URL format internally:
```
2026-02-22 → february-22-2026
```
Conversion uses `datetime.date.fromisoformat()` for parsing and
`date.strftime("%-d")` for unpadded day.

**HTTP behavior**:
- 200 for valid dates with published quotes
- 404 for future dates, invalid dates, and dates without published content
- Not all past dates have quotes (gaps in coverage)
- `Access-Control-Allow-Origin: *` (no CORS issues)
- Server-rendered HTML (no JavaScript needed)

**Dependencies summary**:

| Package | Version | Justification |
|---------|---------|---------------|
| fastmcp | >=3.0 | MCP framework (constitution mandate) |
| httpx | >=0.27 | Async HTTP client for upstream fetches |
| beautifulsoup4 | >=4.12 | HTML parsing to extract quote from `__NEXT_DATA__` |
