# Contract: Subagent Context Package

## Purpose

Before each host implementation subagent starts, the main maintainer must provide the same complete context shape. This prevents source drift and cross-host coupling.

## Required Package

```markdown
# Subagent Context Package: <host>

## Scope
- Host: `<hermes|openclaw|claude|codex>`
- Owned setup profile: `specs/006-agent-adapter-setup/contracts/host-setup-profiles/<host>.md`
- Allowed primary write scope: `<host package/profile files plus owned profile contract>`
- Shared files requiring coordination: `<schemas/contracts/tests list>`

## Required Reads
- `specs/006-agent-adapter-setup/spec.md`
- `specs/006-agent-adapter-setup/plan.md`
- `.specify/memory/constitution.md`
- `docs/ROADMAP.md`
- Prior baseline plans:
  - `specs/005-text-modalities/plan.md`
  - `specs/004-richer-feedback-progress/plan.md`
  - `specs/003-smarter-engine/plan.md`

## Official Source
- URL: `<official host setup URL>`
- Required facts to verify: package model, manifest/files, install/update/inspect/remove, user-owned data boundary, verification path

## Shared Contracts
- `contracts/host-setup-profiles/README.md`
- `contracts/host-capability-profile.md`
- `contracts/conformance-kit.md`
- `contracts/manual-provider-install-report.md`

## Verification Requirements
- Source sections used
- Host setup profile contract created
- Capability profile values declared
- Package privacy checked
- Representative text flows verified or capability-gated
- Manual provider install notes recorded

## Report Requirements
- Source usage
- Setup decisions
- Changed files
- Verification commands/manual checks
- Failures
- Blockers
- Any shared-contract conflicts
```

## Validation

- One context package is required for each included host before implementation begins.
- A host subagent may not create tasks or code until it receives this package.
- Main maintainer must review every changed file reported by the subagent.
