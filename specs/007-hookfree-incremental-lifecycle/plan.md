# Implementation Plan: Hook-Free Incremental Lifecycle

**Branch**: `007-hookfree-incremental-lifecycle` | **Date**: 2026-05-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-hookfree-incremental-lifecycle/spec.md`

## Summary

Replace hook-driven session lifecycle with one shared no-hook model across all
four hosts (claude, codex, openclaw, hermes). The first tutor-skill invocation
of a conversation calls `session-start`; the CLI mints and owns a tutor
`session_id`, persists an `open` session row, and returns it alongside existing
boot context. The agent threads that `session_id` into every subsequent
`bin/tutor` call. Each lesson/exercise/prompt presentation writes a durable
checkpoint immediately; answer/review/mistake events keep their existing
per-answer persistence, now anchored to the active session id. No automatic
session end exists — `closed` is set only by an explicit manual close. `stale`/
`abandoned` are read-time labels derived over `open` rows, never stored. Boot
surfaces the N most-recent prior sessions (default N=3) by `last_seen_at` as
history within the existing token budget. Hook files and hook lifecycle
assertions are removed/deprecated and excluded from capability and conformance
checks.

## Technical Context

**Language/Version**: Python 3.12+ (synchronous core)

**Primary Dependencies**: Pydantic v2 (contracts), stdlib `sqlite3` (storage),
ruamel.yaml (config round-trip), pytest/pyright/ruff (gates)

**Storage**: SQLite (transactional/derived state) — new `sessions` +
`checkpoints` tables plus existing answer/review/mistake/summary/cost ledger.
YAML stays human-editable config only; no new YAML.

**Testing**: pytest (unit/golden/contract/integration/migration/conformance/
packaging-privacy), pyright, ruff

**Target Platform**: Local CLI on macOS/Linux; platform/XDG paths

**Project Type**: Single project — layered CLI tutor (host adapters → core → DAL
→ renderers, plus skills/packaging)

**Performance Goals**: Deterministic, token-budgeted boot context; per-step
persistence adds at most one bounded INSERT/UPSERT per presented step

**Constraints**: No hooks for normal lifecycle; no automatic session end; no
mutation of prior session ids; durable commit on every write path; checkpoints
exclude raw secrets/full logs/transcripts/local config; boot stays backward
compatible

**Scale/Scope**: 4 hosts; 6 modalities (lesson/reading/transcript/vocab/writing/
progress); single local learner

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Layered boundaries** — PASS. Touched layers named in spec Constitution
  Alignment: host adapters (capability profiles only), core (boot/lifecycle/
  session orchestration), DAL (session/checkpoint models, repository methods,
  migration 004), CLI (`session-start`, manual close), skills (checkpoint call on
  presentation), packaging/hooks (removal/deprecation, privacy). Cross-layer calls
  remain immediate-neighbor (CLI→core→repo); no renderer pedagogy change.
- **Contracts and abstractions** — PASS. New data crosses boundaries via Pydantic
  models + JSON-Schema mirrors (`Session`, `Checkpoint`, extended boot result with
  `session_id`), documented CLI JSON (`session-start`, manual close), SQL
  migration 004, and capability-profile fields. No catch-all dicts; `state_json`
  is a bounded, validated safe-metadata model, not an open dictionary.
- **Deterministic tests** — PASS. Plan lists unit (repo methods + commit
  durability), golden (boot context with session id + prior-session block,
  checkpoint render), contract (capability profiles, boot result shape,
  session-start/close JSON), integration (host text flows with mid-session kill;
  single-session-id threading), migration (new tables round-trip), conformance
  (first-message boot + checkpoint persistence per host), packaging-privacy.
- **Skill creation gate** — PASS (applies). Existing tutor skills
  (lesson/reading/transcript/vocab/writing/progress) get `SKILL.md` edits to (a)
  obtain `session_id` from `session-start` and (b) call checkpoint on
  presentation and thread the id. Each edit MUST go through a subagent per skill
  family using the local `writing-skills` helper, the spec's external references,
  and documented RED/GREEN/REFACTOR pressure evidence, with main-agent review of
  changed files. No new skills.
- **Local-first data ownership** — PASS. New state is SQLite-only and
  transactional; YAML unchanged. Paths stay platform/XDG. Packaging excludes
  user-owned `sessions`/`checkpoints` data (SetupPackage already requires
  `sessions` in excluded patterns).
- **Scope discipline** — PASS. Implements only Phase 6.5 / Constitution
  Principle IX requirements. No new hosts, modalities, or speculative fields;
  `session_id_source` and `persistence_mode` are added because Principle IX and
  FR-009 require them as current contract surface.
- **DRY and composition** — PASS. Lifecycle values are single-sourced in the
  capability profile + a shared default; checkpoint step-kind/modality reuse
  existing modality vocabulary; session orchestration composed from injected
  repository methods, no inheritance or global state.

**Result: PASS — no Complexity Tracking entries required.**

## Project Structure

### Documentation (this feature)

```text
specs/007-hookfree-incremental-lifecycle/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── session.schema.json
│   ├── checkpoint.schema.json
│   ├── boot-result.schema.json
│   ├── session-start.cli.md
│   ├── session-close.cli.md
│   └── capability-profile-lifecycle.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
src/language_tutor/
├── schemas.py              # + Session, Checkpoint, SafeStepState, SessionStatus,
│                           #   PersistenceMode, SessionIdSource; extend BootResult
├── lifecycle.py            # + start_session(); keep end_session() as manual close
├── boot_context.py         # extend build_boot_context to take/return session_id +
│                           #   prior-session history block
├── cli.py                  # + `session-start`, `session-close`; checkpoint subcmd
├── adapters/
│   ├── base.py             # lifecycle trigger mapping → first_message everywhere
│   ├── claude.py / codex.py / openclaw.py / hermes.py  # capability profile values
│   └── registry.py
└── dal/
    ├── repositories.py     # + open_session, touch_session, record_checkpoint,
    │                       #   recent_sessions, close_session
    └── migrations.py       # (loader unchanged)

migrations/
└── 004_sessions_checkpoints.sql   # new sessions + checkpoints tables

schemas/                    # JSON-Schema mirrors (session, checkpoint, boot result,
                            #   extended host_capability_profile)

skills/ (or plugin skill dirs)  # SKILL.md edits: obtain + thread session_id,
                                #   checkpoint on presentation

hooks/                      # session-start.sh / session-end.sh / hooks.json:
                            #   removed or marked deprecated legacy-only

tests/
├── unit/                   # repo methods, commit durability, stale/abandoned labels
├── golden/                 # boot context w/ session id + prior block; checkpoint render
├── adapter_contract/       # capability profiles, lifecycle contract, conformance kit,
│                           #   boot result shape, session-start/close JSON
├── integration/            # text flows + mid-session kill; single-session-id threading
├── migration/              # 004 round-trip
└── packaging/              # plugin surface (no hook requirement), privacy
```

**Structure Decision**: Single-project layered layout (Option 1). All changes
land in the existing `src/language_tutor` layers, `migrations/`, `schemas/`,
`hooks/`, skill dirs, and `tests/` trees already present in the repo. No new
top-level project.

## Complexity Tracking

> No Constitution Check violations. Section intentionally empty.
