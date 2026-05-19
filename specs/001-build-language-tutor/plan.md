# Implementation Plan: language-tutor v1

**Branch**: `001-build-language-tutor` | **Date**: 2026-05-20 | **Spec**: `specs/001-build-language-tutor/spec.md`

**Input**: Feature specification from `specs/001-build-language-tutor/spec.md`

**Note**: This plan is filled by `/speckit-plan`. Implementation tasks are generated later by `/speckit-tasks`.

## Summary

Build a local-first Claude Code language-tutor plugin with a synchronous Python 3.12+ core. Claude plugin hooks and user-facing skills shell out to one `bin/tutor` Click CLI; the core owns pedagogy, schemas, SM-2 scheduling, lifecycle, boot context, evaluator validation, and rendering; the DAL owns human-editable YAML profile/preferences and transactional SQLite learner history. v1 ships setup, vocabulary, writing, progress, boot context, session summary, health checks, and distribution scaffolding for macOS and Linux only.

## Technical Context

**Language/Version**: Python 3.12 minimum, target-compatible with Python 3.13. Runtime remains synchronous.

**Primary Dependencies**: Pydantic v2 for contracts and JSON Schema export; `ruamel.yaml` for comment-preserving profile/preferences edits; stdlib `sqlite3`; Click for `bin/tutor`; platformdirs for macOS/Linux paths. Dev dependencies: pytest, syrupy, freezegun, pytest-cov, pyright strict, ruff, hatchling, uv.

**Storage**: Human-editable YAML for profile/preferences only; SQLite for transactional and derived state: lifecycle events, answer events, mistake events, SRS items/reviews, session summaries, skill metrics, migrations, and costs.

**Testing**: pytest unit tests for schemas, SM-2, severity mapping, boot-context selection, YAML validation, and migrations; syrupy golden tests for boot context and markdown rendering; adapter contract tests for Claude hook/CLI JSON; integration tests for setup, vocabulary, writing, progress, lifecycle, and health checks; semantic evaluator fixtures for Slavic feedback quality.

**Target Platform**: Claude Code plugin on macOS and Linux. Windows, alternate hosts, cloud services, and multi-device sync are out of scope for v1.

**Project Type**: Agentic-CLI plugin plus local Python package and CLI. No web service, MCP server, daemon, or terminal UI framework in v1.

**Performance Goals**: Fresh health check plus setup plus first usable vocabulary prompt in under 60 seconds; session-start context readable in under 20 seconds and capped by an enforced token/character budget; progress view under 5 seconds with one year of daily history; deterministic render output for identical validated inputs.

**Constraints**: Local-only data; no telemetry, auth, cloud sync, remote storage, ORM, async core, FSRS, bundled curriculum, games, dashboards, or speculative host adapters. Every state mutation persists immediately through a repository transaction. Shell verification in this repository uses `rtk`.

**Scale/Scope**: Single learner, daily local use, one Claude Code host adapter, four user-facing skills (`tutor-setup`, `tutor-vocab`, `tutor-writing`, `tutor-progress`), one judge subagent for writing evaluation, one install/health command, and one local SQLite database.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate

- **Layered boundaries**: PASS. Affected layers are host adapter, core, DAL, renderer, user-facing skills, hooks, packaging, and tests. Hooks/skills call CLI only; CLI calls core; core calls repositories; DAL calls filesystem.
- **Contracts and abstractions**: PASS. Inter-layer data crosses via Pydantic models, generated JSON schemas, narrow Protocols, SQL migrations, and documented CLI JSON. No catch-all dictionaries are allowed at persistence or renderer boundaries.
- **Deterministic tests**: PASS. Required coverage includes unit, golden, contract, integration, migration, and semantic evaluator fixtures.
- **Local-first data ownership**: PASS. YAML owns editable config only; SQLite owns transactional/derived state only; platformdirs resolves paths.
- **Scope discipline**: PASS. Plan limits v1 to Claude Code, Python core, YAML/SQLite, vocab SRS, writing, feedback rendering, progress, session lifecycle, install checks, and packaging.
- **DRY and composition**: PASS. Schemas, error tags, severity mapping, path rules, and prompt rubrics are single-source. Behavior composes services/repositories/adapters; no inheritance hierarchy is planned.

### Post-Design Gate

- **Layered boundaries**: PASS. `data-model.md` and `contracts/` preserve immediate-neighbor calls. No module reaches through adapter, core, or DAL internals.
- **Contracts and abstractions**: PASS. CLI, plugin surface, evaluator output, lifecycle, and persistence contracts are documented in `contracts/` and backed by Pydantic/SQL schema ownership.
- **Deterministic tests**: PASS. Quickstart and contracts name exact verification tiers; evaluator nondeterminism is isolated to semantic fixtures and schema validation.
- **Local-first data ownership**: PASS. Data model explicitly splits YAML editable fields from SQLite event/state tables and forbids duplicate ownership.
- **Scope discipline**: PASS. Research rejects MCP, alternate hosts, async, ORM, FSRS, cloud, dashboards, and bundled curricula for v1.
- **DRY and composition**: PASS. Shared vocabularies and mappings remain centralized in core modules; skills are orchestration documents only.

## Project Structure

### Documentation (this feature)

```text
specs/001-build-language-tutor/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli-json.md
│   ├── evaluator.md
│   └── plugin-surface.md
└── tasks.md                 # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
.claude-plugin/
└── plugin.json

bin/
└── tutor

hooks/
├── hooks.json
├── session-start.sh
└── session-end.sh

skills/
├── tutor-setup/SKILL.md
├── tutor-vocab/SKILL.md
├── tutor-writing/SKILL.md
└── tutor-progress/SKILL.md

agents/
└── tutor-judge.md

src/
└── language_tutor/
    ├── __init__.py
    ├── cli.py
    ├── schemas.py
    ├── lifecycle.py
    ├── boot_context.py
    ├── srs.py
    ├── feedback.py
    ├── evaluators.py
    ├── session.py
    ├── errors.py
    ├── adapters/
    │   ├── __init__.py
    │   ├── base.py
    │   └── claude.py
    └── dal/
        ├── __init__.py
        ├── paths.py
        ├── yaml_store.py
        ├── sqlite_store.py
        ├── migrations.py
        └── repositories.py

data/
└── defaults/
    ├── profile.yaml
    └── preferences.yaml

migrations/
└── 001_initial.sql

schemas/
├── boot_context.schema.json
├── feedback_envelope.schema.json
├── session_analysis.schema.json
└── answer_event.schema.json

tests/
├── unit/
├── golden/
├── integration/
├── adapter_contract/
└── fixtures/

pyproject.toml
pyrightconfig.json
README.md
```

**Structure Decision**: Use one Python package under `src/language_tutor/` with module boundaries instead of separate core/adapter/DAL packages. v1 has one host and one wheel, so package splitting would add versioning and import complexity without current value. The Claude adapter remains a thin Protocol-backed module because the current host boundary needs contract tests.

## Complexity Tracking

No constitution violations accepted. No added complexity requires justification at this planning stage.
