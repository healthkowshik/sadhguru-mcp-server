<!--
  Sync Impact Report
  ===================
  Version change: 1.0.0 → 1.0.1
  Modified principles: none
  Added sections: none
  Removed sections: none
  Changed:
    - Technology Stack: Package Management changed from
      "uv (preferred) or pip" to "uv (Astral)" as sole tool.
      Added "uv run pytest" convention. Clarified Astral-only
      toolchain (uv + ruff).
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no update needed
    - .specify/templates/spec-template.md ✅ no update needed
    - .specify/templates/tasks-template.md ✅ no update needed
    - .claude/commands/*.md ✅ no update needed
  Follow-up TODOs: none
-->

# Sadhguru MCP Server Constitution

## Core Principles

### I. Content Fidelity

Sadhguru's words MUST be presented accurately. No paraphrasing,
no fabrication, no attribution of unsourced content.

- All quotes MUST be traceable to a verifiable source (video,
  book, article, or official Isha Foundation publication).
- The system MUST NOT generate, interpolate, or rephrase
  Sadhguru's teachings. It serves existing content only.
- When a source cannot be verified, the system MUST clearly
  indicate the content is unverified rather than present it
  as authoritative.

**Rationale**: Misrepresenting a spiritual teacher's words causes
real harm. Accuracy is the foundational value of this project.

### II. MCP-First Design

Every feature MUST be exposed as an MCP tool or resource.
Standard MCP protocol compliance is non-negotiable.

- All functionality MUST be accessible through the MCP protocol;
  no side-channel APIs or direct database access for consumers.
- Tool and resource schemas MUST follow MCP specification
  conventions (typed parameters, structured responses).
- The server MUST work with any MCP-compatible client without
  client-specific workarounds.

**Rationale**: The project exists to serve AI assistants via MCP.
Protocol compliance ensures interoperability and composability.

### III. Test-First (NON-NEGOTIABLE)

TDD is mandatory: tests MUST be written and failing before
implementation. Red-Green-Refactor cycle strictly enforced.

- No production code MUST be written without a corresponding
  failing test first.
- Tests MUST cover MCP tool inputs/outputs (contract tests),
  content retrieval accuracy, and error paths.
- Test names MUST describe the behavior being verified, not
  the implementation detail.

**Rationale**: An MCP server handling spiritual content has zero
tolerance for silent regressions. Tests are the safety net.

### IV. Simplicity (YAGNI)

Start simple. Avoid premature abstractions. Only build what is
immediately needed.

- No feature MUST be added speculatively; every addition MUST
  address a concrete, current requirement.
- Prefer flat structures over deep hierarchies. Prefer functions
  over classes when state is not needed.
- Configuration MUST have sensible defaults; optional complexity
  MUST NOT burden the common path.

**Rationale**: Complexity is the primary risk for a small project.
Every abstraction incurs maintenance cost that must be justified.

## Technology Stack

- **Language**: Python 3.11+
- **MCP Framework**: FastMCP 3.0
- **Testing**: pytest (via `uv run pytest`)
- **Linting/Formatting**: ruff (Astral)
- **Package Management**: uv (Astral)

The project MUST use Astral tooling exclusively: uv for package
management and task running, ruff for linting and formatting.
pip, setuptools, and other legacy tools MUST NOT be used.

All dependencies MUST be pinned in `uv.lock`. New dependencies
MUST be justified against the Simplicity principle before adoption.

## Development Workflow

- Feature work MUST follow the speckit workflow: specify, plan,
  tasks, implement.
- Every MCP tool/resource MUST have contract tests validating
  its schema and behavior before implementation begins.
- Commits MUST be atomic and correspond to a single logical
  change.
- Content data (quotes, sources) MUST be stored separately from
  application logic to enable independent updates.

## Governance

This constitution is the authoritative source for project
decisions. It supersedes all other practices when conflicts arise.

- **Amendments**: Any change to this constitution MUST be
  documented with rationale, versioned, and reflected in a
  Sync Impact Report at the top of this file.
- **Versioning**: MAJOR for principle removals or redefinitions,
  MINOR for new principles or material expansions, PATCH for
  clarifications and wording fixes.
- **Compliance**: All feature specs, plans, and task lists MUST
  pass a constitution check before implementation begins.
  The `/speckit.analyze` command flags violations as CRITICAL.

**Version**: 1.0.1 | **Ratified**: 2026-02-24 | **Last Amended**: 2026-02-24
