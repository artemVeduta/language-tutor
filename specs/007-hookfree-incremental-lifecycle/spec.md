# Feature Specification: Hook-Free Incremental Lifecycle

**Feature Branch**: `007-hookfree-incremental-lifecycle`

**Created**: 2026-05-22

**Status**: Draft

**Input**: User description: "phase 6.5 from docs/roadmap.md and based on draft design HANDOFF-incremental-lifecycle-no-hooks.md"

## Clarifications

### Session 2026-05-22

- Q: What triggers a prior `open` session becoming `stale`/`abandoned`? → A: Lazy, computed at boot — `stale`/`abandoned` are read-time derived labels (no stored mutation, no timer); a prior `open` session is shown as `stale` once a newer session boots, and as `abandoned` past a read-time age cutoff.
- Q: What bounds the prior-session history surfaced at boot? → A: The N most-recent prior sessions by `last_seen_at` (default N=3), ordered deterministically, then trimmed to fit the existing token budget.
- Q: What age cutoff makes a prior `open` session read as `abandoned`? → A: `last_seen_at` older than 14 days.
- Q: How does the system tell a first tutor message from a continuation without lifecycle hooks? → A: The CLI mints the session id and the agent threads it. The host conversation id is NOT reachable from a skill invocation (Claude Code delivers it only to hooks via stdin, which this phase removes), so it is not the key. First tutor-skill invocation of a conversation: the agent calls `session-start` with no id; the CLI mints a new `session_id`, persists the row (`status=open`), and returns it. The agent then carries that `session_id` and passes it to every subsequent `bin/tutor` call this conversation. A new conversation = fresh agent context = no carried id = a new `session_id` is minted. Host conversation id, when present, is stored only as optional non-key enrichment metadata.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mid-lesson app close keeps my work (Priority: P1)

As a learner, when I start a tutoring session on any host and the app closes
mid-lesson (I quit, the host crashes, or the conversation ends with no shutdown
event), every step the tutor showed me and every answer I gave is already saved.
Nothing depends on a clean shutdown to be recorded.

**Why this priority**: This is the core correctness fix the phase exists for.
Without it, learners silently lose progress whenever a session ends without a
shutdown hook firing — which is the normal case on hosts with no reliable session
end. Per-step persistence is the single most valuable outcome.

**Independent Test**: Start a session, present a lesson/exercise (checkpoint
written), submit an answer (answer/review/mistake events written), then terminate
the process without any end event. Re-open and confirm the prior session and all
its steps and answers are intact and readable as history.

**Acceptance Scenarios**:

1. **Given** a new conversation on any supported host, **When** the first tutor
   message is sent, **Then** a new session is created and the active session id is
   returned with boot context.
2. **Given** an active session, **When** the tutor presents a lesson, exercise, or
   prompt, **Then** a checkpoint for that step is persisted immediately under the
   active session id.
3. **Given** an active session, **When** the learner submits an answer, **Then**
   the answer, review, and mistake events persist immediately under the active
   session id.
4. **Given** an active session with at least one checkpoint and answer, **When**
   the app closes with no session-end event, **Then** all data through the last
   checkpoint survives and the session remains `open` (or becomes `stale`).

---

### User Story 2 - New conversation reads prior sessions as history (Priority: P1)

As a returning learner, when I start a fresh conversation, the tutor boots into a
brand-new session but still remembers what I did before — including sessions that
were never formally closed — and uses them as history/resume context without
overwriting them.

**Why this priority**: Boot must produce continuity from incremental data alone,
since there is no end-of-session finalizer to summarize the prior run. This is
what makes per-step persistence usable rather than just safe.

**Independent Test**: Leave a prior session `open`/`stale`, start a new
conversation, and confirm boot creates a different new session id, reads the prior
session as history, and writes all new data only under the new id (prior id
unchanged).

**Acceptance Scenarios**:

1. **Given** a prior `open`/`stale` session exists, **When** a new conversation
   boots, **Then** a new distinct session id is created and the prior session id
   is not mutated.
