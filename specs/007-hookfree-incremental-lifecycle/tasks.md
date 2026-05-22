---
description: "Task list for Hook-Free Incremental Lifecycle"
---

# Tasks: Hook-Free Incremental Lifecycle

**Input**: Design documents from `/specs/007-hookfree-incremental-lifecycle/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Constitution-required tests are included (contract, golden, migration,
integration, conformance, packaging-privacy, unit commit-durability) and are
placed BEFORE their implementation tasks. Skill edits are gated behind subagent
pressure-test baselines per the Skill Creation gate (plan.md Constitution Check).

**Organization**: Tasks grouped by user story for independent implementation and
testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1–US4)
- Exact file paths included

## Path Conventions

Single-project layered layout: `src/language_tutor/`, `migrations/`, `schemas/`,
`skills/`, `hooks/`, `tests/` at repository root (per plan.md Structure Decision).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project init required (existing repo). Confirm working tree
and gates green before changing contracts.

- [X] T001 Confirm clean baseline: run `rtk pytest`, `rtk pyright`, `rtk ruff check` and record current green state in specs/007-hookfree-incremental-lifecycle/ (no source change in this task)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema enums, Pydantic contracts, JSON-Schema mirrors, migration,
and repository signatures that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Boundary contracts (schemas.py + JSON-Schema mirrors)

- [X] T002 Add enums `SessionStatus`, `PersistenceMode`, `SessionIdSource`, `CheckpointStepKind`, `SessionLabel` to src/language_tutor/schemas.py per data-model.md (open/closed stored only; stale/abandoned NOT members)
- [X] T003 Add `SafeStepState` bounded Pydantic model to src/language_tutor/schemas.py (fields: prompt_ref, step_index, total_steps, modality_hint, labels≤16; forbid extra; no secret/log/transcript/config-typed fields) per checkpoint.schema.json
- [X] T004 Add `Session` and `Checkpoint` Pydantic models to src/language_tutor/schemas.py with validators (`closed_at` non-null iff status==closed; `started_at <= last_seen_at`; checkpoint summary maxLength 280) per session.schema.json + checkpoint.schema.json
- [X] T005 Add `SessionView` (stored Session + derived `label: SessionLabel`) and extend `BootResult`/`BootContext` with `prior_sessions` block and active `session_id` in src/language_tutor/schemas.py per boot-result.schema.json (keep existing BootContext fields unchanged)
- [X] T006 [P] Add JSON-Schema mirror schemas/session.schema.json (copy from contracts/session.schema.json, fix `$id`)
- [X] T007 [P] Add JSON-Schema mirror schemas/checkpoint.schema.json (copy from contracts/checkpoint.schema.json, fix `$id`)
- [X] T008 [P] Add JSON-Schema mirror schemas/boot_result.schema.json (copy from contracts/boot-result.schema.json, fix `$id`)
- [X] T009 Extend `AdapterCapabilityProfile` in src/language_tutor/schemas.py with `persistence_mode: PersistenceMode` and `session_id_source: SessionIdSource`; add validator rejecting `lifecycle_start=hook` and hook boot triggers for all hosts per capability-profile-lifecycle.md

### Migration + DAL signatures

- [X] T010 Create migrations/004_sessions_checkpoints.sql: `sessions` table (id PK, host, host_conversation_id, status, started_at, last_seen_at, closed_at; index on last_seen_at and status) and `checkpoints` table (id PK, session_id FK, modality, step_kind, prompt_ref, state, summary, created_at; index on session_id and created_at), sequential version 004, idempotent per data-model.md
- [X] T011 Add repository method stubs/signatures to src/language_tutor/dal/repositories.py: `open_session`, `touch_session`, `record_checkpoint`, `recent_sessions`, `close_session` (FR-012) with durable-commit contract (FR-013)

### Foundational tests (write before behavior in user stories)

- [X] T012 [P] Migration round-trip test for 004 (tables/columns/indexes, idempotent re-apply, version sequencing) in tests/migration/test_004_sessions_checkpoints.py
- [X] T013 [P] Contract test asserting Session/Checkpoint/BootResult Pydantic models validate against schemas/*.schema.json mirrors in tests/contract/test_session_checkpoint_schema.py

### Skill change inventory (Skill Creation gate)

- [X] T014 Inventory affected skills (skills/tutor-lesson, tutor-reading, tutor-vocab, tutor-writing, tutor-progress; transcript handled within reading) and assign one subagent per skill family for the session_id-threading + checkpoint-on-presentation edits required by FR-019/FR-005
- [X] T015 Create skill pressure scenarios via the local writing-skills helper (`/Users/artem.veduta/.claude/.../writing-skills`) covering: agent obtains session_id from session-start, threads it into every bin/tutor call, and calls checkpoint on presentation — before editing any SKILL.md

**Checkpoint**: Contracts, migration, repo signatures, and skill baselines ready — user stories can begin.

---

## Phase 3: User Story 1 - Mid-lesson app close keeps my work (Priority: P1) 🎯 MVP

**Goal**: Every presented step writes a durable checkpoint immediately and answer
events persist under the active session id, so a mid-session kill loses nothing.

**Independent Test**: Start session, present a step (checkpoint written), submit
answer (answer/review/mistake written), kill process with no end event, re-open
and confirm prior session + all steps/answers intact.

### Tests for User Story 1 ⚠️ (write first, must FAIL)

- [X] T016 [P] [US1] Contract test for `checkpoint` CLI JSON shape in tests/contract/test_checkpoint_cli.py per quickstart.md step 2 + checkpoint.schema.json
- [X] T017 [P] [US1] Unit test for `open_session`/`touch_session`/`record_checkpoint` repository methods incl. durable-commit (FR-013) in tests/unit/test_session_repository.py
- [X] T018 [P] [US1] Golden test for checkpoint render + boot context including active session_id in tests/golden/test_checkpoint_render.py
- [X] T019 [P] [US1] Integration test: present step → checkpoint, submit answer, simulate mid-session kill, re-open and assert all data through last checkpoint recoverable (SC-002) in tests/integration/test_midsession_kill.py
- [X] T020 [P] [US1] Skill pressure baseline (no skill change) proving current skills do NOT checkpoint on presentation, via assigned subagent, in tests/ notes per T015 scenarios

### Implementation for User Story 1

- [X] T021 [US1] Implement `open_session`, `touch_session`, `record_checkpoint` in src/language_tutor/dal/repositories.py with durable commit (depends on T010, T011)
- [X] T022 [US1] Implement `start_session()` in src/language_tutor/lifecycle.py (mint `sess_...` id, insert open row, touch last_seen) (FR-003, FR-004)
- [X] T023 [US1] Add `session-start` and `checkpoint` subcommands to src/language_tutor/cli.py returning JSON per session-start.cli.md and quickstart.md (checkpoint takes explicit session_id, FR-006/R6)
- [X] T024 [US1] Anchor existing answer/review/mistake record paths to explicit active `session_id` in src/language_tutor/cli.py + repositories.py (reuse existing paths, FR-006)
- [X] T025 [US1] Update skills/tutor-lesson/SKILL.md and skills/tutor-reading/SKILL.md through assigned subagents (obtain session_id from session-start; thread into every bin/tutor call; checkpoint on presentation) using writing-skills helper (FR-005, FR-019)
- [X] T026 [US1] Update skills/tutor-vocab/SKILL.md, skills/tutor-writing/SKILL.md, skills/tutor-progress/SKILL.md through assigned subagents (same threading + checkpoint contract) using writing-skills helper
- [X] T027 [US1] Verify changed skills with subagent pressure scenarios (T015); record changed files, rationalizations closed, remaining gaps

**Checkpoint**: US1 fully functional — per-step persistence survives a kill.

---

## Phase 4: User Story 2 - New conversation reads prior sessions as history (Priority: P1)

**Goal**: A fresh conversation mints a distinct session id, surfaces N most-recent
prior sessions as history with read-time labels, and writes new data only under
the new id without mutating prior ids.

**Independent Test**: Leave a prior session open/stale, start a new conversation,
confirm a different session id, prior read as history (unchanged), new writes only
under new id.

### Tests for User Story 2 ⚠️ (write first, must FAIL)

- [X] T028 [P] [US2] Unit test for `recent_sessions` ordering by last_seen_at + `SessionView` label derivation (open/stale/abandoned/closed; 14-day cutoff) in tests/unit/test_session_labels.py (FR-018)
- [X] T029 [P] [US2] Golden test for boot context prior-session block (N=3, most-recent-first, token-budget trim, deterministic) in tests/golden/test_boot_prior_sessions.py (SC-005)
- [X] T030 [P] [US2] Integration test: prior open session → new conversation mints distinct id, prior id unmutated, new writes only under new id (SC-003) + single-session-id threading invariant (FR-019) in tests/integration/test_new_conversation_history.py

### Implementation for User Story 2

- [X] T031 [US2] Implement `recent_sessions` in src/language_tutor/dal/repositories.py (order by last_seen_at desc, limit N) (FR-008, FR-012)
- [X] T032 [US2] Implement read-time label derivation (`SessionView`) and 14-day abandoned cutoff in src/language_tutor/lifecycle.py (no stored mutation, FR-018)
- [X] T033 [US2] Extend `build_boot_context` in src/language_tutor/boot_context.py to accept/return active session_id and append deterministic, token-budgeted prior-session block (FR-008, FR-016); keep bare `boot-context` output unchanged
- [X] T034 [US2] Wire `session-start` to call recent_sessions + boot context prior block in src/language_tutor/cli.py (depends on T023, T031, T033)

**Checkpoint**: US1 + US2 work — continuity from incremental data, no mutation of prior sessions.

---

## Phase 5: User Story 3 - All hosts behave identically; no hooks required (Priority: P2)

**Goal**: All four host profiles declare the shared no-hook lifecycle and pass
conformance with zero hooks installed; hook lifecycle removed from required surface.

**Independent Test**: Run conformance suite per host profile; confirm shared
lifecycle values and first-message-boot + checkpoint-persistence pass with no hook.

### Tests for User Story 3 ⚠️ (write first, must FAIL)

- [X] T035 [P] [US3] Adapter-contract test asserting all four profiles declare `lifecycle_start=first_message`, `lifecycle_end=not_available`, `boot_context_trigger=first_tutor_message`, `persistence_mode=incremental_checkpoint`, valid `session_id_source` (FR-009) in tests/adapter_contract/test_lifecycle_fields.py
- [X] T036 [P] [US3] Adapter-contract test asserting hook boot triggers rejected for all hosts (FR-010) in tests/adapter_contract/test_no_hook_lifecycle.py
- [X] T037 [P] [US3] Conformance kit test: per host, first-message boot creates session + returns session_id, checkpoint persists, with no hook installed (SC-001) in tests/adapter_contract/test_conformance_no_hook.py
- [X] T038 [P] [US3] Packaging-privacy test: no package requires a hook for correctness; 0 user-owned sessions/checkpoints data shipped (SC-004, FR-014) in tests/packaging/test_no_hook_privacy.py

### Implementation for User Story 3

- [X] T039 [US3] Set shared lifecycle + new fields in src/language_tutor/adapters/claude.py, codex.py, openclaw.py, hermes.py capability profiles (FR-009)
- [X] T040 [US3] Update boot-trigger mapping in src/language_tutor/adapters/base.py / lifecycle.py `select_boot_trigger`: `first_tutor_message → FIRST_MESSAGE`, command `tutor session-start --json`, fallback MANUAL; remove hook trigger branches from target mapping (capability-profile-lifecycle.md)
- [X] T041 [US3] Remove/deprecate hook files: hooks/session-start.sh, hooks/session-end.sh, hooks/hooks.json — mark deprecated legacy-only and exclude from capability/conformance assertions (FR-011, R7)
- [X] T042 [US3] Exclude user-owned `sessions`/`checkpoints` from packaging in SetupPackage excluded patterns (FR-014, SC-004)

**Checkpoint**: All hosts pass conformance with no hooks; hook lifecycle removed from required surface.

---

## Phase 6: User Story 4 - Explicit manual close on demand (Priority: P3)

**Goal**: A learner-invoked close marks the session `closed`, sets `closed_at`,
writes a final summary, cost flush, and next-focus — never automatically.

**Independent Test**: Run close on active session → closed + closed_at + summary;
confirm no normal path triggers close.

### Tests for User Story 4 ⚠️ (write first, must FAIL)

- [X] T043 [P] [US4] Contract test for `session-close` CLI JSON (input/output, idempotent-already-closed error) in tests/contract/test_session_close_cli.py per session-close.cli.md
- [X] T044 [P] [US4] Integration test: close transitions to closed + closed_at + summary/cost flush/next-focus; assert NO boot/checkpoint/record path calls close (FR-007, SC-003) in tests/integration/test_manual_close.py

### Implementation for User Story 4

- [X] T045 [US4] Implement `close_session` in src/language_tutor/dal/repositories.py (set status=closed, closed_at=now, durable commit) (FR-012)
- [X] T046 [US4] Add `session-close` subcommand to src/language_tutor/cli.py reusing existing `record_session_end` path for summary/cost/next-focus (FR-015) per session-close.cli.md

**Checkpoint**: All four stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T047 [P] Migration docs/tests cleanup: update hooks/README.md, README.md host-setup notes, docs/ROADMAP.md Phase 6 lifecycle wording, host-setup profiles, manual-install reports so none assert hook lifecycle as normal (FR-017)
- [X] T048 [P] Constitution compliance review for SOLID/DRY/KISS/YAGNI/SoC/Demeter across changed layers
- [X] T049 [P] Skill-suite coherence audit (trigger overlap, frontmatter, helper/reference evidence, changed-file reports) for the five edited tutor skills
- [X] T050 Run quickstart.md end-to-end validation and full gates: `rtk pytest`, `rtk pyright`, `rtk ruff check` (SC-006)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (P1)**: no deps.
- **Foundational (P2)**: depends on Setup — BLOCKS all user stories.
- **US1 (P3)**: depends on Foundational. MVP.
- **US2 (P4)**: depends on Foundational; reuses US1 repo/CLI (T021–T023). Independently testable.
- **US3 (P5)**: depends on Foundational; conformance exercises US1 boot+checkpoint paths.
- **US4 (P6)**: depends on Foundational; reuses existing session-end path.
- **Polish (P7)**: depends on all desired stories.

### Within Each User Story

- Required tests written and FAILING before implementation.
- Skill pressure baselines (T020) run before SKILL.md edits (T025–T026); verify after (T027).
- Migration (T010) before repository behavior (T021, T031, T045).
- Models/enums (T002–T005) before everything.
- Repo methods before CLI subcommands; CLI before integration.

### Parallel Opportunities

- T006–T008 (JSON-Schema mirrors) parallel.
- T012–T013 (foundational tests) parallel.
- Within each story, all `[P]` test tasks parallel (different files).
- After Foundational, US1/US2/US3/US4 can be staffed in parallel by different developers (shared files T023/T034 and T021/T031 require coordination).

---

## Parallel Example: User Story 1

```bash
# Required tests together:
Task: "Contract test for checkpoint CLI in tests/contract/test_checkpoint_cli.py"
Task: "Unit test for session repository in tests/unit/test_session_repository.py"
Task: "Golden test for checkpoint render in tests/golden/test_checkpoint_render.py"
Task: "Integration test mid-session kill in tests/integration/test_midsession_kill.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 Setup.
2. Phase 2 Foundational (CRITICAL — blocks all stories).
3. Phase 3 US1 → per-step persistence survives kill.
4. STOP and VALIDATE US1 independently (SC-002).

### Incremental Delivery

US1 (MVP) → US2 (history continuity) → US3 (no-hook conformance) → US4 (manual close).
Each story adds value without breaking prior stories.

---

## Notes

- [P] = different files, no deps.
- Verify required tests FAIL before implementing; verify skill pressure baselines FAIL before SKILL.md edits and PASS after.
- All checkpoint/answer/review/mistake writes in one conversation MUST share exactly one `session_id` (FR-019) — asserted by T019/T030.
- `stale`/`abandoned` are read-time labels only — never written (FR-018).
- Commit after each task or logical group.
