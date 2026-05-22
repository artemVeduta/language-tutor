# Contract: Capability Profile Lifecycle Fields

All four host capability profiles (claude, codex, openclaw, hermes) MUST declare
the shared no-hook lifecycle. Asserted by adapter-contract + conformance tests
(FR-009, FR-010, SC-001).

## Required field values (every host)

| Field | Required value |
| --- | --- |
| `lifecycle_start` | `first_message` |
| `lifecycle_end` | `not_available` |
| `boot_context_trigger` | `first_tutor_message` |
| `persistence_mode` | `incremental_checkpoint` (new field) |
| `session_id_source` | `host_conversation` if available, else `tutor_generated` (new field) |

## Validator changes (`AdapterCapabilityProfile`)

- Add `persistence_mode: PersistenceMode` (only value `incremental_checkpoint`).
- Add `session_id_source: SessionIdSource`.
- Reject `lifecycle_start=hook` and any hook boot trigger
  (`session_start_hook`, `codex_plugin_hook`) for ALL hosts — hook lifecycle is no
  longer a valid target (FR-010, FR-011).

## Conformance kit

For each host profile, `run_conformance` MUST verify:

1. The five lifecycle fields above hold the required values.
2. First-message boot succeeds (creates session, returns `session_id`).
3. Checkpoint persistence succeeds with no hook installed.

No profile may claim hook lifecycle as target architecture; no package may
require a hook for correctness (SC-004).

## Boot trigger mapping (`lifecycle.py:select_boot_trigger`)

`first_tutor_message` → `TriggerType.FIRST_MESSAGE`, command `tutor session-start
--json`, input "first tutor-skill invocation", fallback `MANUAL`. Hook trigger
branches are removed from the target mapping (retained only behind deprecated
legacy markers if any hook file is kept).