2. **Given** prior sessions of any status (`open`, `stale`, `closed`), **When**
   boot builds context, **Then** the N most-recent (default N=3) by `last_seen_at`
   surface as history/resume context, most-recent-first, within the token budget.
3. **Given** the new session is active, **When** new checkpoints/answers are
   recorded, **Then** they write only under the new session id.

---

### User Story 3 - All hosts behave identically; no hooks required (Priority: P2)

As an operator setting up the tutor on Claude, Codex, OpenClaw, or Hermes, I do
not need to install, enable, or validate any host-specific lifecycle hook for the
tutor to record progress correctly. Every host follows the same first-message
boot plus incremental-persistence lifecycle.

**Why this priority**: Removes host-specific install/validation complexity and a
class of silent-failure modes. Depends on US1/US2 being in place first, hence P2.

**Independent Test**: Run the conformance suite against each host profile and
confirm every profile declares the shared lifecycle values and passes
first-message-boot + checkpoint-persistence checks with no hook installed.

**Acceptance Scenarios**:

1. **Given** any supported host profile, **When** its capabilities are inspected,
   **Then** `lifecycle_start=first_message`, `lifecycle_end=not_available`,
   `persistence_mode=incremental_checkpoint`, and
   `boot_context_trigger=first_tutor_message`.
2. **Given** no lifecycle hook is installed on a host, **When** a conversation
   runs end-to-end, **Then** boot, checkpoints, and answer events all persist
   correctly.
3. **Given** the conformance/packaging suites run, **When** profiles and packages
   are checked, **Then** no profile claims hook lifecycle as target architecture
   and no package requires a hook for correctness.

---

### User Story 4 - Explicit manual close on demand (Priority: P3)

As a learner who wants to wrap up deliberately, I can run an explicit close
command that marks the session `closed`, writes a final summary and cost flush,
and records a next-focus decision — but this never happens automatically.

**Why this priority**: Useful housekeeping and richer next-boot memory, but
optional; correctness does not depend on it. Lowest priority.

**Independent Test**: Run the manual close command on an active session and
confirm it transitions to `closed` with `closed_at` set and a final summary
written; confirm no normal lifecycle path triggers close.

**Acceptance Scenarios**:

1. **Given** an active session, **When** the learner runs the explicit close
   command, **Then** the session becomes `closed`, `closed_at` is set, and a final
   summary/cost flush is written.
2. **Given** normal tutoring activity (boot, checkpoint, answer), **When** no close
   command is run, **Then** the session is never closed automatically.

---

### Edge Cases

- **Host conversation id unavailable**: this is the normal case (skills cannot
  read it). The session id is always tutor/CLI-minted regardless; host conversation
  id is recorded only as optional enrichment when present. Lifecycle is identical
  whether or not it is available.
- **Two conversations interleaved / concurrent boots**: each gets its own distinct
  session id; no cross-write between sessions.
- **Stale-session definition**: `stale`/`abandoned` are derived at read time, not
  stored. A prior `open` session is labeled `stale` once a newer session boots; it
  is labeled `abandoned` once its `last_seen_at` is older than 14 days. The
  stored status stays `open` in both cases (see FR-018).
- **Missing transaction commit**: any write path that records a checkpoint/answer
  must durably commit so a hard kill loses nothing past the last completed step.
- **Legacy hook files still present**: deprecated hook files must not be asserted
  by capability/conformance and must not be required for correctness.
- **Checkpoint content safety**: checkpoint state must never capture raw secrets,
  full host logs, full transcripts, or local config.
- **Boot backward compatibility**: existing `boot-context` consumers must keep
  working after boot is extended to return a session id.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST persist explicit session rows with at least: tutor
  session id, host, optional host conversation id, stored status (`open` or
  `closed` only — `closed` set solely by explicit manual close), started-at,
  last-seen-at, and closed-at (set only on explicit close). `stale` and
  `abandoned` are NOT stored statuses; they are read-time derived labels
  (see FR-018), never written back to the row.
- **FR-002**: System MUST persist durable checkpoints for current-work state
  before any answer exists, capturing at least: checkpoint id, session id,
  modality, step kind, optional prompt reference, safe step state, a short rolling
  summary, and created-at.
