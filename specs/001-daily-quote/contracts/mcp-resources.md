# MCP Contracts: Daily Quote

**Date**: 2026-02-24 | **Branch**: `001-daily-quote`

## Tool: `get_daily_quote`

**Type**: Tool (model-controlled, auto-discoverable by LLMs)
**Description**: Get Sadhguru's daily quote.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | `str` | No | Today's date | ISO 8601 date (e.g., `2026-02-24`) |

### Response

Same JSON schema as the resource responses below. The tool shares
the same scraper/cache logic as both resources.

### Rationale

MCP resources are *application-controlled* — the client application
decides when to attach them, and the model cannot invoke them
autonomously. Most MCP clients (Claude Desktop, VS Code/Copilot,
Cursor) only let the model auto-discover and invoke tools. The
`get_daily_quote` tool provides model-controlled access to the same
quote functionality, ensuring the server works across all clients
without requiring manual resource attachment.

---

## Resource Template: `sadhguru://daily-quote/{date}`

**Type**: Resource Template (appears in `list_resource_templates`)
**MIME type**: `application/json`
**Description**: Sadhguru's daily quote for a specific date.

### URI Parameter

| Parameter | Type | Format | Example |
|-----------|------|--------|---------|
| `date` | `str` | ISO 8601 `yyyy-mm-dd` | `2026-02-22` |

### Success Response (200)

```json
{
  "quote": "Meditation is not a conquest or achievement – it is a homecoming.",
  "date": "2026-02-22",
  "source_url": "https://isha.sadhguru.org/en/wisdom/quotes/date/february-22-2026"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `quote` | `string` | Exact quote text from the source page |
| `date` | `string` | The requested date in ISO 8601 format (`yyyy-mm-dd`) |
| `source_url` | `string` | Full URL to the source page for attribution (uses source website's date format) |

### Error Responses

**Invalid date format** (e.g., `not-a-date`, `22-02-2026`):
- Error with message describing the expected format:
  `"Invalid date format: 'not-a-date'. Expected format: yyyy-mm-dd (e.g., 2026-02-22)"`

**No quote available** (e.g., future date, date with no published content):
- Error with message:
  `"No quote available for date: 2030-01-01"`

**Upstream unreachable** (network error, timeout):
- Error with message:
  `"Unable to fetch quote: upstream source is unavailable"`

---

## Fixed Resource: `sadhguru://daily-quote/today`

**Type**: Fixed Resource (appears in `list_resources`)
**MIME type**: `application/json`
**Description**: Sadhguru's daily quote for today.

### Parameters

None. The server resolves "today" to the current calendar date using
server-local timezone.

### Success Response (200)

Same schema as the resource template response.

### Error Responses

Same error types as the resource template. The `today` resource
internally resolves to a date string and delegates to the same
fetch/cache logic.

### Caching Behavior

- First request for a given date fetches from the upstream source.
- Subsequent requests for the same date (same calendar day) are
  served from in-memory cache.
- At midnight (server-local time), the cache is lazily invalidated
  on the next request.
- Cache is not persistent across server restarts.

---

## Contract Test Expectations

Tests MUST verify:

1. **Schema**: Response contains `quote`, `date`, and `source_url`
   fields, all non-empty strings.
2. **Idempotency**: Two reads of the same date return identical content.
3. **Today resolution**: `sadhguru://daily-quote/today` returns a
   response with `date` matching today's date in ISO 8601 format.
4. **Invalid format error**: Non-ISO-8601 date strings produce a
   descriptive error mentioning the expected format (`yyyy-mm-dd`).
5. **Unavailable date error**: Dates with no content produce a
   descriptive error.
6. **Source URL correctness**: The `source_url` field matches
   `https://isha.sadhguru.org/en/wisdom/quotes/date/{date}`.
