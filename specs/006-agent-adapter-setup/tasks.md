# Tasks: Agent Adapter Setup

**Input**: Design documents from `specs/006-agent-adapter-setup/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Required by the feature specification and constitution. Contract, schema, lifecycle, packaging privacy, conformance, integration, and manual verification tasks appear before implementation tasks in their phase.
**User Context**: Each adapter implementation must spawn one separate sub-agent. Host slices are Hermes, OpenClaw, Claude, and Codex only.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare evidence directories and shared fixtures before contract or host work.

- [X] T001 Create implementation evidence directories in `specs/006-agent-adapter-setup/subagent-reports/` and `specs/006-agent-adapter-setup/manual-install-reports/`
- [X] T002 [P] Create host setup profile target directory placeholders in `specs/006-agent-adapter-setup/contracts/host-setup-profiles/`
- [X] T003 [P] Create adapter contract test file placeholders in `tests/adapter_contract/test_host_capability_profile.py`, `tests/adapter_contract/test_lifecycle_contract.py`, and `tests/adapter_contract/test_conformance_kit.py`
- [X] T004 [P] Create packaging test file placeholders in `tests/packaging/test_host_setup_profiles.py`, `tests/packaging/test_distribution_privacy.py`, `tests/packaging/test_claude_plugin_package.py`, `tests/packaging/test_codex_plugin_package.py`, `tests/packaging/test_hermes_profile_distribution.py`, and `tests/packaging/test_openclaw_plugin_package.py`
- [X] T005 [P] Create host adapter test file placeholders in `tests/adapter_contract/test_claude_adapter.py`, `tests/adapter_contract/test_codex_adapter.py`, `tests/adapter_contract/test_hermes_adapter.py`, and `tests/adapter_contract/test_openclaw_adapter.py`
- [X] T006 [P] Create shared integration test placeholders in `tests/integration/test_host_text_flows.py` and `tests/integration/test_local_data_ownership.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, schemas, and lifecycle abstractions that every story depends on.

**Critical**: No user story work starts until this phase is complete.

- [X] T007 [P] Add failing schema tests for `HostSetupTarget`, `OfficialSourceEvidence`, `HostSetupProfileContract`, `AdapterCapabilityProfile`, `BootContextTrigger`, `SetupPackage`, `ConformanceRun`, `ManualProviderInstallReport`, and `HostSetupFailure` in `tests/unit/test_schemas.py`
- [X] T008 [P] Add failing lifecycle contract tests for hook, explicit command, first-message, manual, and not-available triggers in `tests/adapter_contract/test_lifecycle_contract.py`
- [X] T009 [P] Add failing host capability profile contract tests for text support, lifecycle alternatives, flow gates, and Antigravity rejection in `tests/adapter_contract/test_host_capability_profile.py`
- [X] T010 [P] Add failing conformance kit contract tests for reading, lesson, transcript, vocab, writing, progress, error behavior, and data ownership results in `tests/adapter_contract/test_conformance_kit.py`
- [X] T011 [P] Add failing packaging privacy tests for excluded secrets, memories, sessions, SQLite files, logs, caches, local overrides, and machine-local config in `tests/packaging/test_distribution_privacy.py`
- [X] T012 Implement host setup, source evidence, capability, lifecycle, package, conformance, manual report, and setup failure Pydantic models in `src/language_tutor/schemas.py`
- [X] T013 Export JSON schema mirrors for host capability, host setup profile, lifecycle trigger, conformance run, and manual provider install report in `schemas/host_capability_profile.schema.json`, `schemas/host_setup_profile.schema.json`, `schemas/lifecycle_trigger.schema.json`, `schemas/conformance_run.schema.json`, and `schemas/manual_provider_install_report.schema.json`
- [X] T014 Update schema export mapping for host adapter contracts in `src/language_tutor/schemas.py`
- [X] T015 Define narrow host capability, lifecycle trigger, setup package, conformance runner, and manual report Protocols in `src/language_tutor/adapters/base.py`
- [X] T016 Add host setup failure rendering and learner-safe remediation helpers in `src/language_tutor/errors.py`
- [X] T017 Add deterministic boot trigger selection helper for hook and non-hook hosts in `src/language_tutor/boot_context.py`
- [X] T018 Add CLI JSON command group for host capability, boot trigger, setup profile, and conformance checks in `src/language_tutor/cli.py`
- [X] T019 Update project build include paths for `.codex-plugin/`, `openclaw-plugin/`, `hermes-profile/`, `.agents/plugins/`, and new schemas in `pyproject.toml`
- [X] T020 Run foundational contract gates `rtk uv run pytest tests/unit/test_schemas.py tests/adapter_contract/test_host_capability_profile.py tests/adapter_contract/test_lifecycle_contract.py tests/adapter_contract/test_conformance_kit.py tests/packaging/test_distribution_privacy.py` from `/Users/artem.veduta/python/language-tutor`

