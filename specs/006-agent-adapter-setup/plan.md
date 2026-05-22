# Implementation Plan: Agent Adapter Setup

**Branch**: `006-agent-adapter-setup` | **Date**: 2026-05-22 | **Spec**: `specs/006-agent-adapter-setup/spec.md`

**Input**: Feature specification from `specs/006-agent-adapter-setup/spec.md`

**Note**: This file is the `/speckit-plan` output. Phase 2 task generation is intentionally deferred to `/speckit-tasks`.

## Summary

Set up source-backed distribution paths for Hermes, OpenClaw, Claude, and Codex while keeping language-tutor pedagogy and learner data host-independent. The implementation introduces explicit host setup profile contracts, host capability profiles, lifecycle boot-trigger handling for hosts without Claude-style hooks, shared conformance verification for all Phase 5 text flows, and manual provider install reports. Antigravity, audio, image, dashboards, cloud sync, new learner persistence, bundled curricula, and scheduler changes remain out of scope.

## Technical Context

**Language/Version**: Python 3.12+ with the existing synchronous core. Host packages may add host-native metadata/configuration files. OpenClaw packaging uses Node >=22 and TypeScript ESM for its plugin slice only.

**Primary Dependencies**: Existing core runtime dependencies remain Click, Pydantic v2, ruamel.yaml, platformdirs, and stdlib `sqlite3`/`json`/`datetime`/`pathlib`. Dev tooling remains pytest, syrupy, freezegun, pytest-cov, pyright, ruff, hatchling, uv, and pre-commit. Host-specific verification uses official host tools where available: `hermes`, OpenClaw/ClawHub commands and `pnpm`, `claude plugin validate` and `claude --plugin-dir`, and Codex local marketplace/plugin installation flows. No new Python runtime dependency is planned for the host-capability layer.

**Storage**: Existing local SQLite remains the source of truth for learner events, mistake events, sessions, reviews, costs, and progress inputs. YAML remains human-editable profile/preferences only. Host setup profiles, subagent reports, conformance records, and manual install reports are repository artifacts under `specs/006-agent-adapter-setup/`. Host packages must not include user secrets, learner memories, conversation sessions, SQLite state, logs, local overrides, or machine-specific config.

**Testing**: pytest for unit, contract, integration, migration/no-migration, packaging privacy, and CLI tests; syrupy for deterministic rendering where host-visible output changes; pyright and ruff for static gates. Host setup verification also requires official/manual host gates: local Hermes profile install/update/info/delete, OpenClaw package metadata and SDK checks, Claude plugin validation/local load/reload, Codex local marketplace install/restart verification, and final manual provider install tests covering every Phase 5 text flow.

**Target Platform**: macOS and Linux local developer machines with Hermes, OpenClaw, Claude Code, and Codex installed as separate host runtimes. The shared tutor core stays local-first and host-independent.

**Project Type**: Local Python package plus multi-host agent/plugin/profile distribution surfaces. This feature changes host adapter contracts, capability schemas, lifecycle boot routing, setup/package metadata, conformance tests, manual verification docs, and host-specific distribution files.

**Performance Goals**: Capability checks and boot-context trigger selection remain deterministic and fast enough for per-session host startup. Existing boot context stays within its token/character budget. Conformance runs cover six representative text flows without adding persistent exercise bodies or host-specific progress logic.

**Constraints**: Official Hermes, OpenClaw, Claude, and Codex setup docs are source-of-truth inputs. Each included host implementation must be owned by exactly one primary implementation subagent after receiving the main-maintainer context package. Host-specific code cannot import or own pedagogy, scheduling, feedback semantics, progress calculation, or DAL internals. Hosts without hook-driven startup must use an explicit alternate boot-context trigger. Any representative tutor-flow failure blocks readiness unless a capability profile gates the flow and the manual install report records the skip. Antigravity remains fully excluded.

