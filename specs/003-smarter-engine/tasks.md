# Tasks: Smarter Engine

**Input**: Design documents from `/specs/003-smarter-engine/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required by the feature specification and constitution. Write the listed unit, contract, golden, integration, migration, and SRS invariance tests before implementation tasks in each phase.

**Organization**: Tasks are grouped by independently testable user story. Phase 2 contains shared contracts and repository reads that block all user stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on another incomplete task.
- **[Story]**: Required only for user story phases.
- Every task names exact repository paths.

## Phase 1: Setup (Shared Test Fixtures)

**Purpose**: Add reusable fixture data for deterministic Phase 3 tests.

- [X] T001 Create weak-tag signal session fixture data with repeated tags, one-off tags, invalid summaries, and low-quality reviews in `tests/fixtures/vocabulary/smarter_engine_history.json`
- [X] T002 [P] Create queue-selection card fixture data with overdue, due-today, new, weak-tagged, non-weak, filtered, untagged, multi-tag, no weak-matching vocabulary, and weak-card-not-due cases in `tests/fixtures/vocabulary/smarter_engine_seed.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared contracts, schemas, and DAL reads that every user story depends on.

**Critical**: No user story work can begin until this phase is complete.

### Tests

- [X] T003 Add schema tests for `WeakTagSignal`, `SelectionReason`, `SelectionPolicy`, and extended `VocabularySessionPlan` in `tests/unit/test_schemas.py`
- [X] T004 Add schema export tests for `weak_tag_signal.schema.json`, `selection_reason.schema.json`, and extended `vocabulary_session_plan.schema.json` in `tests/unit/test_schemas.py`
- [X] T005 Add repository tests for recent completed analyzed session ordering and bounded source reads in `tests/unit/test_repositories.py`
- [X] T006 Add repository tests for vocabulary selection candidates, stored ordering fields, and explicit tag filtering boundaries in `tests/unit/test_repositories.py`
- [X] T007 Add migration compatibility coverage for existing vocabulary cards, reviews, mistakes, and summaries without a new Phase 3 migration in `tests/migration/test_migrations.py`

### Implementation

- [X] T008 Define `WeakTagSourceCounts`, `WeakTagSignal`, `SelectionReason`, `SelectionPolicy`, and additive `VocabularySessionPlan` fields in `src/language_tutor/schemas.py`
- [X] T009 Export new schema files and extended vocabulary plan schema from `src/language_tutor/schemas.py`
- [X] T010 Update generated JSON schemas in `schemas/vocabulary_session_plan.schema.json`, `schemas/weak_tag_signal.schema.json`, and `schemas/selection_reason.schema.json`
- [X] T011 Implement narrow repository read methods for recent session summaries, weak-tag source rows, and vocabulary selection candidates in `src/language_tutor/dal/repositories.py`

**Checkpoint**: Contracts, schemas, and repository reads exist; story work can start.

---

## Phase 3: User Story 1 - Target Recurring Weak Tags (Priority: P1) - MVP

**Goal**: Derive active weak tags from recent completed analyzed sessions, expose a safe top-5 summary, and let recurring weak tags bias comparable due cards.

**Independent Test**: Record multiple sessions with repeated weak tags, start a limited vocabulary drill with competing due cards, and confirm weak-tag-matching due cards replace comparable non-matching due cards while boot context shows a compact safe summary.

### Tests for User Story 1

- [X] T012 [US1] Add unit tests for weak-tag contribution, `session_count >= 2`, top-5 ranking, source counts, and deterministic tie-breaks in `tests/unit/test_vocab_selection.py`
- [X] T013 [P] [US1] Add golden boot-context and progress rendering tests for safe weak-tag signal summaries below the 6000-character context budget with 10 analyzed sessions and 25 weak-tag events, without raw answers or full feedback prose, in `tests/golden/test_boot_context.py` and `tests/golden/test_progress_rendering.py`
- [X] T014 [P] [US1] Add adapter contract coverage for `tutor boot-context --json` weak-tag summary fields in `tests/adapter_contract/test_cli_json_contract.py`
- [X] T015 [US1] Add integration coverage for repeated weak tags changing at least one selected due card versus baseline due-date-only order in `tests/integration/test_vocabulary_flow.py`

