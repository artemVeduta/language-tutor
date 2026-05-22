# Contract: Host Setup Profiles

Host setup profiles are versioned, source-backed markdown contracts. During implementation, each primary host subagent creates exactly one file here:

- `hermes.md`
- `openclaw.md`
- `claude.md`
- `codex.md`

Antigravity files are forbidden for spec 006.

## Required Header

```markdown
# Host Setup Profile: <Display Name>

**Host ID**: `<hermes|openclaw|claude|codex>`
**Schema Version**: `1`
**Owner Subagent**: `<subagent name or id>`
**Official Source Checked**: `<YYYY-MM-DD>`
**Status**: `<planned|implemented|verified|blocked>`
```

## Required Sections

### Official Sources

List every official source URL used. For each source, include:

- URL
- Retrieved date
- Source sections or headings used
- Facts copied into this profile
- Unsupported assumptions rejected
- Ambiguities or blockers

### Package Model

Describe the host's documented package/profile/plugin model and why the selected implementation follows it.

### Package Files

List package-owned files and directories. Mark optional files separately from required files.

### Prerequisites

List host software, versions, package managers, CLIs, credentials, env vars, and user approvals needed before install.

### Install Flow

Document the host-supported install path with commands or manual steps.

### Launch Flow

Document how the tutor is launched or invoked after installation.

### Inspect Flow

Document how a maintainer or user confirms the host installed the package/profile/plugin correctly.

### Update Or Reload Flow

Document the host-supported update, reload, or cache-refresh behavior.

### Remove Flow

Document remove/cleanup behavior if supported. If unsupported or manual-only, record the limitation.

### User-Owned Data Boundary

List all data that must not be packaged, copied, overwritten, logged, or published:

- API keys, auth tokens, credentials, and `.env` files
- Learner memories and conversation sessions
- SQLite state, WAL/SHM files, migrations state, and local event data
- Logs, traces, generated workspaces, caches, scratch plans, and local overrides
- Machine-local config and user-provided secrets

Host-specific exclusions may add to this list but cannot weaken it.

### Capability Profile

Reference the host's `AdapterCapabilityProfile` values:

- Text support
- Lifecycle start/end availability
- Boot context trigger
- Setup entry point
- Update behavior
- Optional side-effectful capabilities
- Unsupported capabilities and flow gates

### Verification Expectations

List automated tests, host validation commands, manual provider install checks, and conformance runs required before readiness.

### Known Limitations

Record documented limitations, missing source details, capability-gated skips, or host requirements that could block a representative tutor flow.

## Acceptance Rules

- Every included host has one profile file.
- Every setup behavior is source-backed or explicitly out of scope.
- Every profile names package-owned and user-owned boundaries.
- Every profile includes install, launch, inspect, update/reload, and verification expectations.
- Every profile is reviewed by the main maintainer after the owning subagent reports changed files.