- **FR-003**: On the first tutor-skill invocation of a conversation (any tutor
  skill, e.g. `/tutor-lesson`), the agent MUST call `session-start` with no
  session id; System MUST mint a new tutor `session_id`, persist the session row
  (`status=open`), and return that `session_id` alongside boot context. The agent
  MUST then carry the returned `session_id` and pass it to every subsequent
  `bin/tutor` call in the same conversation, which reuse that session (no boot
  flag, host conversation id, or lifecycle hook required).
- **FR-004**: System MUST mint and own the tutor `session_id` (CLI-generated);
  the host conversation id MUST NOT be the session key — it is unavailable to a
  skill invocation and is stored only as optional non-key enrichment metadata when
  supplied. A new conversation (fresh agent context carrying no id) MUST mint a new
  `session_id`; System MUST NOT mutate prior session ids.
- **FR-005**: System MUST write a checkpoint immediately whenever the tutor
  presents a lesson, exercise, or prompt.
- **FR-006**: System MUST persist learner answers and their review/mistake events
  immediately under the active session id (preserving existing answer-event paths).
- **FR-007**: System MUST NOT end any session automatically; a session becomes
  `closed` only via an explicit manual close command.
- **FR-008**: On boot, System MUST read the N most-recent prior sessions (default
  N=3) by `last_seen_at` — across stored `open`/`closed` rows, with `stale`/
  `abandoned` applied as read-time labels — ordered deterministically (most recent
  first) and trimmed to the existing token budget, surfacing them as history/
  resume context; all new data MUST write only under the new session id.
- **FR-009**: All supported host capability profiles MUST declare
  `lifecycle_start=first_message`, `lifecycle_end=not_available`,
  `persistence_mode=incremental_checkpoint`, and
  `boot_context_trigger=first_tutor_message`.
- **FR-010**: Host capability profiles MUST NOT model Codex `Stop`, Claude
  `SessionStart`/`SessionEnd`, OpenClaw `session_end`, or Hermes `on_session_end`
  as target tutor lifecycle.
- **FR-011**: System MUST remove hook lifecycle assertions and package
  requirements; hook files, if retained, MUST be marked deprecated legacy
  compatibility and excluded from capability and conformance assertions.
- **FR-012**: System MUST provide repository operations to open a session, touch
  (update last-seen) a session, record a checkpoint, list recent open/stale
  sessions, and close a session (explicit manual close only).
- **FR-013**: System MUST ensure every checkpoint/session/answer write path
  durably commits so a process kill loses no data past the last completed step.
- **FR-014**: Checkpoint and session state MUST exclude raw secrets, full host
  logs, full conversation transcripts, and local config; packaging MUST NOT ship
  user-owned session/checkpoint data.
- **FR-015**: The explicit manual close command MUST, when run, mark the session
  `closed`, set closed-at, and write a final summary, cost flush, and next-focus
  decision.
- **FR-016**: Boot output MUST remain backward compatible for existing
  `boot-context` consumers while adding the active session id.
- **FR-017**: Migration MUST update affected docs and tests (`hooks/README.md`,
  `README.md` host-setup notes, Phase 6 lifecycle wording in `docs/ROADMAP.md`,
  host-setup profiles, manual-install reports, and the adapter/packaging tests
  listed in the HANDOFF) so none assert hook lifecycle as normal behavior.
- **FR-018**: System MUST derive `stale` and `abandoned` as read-time labels over
  prior `open` sessions without mutating stored rows: a prior `open` session
  reads as `stale` once a newer session exists, and as `abandoned` when its
  `last_seen_at` is older than 14 days. No background job or timer performs these
  transitions.
- **FR-019**: The agent-threading contract MUST be explicit and enforced: each
  tutor `SKILL.md` MUST instruct the agent to obtain the `session_id` from
  `session-start` and pass that same id into every subsequent `bin/tutor` call,
  and validation MUST assert that all checkpoint/answer/review/mistake writes in a
  single conversation flow share exactly one `session_id` (golden + integration).