### Implementation for User Story 1

- [X] T016 [US1] Implement active weak-tag derivation, session-level contribution counting, ranking, and top-5 limiting in `src/language_tutor/vocab.py`
- [X] T017 [US1] Add weak-aware due-today ranking for comparable due cards and matching selection reasons in `src/language_tutor/vocab.py`
- [X] T018 [US1] Replace legacy mistake-count weak-tag rendering with shared weak-tag signals in `src/language_tutor/boot_context.py`
- [X] T019 [US1] Replace progress weak-tag signal aggregation with shared weak-tag signals in `src/language_tutor/progress.py`

**Checkpoint**: User Story 1 is independently testable through weak-tag signal unit tests, boot-context/progress golden tests, and targeted due-card integration tests.

---

## Phase 4: User Story 2 - Adapt Due And New Item Selection (Priority: P1)

**Goal**: Build a deterministic due-first session queue that balances overdue reviews, weak-tag due cards, reserved non-weak due coverage, explicit filters, and weak-tagged new-card fill.

**Independent Test**: Use a fixture containing overdue cards, due-today weak cards, due-today non-weak cards, new weak cards, new unrelated cards, and explicit filters; verify selected IDs, reasons, and order are deterministic.

### Tests for User Story 2

- [X] T020 [US2] Add unit tests for overdue-first ordering, UTC overdue-vs-due-today boundaries, weak priority within due-today cards, reserved non-weak due slot behavior, multi-tag weak matches, and deterministic due timestamp, creation timestamp, prompt, and item-ID tie-breaks in `tests/unit/test_vocab_selection.py`
- [X] T021 [US2] Add unit tests for due-first new-card fill, weak-tagged new-card preference, no matching weak-tag vocabulary cards, all weak-tag cards not due, no new cards when due fills queue, untagged-card fallback, and new-card tie-breaks that start with creation timestamp when due timestamp is absent in `tests/unit/test_vocab_selection.py`
- [X] T022 [US2] Add unit tests proving explicit tag filters are hard boundaries when active weak tags conflict with the requested tags in `tests/unit/test_vocab_selection.py`
- [X] T023 [P] [US2] Add `tutor vocab start --json` contract tests for `effective_count`, `active_weak_tags`, `selection_reasons`, `selection_policy`, and filter invariants in `tests/adapter_contract/test_vocab_cli.py`
- [X] T024 [P] [US2] Add schema contract assertions that every `selection_reasons[*].item_id` appears in `items` and no raw event data is exposed in `tests/adapter_contract/test_cli_json_contract.py`
- [X] T025 [P] [US2] Add golden queue-selection snapshot coverage for selected IDs, selection reasons, selection policy, and deterministic ordering in `tests/golden/test_vocab_feedback.py`
- [X] T026 [US2] Add integration coverage for cross-session weak targeting, explicit filter precedence, missing/invalid/incomplete analysis fallback, and 100 repeated deterministic queue builds in `tests/integration/test_vocabulary_flow.py`

### Implementation for User Story 2

- [X] T027 [US2] Implement `VocabularySelectionCandidate` construction, normalized tags, due/new flags, overdue flags, and explicit filter annotations in `src/language_tutor/vocab.py`
- [X] T028 [US2] Implement due-first queue selection with UTC overdue/due-today bucket boundaries, due-today weak priority, reserved non-weak due slot, and stable tie-breakers in `src/language_tutor/vocab.py`
- [X] T029 [US2] Implement weak-tagged new-card fill only when due cards cannot fill effective queue size, with deterministic new-card tie-breaks for cards that have no due timestamp, in `src/language_tutor/vocab.py`
- [X] T030 [US2] Wire `start_vocab` through candidate reads, active weak-tag signals, effective queue size, selection policy, presentation conversion, and starter seeding in `src/language_tutor/vocab.py`
- [X] T031 [US2] Preserve existing `invalid_vocab_start`, `invalid_vocab_filter`, empty filtered queue, and starter content behavior in `src/language_tutor/cli.py`

**Checkpoint**: User Story 2 is independently testable through queue unit tests, CLI JSON contract tests, and integration flow tests.

