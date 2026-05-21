# Implementation Plan: Smarter Engine

**Branch**: `003-smarter-engine` | **Date**: 2026-05-21 | **Spec**: `specs/003-smarter-engine/spec.md`

**Input**: Feature specification from `specs/003-smarter-engine/spec.md`

**Note**: This file is the `/speckit-plan` output and is paired with generated tasks in `tasks.md`.

## Summary

Deepen the existing local vocabulary engine with cross-session weak-tag signals, deterministic weak-aware queue selection, learner-visible selection reasons, and documented review-intensity behavior. The implementation keeps SM-2 unchanged, derives signals from recent analyzed local sessions, keeps explicit tag filters as hard boundaries, and extends the existing Python core/DAL/contracts/renderers plus `tutor vocab` and boot-context surfaces without adding host-specific behavior or new scheduling algorithms.

## Technical Context

**Language/Version**: Python 3.12+ with the existing synchronous core.

**Primary Dependencies**: Existing runtime dependencies only: Click for `bin/tutor`, Pydantic v2 for contracts and schema export, ruamel.yaml for preferences/profile, platformdirs for local paths, and stdlib `sqlite3`/`json`/`datetime` for local state and deterministic ordering. Dev tooling remains pytest, syrupy, freezegun, pytest-cov, pyright, ruff, hatchling, uv, and pre-commit.

**Storage**: SQLite remains the canonical transactional/derived store for answer events, mistake events, vocabulary reviews, vocabulary cards, session summaries, and any derived selection inputs. YAML remains human-editable profile/preferences only; review intensity stays in preferences. No cloud, remote, or host-owned storage.

**Testing**: pytest for unit, contract, integration, and migration tests; syrupy for deterministic boot-context and queue-rendering snapshots; freezegun for queue-time, due-date, and SM-2 invariance fixtures; pyright and ruff for type/lint gates.

**Target Platform**: macOS and Linux local Claude Code plugin runtime. Host-independent CLI behavior only; no new host adapter work.

**Project Type**: Local Python package plus Claude Code plugin surface. This feature changes Python core/DAL/renderers/contracts and existing skill/CLI surfaces.

**Performance Goals**: Weak-tag extraction considers at most the last 10 completed analyzed sessions; queue selection remains deterministic and suitable for low-thousands local vocabulary cards; boot-context weak-tag summary stays within the existing 6000 rendered-character budget; review history and selection output should remain below 2 seconds for local fixtures around 500 attempts/cards. The 2-second target is a manual implementation-sizing review item, not an automated Phase 3 verification gate.

**Constraints**: SM-2 math must remain byte-for-behavior unchanged for identical prior state, verdict, and timestamp. Queue size is light 50%, normal 100%, heavy 150% of configured session length, capped at 60 cards. Weak summary is top 5 active weak tags. Explicit tag filters are hard boundaries. No FSRS, alternate schedulers, dashboards, host adapters, audio, cloud sync, gamification, bundled curricula, ORM, async storage, or speculative APIs.