**Checkpoint**: Foundation ready. User story implementation can now start.

---

## Phase 3: User Story 1 - Source-Backed Host Setup Scope (Priority: P1)

**Goal**: Hermes, OpenClaw, Claude, and Codex are the only setup targets, with source-backed profile contracts and no Antigravity deliverables.

**Independent Test**: Review contract validation and generated host target registry; confirm four supported hosts, official URLs, profile paths, verification expectations, and Antigravity rejection.

### Tests for User Story 1

- [X] T021 [P] [US1] Add failing tests that only `hermes`, `openclaw`, `claude`, and `codex` are accepted setup targets in `tests/unit/test_schemas.py`
- [X] T022 [P] [US1] Add failing tests that every host setup profile requires official source evidence, package model, install/update/inspect/remove flows, and user-owned boundaries in `tests/packaging/test_host_setup_profiles.py`
- [X] T023 [P] [US1] Add failing tests that Antigravity files, adapters, docs, reports, or setup profiles are rejected in `tests/packaging/test_host_setup_profiles.py`
- [X] T024 [P] [US1] Add failing tests that host setup profile contracts cite one approved official source URL per host in `tests/packaging/test_host_setup_profiles.py`

### Implementation for User Story 1

- [X] T025 [US1] Implement supported host target registry with approved official URLs and contract paths in `src/language_tutor/adapters/base.py`
- [X] T026 [US1] Implement source evidence validation rules for host setup profile contracts in `src/language_tutor/schemas.py`
- [X] T027 [US1] Implement host setup profile contract validation loader for markdown files in `src/language_tutor/adapters/base.py`
- [X] T028 [US1] Update host setup profile README acceptance notes to require sub-agent ownership for each host file in `specs/006-agent-adapter-setup/contracts/host-setup-profiles/README.md`
- [X] T029 [US1] Update quickstart source-scope validation steps and Antigravity exclusion check in `specs/006-agent-adapter-setup/quickstart.md`
- [X] T030 [US1] Run US1 gates `rtk uv run pytest tests/unit/test_schemas.py tests/packaging/test_host_setup_profiles.py` from `/Users/artem.veduta/python/language-tutor`

**Checkpoint**: User Story 1 independently validates supported setup scope.

---

## Phase 4: User Story 2 - Independent Per-Host Implementation Slices (Priority: P1)

**Goal**: Each supported host implementation is owned by exactly one primary sub-agent after the main maintainer provides the full context package.

**Independent Test**: Inspect sub-agent reports and changed-file lists; confirm one owner per host, source sections used, setup decisions, verification evidence, and main-agent review status.

### Tests for User Story 2