---

## Phase 5: User Story 3 - Tune Review Intensity Safely (Priority: P2)

**Goal**: Make light, normal, and heavy review intensity adjust queue pressure while SM-2 scheduling output remains unchanged.

**Independent Test**: Build queues from the same learner state under every intensity and verify effective queue size changes, then answer the same cards with identical outcomes and timestamps to prove SM-2 results are identical.

### Tests for User Story 3

- [X] T032 [US3] Add unit tests for light, normal, heavy, Python `round()` behavior, minimum 1, and 60-card cap queue sizing in `tests/unit/test_vocab_selection.py`
- [X] T033 [P] [US3] Add preference validation tests for missing and unsupported `review_intensity` values in `tests/unit/test_schemas.py` and validation/repair-flow contract coverage for unsupported intensity guidance in `tests/adapter_contract/test_cli_json_contract.py`
- [X] T034 [P] [US3] Add SM-2 invariance tests across light, normal, and heavy intensity using identical previous state, verdict, and frozen review timestamp in `tests/unit/test_srs.py`
- [X] T035 [P] [US3] Add CLI contract coverage for effective count and selection policy intensity in `tests/adapter_contract/test_vocab_cli.py`

### Implementation for User Story 3

- [X] T036 [US3] Cap review-intensity queue sizing at 60 while preserving minimum 1 and current rounding behavior in `src/language_tutor/vocab.py`
- [X] T037 [US3] Populate `requested_count`, `effective_count`, and `selection_policy.intensity` consistently for requested-count and preference-derived queues in `src/language_tutor/vocab.py`
- [X] T038 [US3] Keep `schedule_review` independent from `LearnerPreferences.review_intensity` while preserving existing scheduler API in `src/language_tutor/srs.py`
- [X] T039 [US3] Surface light, normal, and heavy review-intensity meanings in the vocabulary skill guidance in `skills/tutor-vocab/SKILL.md`

**Checkpoint**: User Story 3 is independently testable through intensity unit tests, SM-2 invariance tests, and CLI contract tests.

---

## Phase 6: Polish And Cross-Cutting Concerns

**Purpose**: Documentation, skill surface, verification, and architecture review.

- [X] T040 [P] Update feature documentation for weak targeting, selection reasons, explicit filter boundaries, and intensity behavior in `docs/FEATURES.md`
- [X] T041 [P] Update architecture documentation for core/DAL/schema/renderer boundaries and shared weak-tag signal helper ownership in `docs/ARCHITECTURE.md`
- [X] T042 [P] Update pitfall documentation for SM-2 invariance, explicit filter hard boundaries, and weak-summary privacy limits in `docs/PITFALLS.md`
- [X] T043 [P] Update progress skill guidance for active weak-tag signal summaries in `skills/tutor-progress/SKILL.md`
- [X] T044 Run quickstart verification commands from `specs/003-smarter-engine/quickstart.md`
- [X] T045 Run full static and lint gates for `src/language_tutor` and `tests` with `rtk pyright` and `rtk ruff check .`
- [X] T046 Perform constitution compliance and manual implementation-sizing review for SOLID, DRY, KISS, YAGNI, SoC, composition, Demeter, local-first data ownership, host independence, and the 2-second local fixture target around 500 attempts/cards in `specs/003-smarter-engine/tasks.md`

---

## Dependencies And Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2.
- **Phase 4 US2**: Depends on Phase 2 and may reuse US1 weak-tag signals when implemented sequentially.
- **Phase 5 US3**: Depends on Phase 2 and can run alongside US1 or US2 if file ownership is coordinated.
- **Phase 6 Polish**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: MVP. Starts after foundational contracts/repository reads. No dependency on US2 or US3.
- **US2 (P1)**: Starts after foundational contracts/repository reads. Uses the same weak-tag signal contracts as US1 but remains independently testable with injected active weak-tag signals.
- **US3 (P2)**: Starts after foundational schema contracts. Queue-size behavior can be tested independently of weak-tag signal history.

### Within Each User Story

- Tests must be written and fail before implementation.
- Contract/schema changes before CLI integration.
- Repository reads before core selection that consumes them.
- Core selection before boot context, progress, or CLI output integration.
- Integration tests run after the story implementation.