### Key Entities *(include if feature involves data)*

- **Session**: a single tutoring run. Owns id, host, optional host conversation
  id, status lifecycle, and timestamps. A new conversation always creates a new
  Session; prior Sessions are immutable history once a new one starts.
- **Checkpoint**: a durable snapshot of current-work state for a step the tutor
  presented, before any answer. Belongs to one Session; carries modality, step
  kind, optional prompt reference, safe state, rolling summary, and timestamp.
- **Answer/Review/Mistake events**: existing per-answer records, now anchored to
  the active Session id (relationship preserved from prior phases).

## Constitution Alignment *(mandatory)*

- **Affected Layers**: Host adapters (capability profiles), core (boot/lifecycle),
  DAL (session/checkpoint models, repositories, migrations), CLI (boot/session
  command, manual close), skills (checkpoint calls on presentation),
  hooks/packaging (hook removal/deprecation, privacy tests). No renderer pedagogy
  change; pedagogy stays host-blind.
- **Data Ownership**: SQLite state — new `sessions` + `checkpoints` tables plus
  existing answer/review/mistake ledger; no new YAML config. User-owned data MUST
  NOT be packaged.
- **Contract Surfaces**: Pydantic models + JSON-Schema mirrors for session,
  checkpoint, and extended boot result; CLI JSON for boot/session-start and manual
  close; SQL migration for new tables; capability-profile contract fields.
- **Required Validation**: Unit (repository methods, transaction commits), golden
  (deterministic boot context with session id, checkpoint rendering), contract
  (capability profiles, boot result shape), integration (host text flows with
  mid-session kill), migration (new tables/round-trip), conformance kit
  (first-message boot + checkpoint persistence per host), packaging-privacy.
- **Skill Creation**: No new skills. Existing tutor skills (lesson/reading/
  transcript/vocab/writing/progress) are edited to call checkpoint on
  presentation; any `SKILL.md` edit MUST use the local writing-skills helper plus
  required external references and subagent RED/GREEN/REFACTOR pressure evidence.
- **Scope Guardrails**: No hooks for normal lifecycle; no host-specific hook
  packages; no automatic session end; no mutation of prior session ids; no Codex
  `Stop` treated as session end; no storage of raw host logs/transcripts/secrets/
  local config; no new modality; enforces Constitution Principle IX (v1.2.0).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of supported host profiles (claude, codex, openclaw, hermes)
  declare the shared lifecycle values and pass first-message-boot + checkpoint
  persistence in the conformance suite, with zero hooks installed.
- **SC-002**: After a mid-session process kill with no end event, 100% of steps
  and answers recorded before the kill are recoverable on the next boot.
- **SC-003**: A new conversation always boots a distinct session id and never
  mutates a prior session id (0 occurrences across the test suite).
- **SC-004**: No host setup profile or package requires a hook for correctness;
  packaging-privacy checks find 0 user-owned session/checkpoint files shipped.
- **SC-005**: Boot context (now including session id and the N most-recent
  prior sessions, default N=3, most-recent-first) remains deterministic and
  within the existing token budget.
- **SC-006**: All automated gates — pytest, pyright, ruff — are green; all docs
  and tests listed for migration no longer assert hook lifecycle as normal.

## Assumptions

- Existing answer/review/mistake persistence paths already work and are reused,
  not rebuilt (per HANDOFF "Current Repo State").
- The four supported hosts are claude, codex, openclaw, hermes; antigravity stays
  out of scope (rejected at the `HostId` schema layer in Phase 6.x).
- Boot is extended compatibly (existing `boot-context` keeps working) rather than
  replaced; a dedicated `session-start` command may be added — final command shape
  decided in planning (see clarifications).
- Rolling summaries for boot/resume are derived from persisted events/checkpoints
  by a deterministic local renderer, consistent with the token-budgeted,
  deterministic boot-context rule (subject to clarification).
- "Safe step state" means bounded, non-sensitive metadata; prompt references are
  preferred over raw prompt text where a stable reference exists.
- SM-2, scheduling math, and pedagogy are unchanged by this phase.
