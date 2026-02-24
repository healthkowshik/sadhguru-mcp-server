# MCP Resource Contracts: Daily Quote

**Date**: 2026-02-24 | **Branch**: `001-daily-quote`

## Resource Template: `sadhguru://daily-quote/{date}`

**Type**: Resource Template (appears in `list_resource_templates`)
**MIME type**: `application/json`
**Description**: Sadhguru's daily quote for a specific date.

### URI Parameter

| Parameter | Type | Format | Example |
|-----------|------|--------|---------|
| `date` | `str` | `month-day-year` (lowercase full month, unpadded day, 4-digit year) | `february-22-2026` |

### Success Response (200)

```json
{
  "quote": "Meditation is not a conquest or achievement – it is a homecoming.",
  "date": "february-22-2026",
  "source_url": "https://isha.sadhguru.org/en/wisdom/quotes/date/february-22-2026"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `quote` | `string` | Exact quote text from the source page |
| `date` | `string` | The requested date in `month-day-year` format |
| `source_url` | `string` | Full URL to the source page for attribution |

### Error Responses

**Invalid date format** (e.g., `not-a-date`, `02-22-2026`):
- Error with message describing the expected format:
  `"Invalid date format: 'not-a-date'. Expected format: month-day-year (e.g., february-22-2026)"`

**No quote available** (e.g., future date, date with no published content):
- Error with message:
  `"No quote available for date: january-01-2030"`

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
   response with `date` matching today's date.
4. **Invalid format error**: Invalid date strings produce a descriptive
   error mentioning the expected format.
5. **Unavailable date error**: Dates with no content produce a
   descriptive error.
6. **Source URL correctness**: The `source_url` field matches
   `https://isha.sadhguru.org/en/wisdom/quotes/date/{date}`.
