# Feature Specification: Daily Quote Resource

**Feature Branch**: `001-daily-quote`
**Created**: 2026-02-24
**Status**: Draft
**Input**: User description: "An MCP resource that serves Sadhguru's daily
quote by scraping https://isha.sadhguru.org/en/wisdom/quotes/date/{date}.
Exposed as a resource template at sadhguru://daily-quote/{date} where
date uses ISO 8601 format (e.g., 2026-02-22). The server internally
converts to the source URL format (month-day-year). A convenience
resource sadhguru://daily-quote/today resolves to the current date. Returns
the quote text with source URL attribution. Responses MUST be cached for
the duration of the day to avoid redundant requests."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Get Today's Quote (Priority: P1)

A client requests today's Sadhguru daily quote by reading the
`sadhguru://daily-quote/today` resource and receives the quote text
along with the source URL for proper attribution.

**Why this priority**: This is the primary use case. Most consumers want
"today's wisdom" without needing to know or construct a date string.

**Independent Test**: Can be fully tested by reading the
`sadhguru://daily-quote/today` resource and verifying it returns a
non-empty quote with a valid source URL pointing to today's date on
isha.sadhguru.org.

**Acceptance Scenarios**:

1. **Given** the MCP server is running, **When** a client reads
   `sadhguru://daily-quote/today`, **Then** it receives the quote text
   for the current date (in ISO 8601 format) and a source URL in the
   format `https://isha.sadhguru.org/en/wisdom/quotes/date/{month}-{day}-{year}`.
2. **Given** a client reads `sadhguru://daily-quote/today` twice within
   the same calendar day, **When** the second request is made, **Then**
   the response is served from cache without fetching the source again.

---

### User Story 2 - Get Quote by Date (Priority: P2)

A client requests a Sadhguru quote for a specific date — for example,
a user's birthday or a memorable occasion. The client reads
`sadhguru://daily-quote/2026-02-22` and receives that day's quote
with source attribution.

**Why this priority**: Enables historical access and date-specific
lookups, which broadens utility beyond just "today." Depends on the
same fetching and parsing logic as P1.

**Independent Test**: Can be tested by reading
`sadhguru://daily-quote/2026-02-22` and verifying the returned
quote matches the content at the corresponding source URL.

**Acceptance Scenarios**:

1. **Given** the MCP server is running, **When** a client reads
   `sadhguru://daily-quote/2026-02-22`, **Then** it receives the
   quote text published on that date with the matching source URL.
2. **Given** a client reads the same date resource multiple times,
   **When** subsequent requests occur within the cache window, **Then**
   responses are served from cache.

---

### User Story 3 - Graceful Error on Unavailable Date (Priority: P3)

A client requests a quote for a date that has no content — for example,
a future date not yet published or a malformed date string.
The system returns a clear error message rather than crashing or
returning empty content.

**Why this priority**: Error resilience is important but secondary to
the core happy-path functionality. Prevents confusing failures for
MCP clients.

**Independent Test**: Can be tested by reading a resource with a
far-future date (e.g., `sadhguru://daily-quote/2030-01-01`) or
an invalid string (e.g., `sadhguru://daily-quote/not-a-date`) and
verifying a descriptive error is returned.

**Acceptance Scenarios**:

1. **Given** the MCP server is running, **When** a client reads
   `sadhguru://daily-quote/2030-01-01` and no quote exists for
   that date, **Then** the system returns an error indicating no quote
   is available for the requested date.
2. **Given** the MCP server is running, **When** a client reads
   `sadhguru://daily-quote/not-a-date`, **Then** the system returns
   an error indicating the date format is invalid, with the expected
   format (e.g., "yyyy-mm-dd like 2026-02-22").

---

### Edge Cases

- What happens when the source website is temporarily unreachable?
  The system MUST return a clear error indicating the upstream source
  is unavailable, not an empty or malformed quote.
- What happens when the source page exists but contains no quote text?
  The system MUST return an error rather than an empty string.
