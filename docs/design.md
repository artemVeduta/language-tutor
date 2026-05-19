# Language Tutor AI Core Architecture Design

## 1. System Goals & Requirements

Build a cross-platform AI language tutor system that runs on Claude, Codex, OpenClaw, and Hermess while preserving one consistent learner experience.

### Core Requirements

- **Platform agnostic core:** Teaching logic, spaced repetition, feedback formatting, evaluator orchestration, session lifecycle, and persistence rules live outside the LLM host.
- **Same session lifecycle on every host:** All supported hosts must map to the same canonical session lifecycle. Host-specific lifecycle differences are handled only inside adapters.
- **Context efficiency:** Session startup loads only high-value learner state via `get_boot_context()` to reduce token use and latency.
- **Consistent learner experience:** Feedback layout, severity mapping, correction format, mistake tracking, and review scheduling remain identical across hosts.
- **Hybrid state management:** Human-editable configuration uses YAML. Transactional learner history and analytics use SQLite.
- **Python shared core:** Python powers the shared engine, adapters, and DAL because it integrates well with target hosts and includes `sqlite3`.
- **Host memory optional:** Native host memory may be used only as a projection/cache. YAML and SQLite remain source of truth.

## 2. Architectural Model

The system follows explicit layered architecture.

```txt
platform manifests + hooks
        ↓
host adapters normalize lifecycle
        ↓
shared core engine executes tutoring
        ↓
DAL persists YAML/SQLite
        ↓
skills define user-facing tutor modes
```

### Layer Responsibilities

#### Platform Manifests & Hooks

Defines how each host discovers and starts the tutor.

Examples:

- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.openclaw-plugin/plugin.json`
- `hermess/profile-distributions/*`
- `hooks/*`

Responsibilities:

- Register tutor skills with each host.
- Bind host events to adapter entrypoints.
- Provide platform-specific metadata.
- Avoid business logic.

#### Host Adapters

Adapters translate each host's native lifecycle, IO format, prompt format, and hook model into the canonical tutor lifecycle.

Responsibilities:

- Normalize inbound user/session events.
- Call shared core lifecycle methods.
- Render core output into host-compatible messages.
- Expose lifecycle support checks.
- Fail fast when required lifecycle events cannot be mapped.

Adapters do not:

- Evaluate language answers.
- Update SRS data directly.
- Format feedback semantics.
- Mutate learner state outside core/DAL.

#### Shared Core Engine

The Python core owns teaching behavior.

Responsibilities:

- Build boot context.
- Orchestrate session lifecycle.
- Select due reviews and weak patterns.
- Present exercises.
- Evaluate answers through structured evaluator contracts.
- Produce `FeedbackEnvelope`.
- Run session analyzer.
- Update learner state after session.

#### Data Access Layer

DAL abstracts local persistence.

Responsibilities:

- Read/write YAML profiles and preferences.
- Initialize and migrate SQLite schema.
- Persist answer events, mistake events, SRS reviews, summaries, and metrics.
- Expose repository-style interfaces to core.

#### Skills

Skills define user-facing tutor modes and host-discoverable behavior.

Skills are shared across hosts. Host-specific duplication is forbidden unless platform syntax requires a thin wrapper.

## 3. Repository Structure

Use a Superpowers-style repository: shared skills at root, platform manifests at root, shared hooks, and platform-specific shells only where necessary.

```txt
language-tutor/
  .claude-plugin/
    plugin.json

  .codex-plugin/
    plugin.json

  .openclaw-plugin/
    plugin.json
    config.schema.json

  hermess/
    profile-distributions/
      language-tutor.yaml
    README.md

  hooks/
    hooks.json
    hooks-claude.json
    hooks-codex.json
    hooks-openclaw.json
    run-hook
    session-start
    session-end
    session-compact

  skills/
    tutor-setup/
      SKILL.md
    tutor-progress/
      SKILL.md
    tutor-vocab/
      SKILL.md
    tutor-writing/
      SKILL.md
    tutor-reading/
      SKILL.md
    tutor-listening/
      SKILL.md
    tutor-speaking/
      SKILL.md
    tutor-lesson/
      SKILL.md
    tutor-feedback/
      SKILL.md
    tutor-session-analyzer/
      SKILL.md

  core/
    language_tutor/
      __init__.py
      lifecycle.py
      boot_context.py
      session.py
      feedback.py
      srs.py
      evaluators.py
      schemas.py
      errors.py

  adapters/
    language_tutor_adapters/
      __init__.py
      base.py
      claude.py
      codex.py
      openclaw.py
      hermess.py

  dal/
    language_tutor_dal/
      __init__.py
      sqlite_store.py
      yaml_store.py
      repositories.py
      migrations.py

  data/
    defaults/
      profile.yaml
      preferences.yaml
    migrations/
      001_initial.sql

  schemas/
    boot_context.schema.json
    answer_event.schema.json
    feedback_envelope.schema.json
    session_analysis.schema.json
    lifecycle_event.schema.json

  tests/
    unit/
    integration/
    golden/
    fixtures/
    adapter_contract/

  docs/
    architecture.md
    lifecycle.md
    plugin-installation.md
    state-model.md
    skill-contracts.md

  scripts/
    init-db
    validate-schemas
    validate-adapters
    bump-version

  README.md
  pyproject.toml
```

## 4. Canonical Session Lifecycle

All hosts must support the same tutor lifecycle. Adapter implementation may differ, but core receives identical lifecycle events.

```txt
SessionStart
BootContextRequested
BootContextLoaded
DueReviewsLoaded
WeakPatternsLoaded
ExercisePresented
AnswerReceived
AnswerRecorded
FeedbackRendered
SessionAnalysisRequested
SessionAnalyzed
StatePersisted
SessionEnd
```

### Lifecycle Rules

- `SessionStart` creates temporary run state.
- `BootContextRequested` calls `get_boot_context()`.
- `BootContextLoaded` freezes startup learner context for the session.
- `DueReviewsLoaded` retrieves due SRS items.
- `WeakPatternsLoaded` retrieves targeted historical error patterns.
- `ExercisePresented` emits one active learner task.
- `AnswerReceived` captures raw learner input.
- `AnswerRecorded` persists structured answer event.
- `FeedbackRendered` emits standardized feedback.
- `SessionAnalysisRequested` starts end-of-session analysis.
- `SessionAnalyzed` validates analyzer output.
- `StatePersisted` commits summaries, streaks, metrics, and timestamps.
- `SessionEnd` clears run state and closes SQLite connections.

### Adapter Compliance

Every adapter must implement:

```txt
supports_lifecycle() -> bool
map_host_event_to_lifecycle_event(host_event) -> LifecycleEvent
render_core_message(core_message) -> HostMessage
receive_user_input(host_payload) -> UserInput
emit_event(lifecycle_event) -> AdapterResult
```

A host adapter is invalid if it cannot map required events to the canonical lifecycle.

## 5. Boot Context Contract

`get_boot_context()` must return only high-value context needed for the current session.

### Boot Context Contents

```txt
BootContext
- learner_profile_summary
- active_cefr_target
- current_skill_focus
- hard_preferences
- active_constraints
- top_weak_patterns
- due_srs_summary
- last_session_summary
- recent_progress_snapshot
```

### Boot Context Rules

- Must be deterministic.
- Must have character/token budget.
- Must not load full histories.
- Must prefer summarized metrics over raw logs.
- Must include enough state for first exercise selection.
- Must exclude sensitive or unrelated profile data.

## 6. Feedback Contract

Core returns structured feedback. Renderers convert it into markdown and emojis.

```txt
FeedbackEnvelope
- verdict
- corrected_answer
- error_spans[]
- severity
- explanation
- next_drill_hint
- tags[]
- srs_updates[]
```

### Severity Mapping

```txt
✅ correct
🟡 minor issue
🟠 important issue
🔴 blocking issue
```

### Feedback Rules

- Same answer should produce same structured feedback regardless of host.
- Markdown rendering must be golden-tested.
- Emojis and layout are renderer-level output, not evaluator logic.
- Error tags must be controlled vocabulary, not arbitrary prose.

## 7. Persistence Model

### YAML

Stores human-readable profile/configuration.

```txt
profile.yaml
- learner name
- native language
- target language
- CEFR target
- preferred correction style
- topics/interests
- hard constraints

preferences.yaml
- session length
- review intensity
- feedback verbosity
- transliteration preference
- host-specific display preferences
```

### SQLite

Stores transactional state and analytics.

Core tables:

```txt
answer_events
mistake_events
srs_items
srs_reviews
session_summaries
skill_metrics
schema_migrations
```

### Persistence Rules

- Answer/session events should be append-only where possible.
- Derived metrics should be recalculable.
- SRS state updates must be transactional.
- Analyzer output must pass schema validation before persistence.
- SQLite connections close on `SessionEnd`.

## 8. Session Analyzer Contract

`tutor-session-analyzer(summary)` produces structured JSON only.

```txt
SessionAnalysis
- session_id
- severity_counts
- new_error_tags[]
- repeated_error_tags[]
- resolved_error_tags[]
- pattern_drift
- recommended_next_focus
- srs_adjustments[]
- summary_for_next_boot
```

Rules:

- Reject invalid schema.
- Never persist freeform analysis as canonical state.
- Store concise summary for next `get_boot_context()`.
- Preserve raw event history separately.

## 9. Skills

### Required Skills

```txt
tutor-setup
tutor-progress
tutor-vocab
tutor-writing
tutor-reading
tutor-listening
tutor-speaking
tutor-lesson
tutor-feedback
tutor-session-analyzer
```

### Skill Rules

- Skills live once under root `skills/`.
- Each skill has `SKILL.md`.
- Frontmatter `description` defines trigger conditions.
- Skills call core contracts, not host APIs directly.
- Host-specific skill forks require explicit justification.

Example:

```yaml
---
name: tutor-vocab
description: Use when the learner wants vocabulary practice, due SRS reviews, word recall drills, or lexical correction.
---
```

## 10. Roadmap

### Phase 0A: Monorepo, Contracts, Schemas

- Initialize repository structure.
- Add platform manifests.
- Define lifecycle contract.
- Define core schemas.
- Add adapter compliance contract.
- Add README with architecture overview.

### Phase 0B: Reference Host Adapter

- Implement one reference adapter.
- Add minimal hook bindings.
- Validate full lifecycle from startup to session end.
- Keep tutoring behavior minimal.

### Phase 0C: Adapter Test Harness

- Build adapter contract tests.
- Add lifecycle event fixtures.
- Add validation script for supported hosts.
- Ensure each host maps to same lifecycle.

### Phase 1: Foundations & DAL

- Implement YAML loaders.
- Implement SQLite migrations.
- Implement repositories.
- Add transactional persistence.
- Add fixtures and migration tests.

### Phase 2: Onboarding & Profile

- Build `tutor-setup`.
- Support interactive `/fluent-setup` flow.
- Write initial profile/preferences YAML.
- Build `tutor-progress` analytics view.

### Phase 3: Core Mechanics & Vocabulary

- Build `tutor-vocab`.
- Implement SRS math.
- Implement `FeedbackEnvelope`.
- Implement standardized markdown rendering.
- Implement `tutor-session-analyzer`.
- Implement session-end persistence hooks.

### Phase 4: Production Skills

- Build `tutor-writing`.
- Build `tutor-reading`.
- Build `tutor-listening`.
- Build `tutor-speaking`.
- Add modality capability checks for hosts with limited IO support.

### Phase 5: Compound Sessions

- Build `tutor-lesson`.
- Sequence vocab, reading, writing, listening, and speaking.
- Add adaptive routing from weak patterns.
- Add lesson summaries and next-session recommendations.

## 11. Testing Strategy

### Unit Tests

- SRS math.
- Boot context selection.
- Feedback envelope generation.
- YAML parsing.
- SQLite repositories.
- Session analyzer validation.

### Integration Tests

- Full lifecycle through reference adapter.
- Session start to session end.
- Answer recording and feedback rendering.
- SRS update transaction.
- Analyzer output persistence.

### Golden Tests

- Feedback markdown output.
- Severity rendering.
- Skill prompt structure.
- Boot context format.

### Adapter Contract Tests

Each adapter must prove:

```txt
- all canonical lifecycle events supported
- host input maps to UserInput
- core output maps to host message
- session end closes resources
- adapter rejects unsupported host state cleanly
```

## 12. MVP Scope

Initial MVP should include:

- Repository structure.
- One reference adapter.
- Lifecycle contract.
- YAML profile/preferences.
- SQLite migrations.
- `get_boot_context()`.
- `tutor-vocab`.
- `tutor-writing`.
- `FeedbackEnvelope`.
- Session analyzer.
- Golden feedback tests.

Defer:

- Full speaking/audio.
- Rich analytics dashboards.
- Multi-user sync.
- Cloud persistence.
- Cross-device state sharing.
- Complex lesson planner.

## 13. Design Principle

```txt
Adapters translate.
Core decides.
DAL persists.
Renderers display.
Skills expose tutor modes.
```

No host-specific layer may own pedagogy, SRS rules, correction semantics, or canonical learner state.
