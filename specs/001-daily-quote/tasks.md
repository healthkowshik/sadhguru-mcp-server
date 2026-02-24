# Tasks: Daily Quote Resource

**Input**: Design documents from `/specs/001-daily-quote/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-resources.md

**Tests**: Included — constitution principle III (Test-First) is NON-NEGOTIABLE.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency installation, directory structure

- [ ] T001 Create `pyproject.toml` with project metadata, Python 3.11+ requirement, and dependencies (fastmcp>=3.0, httpx>=0.27, beautifulsoup4>=4.12) plus dev dependencies (pytest, ruff) using uv-compatible configuration in `pyproject.toml`
- [ ] T002 Create source package directory structure: `src/sadhguru_mcp_server/__init__.py`
- [ ] T003 Create test directory structure: `tests/__init__.py`, `tests/contract/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`
- [ ] T004 Run `uv sync` to generate `uv.lock` and install all dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core modules (cache, scraper, shared fixtures) that MUST be complete before ANY user story resource can be registered

**Constitution**: Test-First — write tests RED, then implement GREEN for each module.

### Cache Module

- [ ] T005 [P] Write failing unit tests for QuoteCache (`get`, `set`, midnight expiry) in `tests/unit/test_cache.py`
- [ ] T006 Implement QuoteCache dataclass with lazy midnight expiry in `src/sadhguru_mcp_server/cache.py`

### Scraper Module

- [ ] T007 [P] Create shared test fixtures (mock `__NEXT_DATA__` HTML response, mock 404 response) in `tests/conftest.py`
- [ ] T008 [P] Write failing unit tests for `fetch_quote` (parse `__NEXT_DATA__` JSON, extract quote text, build DailyQuote) in `tests/unit/test_scraper.py`
- [ ] T009 Implement `fetch_quote` async function: HTTP GET with httpx, parse `__NEXT_DATA__` via beautifulsoup4, extract `summary[0].value`, return DailyQuote dict in `src/sadhguru_mcp_server/scraper.py`

**Checkpoint**: Cache and scraper modules are independently tested. No MCP resources registered yet.

---

## Phase 3: User Story 1 — Get Today's Quote (Priority: P1) MVP

**Goal**: A client reads `sadhguru://daily-quote/today` and receives today's quote with source attribution.

**Independent Test**: Read `sadhguru://daily-quote/today` and verify response contains non-empty `quote`, `date` matching today, and valid `source_url`.

### Tests for User Story 1

> **Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [US1] Write failing contract tests for `sadhguru://daily-quote/today` resource in `tests/contract/test_daily_quote_resource.py`: response schema has `quote`, `date`, `source_url` fields (all non-empty strings); `date` matches today; `source_url` matches `https://isha.sadhguru.org/en/wisdom/quotes/date/{date}`; second read returns identical content (idempotency/caching)

### Implementation for User Story 1

- [ ] T011 [US1] Create FastMCP server instance and register `sadhguru://daily-quote/today` fixed resource (resolves today's date, checks cache, calls scraper on miss, returns JSON via `json.dumps`) in `src/sadhguru_mcp_server/server.py`
- [ ] T012 [US1] Create entry point that runs the MCP server in `src/sadhguru_mcp_server/__main__.py`
- [ ] T013 [US1] Verify contract tests pass (GREEN) — run `uv run pytest tests/contract/test_daily_quote_resource.py`

**Checkpoint**: `sadhguru://daily-quote/today` is fully functional. MVP deliverable.

---

## Phase 4: User Story 2 — Get Quote by Date (Priority: P2)

**Goal**: A client reads `sadhguru://daily-quote/2026-02-22` and receives that day's quote with source attribution.

**Independent Test**: Read `sadhguru://daily-quote/2026-02-22` and verify the returned quote matches the source page content.

### Tests for User Story 2

> **Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [US2] Write failing contract tests for `sadhguru://daily-quote/{date}` resource template in `tests/contract/test_daily_quote_resource.py`: response schema for a specific date; `date` field matches requested date; `source_url` is correct; cached response matches first response

### Implementation for User Story 2

- [ ] T015 [US2] Implement date validation and ISO-to-source conversion function (validate ISO 8601 `yyyy-mm-dd` via `datetime.date.fromisoformat()`, convert to source format `month-day-year` e.g. `2026-02-22` → `february-22-2026`) in `src/sadhguru_mcp_server/scraper.py`
- [ ] T016 [US2] Register `sadhguru://daily-quote/{date}` resource template (accepts ISO 8601 date, validates, converts to source format, checks cache, calls scraper on miss, returns JSON with ISO date) in `src/sadhguru_mcp_server/server.py`
- [ ] T017 [US2] Verify contract tests pass (GREEN) — run `uv run pytest tests/contract/test_daily_quote_resource.py`

**Checkpoint**: Both `today` and `{date}` resources are functional. Clients can fetch any valid date.

---

## Phase 5: User Story 3 — Graceful Error on Unavailable Date (Priority: P3)

**Goal**: Invalid or unavailable date requests return descriptive errors instead of crashing or returning empty content.

**Independent Test**: Read `sadhguru://daily-quote/not-a-date` and `sadhguru://daily-quote/2030-01-01` and verify descriptive error messages are returned.

### Tests for User Story 3

> **Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US3] Write failing tests for invalid date format error (e.g., `not-a-date`, `22-02-2026`) — must return error mentioning expected ISO 8601 format — in `tests/contract/test_daily_quote_resource.py`
- [ ] T019 [P] [US3] Write failing tests for unavailable date error (e.g., `2030-01-01`) — must return error indicating no quote available — in `tests/contract/test_daily_quote_resource.py`
- [ ] T020 [P] [US3] Write failing tests for upstream errors (network timeout, connection refused) — must return error indicating upstream unavailable — in `tests/unit/test_scraper.py`