- What happens at midnight when "today" rolls over? The cache for the
  previous day's "today" request MUST be invalidated so the next
  request fetches the new day's quote.
- What happens when the source URL format changes? The system MUST
  fail visibly (error) rather than silently returning wrong content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an MCP resource template at
  `sadhguru://daily-quote/{date}` where `{date}` follows ISO 8601
  format `yyyy-mm-dd` (e.g., `2026-02-22`). The server internally
  converts to the source website's format for fetching.
- **FR-001a**: System MUST expose a `get_daily_quote` MCP tool with
  an optional `date` parameter (ISO 8601, defaults to today).
  MCP resources are application-controlled and not auto-discoverable
  by models; the tool provides model-controlled access to the same
  functionality, ensuring cross-client compatibility.
- **FR-002**: System MUST expose a convenience resource at
  `sadhguru://daily-quote/today` that resolves to the current
  calendar date.
- **FR-003**: System MUST fetch the quote content from the source URL
  `https://isha.sadhguru.org/en/wisdom/quotes/date/{date}`.
- **FR-004**: System MUST return the exact quote text as published on
  the source page — no paraphrasing, truncation, or modification.
- **FR-005**: System MUST include the source URL in every response so
  clients can attribute the quote.
- **FR-006**: System MUST cache responses per date for the remainder
  of the calendar day (until midnight) to avoid redundant fetches.
- **FR-007**: System MUST return a descriptive error when the requested
  date has no published quote or the source is unreachable.
- **FR-008**: System MUST validate the date parameter as a valid
  ISO 8601 date (`yyyy-mm-dd`) and return a descriptive error with
  the expected format when invalid.

### Key Entities

- **DailyQuote**: A single Sadhguru quote for a specific date.
  Attributes: `quote` (the exact quote text), `date` (the date in
  ISO 8601 format, e.g., `2026-02-22`), `source_url` (full URL to
  the source page). Returned as a structured object with these three
  separate fields.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A client reading `sadhguru://daily-quote/today` receives
  the correct quote within 2 seconds on first request.
- **SC-002**: Cached requests (same date, same day) are served within
  100 milliseconds.
- **SC-003**: The returned quote text exactly matches the content
  displayed on the source webpage for that date.
- **SC-004**: 100% of requests for invalid or unavailable dates return
  a descriptive error message (never an empty or malformed response).

## Clarifications

### Session 2026-02-24

- Q: Should user stories say "AI assistant" or use a more inclusive term? → A: Use "client" — neutral MCP term covering both AI and human consumers.
- Q: Should the response be plain text, structured fields, or markdown? → A: Structured object with separate `quote`, `date`, and `source_url` fields.
- Q: Should the system rate-limit requests to the upstream source? → A: No — per-date caching is sufficient protection.
- Q: Should the resource support multiple languages? → A: English only. Multi-language deferred to a future feature.
- Q: Should cache persist across server restarts? → A: No — in-memory only.
- Q: Why expose a tool in addition to resources? → A: MCP resources are
  application-controlled (the client app decides when to attach them).
  Most MCP clients (Claude Desktop, VS Code, Cursor) only let the model
  autonomously invoke tools, not resources. A `get_daily_quote` tool
  ensures the model can discover and use the server without manual user
  intervention. The tool shares the same scraper/cache logic as the
  resources.

## Out of Scope

- Multi-language quote support (source offers 15+ languages; deferred
  to a future feature).
- Rate limiting or throttling of upstream fetches beyond per-date
  caching.

## Assumptions

- The source URL pattern
  `https://isha.sadhguru.org/en/wisdom/quotes/date/{date}` is stable
  and publicly accessible without authentication.
- Each date has at most one quote published.
- The MCP resource accepts dates in ISO 8601 format (`yyyy-mm-dd`).
  The server converts to the source website's format internally.
- "Today" is determined by the server's local timezone.
- Cache is in-memory only; a server restart clears the cache and
  subsequent requests re-fetch from the source.
