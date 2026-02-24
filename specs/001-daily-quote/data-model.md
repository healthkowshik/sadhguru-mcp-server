# Data Model: Daily Quote Resource

**Date**: 2026-02-24 | **Branch**: `001-daily-quote`

## Entities

### DailyQuote

Represents a single Sadhguru quote for a specific date, as retrieved
from the Isha Foundation website.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `quote` | `str` | Exact quote text as published | Non-empty; no modification from source |
| `date` | `str` | Date in `month-day-year` format | Matches pattern `^[a-z]+-\d{1,2}-\d{4}$` |
| `source_url` | `str` | Full URL to the source page | Valid HTTPS URL on `isha.sadhguru.org` |

**Validation rules**:
- `quote` must be non-empty after stripping whitespace.
- `date` must be a valid calendar date in the expected format
  (lowercase full month name, unpadded day, four-digit year).
- `source_url` is deterministically derived from `date`:
  `https://isha.sadhguru.org/en/wisdom/quotes/date/{date}`

**State transitions**: None. DailyQuote is immutable once fetched.

### QuoteCache

In-memory cache for fetched quotes. Not a domain entity — purely an
implementation detail for performance.

| Field | Type | Description |
|-------|------|-------------|
| `_store` | `dict[str, DailyQuote]` | Date-keyed cache entries |
| `_date_key` | `str` | The calendar day the cache was last validated |

**Behavior**:
- On `get(date)`: If `_date_key` differs from today, clear `_store`
  and update `_date_key`. Then return the entry or `None`.
- On `set(date, quote)`: Same staleness check, then store the entry.

## Relationships

```
MCP Client ──reads──▶ Resource("sadhguru://daily-quote/{date}")
                           │
                           ▼
                      QuoteCache
                           │ (cache miss)
                           ▼
                      Isha Foundation website
                           │
                           ▼
                      DailyQuote (returned to client as JSON)
```

## Serialization

DailyQuote is serialized to JSON via `json.dumps()` for the MCP
resource response:

```json
{
  "quote": "The only way out is in.",
  "date": "february-24-2026",
  "source_url": "https://isha.sadhguru.org/en/wisdom/quotes/date/february-24-2026"
}
```