**Scale/Scope**: Four supported setup targets, one setup profile contract per target, one capability profile per target, one subagent implementation slice per target, six Phase 5 text flows per target, single local learner, existing local state only.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Layered boundaries**: PASS. Affected layers are host adapters, host capability contracts, lifecycle boot-context routing, setup/distribution packaging, plugin/profile metadata, conformance tests, integration tests, and verification documentation. Core pedagogy, scheduling, feedback semantics, progress calculation, and DAL ownership remain host-independent.
- **Contracts and abstractions**: PASS. New data crosses boundaries through Pydantic models, JSON schema mirrors, documented CLI JSON, host setup profile contracts, capability profile contracts, lifecycle trigger contracts, and manual report contracts. Host packages depend on tutor CLI/core contracts, not concrete DAL internals.
- **Deterministic tests**: PASS. Required coverage includes unit tests for capability/lifecycle models, contract tests for host setup profile schema and capability profile schema, adapter conformance tests for all hosts, integration tests for the six Phase 5 text flows through host adapters, packaging privacy tests, and regression tests preserving the existing Claude baseline.
- **Skill creation gate**: PASS. Host packages may create or update `SKILL.md` files for Claude/Codex-style distribution. Any project `SKILL.md` creation or edit must be handled by the assigned host subagent using the local writing-skills helper at `/Users/artem.veduta/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-skills`, required external references, RED/GREEN/REFACTOR pressure evidence, activation/description review, and main-agent changed-file review.
- **Local-first data ownership**: PASS. SQLite and YAML ownership remain unchanged. Distribution packages include metadata, prompts, skill wrappers, hooks, manifests, and defaults only. Secrets, memories, sessions, SQLite files, logs, local overrides, and machine-local config are excluded from every package and verified by packaging tests.
- **Scope discipline**: PASS. This feature explicitly moves Hermes, OpenClaw, Claude, and Codex setup into current scope as the Phase 6/6.x host setup slice. Antigravity and all new modalities, dashboards, cloud sync, multi-user behavior, new scheduler algorithms, bundled curricula, gamification, and new learner data stores are rejected.
- **DRY and composition**: PASS. Capability names, lifecycle trigger values, representative flow names, setup profile fields, privacy exclusion lists, and conformance expectations are single-source contracts. Behavior is composed through adapter/capability collaborators, not inheritance, service locators, or global mutable state.

## Project Structure

### Documentation (this feature)

```text
specs/006-agent-adapter-setup/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- conformance-kit.md
|   |-- host-capability-profile.md
|   |-- manual-provider-install-report.md
|   |-- subagent-context-package.md
|   `-- host-setup-profiles/
|       `-- README.md                # schema/template; host files owned by implementation subagents
|-- subagent-reports/                # planned implementation evidence
|-- manual-install-reports/          # planned implementation evidence
`-- tasks.md                         # Generated by /speckit-tasks
```

### Source Code (repository root)

```text
.claude-plugin/
`-- plugin.json                      # existing Claude package metadata, preserved/extended only as needed

.codex-plugin/
`-- plugin.json                      # planned Codex package metadata if implemented as repo plugin

.agents/
`-- plugins/
    `-- marketplace.json             # planned repo-local Codex marketplace entry if selected

openclaw-plugin/                     # planned host-specific package boundary, exact path finalized by subagent
|-- package.json
|-- openclaw.plugin.json
`-- src/
    `-- index.ts

hermes-profile/                      # planned profile distribution boundary, exact path finalized by subagent
|-- distribution.yaml
|-- SOUL.md
|-- config.yaml
|-- skills/
`-- mcp.json                         # only if needed by documented setup

skills/
|-- tutor-setup/
|-- tutor-vocab/
|-- tutor-writing/
|-- tutor-progress/
|-- tutor-reading/
`-- tutor-lesson/

hooks/
|-- hooks.json
`-- session_start.py                 # existing/extended hook path if host package needs it

bin/
`-- tutor

src/language_tutor/
|-- adapters/
|   |-- base.py                      # host capability/lifecycle Protocols planned
|   |-- claude.py                    # preserve existing baseline while adapting to common contracts
|   |-- codex.py                     # planned if runtime translation differs from package-only setup
|   |-- hermes.py                    # planned if runtime translation differs from package-only setup
|   `-- openclaw.py                  # planned if runtime translation differs from package-only setup
|-- boot_context.py                  # alternate boot trigger support
|-- cli.py                           # capability/check/conformance JSON commands if needed
|-- schemas.py                       # Pydantic contracts and JSON schema export mapping
`-- dal/                             # no host-owned learner state

schemas/
|-- host_capability_profile.schema.json
|-- host_setup_profile.schema.json
|-- lifecycle_trigger.schema.json
|-- conformance_run.schema.json
`-- manual_provider_install_report.schema.json

tests/
|-- adapter_contract/
|   |-- test_host_capability_profile.py
|   |-- test_lifecycle_contract.py
|   |-- test_conformance_kit.py
|   |-- test_claude_adapter.py
|   |-- test_codex_adapter.py
|   |-- test_hermes_adapter.py
|   `-- test_openclaw_adapter.py
|-- integration/
|   |-- test_host_text_flows.py
|   `-- test_local_data_ownership.py
|-- packaging/
|   |-- test_host_setup_profiles.py
|   |-- test_distribution_privacy.py
|   |-- test_claude_plugin_package.py
|   |-- test_codex_plugin_package.py
|   |-- test_hermes_profile_distribution.py
|   `-- test_openclaw_plugin_package.py
`-- unit/
    |-- test_boot_context.py
    `-- test_schemas.py
```

**Structure Decision**: Extend the existing single Python package for shared capability/lifecycle contracts and conformance logic. Keep host-specific distribution files in explicit package/profile boundaries so Hermes, OpenClaw, Claude, and Codex subagents can work independently. Host packages may wrap `bin/tutor`, skills, hooks, and metadata, but the tutor core remains the single owner of pedagogy, feedback, progress, and learner state. A new persistence layer, new core package split, or generic "all hosts" abstraction beyond the four documented hosts is rejected.

## Phase 0: Research

**Output**: `specs/006-agent-adapter-setup/research.md`

All technical-context unknowns are resolved:

- Supported hosts are exactly Hermes, OpenClaw, Claude, and Codex. Antigravity is excluded despite the older roadmap listing because the active spec explicitly skips it.
- Hermes uses a git-backed profile distribution with `distribution.yaml`, profile prompt/config, optional skills/cron/MCP, `env_requires`, `hermes profile install`, `hermes profile update`, `hermes profile info/list`, and hard exclusions for secrets, memories, sessions, state, logs, workspaces, caches, and `local/`.
- OpenClaw uses a Node >=22 TypeScript ESM plugin package with `package.json`, `openclaw.plugin.json`, focused `openclaw/plugin-sdk/<subpath>` imports, `definePluginEntry` or `defineChannelPluginEntry`, `api.registerTool`, optional tools for side-effectful/binary-dependent capabilities, ClawHub or npm install, and `pnpm` verification.
- Claude preserves the existing plugin baseline: `.claude-plugin/plugin.json`, root-level `skills/`, `agents/`, `hooks/hooks.json`, `bin/`, local `claude --plugin-dir`, `/reload-plugins`, and `claude plugin validate`.
- Codex uses `.codex-plugin/plugin.json` as the required plugin entry point, root-level `skills/`, optional `.app.json`, `.mcp.json`, `hooks/`, repo or personal marketplace files, cached local install, plugin-scoped MCP policy, and hook gating through `[features].plugin_hooks = true`.
- Capability modeling needs two axes: text modality support and lifecycle/boot availability. Claude and Codex can use hook-based startup when enabled; hosts without equivalent hooks must declare an alternate trigger such as explicit command or first-message bootstrap.
- Conformance must run every Phase 5 text flow: reading comprehension, guided lesson, transcript drill, vocab drill, free-writing feedback, and progress check. Failure blocks readiness unless capability gating and manual reports document the skip.
- Each host implementation slice must receive the same context package, own exactly one host setup profile contract file, report source sections used, changed files, verification commands/manual checks, failures, and blockers, then wait for main-agent changed-file review.

## Phase 1: Design And Contracts

**Output**:

- `specs/006-agent-adapter-setup/data-model.md`
- `specs/006-agent-adapter-setup/contracts/host-setup-profiles/README.md`
- `specs/006-agent-adapter-setup/contracts/host-capability-profile.md`
- `specs/006-agent-adapter-setup/contracts/conformance-kit.md`
- `specs/006-agent-adapter-setup/contracts/subagent-context-package.md`
- `specs/006-agent-adapter-setup/contracts/manual-provider-install-report.md`
- `specs/006-agent-adapter-setup/quickstart.md`
- `AGENTS.md` Speckit plan reference

Design decisions:

- `HostSetupTarget` enumerates only `hermes`, `openclaw`, `claude`, and `codex`; Antigravity is represented only as an explicit exclusion in plan/tasks/reports.
- `HostSetupProfileContract` is a versioned markdown contract stored under `contracts/host-setup-profiles/`. The planning output defines the required schema/template; implementation subagents create `hermes.md`, `openclaw.md`, `claude.md`, and `codex.md`.
- `OfficialSourceEvidence` captures official URL, retrieved date, source sections, facts used, and unsupported assumptions. Source evidence is required for every setup behavior.
- `AdapterCapabilityProfile` declares text support, lifecycle availability, boot trigger, setup entry point, update behavior, optional side-effectful capabilities, and unsupported capabilities.
- `SetupPackage` describes host-owned distribution files and user-owned exclusions. Package verification checks both manifest correctness and privacy exclusions.
- `BootContextTrigger` formalizes hook, explicit command, first-message, and manual/provider-specific boot paths without assuming Claude SessionStart exists.
- `ConformanceRun` records six representative text flow outcomes, capability gates, error behavior, and local data ownership checks for each host.
- `ManualProviderInstallReport` records install, launch, capability check, representative flow verification, update/reload, inspect, remove, and user-data preservation checks.
- `SubagentContextPackage` is required before each host subagent starts. It includes active spec/plan, constitution, roadmap, official source URL, target contract path, shared conformance expectations, verification/reporting requirements, and existing baseline notes.
- Host-specific setup failures use a structured error shape that names host, phase, missing prerequisite/invalid config/unsupported capability, remediation, and data-safety status.

## Post-Design Constitution Check

- **Layered boundaries**: PASS. Design separates host package/profile metadata, adapter capability contracts, lifecycle boot routing, conformance tests, manual verification, and shared tutor core.
- **Contracts and abstractions**: PASS. Data model and contract docs define the Pydantic/JSON/markdown surfaces before implementation. Host-specific packages consume documented CLI/core contracts and do not reach into DAL internals.
- **Deterministic tests**: PASS. Quickstart and contracts identify unit, contract, integration, packaging privacy, host-specific validation, and manual provider gates.
- **Skill creation gate**: PASS. Any Claude/Codex/Hermes package `SKILL.md` change is explicitly assigned to the owning host subagent and gated by the local writing-skills helper plus pressure evidence and main-agent review.
- **Local-first data ownership**: PASS. No host distribution may package user secrets, learner memories, conversation sessions, SQLite state, logs, local overrides, or machine-local config. Existing SQLite/YAML ownership remains unchanged.
- **Scope discipline**: PASS. Design covers only Hermes, OpenClaw, Claude, and Codex setup/verification. Antigravity and non-text/product expansion remain excluded.
- **DRY and composition**: PASS. Shared host/profile/conformance fields are centralized in contracts and schemas. Host adapters compose common boot/capability behavior through Protocols and small helpers.

## Verification Gates

```bash
rtk uv run pytest tests/unit/test_schemas.py tests/unit/test_boot_context.py
rtk uv run pytest tests/adapter_contract/test_host_capability_profile.py tests/adapter_contract/test_lifecycle_contract.py tests/adapter_contract/test_conformance_kit.py
rtk uv run pytest tests/adapter_contract/test_claude_adapter.py tests/adapter_contract/test_codex_adapter.py tests/adapter_contract/test_hermes_adapter.py tests/adapter_contract/test_openclaw_adapter.py
rtk uv run pytest tests/integration/test_host_text_flows.py tests/integration/test_local_data_ownership.py
rtk uv run pytest tests/packaging/test_host_setup_profiles.py tests/packaging/test_distribution_privacy.py tests/packaging/test_claude_plugin_package.py tests/packaging/test_codex_plugin_package.py tests/packaging/test_hermes_profile_distribution.py tests/packaging/test_openclaw_plugin_package.py
rtk uv run pytest tests/golden/test_boot_context.py tests/golden/test_feedback_rendering.py tests/golden/test_progress_rendering.py tests/golden/test_text_modality_rendering.py
rtk uv run pyright
rtk uv run ruff check .
```

Host-specific manual gates:

```bash
rtk hermes profile install <local-hermes-profile-path> --name language-tutor-test --alias
rtk hermes profile info language-tutor-test
rtk hermes profile update language-tutor-test
rtk hermes profile delete language-tutor-test

rtk pnpm test -- <openclaw-plugin-root>
rtk pnpm check
rtk clawhub package publish <org>/<plugin> --dry-run

rtk claude plugin validate <plugin-root> --strict
rtk claude --plugin-dir <plugin-root>
```

Codex manual verification currently has no documented CLI validator in the required source. Implementation must record Codex local marketplace installation, Codex restart/reload, plugin visibility, skill surface exposure, optional hook enablement status, and representative tutor-flow results in `manual-install-reports/codex.md`.

## Complexity Tracking

No constitution violations. No complexity exceptions required.

## Getting Started Instructions

These host quickstarts are the end-of-plan starting point for implementation subagents and manual provider verification. Host package roots are finalized by the owning subagent. Antigravity remains out of scope.

### Hermes

Use the Hermes profile distribution created by the Hermes subagent:

```bash
rtk hermes profile install <local-hermes-profile-path> --name language-tutor-test --alias
rtk hermes profile info language-tutor-test
rtk hermes profile update language-tutor-test
rtk hermes profile delete language-tutor-test
```

Verify `distribution.yaml`, tutor prompt/config/skills, required `env_requires`, install/update/inspect/remove behavior, and preservation of `.env`, memories, sessions, state DBs, logs, caches, and `local/`.

### OpenClaw

Use the OpenClaw plugin package created by the OpenClaw subagent:

```bash
rtk pnpm test -- <openclaw-plugin-root>
rtk pnpm check
rtk clawhub package publish <org>/<plugin> --dry-run
rtk openclaw plugins install <package-name>
```

Verify `package.json`, `openclaw.plugin.json`, TypeScript ESM entry point, focused `openclaw/plugin-sdk/<subpath>` imports, optional side-effectful tools, and user allowlist behavior.

### Claude

Use the existing Claude plugin root, preserving the current baseline:

```bash
rtk claude plugin validate <plugin-root> --strict
rtk claude --plugin-dir <plugin-root>
```

Inside Claude, run `/reload-plugins`, verify tutor skills, agents, hooks, and `bin/tutor`, then run reading, lesson, transcript, vocab, writing, and progress flows.

### Codex

Use the Codex plugin package and local/repo marketplace entry created by the Codex subagent:

1. Verify `.codex-plugin/plugin.json` points to `./skills/` and any intended `.mcp.json`, `.app.json`, or hooks.
2. Add or update the repo or personal marketplace entry.
3. Restart Codex.
4. Install or enable the plugin from the selected marketplace.
5. Verify tutor skills are visible.
6. Keep hooks disabled unless `[features].plugin_hooks = true` is intentionally enabled.
7. Run reading, lesson, transcript, vocab, writing, and progress flows.

Codex has no standalone CLI validator documented in the required source, so record marketplace install, restart/reload, plugin visibility, hook status, and flow results in `specs/006-agent-adapter-setup/manual-install-reports/codex.md`.
