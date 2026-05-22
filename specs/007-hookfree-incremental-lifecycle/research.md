# Phase 0 Research: Hook-Free Incremental Lifecycle

All HANDOFF "Open Questions" were resolved by the spec clarification session
(2026-05-22) and the constitution v1.2.0 amendment. No NEEDS CLARIFICATION
remain. Decisions below are the authoritative inputs to Phase 1 design.

## R1 — Boot command shape

- **Decision**: Add a dedicated `session-start` CLI command that mints the
  session id, persists the `open` row, and returns `{session_id, context}`. Keep
  `boot-context` working unchanged for existing consumers (FR-016).
- **Rationale**: Session creation is a state-mutating concern distinct from pure
  context rendering; a separate command keeps `boot-context` a deterministic,
  side-effect-free renderer (SoC, Constitution I/II). Backward compatibility is a
  hard requirement.
- **Alternatives rejected**: Overloading `boot-context` to also create sessions —
  breaks its read-only contract and risks duplicate session minting from existing
  callers.

## R2 — Session id ownership / first-message detection

- **Decision**: CLI mints and owns `session_id`. The agent threads it: first
  tutor-skill invocation calls `session-start` with no id → CLI mints + returns;
  agent passes that id to every later `bin/tutor` call this conversation. New
  conversation = fresh agent context = no carried id = new session minted. Host
  conversation id is stored only as optional non-key enrichment.
- **Rationale**: Skills cannot read the host conversation id (Claude delivers it
  only to hooks via stdin, which this phase removes); it cannot be the key. Agent
  threading is the only host-independent mechanism (FR-003, FR-004, FR-019).
- **Alternatives rejected**: Host conversation id as key (unreachable from a
  skill); boot-flag heuristics (no reliable per-host signal).

## R3 — Checkpoint state content

- **Decision**: Store bounded safe step metadata + a stable `prompt_ref` where
  one exists + a short rolling summary. Never store raw prompt text when a stable
  reference exists, and never raw secrets/full logs/transcripts/local config.
- **Rationale**: Constitution IV and FR-014 forbid sensitive content; references
  are smaller and stable. `state_json` is a validated `SafeStepState` model, not
  an open dict (Constitution II).
- **Alternatives rejected**: Full prompt text (privacy + size); arbitrary dict
  (catch-all forbidden).

## R4 — Stale / abandoned definition

- **Decision**: Read-time labels, no stored mutation, no timer. A prior `open`
  session reads as `stale` once a newer session exists; reads as `abandoned` when
  `last_seen_at` is older than 14 days. Stored status stays `open`.
- **Rationale**: Avoids background jobs and write amplification; deterministic and
  cheap to compute at boot (FR-018, clarifications).
- **Alternatives rejected**: Stored status transitions (needs a writer/timer);
  host-based staleness (host-specific complexity).

## R5 — Rolling summary generation

- **Decision**: Deterministic local renderer derives summaries from persisted
  events/checkpoints, consistent with the token-budgeted deterministic
  boot-context rule.
- **Rationale**: Boot must be deterministic and reproducible in golden tests
  (Constitution III, operational constraint on boot context). No LLM call in the
  boot path.
- **Alternatives rejected**: Agent-generated per-step summaries (nondeterministic,
  unverifiable in golden tests).

## R6 — session_id on record commands

- **Decision**: Every record/checkpoint command takes the active `session_id`
  explicitly (threaded by the agent). No default/generated id at record time.
- **Rationale**: FR-019 requires all writes in one conversation to share exactly
  one `session_id`; an implicit default would let writes leak across sessions.
- **Alternatives rejected**: Optional/default id (breaks the single-session-id
  invariant; untestable).

## R7 — Old hook files

- **Decision**: Remove hook lifecycle from required surface; if any hook file is
  retained it is marked deprecated legacy compatibility and excluded from
  capability and conformance assertions (FR-011, FR-010, HANDOFF "Remove Old Hook
  Implementation").
- **Rationale**: Hooks must not be an alternate supported lifecycle; one no-hook
  model only.
- **Alternatives rejected**: Keeping hooks as optional behavior (re-introduces
  per-host divergence the phase exists to remove).

## R8 — New capability fields

- **Decision**: Add `persistence_mode` (`incremental_checkpoint`) and
  `session_id_source` (`host_conversation` | `tutor_generated`) to the capability
  profile; set `lifecycle_start=first_message`, `lifecycle_end=not_available`,
  `boot_context_trigger=first_tutor_message` for all four hosts.
- **Rationale**: FR-009 and Principle IX require these as declared contract
  fields; existing enums already contain `first_message`/`not_available`/
  `first_tutor_message`. New `PersistenceMode` enum + `SessionIdSource` enum
  needed.
- **Alternatives rejected**: Encoding persistence mode in prose/docs only (not
  contract-testable; conformance must assert it).
