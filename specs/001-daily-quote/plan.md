# Implementation Plan: Daily Quote Resource

**Branch**: `001-daily-quote` | **Date**: 2026-02-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-daily-quote/spec.md`

## Summary

An MCP server that serves Sadhguru's daily quote by scraping the Isha
Foundation website. Exposes three MCP endpoints sharing the same
scraper/cache logic:

- **Tool**: `get_daily_quote` — model-controlled, works across all
  MCP clients. Optional `date` parameter (ISO 8601, defaults to today).
- **Resource template**: `sadhguru://daily-quote/{date}` — accepts
  ISO 8601 dates like `2026-02-22`.
- **Fixed resource**: `sadhguru://daily-quote/today` — convenience
  alias resolving to the current date.

The server converts ISO dates to the source website's format internally.
Returns structured JSON with `quote`, `date`, and `source_url` fields.
Responses are cached in-memory per date for the remainder of the calendar day.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastMCP 3.0, httpx (HTTP client), beautifulsoup4 (HTML parsing)
**Storage**: In-memory cache (dict with date-keyed entries, TTL until midnight)
**Testing**: pytest (via `uv run pytest`)
**Target Platform**: Any platform supporting Python 3.11+ (server process)
**Project Type**: MCP server (library/service)
**Performance Goals**: <2s first request, <100ms cached requests (from spec SC-001, SC-002)
**Constraints**: In-memory cache only; no persistence across restarts
**Scale/Scope**: Single MCP server, 1 tool, 1 resource template, 1 convenience resource

## Constitution Check (Pre-Research)

*GATE: Must pass before Phase 0 research.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Content Fidelity | PASS | Spec FR-004 requires exact quote text, no paraphrasing. FR-005 requires source URL attribution. Scraping preserves original content. |
| II. MCP-First Design | PASS | Feature is exposed as MCP tool (`get_daily_quote`) and resources (`sadhguru://daily-quote/{date}`, `sadhguru://daily-quote/today`). Tool added for model-controlled cross-client compatibility. No side-channel APIs. |
| III. Test-First | PASS | Will be enforced during implementation. Contract tests for MCP resource schema + behavior will be written before production code. |
| IV. Simplicity (YAGNI) | PASS | Single resource template, in-memory cache, no ORM or database. Flat module structure. Only httpx + beautifulsoup4 added as dependencies (both justified by scraping requirement). |
| Tech Stack | PASS | Python 3.11+, FastMCP 3.0, pytest, ruff, uv — all per constitution. |
| Dev Workflow | PASS | Following speckit workflow. Contract tests planned before implementation. |

## Constitution Check (Post-Design)

*Re-check after Phase 1 design artifacts are complete.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Content Fidelity | PASS | Scraper extracts exact quote from `__NEXT_DATA__` JSON — no paraphrasing. `source_url` included in every response per contract. |
| II. MCP-First Design | PASS | One MCP tool (`@mcp.tool()`) and two MCP resources (`@mcp.resource()`) registered. Tool ensures model-controlled discovery; resources provide application-controlled access. No side-channel APIs. |
| III. Test-First | PASS | Contract test expectations defined in `contracts/mcp-resources.md`. Test directory structure planned with contract/unit/integration separation. |
| IV. Simplicity (YAGNI) | PASS | Three focused modules (`server.py`, `scraper.py`, `cache.py`). No class hierarchies. Dict-based cache with lazy expiry — simplest correct approach. |
| Tech Stack | PASS | All dependencies justified in `research.md`: httpx (async HTTP), beautifulsoup4 (HTML parsing with stdlib parser). No unnecessary additions. |
| Dev Workflow | PASS | Content fetched from external source at runtime, not stored alongside code. Flat module structure supports atomic commits. |

## Project Structure

### Documentation (this feature)

```text
specs/001-daily-quote/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: technology decisions
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: setup and usage guide
├── contracts/
│   └── mcp-resources.md # Phase 1: MCP resource contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
└── sadhguru_mcp_server/
    ├── __init__.py        # Package init
    ├── __main__.py        # Entry point: mcp.run()
    ├── server.py          # FastMCP instance + tool & resource registration
    ├── scraper.py         # Fetch + parse quotes from source website
    └── cache.py           # In-memory cache with midnight expiry

tests/
├── conftest.py            # Shared fixtures (mock HTTP responses, etc.)
├── contract/
│   └── test_daily_quote_resource.py  # MCP resource schema + behavior
├── unit/
│   ├── test_scraper.py    # Scraping and parsing logic
│   └── test_cache.py      # Cache expiry behavior
└── integration/
    └── test_daily_quote_e2e.py       # End-to-end with real upstream
```

**Structure Decision**: Single project layout. Flat module structure
under `src/sadhguru_mcp_server/` with three focused modules (`server`,
`scraper`, `cache`). No models/ or services/ subdirectories — the
project is too small to warrant them. Tests are organized by type
(contract, unit, integration) per constitution.

## Complexity Tracking

> No constitution violations. Table intentionally left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | | |
