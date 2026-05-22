# Subagent Context Package: codex

## Scope
- Host: `codex`
- Owned setup profile: `specs/006-agent-adapter-setup/contracts/host-setup-profiles/codex.md`
- Allowed primary write scope: `.codex-plugin/**`, `.agents/plugins/**`, owned profile contract
- Shared files requiring coordination: `src/language_tutor/schemas.py`, `src/language_tutor/adapters/base.py`, `src/language_tutor/adapters/registry.py`, `tests/**` (coordinate via main agent before editing)

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
- URL: `https://developers.openai.com/codex/plugins`
- Required facts to verify: package model (local_marketplace_plugin), manifest/files, install/update/inspect/remove, user-owned data boundary, verification path

## Shared Contracts
- `contracts/host-setup-profiles/README.md`
- `contracts/host-capability-profile.md`
- `contracts/conformance-kit.md`
- `contracts/manual-provider-install-report.md`

## Verification Requirements
- Source sections used
- Host setup profile contract created at `contracts/host-setup-profiles/codex.md` (with embedded ```json contract block matching HostSetupProfileContract)
- Capability profile values declared (must match `src/language_tutor/adapters/registry.py` defaults)
- Package privacy checked (no secrets, memories, sessions, SQLite, logs, caches, local overrides, machine-local config)
- Representative text flows verified or capability-gated: reading, lesson, transcript, vocab, writing, progress
- Manual provider install notes recorded in `manual-install-reports/codex.md`

## Report Requirements
Record in `specs/006-agent-adapter-setup/subagent-reports/codex.md`:
- Source usage
- Setup decisions
- Changed Files (full list)
- Verification commands/manual checks
- Failures
- Blockers
- Any shared-contract conflicts (resolve centrally with main agent)