**Scale/Scope**: Single local learner, last 10 completed analyzed sessions, top 5 active weak tags, local vocabulary decks in the low-thousands, one queue request at a time, and machine-readable selection reasons for selected cards only.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Layered boundaries**: PASS. Affected layers are vocabulary core selection, weak-tag signal aggregation, boot-context rendering, preference validation, Pydantic schemas, JSON schema mirrors, SQLite repository reads, `tutor vocab` CLI JSON, `tutor-progress`/boot weak-tag signal surfaces, and tests. Host adapters remain out of scope. Cross-layer calls stay CLI -> core -> repository and core -> renderer.
- **Contracts and abstractions**: PASS. New data crosses boundaries through Pydantic models, JSON schema mirrors, documented CLI JSON, and narrow repository methods. Weak-tag signal and selection contracts are explicit; no catch-all dictionaries or concrete DAL internals leak into skills or renderers.
- **Deterministic tests**: PASS. Required coverage includes unit tests for weak-tag extraction/ranking, queue sizing, due/new bucket ordering, weak-slot reservation, explicit filter boundaries, and SM-2 invariance; golden tests for queue explanations and boot weak-tag summaries; contract tests for CLI JSON and preferences; integration tests for cross-session targeting and recovery with invalid/missing analysis; migration tests only if stored schema changes.
- **Local-first data ownership**: PASS. SQLite owns events, reviews, session summaries, and derived selection inputs. YAML owns human-editable review intensity. No cloud, telemetry, remote state, or host-owned learner data.
- **Scope discipline**: PASS. Work is limited to roadmap Phase 3 smarter engine. FSRS, scheduler replacement, dashboards, exports, host adapters, writing-feedback changes, new modalities, cloud sync, and multi-user behavior are excluded.
- **DRY and composition**: PASS. Tag normalization, review-intensity queue sizing, weak-tag signal ranking, due/new bucket ordering, and selection-reason vocabulary are planned as single-source helpers composed by the CLI/core/repository boundary. No inheritance hierarchy, service locator, or global mutable state is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/003-smarter-engine/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli-json.md
│   ├── preferences.md
│   └── weak-tag-summary.md
└── tasks.md              # Generated by /speckit-tasks
```

### Source Code (repository root)

```text
skills/
└── tutor-vocab/
    ├── SKILL.md
    └── scripts/
        └── run.py

src/language_tutor/
├── boot_context.py
├── cli.py
├── progress.py
├── schemas.py
├── srs.py
├── vocab.py
└── dal/
    └── repositories.py

migrations/
├── 001_initial.sql
└── 002_vocab_depth.sql

schemas/
├── boot_context.schema.json
├── session_analysis.schema.json
├── vocabulary_session_plan.schema.json
├── weak_tag_signal.schema.json              # planned if exported as a standalone schema
└── selection_reason.schema.json             # planned if exported as a standalone schema

tests/
├── adapter_contract/
│   ├── test_cli_json_contract.py
│   └── test_vocab_cli.py
├── golden/
│   └── test_boot_context.py
├── integration/
│   └── test_vocabulary_flow.py
├── migration/
│   └── test_migrations.py
└── unit/
    ├── test_repositories.py
    ├── test_schemas.py
    ├── test_srs.py
    └── test_vocab_selection.py