### Implementation for User Story 3

- [ ] T021 [US3] Implement error handling for invalid date format: raise descriptive error with expected ISO 8601 format hint in `src/sadhguru_mcp_server/scraper.py`
- [ ] T022 [US3] Implement error handling for HTTP 404 (no quote for date) and missing quote in parsed HTML in `src/sadhguru_mcp_server/scraper.py`
- [ ] T023 [US3] Implement error handling for upstream network errors (httpx.ConnectError, httpx.TimeoutException) in `src/sadhguru_mcp_server/scraper.py`
- [ ] T024 [US3] Verify all error-path tests pass (GREEN) — run `uv run pytest tests/contract/ tests/unit/`

**Checkpoint**: All three user stories are complete. Every error path returns a descriptive message.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all stories

- [ ] T025 [P] Run full test suite and verify all tests pass — `uv run pytest`
- [ ] T026 [P] Run linter and formatter — `uv run ruff check . && uv run ruff format --check .`
- [ ] T027 Validate quickstart.md by following setup instructions on a clean environment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP target
- **US2 (Phase 4)**: Depends on Foundational — can start after or in parallel with US1
- **US3 (Phase 5)**: Depends on US1 and US2 (error handling wraps existing resources)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational only. No cross-story dependencies.
- **US2 (P2)**: Depends on Foundational only. Shares `server.py` with US1 but adds new resource registration — no conflict. Can run in parallel with US1 if different developers.
- **US3 (P3)**: Depends on US1 and US2. Adds error handling to existing scraper and server code.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (constitution III)
- Implementation makes tests GREEN
- Verify checkpoint before moving to next story

### Parallel Opportunities

- T005 (cache tests) and T007/T008 (conftest + scraper tests) can run in parallel
- T018, T019, T020 (US3 error tests) can all run in parallel
- T025 and T026 (test suite + linting) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch cache and scraper test writing in parallel:
Task: "Write failing unit tests for QuoteCache in tests/unit/test_cache.py"
Task: "Create shared test fixtures in tests/conftest.py"
Task: "Write failing unit tests for fetch_quote in tests/unit/test_scraper.py"

# Then implement sequentially (or in parallel since different files):
Task: "Implement QuoteCache in src/sadhguru_mcp_server/cache.py"
Task: "Implement fetch_quote in src/sadhguru_mcp_server/scraper.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (cache + scraper with tests)
3. Complete Phase 3: User Story 1 (`today` resource)
4. **STOP and VALIDATE**: Test US1 independently
5. Ship MVP — clients can get today's quote

### Incremental Delivery

1. Setup + Foundational → Core modules tested
2. Add US1 → `today` resource works → MVP
3. Add US2 → `{date}` template works → Historical access
4. Add US3 → Error handling → Production-ready
5. Polish → Linting, full validation → Release

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Constitution III (Test-First) is enforced: every implementation task has a preceding test task
- Each user story is independently completable and testable at its checkpoint
- Commit after each task or logical group
- All file paths are relative to repository root
