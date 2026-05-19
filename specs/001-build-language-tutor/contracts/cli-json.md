# CLI JSON Contract

`bin/tutor` is the stable boundary used by hooks, skills, tests, and contributors. Commands write JSON to stdout for machine-readable operations and exit non-zero only for actionable failures.

## Global Rules

- Output JSON is UTF-8, schema-validated, and deterministic for identical input/state.
- Errors use `{ "error": { "code": "...", "message": "...", "repair_hint": "..." } }`.
- Commands that mutate state perform exactly one transaction and return the committed record id or summary.
- Commands must not read or write data outside platformdirs-resolved config/data/state paths unless an explicit test path is provided.

## Commands

### `tutor doctor --json`

Checks runtime, plugin registration, data paths, migrations, schema health, and common setup problems.

**Output**: `DoctorReport`.

### `tutor setup read --json`

Loads current profile/preferences or defaults.

**Output**: `SetupState`.

### `tutor setup write --json <payload>`

Validates and writes profile/preferences YAML without touching learning history.

**Input**: `LearnerProfile` plus `LearnerPreferences`.

**Output**: `SetupWriteResult`.

### `tutor boot-context --json`

Builds session-start learner context from local state.

**Output**: `BootContext`.

### `tutor render boot-context --json <payload>`

Renders a validated `BootContext` as markdown-style host text.

**Output**: `{ "markdown": "..." }`.

### `tutor vocab start --json`

Returns due queue and optional starter-content request metadata.

**Output**: `VocabularySessionPlan`.

### `tutor vocab answer --json <payload>`

Records one vocabulary answer, evaluates against accepted answers, applies SM-2 exactly once, and returns feedback.

**Input**: `VocabularyAnswerInput`.

**Output**: `VocabularyAnswerResult` containing `FeedbackEnvelope`, `AnswerEvent`, and `VocabularyReview`.

### `tutor writing prompt --json`

Returns a level-appropriate writing prompt or prompt choices.

**Output**: `WritingPromptResult`.

### `tutor writing record --json <payload>`

Validates judge output, records answer/mistakes, and returns the validated or downgraded feedback.

**Input**: `WritingRecordInput` containing learner answer and candidate `FeedbackEnvelope`.

**Output**: `WritingRecordResult`.

### `tutor render feedback --json <payload>`

Renders a validated feedback envelope.

**Output**: `{ "markdown": "...", "ascii_markdown": "..." }`.

### `tutor progress --json`

Returns streak, due counts, weak patterns, item maturity, latest recap, and month-to-date cost.

**Output**: `ProgressReport`.

### `tutor session-end --json`

Handles SessionEnd analysis input and persists validated summary/cost/metrics. It is safe to run asynchronously and must not block host shutdown on non-critical analyzer failure.

**Output**: `SessionEndResult`.

## Contract Tests

- Invalid YAML returns repair-oriented error and does not mutate SQLite.
- Duplicate `vocab answer` calls with same idempotency key do not double-apply SRS.
- Same DB/profile state produces byte-identical `boot-context` JSON and rendered markdown.
- Unsupported evaluator tags are rejected or downgraded before persistence.