- [X] T031 [P] [US2] Add failing tests for required sub-agent context package fields and report paths in `tests/adapter_contract/test_conformance_kit.py`
- [X] T032 [P] [US2] Add failing tests that each host has exactly one primary sub-agent owner and one report file in `tests/packaging/test_host_setup_profiles.py`
- [X] T033 [P] [US2] Add failing tests that sub-agent changed-file reports cannot include Antigravity paths or unreviewed shared-contract conflicts in `tests/packaging/test_host_setup_profiles.py`
- [X] T034 [P] [US2] Add failing Claude package regression tests for existing `.claude-plugin/plugin.json`, `skills/`, `hooks/`, `agents/`, and `bin/tutor` components in `tests/packaging/test_claude_plugin_package.py`
- [X] T035 [P] [US2] Add failing Codex plugin package tests for `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, root `skills/`, optional hooks policy, and cache-safe metadata in `tests/packaging/test_codex_plugin_package.py`
- [X] T036 [P] [US2] Add failing Hermes profile distribution tests for `hermes-profile/distribution.yaml`, `hermes-profile/SOUL.md`, `hermes-profile/config.yaml`, optional `hermes-profile/skills/`, and privacy exclusions in `tests/packaging/test_hermes_profile_distribution.py`
- [X] T037 [P] [US2] Add failing OpenClaw package tests for `openclaw-plugin/package.json`, `openclaw-plugin/openclaw.plugin.json`, TypeScript ESM entry point, focused SDK imports, and optional side-effectful tool flags in `tests/packaging/test_openclaw_plugin_package.py`

### Implementation for User Story 2

- [X] T038 [P] [US2] Create Hermes sub-agent context package in `specs/006-agent-adapter-setup/subagent-reports/hermes-context.md`
- [X] T039 [P] [US2] Create OpenClaw sub-agent context package in `specs/006-agent-adapter-setup/subagent-reports/openclaw-context.md`
- [X] T040 [P] [US2] Create Claude sub-agent context package in `specs/006-agent-adapter-setup/subagent-reports/claude-context.md`
- [X] T041 [P] [US2] Create Codex sub-agent context package in `specs/006-agent-adapter-setup/subagent-reports/codex-context.md`
- [X] T042 [P] [US2] Spawn Hermes sub-agent to create `specs/006-agent-adapter-setup/contracts/host-setup-profiles/hermes.md`, `hermes-profile/distribution.yaml`, `hermes-profile/SOUL.md`, `hermes-profile/config.yaml`, optional `hermes-profile/skills/`, and `specs/006-agent-adapter-setup/subagent-reports/hermes.md`
- [X] T043 [P] [US2] Spawn OpenClaw sub-agent to create `specs/006-agent-adapter-setup/contracts/host-setup-profiles/openclaw.md`, `openclaw-plugin/package.json`, `openclaw-plugin/openclaw.plugin.json`, `openclaw-plugin/src/index.ts`, and `specs/006-agent-adapter-setup/subagent-reports/openclaw.md`
- [X] T044 [P] [US2] Spawn Claude sub-agent to update or verify `specs/006-agent-adapter-setup/contracts/host-setup-profiles/claude.md`, `.claude-plugin/plugin.json`, `hooks/hooks.json`, `skills/`, `agents/tutor-judge.md`, `bin/tutor`, and `specs/006-agent-adapter-setup/subagent-reports/claude.md`
- [X] T045 [P] [US2] Spawn Codex sub-agent to create `specs/006-agent-adapter-setup/contracts/host-setup-profiles/codex.md`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, optional `.app.json`, optional `.mcp.json`, optional `hooks/`, and `specs/006-agent-adapter-setup/subagent-reports/codex.md`
- [X] T046 [US2] Implement Hermes adapter capability translation if runtime behavior differs from package-only setup in `src/language_tutor/adapters/hermes.py`
- [X] T047 [US2] Implement OpenClaw adapter capability translation if runtime behavior differs from package-only setup in `src/language_tutor/adapters/openclaw.py`
- [X] T048 [US2] Implement Claude adapter capability translation while preserving existing baseline in `src/language_tutor/adapters/claude.py`
- [X] T049 [US2] Implement Codex adapter capability translation if runtime behavior differs from package-only setup in `src/language_tutor/adapters/codex.py`
- [X] T050 [US2] Review every sub-agent reported changed file and record pass/fail decisions in `specs/006-agent-adapter-setup/subagent-reports/main-agent-review.md`
- [X] T051 [US2] Verify any sub-agent `SKILL.md` creation or edit includes local writing-skills helper evidence in `specs/006-agent-adapter-setup/subagent-reports/main-agent-review.md`
- [X] T052 [US2] Run US2 gates `rtk uv run pytest tests/packaging/test_claude_plugin_package.py tests/packaging/test_codex_plugin_package.py tests/packaging/test_hermes_profile_distribution.py tests/packaging/test_openclaw_plugin_package.py tests/packaging/test_host_setup_profiles.py` from `/Users/artem.veduta/python/language-tutor`

**Checkpoint**: User Story 2 independently proves per-host sub-agent ownership and package/profile outputs.

---

## Phase 5: User Story 3 - Manual Provider Install And Update Verification (Priority: P2)

**Goal**: Manual provider install reports prove each host can install, launch, inspect, update or reload, remove where supported, and preserve user-owned data.

**Independent Test**: Manually run each host verification path and inspect `manual-install-reports/*.md` for install, launch, capability, six text flows, update/reload, inspect, remove, data preservation, blockers, and decision.

### Tests for User Story 3

- [X] T053 [P] [US3] Add failing tests for manual provider install report required sections and decision values in `tests/packaging/test_host_setup_profiles.py`
- [X] T054 [P] [US3] Add failing tests that manual reports include all six representative text flows and capability-gated skip explanations in `tests/adapter_contract/test_conformance_kit.py`
- [X] T055 [P] [US3] Add failing tests that install/update/remove evidence preserves user-owned data paths in `tests/integration/test_local_data_ownership.py`

### Implementation for User Story 3

- [X] T056 [P] [US3] Create Hermes manual install report template and evidence file in `specs/006-agent-adapter-setup/manual-install-reports/hermes.md`
- [X] T057 [P] [US3] Create OpenClaw manual install report template and evidence file in `specs/006-agent-adapter-setup/manual-install-reports/openclaw.md`
- [X] T058 [P] [US3] Create Claude manual install report template and evidence file in `specs/006-agent-adapter-setup/manual-install-reports/claude.md`
- [X] T059 [P] [US3] Create Codex manual install report template and evidence file in `specs/006-agent-adapter-setup/manual-install-reports/codex.md`
- [X] T060 [P] [US3] Run and record Hermes manual commands `rtk hermes profile install`, `rtk hermes profile info`, `rtk hermes profile update`, and `rtk hermes profile delete` in `specs/006-agent-adapter-setup/manual-install-reports/hermes.md`
- [X] T061 [P] [US3] Run and record OpenClaw manual commands `rtk pnpm test -- <openclaw-plugin-root>`, `rtk pnpm check`, and `rtk clawhub package publish <org>/<plugin> --dry-run` in `specs/006-agent-adapter-setup/manual-install-reports/openclaw.md`
- [X] T062 [P] [US3] Run and record Claude manual commands `rtk claude plugin validate <plugin-root> --strict`, `rtk claude --plugin-dir <plugin-root>`, and `/reload-plugins` in `specs/006-agent-adapter-setup/manual-install-reports/claude.md`
- [X] T063 [P] [US3] Run and record Codex local marketplace install, Codex restart or reload, plugin visibility, skill exposure, and hook policy checks in `specs/006-agent-adapter-setup/manual-install-reports/codex.md`
- [X] T064 [US3] Run US3 gates `rtk uv run pytest tests/packaging/test_host_setup_profiles.py tests/adapter_contract/test_conformance_kit.py tests/integration/test_local_data_ownership.py` from `/Users/artem.veduta/python/language-tutor`

**Checkpoint**: User Story 3 independently proves manual install and update verification evidence.

---

## Phase 6: User Story 4 - Host-Portable Tutor Behavior (Priority: P2)

**Goal**: Every supported text-capable host uses the same tutor contracts for capability reporting, boot context, feedback, progress, setup errors, and local data ownership.

**Independent Test**: Run the shared conformance kit for Hermes, OpenClaw, Claude, and Codex against reading, lesson, transcript, vocab, writing, and progress flows.

### Tests for User Story 4

- [X] T065 [P] [US4] Add failing adapter tests for Claude capability, lifecycle, package surface, and baseline preservation in `tests/adapter_contract/test_claude_adapter.py`
- [X] T066 [P] [US4] Add failing adapter tests for Codex capability, lifecycle, package surface, and hook-disabled behavior in `tests/adapter_contract/test_codex_adapter.py`
- [X] T067 [P] [US4] Add failing adapter tests for Hermes capability, lifecycle, profile setup, and explicit boot trigger behavior in `tests/adapter_contract/test_hermes_adapter.py`
- [X] T068 [P] [US4] Add failing adapter tests for OpenClaw capability, lifecycle, package setup, and optional side-effectful tool behavior in `tests/adapter_contract/test_openclaw_adapter.py`
- [X] T069 [P] [US4] Add failing host text flow integration tests for reading, lesson, transcript, vocab, writing, and progress across all included hosts in `tests/integration/test_host_text_flows.py`
- [X] T070 [P] [US4] Add failing setup error behavior tests for missing prerequisite, invalid configuration, permission required, unsupported capability, source changed, and unknown categories in `tests/adapter_contract/test_conformance_kit.py`

### Implementation for User Story 4

- [X] T071 [US4] Implement shared conformance runner for capability, boot context, text flows, error behavior, and data ownership in `src/language_tutor/adapters/base.py`
- [X] T072 [US4] Implement host capability profile defaults for Hermes, OpenClaw, Claude, and Codex in `src/language_tutor/adapters/hermes.py`, `src/language_tutor/adapters/openclaw.py`, `src/language_tutor/adapters/claude.py`, and `src/language_tutor/adapters/codex.py`
- [X] T073 [US4] Wire non-hook boot context triggers into CLI and core without changing pedagogy or DAL ownership in `src/language_tutor/cli.py` and `src/language_tutor/boot_context.py`
- [X] T074 [US4] Implement host-specific setup error messages with data-safety status in `src/language_tutor/errors.py`
- [X] T075 [US4] Update local data ownership integration coverage for host packages and runtime state writes in `tests/integration/test_local_data_ownership.py`
- [X] T076 [US4] Run US4 gates `rtk uv run pytest tests/adapter_contract/test_claude_adapter.py tests/adapter_contract/test_codex_adapter.py tests/adapter_contract/test_hermes_adapter.py tests/adapter_contract/test_openclaw_adapter.py tests/integration/test_host_text_flows.py tests/integration/test_local_data_ownership.py` from `/Users/artem.veduta/python/language-tutor`

**Checkpoint**: User Story 4 independently proves host-portable tutor behavior.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final review, docs sync, privacy hardening, and full verification.

- [X] T077 [P] Update architecture and feature documentation for host capability, adapter setup, and manual verification in `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, `docs/PITFALLS.md`, `docs/PROJECT.md`, `docs/REQUIREMENTS.md`, `docs/ROADMAP.md`, `docs/STACK.md`, and `docs/SUMMARY.md`
- [X] T078 [P] Update README host setup summary and Antigravity exclusion notes in `README.md`
- [X] T079 [P] Run Antigravity implementation-artifact scan `rtk rg -n "antigravity|Antigravity" src schemas .claude-plugin .codex-plugin hermes-profile openclaw-plugin .agents/plugins specs/006-agent-adapter-setup/contracts/host-setup-profiles specs/006-agent-adapter-setup/manual-install-reports specs/006-agent-adapter-setup/subagent-reports` from `/Users/artem.veduta/python/language-tutor`
- [X] T080 [P] Run package privacy scan for `.env`, SQLite, logs, caches, local overrides, memories, sessions, and machine-local config in `tests/packaging/test_distribution_privacy.py`
- [X] T081 [P] Run schema and contract verification `rtk uv run pytest tests/unit/test_schemas.py tests/adapter_contract/test_host_capability_profile.py tests/adapter_contract/test_lifecycle_contract.py tests/adapter_contract/test_conformance_kit.py` from `/Users/artem.veduta/python/language-tutor`
- [X] T082 [P] Run packaging verification `rtk uv run pytest tests/packaging/test_host_setup_profiles.py tests/packaging/test_distribution_privacy.py tests/packaging/test_claude_plugin_package.py tests/packaging/test_codex_plugin_package.py tests/packaging/test_hermes_profile_distribution.py tests/packaging/test_openclaw_plugin_package.py` from `/Users/artem.veduta/python/language-tutor`
- [X] T083 [P] Run Phase 5 regression gates `rtk uv run pytest tests/golden/test_boot_context.py tests/golden/test_feedback_rendering.py tests/golden/test_progress_rendering.py tests/golden/test_text_modality_rendering.py tests/integration/test_text_modality_flow.py` from `/Users/artem.veduta/python/language-tutor`
- [X] T084 Run full automated gate `rtk uv run pytest` from `/Users/artem.veduta/python/language-tutor`
- [X] T085 Run static type gate `rtk uv run pyright` from `/Users/artem.veduta/python/language-tutor`
- [X] T086 Run lint gate `rtk uv run ruff check .` from `/Users/artem.veduta/python/language-tutor`
- [X] T087 Record final dogfood report for Hermes, OpenClaw, Claude, and Codex tutor launch plus six representative text flows in `specs/006-agent-adapter-setup/manual-install-reports/dogfood.md`

---

## Dependencies & Execution Order

### Phase Dependencies

Setup has no dependencies.
Foundational depends on Setup completion and blocks all user stories.
US1 and US2 are both P1 and depend on Foundational.
US3 depends on host package/profile outputs from US2.
US4 depends on Foundational and can start after host capability defaults exist, but final completion depends on US2 and US3 evidence.
Polish depends on all selected user stories.

### User Story Dependencies

US1 can start after Foundational and has no dependency on other stories.
US2 can start after Foundational and must spawn exactly one sub-agent per host.
US3 starts after US2 creates installable host package/profile/plugin outputs.
US4 starts after Foundational, then integrates US2 host outputs and US3 manual report gates before readiness.

### Within Each User Story

Tests are written first and must fail before implementation.
Context packages are prepared before any host sub-agent starts.
Each host sub-agent owns exactly one host setup profile contract.
Host package/profile files are created before manual install reports.
Capability profiles are declared before representative tutor flows run.
Main-agent changed-file review completes before readiness.
Any `SKILL.md` change requires sub-agent pressure evidence and local writing-skills helper use before acceptance.

---

## Parallel Opportunities

Phase 1 placeholders marked `[P]` can run in parallel.
Foundational tests T007 through T011 can run in parallel before T012 through T019.
US1 tests T021 through T024 can run in parallel.
US2 tests T031 through T037 can run in parallel.
US2 context packages T038 through T041 can run in parallel.
US2 adapter sub-agent tasks T042 through T045 must run as four separate sub-agents and can run in parallel after their context packages exist.
US3 manual report templates T056 through T059 can run in parallel.
US3 manual provider checks T060 through T063 can run in parallel if host tools and accounts are available.
US4 adapter tests T065 through T068 can run in parallel.
Polish verification tasks T077 through T083 can run in parallel before full gates T084 through T086.

---

## Parallel Example: User Story 2

```bash
# Main maintainer prepares one context package per host:
Task: "T038 Create Hermes sub-agent context package in specs/006-agent-adapter-setup/subagent-reports/hermes-context.md"
Task: "T039 Create OpenClaw sub-agent context package in specs/006-agent-adapter-setup/subagent-reports/openclaw-context.md"
Task: "T040 Create Claude sub-agent context package in specs/006-agent-adapter-setup/subagent-reports/claude-context.md"
Task: "T041 Create Codex sub-agent context package in specs/006-agent-adapter-setup/subagent-reports/codex-context.md"

# Then spawn one independent sub-agent per adapter:
Task: "T042 Spawn Hermes sub-agent..."
Task: "T043 Spawn OpenClaw sub-agent..."
Task: "T044 Spawn Claude sub-agent..."
Task: "T045 Spawn Codex sub-agent..."
```

## Parallel Example: User Story 4

```bash
Task: "T065 Add failing adapter tests for Claude capability..."
Task: "T066 Add failing adapter tests for Codex capability..."
Task: "T067 Add failing adapter tests for Hermes capability..."
Task: "T068 Add failing adapter tests for OpenClaw capability..."
```

---

## Implementation Strategy

### MVP First

Complete Phase 1, Phase 2, and Phase 3. Validate that supported setup scope is correct, source-backed, and excludes Antigravity before host implementation begins.

### Adapter Slice Delivery

After the MVP, complete Phase 4 by spawning four separate sub-agents: Hermes, OpenClaw, Claude, and Codex. Each sub-agent receives its context package, owns one profile contract, reports changed files, and returns verification evidence.

### Verification Delivery

Complete Phase 5 manual provider install reports, then Phase 6 shared conformance. Stop before readiness if any representative flow fails without a documented capability gate in both capability profile and manual install report.

### Final Gate

Run package privacy, Antigravity implementation-artifact scan, full pytest, pyright, ruff, manual provider reports, main-agent changed-file review, and dogfood report before marking the feature ready.
