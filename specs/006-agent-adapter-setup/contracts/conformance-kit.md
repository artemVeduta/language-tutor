# Contract: Host Conformance Kit

## Purpose

Verify that Hermes, OpenClaw, Claude, and Codex expose the same learner-visible text tutor behavior while setup mechanics remain host-specific.

## Required Inputs

- Host setup profile contract
- Host capability profile
- Installed host package/profile/plugin
- Local test learner home with no production learner data
- Existing Phase 5 text-flow fixtures

## Required Checks

### Capability Check

- Host declares text support.
- Host declares lifecycle start/end availability.
- Host declares boot context trigger.
- Host declares unsupported capabilities before a flow starts.

### Boot Context Check

- Hook-capable hosts build boot context through the documented hook.
- Non-hook hosts build boot context through an explicit alternate trigger.
- Rendered boot context remains deterministic and within the existing budget.
- Boot context code does not package or read host-owned secrets.

### Representative Text Flows

Run or manually verify all six Phase 5 text flows:

- Reading comprehension
- Guided lesson
- Transcript drill
- Vocab drill
- Free-writing feedback
- Progress check

Each flow must preserve:

- Validated tutor contracts
- Existing `FeedbackEnvelope` behavior where feedback is produced
- Host-independent progress and local data behavior
- Learner-safe setup/error messages

### Data Ownership Check

- No distributed package contains secrets, sessions, memories, SQLite state, logs, caches, local overrides, or machine-local config.
- Runtime learner state is written only through existing SQLite/YAML ownership boundaries.
- Package update/reload does not overwrite user-owned state.

### Error Behavior Check

Host setup failures must identify:

- Host
- Failed phase
- Missing prerequisite, invalid configuration, permission requirement, or unsupported capability
- Concrete remediation
- Data-safety result

## Result Shape

```json
{
  "schema_version": 1,
  "host": "claude",
  "capability_profile": "schemas/host_capability_profile.schema.json",
  "flows": {
    "reading": "pass",
    "lesson": "pass",
    "transcript": "pass",
    "vocab": "pass",
    "writing": "pass",
    "progress": "pass"
  },
  "boot_context_result": "pass",
  "feedback_contract_result": "pass",
  "progress_contract_result": "pass",
  "error_behavior_result": "pass",
  "data_ownership_result": "pass",
  "skipped_flows": [],
  "decision": "pass"
}
```

## Blocking Rules

- Any failed representative flow blocks readiness unless capability gating is documented in the capability profile and manual provider install report.
- Any package privacy failure blocks readiness.
- Any existing Claude baseline regression blocks readiness.
- Any Antigravity artifact fails conformance for this feature.