```

**Structure Decision**: Extend the existing single Python package and `tutor vocab` CLI group. Keep weak-tag signal derivation and queue ranking in core (`vocab.py` or a small core helper) with repository methods returning immediate local state only. A new package, new scheduler module family, new host adapter, persisted weak-tag cache, or selection-history table is rejected because Phase 3 can derive signals from existing local SQLite state and expose decisions through validated command output.

## Phase 0: Research

**Output**: `specs/003-smarter-engine/research.md`

All technical-context unknowns are resolved:

- Weak-tag source: derive active weak-tag signals from the 10 most recent valid completed analyzed sessions in `session_summaries`, joining their `session_id` to `mistake_events` and `vocabulary_reviews`; ignore missing, invalid, incomplete, or interrupted analyses before applying the 10-session limit.
- Weak-tag contribution: a session contributes a tag once when it has a tagged mistake event or a vocabulary review with `quality < 3` whose reviewed card has that normalized tag.
- Weak-tag ranking: sort by session frequency descending, most recent occurrence descending, then normalized tag ascending.
- Queue selection: repository returns eligible vocabulary candidates and recent weak-tag signals; core partitions candidates into overdue due, due-today, and new buckets; core applies weak priority only where allowed by the spec; remaining due-card ties resolve by due timestamp, stored creation timestamp, normalized prompt text, then item ID, while new-card ties with no due timestamp start at stored creation timestamp.
- Overdue definition: because SM-2 stores day-scale intervals with timestamps, overdue means `due_at` is before the current UTC calendar day; due-today means `due_at <= now` on the current UTC date.
- Weak-slot cap: when selecting at least two due cards and non-weak due cards exist, reserve one due slot for the highest-ranked non-weak due card.
- New-card fill: only fill from new cards after due cards cannot fill the effective queue size; weak-tagged new cards rank first inside the new-card bucket.
- Review intensity: keep existing `ReviewIntensity` values and queue-size concept, calculate effective queue size as `min(60, max(1, round(session_length * multiplier)))`, and document learner-facing meanings; invalid values continue through existing validation/repair behavior.
- SM-2: keep `schedule_review` unchanged and prove invariance with fixtures that vary intensity outside the scheduler call.

## Phase 1: Design And Contracts

**Output**:

- `specs/003-smarter-engine/data-model.md`
- `specs/003-smarter-engine/contracts/cli-json.md`
- `specs/003-smarter-engine/contracts/preferences.md`
- `specs/003-smarter-engine/contracts/weak-tag-summary.md`
- `specs/003-smarter-engine/quickstart.md`
- `AGENTS.md` Speckit plan reference

Design decisions:

- `WeakTagSignal` is a derived Pydantic contract, not a stored table. It contains tag, contributing session count, latest occurrence, priority rank, and safe source counts.
- `VocabularySessionPlan` remains the CLI response for `tutor vocab start` and gains effective queue size, active weak tags, selection policy metadata, and per-selected-card `SelectionReason` entries.
- `SelectionReason` is learner-safe and machine-readable. It reports broad reasons such as overdue, due, weak-tag match, explicit filter match, reserved non-weak due, and new-card fill; it never includes raw learner answers or full feedback prose.
- `VocabularyDrillRequest.tags` remains an inclusive hard filter. Weak targeting ranks only cards already inside the explicit filter.
- `ReviewIntensity` stays in `LearnerPreferences`; missing intensity defaults to `normal`, unsupported values fail validation and surface through existing setup/repair flows.
- Boot context and progress reuse the same weak-tag signal helper so weak-tag summaries are single-source and bounded to the top 5 active weak-tag signals.
- No SQLite migration is planned. Existing tables contain the needed state: `session_summaries`, `mistake_events`, `vocabulary_reviews`, and `vocabulary_items`. Add a migration only if implementation later requires persisted selection data, which is not planned.

## Post-Design Constitution Check

- **Layered boundaries**: PASS. Design keeps host adapters untouched and separates CLI parsing, core selection, repository reads, schema contracts, and rendering.
- **Contracts and abstractions**: PASS. Data model and contract docs define Pydantic/JSON surfaces before tasks. Repository additions are narrow candidate/signal reads and do not own pedagogy.
- **Deterministic tests**: PASS. Quickstart and contracts identify unit, golden, contract, integration, migration, and SM-2 invariance gates.
- **Local-first data ownership**: PASS. Weak-tag signals are derived from local SQLite; preferences remain YAML; no remote or host-owned state is introduced.
- **Scope discipline**: PASS. Design excludes FSRS, alternate schedulers, dashboards, exports, new hosts, new modalities, and unrelated writing-feedback changes.
- **DRY and composition**: PASS. Shared weak-tag signal, tag-normalization, queue-size, selection-ranking, and explanation helpers prevent duplicated rules and remain injected/composed collaborators.

## Verification Gates

```bash
rtk pytest tests/unit/test_vocab_selection.py tests/unit/test_schemas.py tests/unit/test_repositories.py tests/unit/test_srs.py
rtk pytest tests/golden/test_boot_context.py tests/golden/test_vocab_feedback.py
rtk pytest tests/adapter_contract/test_vocab_cli.py tests/adapter_contract/test_cli_json_contract.py
rtk pytest tests/integration/test_vocabulary_flow.py
rtk pytest tests/migration/test_migrations.py
rtk pyright
rtk ruff check .
```

The `test_srs.py` gate MUST include the invariant that identical previous card state, answer outcome, and review timestamp produce identical SM-2 outputs for light, normal, and heavy intensity. The adapter-contract and integration gates MUST keep existing unfiltered and tag-filtered vocabulary start regressions in scope.

## Complexity Tracking

No constitution violations. No complexity exceptions required.
