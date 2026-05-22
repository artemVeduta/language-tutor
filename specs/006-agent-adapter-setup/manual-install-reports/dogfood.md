# Dogfood Report: Agent Adapter Setup

Date: 2026-05-22
Scope: Hermes, OpenClaw, Claude, Codex tutor launch + six representative text flows.

## Host Launch / Capability Inspection

All four hosts inspected via the tutor host CLI (`tutor host capability <host>`,
`tutor host boot-trigger <host>`):

| Host | text_support | lifecycle_start | boot trigger | result |
|------|-------------|-----------------|--------------|--------|
| Hermes | supported | explicit_command | explicit_tutor_command | PASS |
| OpenClaw | supported | first_message | first_tutor_message | PASS |
| Claude | supported | hook | session_start_hook | PASS |
| Codex | supported | hook | codex_plugin_hook | PASS |

`tutor host targets` lists exactly the four approved hosts with approved official
source URLs. No Antigravity target.

## Six Representative Text Flows

The learner-visible tutor flows are host-independent and exercised by the
automated suite (these pass; run via `bin/tutor` + `tests/integration`,
`tests/golden`):

| Flow | Underlying tutor behavior | Per-host surface |
|------|---------------------------|------------------|
| Reading comprehension | PASS (automated) | host-surface pending live session |
| Guided lesson | PASS (automated) | host-surface pending live session |
| Transcript drill | PASS (automated) | host-surface pending live session |
| Vocab drill | PASS (automated) | host-surface pending live session |
| Free-writing feedback | PASS (automated) | host-surface pending live session |
| Progress check | KNOWN PRE-EXISTING FAILURE* | host-surface pending live session |

\* The progress flow has a pre-existing, spec-005 date-fixture bug
(`progress.py` computes a negative `last_seen_age_days` when the run date is past
the hardcoded fixture `BASE_TIME` of 2026-05-21). It is unrelated to spec 006 —
`progress.py` is unchanged by this feature. Tracked separately; does not gate the
adapter-setup deliverable.

## Conformance

`run_conformance` returns `decision=pass` for all four hosts with all six flows
present and no ungated failures (`tests/integration/test_host_text_flows.py`).

## Decision

PASS for the adapter-setup layer (capability, lifecycle, conformance, packaging
privacy, host CLI). Live in-host manual provider verification remains BLOCKED
where host CLIs are unavailable locally (`hermes`, `clawhub`) — see per-host
manual install reports. One pre-existing, out-of-scope progress date-fixture
failure noted above.
