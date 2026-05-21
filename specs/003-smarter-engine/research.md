# Research: Smarter Engine

**Feature**: `003-smarter-engine`

## Decision: Derive Active Weak Tags From Recent Completed Analyzed Sessions

Use the last 10 `session_summaries` rows as the recent completed analyzed session window. Join those `session_id` values to `mistake_events` and `vocabulary_reviews`, and ignore sessions without a valid summary.

**Rationale**: `session_summaries` is only written when session-end analysis is accepted, so it is the existing local marker for completed analyzed sessions. This avoids a new lifecycle table or host-specific signal.

**Alternatives considered**:

- Use all historical events: rejected because old weak tags could dominate current practice.
- Add a weak-tag cache table: rejected because the current feature can derive bounded signals from existing local SQLite state.
- Trust only `SessionAnalysis.repeated_tags`: rejected because the spec requires tagged mistake events and low-quality vocabulary reviews to count.

## Decision: Count One Weak Tag Contribution Per Session

A session contributes a normalized tag once if it has at least one matching mistake event or at least one vocabulary review with `quality < 3` whose reviewed vocabulary card has that normalized tag.

**Rationale**: Session-level counting matches the requirement that a weak tag appear in at least two recent sessions. It prevents one bad session with many repeated events from displacing recurring weak patterns.

**Alternatives considered**:

- Count every event equally: rejected because high-volume single-session mistakes would overfit the next queue.
- Count only writing mistakes: rejected because low-quality vocabulary reviews are required input.
- Count review verdicts without card tags: rejected because untagged cards cannot support weak-tag targeting.

## Decision: Rank Weak Tags By Frequency, Recency, Then Tag

Sort active weak tags by contributing session count descending, latest occurrence descending, then normalized tag ascending. Keep only the top 5 in boot/session context.

**Rationale**: This directly matches the spec and gives deterministic tie-breaking from stored local data.

**Alternatives considered**:

- Weighted severity score: rejected as speculative and not required by Phase 3.
- LLM-generated priority: rejected because selection must be deterministic and host-independent.
- Alphabetical-only priority: rejected because it ignores learner history strength.

## Decision: Keep Pedagogy In Core, Repository As Candidate Provider

Add narrow repository reads for recent session IDs, weak-tag source events, and vocabulary selection candidates. Keep weak-ranking and queue selection in core vocabulary logic.

**Rationale**: The DAL should own SQLite reads, not pedagogy. Core can be unit-tested with in-memory fixtures and can preserve the CLI/repository boundary.

**Alternatives considered**:

- Sort everything in SQL: rejected because it mixes pedagogy with persistence and makes golden fixture reasoning harder.
- Load raw rows into CLI code: rejected because it leaks DAL details and violates layered boundaries.
- Persist a pre-ranked queue: rejected because Phase 3 only needs command output, not selection history.

## Decision: Treat Overdue As Before Current UTC Date

For selection, overdue due cards are cards with `state != "new"` and `due_at.date() < now.date()` in UTC. Due-today cards are cards with `state != "new"`, `due_at <= now`, and `due_at.date() == now.date()`.

**Rationale**: SM-2 intervals are day-scale. If overdue meant any timestamp before `now`, almost every due card would be overdue by seconds or hours and weak priority would rarely apply.

**Alternatives considered**:

- `due_at < now` as overdue: rejected because it collapses due-today into overdue and conflicts with weak-priority acceptance cases.
- Store date-only due values: rejected because it would require a migration and alter existing review state shape.
- Ignore overdue distinction: rejected because the spec requires overdue cards to outrank weak priority.

## Decision: Apply Weak Priority Only Within Allowed Buckets

Selection order is due-first:

1. Select overdue due cards by due date and stable stored tie-breakers.
2. Select due-today cards with weak-tag priority.
3. Reserve one due slot for the highest-ranked non-weak due card when at least two due slots and a non-weak due card exist.
4. Fill remaining capacity from new cards only when due cards cannot fill the queue; weak-tagged new cards rank before unrelated new cards.

**Rationale**: This preserves trust in due reviews while letting recurring weak tags affect limited queues.

**Alternatives considered**:

- Let weak-tagged cards outrank overdue cards: rejected by requirement.
- Let weak-tagged new cards outrank due cards: rejected by due-first requirement.
- Always reserve a non-weak slot: rejected because it would waste capacity when only one due slot or no non-weak due cards exist.

## Decision: Keep Review Intensity As Queue Pressure Only

Use `LearnerPreferences.review_intensity` to calculate effective queue size: light 50%, normal 100%, heavy 150% of `session_length`, with final cap 60 and minimum 1. Do not pass intensity into `schedule_review`.

**Rationale**: The preference should control session pressure without changing SM-2 interval, ease, repetition, state, or due date math.

**Alternatives considered**:

- Adjust SM-2 ease/interval by intensity: rejected because SM-2 must stay unchanged.
- Add per-skill intensity settings: rejected because the current preference already exists.
- Add more intensity levels: rejected by YAGNI and current spec.

## Decision: Extend `VocabularySessionPlan` With Safe Selection Reasons

Expose selected-card reasons in `tutor vocab start` JSON through Pydantic models and JSON schema mirrors. Reasons include broad labels such as `overdue`, `due`, `weak_tag_match`, `explicit_filter_match`, `reserved_non_weak_due`, and `new_card_fill`.

**Rationale**: Tests and future summaries need machine-readable explanations, but the next-session context must not expose raw answers or full feedback prose.

**Alternatives considered**:

- Explain only in markdown: rejected because contract tests need machine-readable output.
- Persist selection reasons: rejected because no current workflow needs historical selection audit.
- Include raw event snippets: rejected by privacy and context-budget requirements.

## Decision: Reuse Existing Preference Validation And Repair Flow

Missing `review_intensity` defaults to `normal` through `LearnerPreferences`. Unsupported values fail Pydantic validation and surface through existing YAML setup/repair flows.

**Rationale**: This keeps preferences human-editable while avoiding silent repair of unsupported values.

**Alternatives considered**:

- Coerce unknown values to `normal`: rejected because the requirement says unsupported values must be rejected and fallback only through validation/repair.
- Add a new migration for preferences: rejected because preferences are YAML, not SQLite.
- Move intensity to SQLite: rejected because it is human-editable configuration.