---

## Parallel Opportunities

- T001 and T002 can run in parallel.
- T003, T005, and T007 can run in parallel because they touch separate test files.
- T008 and T011 should not run in parallel with each other until repository return contracts are agreed.
- US1 T013 and T014 can run in parallel after T008-T011.
- US2 T023, T024, and T025 can run in parallel after T008-T011.
- US3 T033, T034, and T035 can run in parallel after T008-T011.
- Polish documentation tasks T040-T043 can run in parallel after implemented behavior is stable.

---

## Parallel Example: User Story 1

```bash
Task: "Add golden boot-context tests for safe weak summaries without raw answers or full feedback prose in tests/golden/test_boot_context.py"
Task: "Add adapter contract coverage for tutor boot-context --json weak-tag summary fields in tests/adapter_contract/test_cli_json_contract.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add tutor vocab start --json contract tests for effective_count, active_weak_tags, selection_reasons, selection_policy, and filter invariants in tests/adapter_contract/test_vocab_cli.py"
Task: "Add schema contract assertions that every selection_reasons[*].item_id appears in items and no raw event data is exposed in tests/adapter_contract/test_cli_json_contract.py"
Task: "Add golden queue-selection snapshot coverage for selected IDs, reasons, policy, and deterministic ordering in tests/golden/test_vocab_feedback.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add preference validation tests for missing and unsupported review_intensity values in tests/unit/test_schemas.py and validation/repair-flow contract coverage in tests/adapter_contract/test_cli_json_contract.py"
Task: "Add SM-2 invariance tests across light, normal, and heavy intensity using identical previous state, verdict, and frozen review timestamp in tests/unit/test_srs.py"
Task: "Add CLI contract coverage for effective count and selection policy intensity in tests/adapter_contract/test_vocab_cli.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate weak-tag ranking, boot-context summary, and targeted due-card selection.
4. Stop for review before expanding queue-selection behavior.

### Incremental Delivery

1. Deliver US1 for active weak-tag targeting and safe learner-visible summary.
2. Deliver US2 for deterministic full queue selection, explicit filters, and new-card fill.
3. Deliver US3 for review-intensity queue pressure and SM-2 invariance proof.
4. Run Phase 6 verification and documentation updates.

### Verification Gates

```bash
rtk pytest tests/unit/test_vocab_selection.py tests/unit/test_schemas.py tests/unit/test_repositories.py tests/unit/test_srs.py
rtk pytest tests/golden/test_boot_context.py tests/golden/test_vocab_feedback.py
rtk pytest tests/adapter_contract/test_vocab_cli.py tests/adapter_contract/test_cli_json_contract.py
rtk pytest tests/integration/test_vocabulary_flow.py
rtk pytest tests/migration/test_migrations.py
rtk pyright
rtk ruff check .
```

---

## Notes

- Keep SM-2 math byte-for-behavior unchanged for identical prior state, answer outcome, and timestamp.
- Keep explicit tag filters as hard boundaries before weak-target annotation.
- Keep weak summaries learner-safe: no raw answers, full feedback prose, or complete event logs.
- Keep weak targeting derived from local SQLite state; do not add cloud, telemetry, host adapters, FSRS, dashboards, or new scheduler algorithms.
- Keep shared rules single-source in core helpers and narrow repository reads; do not duplicate weak-ranking, tag-normalization, queue-size, or selection-reason vocabulary.

## T046 Compliance Review

- SOLID/SoC: PASS. DAL supplies bounded rows; core owns pedagogy; renderers only format safe summaries.
- DRY/KISS/YAGNI: PASS. Weak-signal ranking, tag normalization, queue sizing, and selection reasons are single-source helpers; no new scheduler, table, service layer, or host adapter.
- Composition/Demeter: PASS. CLI calls core through existing functions; core consumes repository methods and Pydantic contracts only.
- Local-first ownership: PASS. Signals derive from SQLite; preferences remain YAML; no remote state or telemetry.
- Performance sizing: PASS by inspection. Weak signals read at most 10 sessions; queue selection sorts local candidate lists and remains appropriate for the 500-card/attempt fixture target.
