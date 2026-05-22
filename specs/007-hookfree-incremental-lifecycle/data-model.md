# Phase 1 Data Model: Hook-Free Incremental Lifecycle

## New enums (schemas.py)

- `SessionStatus(StrEnum)`: `open`, `closed`. **Stored values only.**
  `stale`/`abandoned` are NOT members — they are read-time labels (see
  `SessionView` below).
- `PersistenceMode(StrEnum)`: `incremental_checkpoint`.
- `SessionIdSource(StrEnum)`: `host_conversation`, `tutor_generated`.
- `CheckpointStepKind(StrEnum)`: `started`, `prompt_shown`, `feedback_shown`,
  `progress_shown`. (Reuse existing modality vocabulary for `modality`.)
- `SessionLabel(StrEnum)` (derived, not stored): `open`, `stale`, `abandoned`,
  `closed`.

## Entity: Session

Stored in new `sessions` table; mirrored by Pydantic `Session`.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | str (`sess_...`) | PK, CLI-minted, immutable, never mutated by a new conversation (FR-004). |
| `host` | HostId | one of claude/codex/openclaw/hermes. |
| `host_conversation_id` | str \| None | optional non-key enrichment only (FR-004). |
| `status` | SessionStatus | `open` on create; `closed` only via manual close (FR-001, FR-007). |
| `started_at` | datetime (UTC) | set on create. |
| `last_seen_at` | datetime (UTC) | updated by `touch_session` on boot/checkpoint/record. |
| `closed_at` | datetime \| None | set only by explicit close (FR-015). |

**Validation**: `closed_at` non-null iff `status == closed`. `started_at <=
last_seen_at`. No `stale`/`abandoned` ever written (FR-018).

## Entity: Checkpoint

Stored in new `checkpoints` table; mirrored by Pydantic `Checkpoint`.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | str (`ckpt_...`) | PK. |
| `session_id` | str | FK → sessions.id; the active session (FR-005). |
| `modality` | Modality | lesson/reading/transcript/vocab/writing/progress. |
| `step_kind` | CheckpointStepKind | started/prompt_shown/feedback_shown/progress_shown. |
| `prompt_ref` | str \| None | stable prompt/exercise id when available (preferred over raw text). |
| `state` | SafeStepState | bounded safe metadata model (no open dict). |
| `summary` | str | short rolling summary, length-bounded. |
| `created_at` | datetime (UTC) | checkpoint time. |

**Validation**: `state` rejects keys/values resembling secrets/log/transcript/
config payloads; `summary` length-capped (FR-002, FR-014).

## Value object: SafeStepState

Bounded Pydantic model (NOT a catch-all dict). Carries only safe step metadata:
e.g. `prompt_ref`, `step_index`, `total_steps`, `modality_hint`, small bounded
tag/label lists. Forbids fields named/typed as raw transcript, secret, log, or
local config. Single source of truth for "what is safe to checkpoint."

## Extended: BootResult (boot result shape)

`session-start` returns:

```json
{ "session_id": "sess_...", "context": { "...existing BootContext..." } }
```

`BootContext` gains a prior-session history block: the N most-recent
(default N=3) prior sessions by `last_seen_at`, most-recent-first, each rendered
with its derived `SessionLabel`, trimmed to the existing token budget (FR-008,
FR-016, SC-005). Existing `boot-context` output stays unchanged for old
consumers.

## Derived view: SessionView (read-time)

Not stored. Produced when reading prior sessions for boot. Wraps a stored
`Session` plus a computed `label: SessionLabel`:

- `closed` → `closed`.
- `open` AND a newer session exists AND `last_seen_at` older than 14 days →
  `abandoned`.
- `open` AND a newer session exists → `stale`.
- `open` AND newest → `open`.

Deterministic given the session set + boot time `now` (FR-018).

## Extended: AdapterCapabilityProfile

Add `persistence_mode: PersistenceMode = incremental_checkpoint` and
`session_id_source: SessionIdSource`. All four host profiles MUST declare
`lifecycle_start=first_message`, `lifecycle_end=not_available`,
`boot_context_trigger=first_tutor_message`, `persistence_mode=
incremental_checkpoint` (FR-009, FR-010). Validator updated: hook boot triggers
are no longer a valid target for any profile.

## Relationships

- Session 1—N Checkpoint (via `session_id`).
- Session 1—N existing answer/review/mistake events (relationship preserved;
  events anchored to active `session_id`, FR-006).
- A new conversation creates a new Session; prior Sessions are immutable history
  (FR-004).

## Migration 004 (`migrations/004_sessions_checkpoints.sql`)

- `CREATE TABLE sessions(...)` with columns above; PK `id`; index on
  `last_seen_at` (boot ordering) and on `status`.
- `CREATE TABLE checkpoints(...)` with columns above; PK `id`; FK/index on
  `session_id`; index on `created_at`.
- Sequential version 004 (loader enforces no gaps). Idempotent via
  `migration_records`. No backfill of legacy answer rows (they keep their
  existing session linkage).
