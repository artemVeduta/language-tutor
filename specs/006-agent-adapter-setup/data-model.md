# Data Model: Agent Adapter Setup

## HostSetupTarget

One supported host setup target.

**Fields**:

- `id`: `hermes`, `openclaw`, `claude`, or `codex`.
- `display_name`: human-readable host name.
- `official_source_url`: official setup documentation URL.
- `setup_model`: `profile_distribution`, `plugin_package`, or `local_marketplace_plugin`.
- `primary_subagent`: implementation subagent assigned to this host.
- `contract_path`: `specs/006-agent-adapter-setup/contracts/host-setup-profiles/<host>.md`.
- `status`: `planned`, `in_progress`, `blocked`, `verified`, or `skipped`.

**Validation rules**:

- Antigravity is not a valid target.
- Every included target has exactly one primary subagent during implementation.
- Official source URL is required and must be one of the approved host docs.

## OfficialSourceEvidence

Source-backed fact record used by a host setup profile.

**Fields**:

- `source_url`: official documentation URL.
- `retrieved_on`: date the source was checked.
- `source_sections`: headings, anchors, or concise section labels.
- `facts_used`: setup facts copied into the host setup profile.
- `unsupported_assumptions`: proposed behaviors rejected because the source does not support them.
- `source_risk`: `stable`, `changed`, `unreachable`, or `ambiguous`.

**Validation rules**:

- Required for every host setup profile.
- If `source_risk` is `changed`, `unreachable`, or `ambiguous`, implementation records the blocker or mitigation before tasks proceed.

## HostSetupProfileContract

Versioned contract file under `contracts/host-setup-profiles/`.

**Fields**:

- `host`: `HostSetupTarget.id`.
- `schema_version`: integer, starting at `1`.
- `official_sources`: list of `OfficialSourceEvidence`.
- `package_model`: host-specific distribution/package model.
- `package_files`: files and directories owned by the host package.
- `prerequisites`: host software, versions, package managers, and external commands.
- `install_flow`: documented install steps.
- `launch_flow`: documented launch or invocation steps.
- `inspect_flow`: documented inspection/status steps.
- `update_or_reload_flow`: documented update/reload steps.
- `remove_flow`: documented remove/cleanup steps where supported.
- `required_user_values`: secrets, env vars, config values, or local approvals the user must provide.
- `user_owned_boundaries`: files and data that must not be packaged or overwritten.
- `capability_profile_path`: planned or generated capability profile path.
- `verification_expectations`: automated and manual checks for the host.
- `known_limitations`: capability gates or source-backed setup gaps.

**Validation rules**:

- One contract file per included host.
- Every setup behavior must cite official source evidence or be marked out of scope.
- User-owned data exclusions are mandatory.

## AdapterCapabilityProfile

Host declaration used before tutor flows depend on host behavior.

**Fields**:

- `host`: `HostSetupTarget.id`.
- `text_support`: `supported`, `unsupported`, or `partial`.
- `audio_support`: `unsupported` for this feature.
- `image_support`: `unsupported` for this feature.
- `lifecycle_start`: `hook`, `explicit_command`, `first_message`, or `manual`.
- `lifecycle_end`: `hook`, `explicit_command`, `not_available`, or `manual`.
- `boot_context_trigger`: `session_start_hook`, `codex_plugin_hook`, `explicit_tutor_command`, `first_tutor_message`, or `host_specific`.
- `setup_entry_point`: package/profile/install entry point.
- `update_behavior`: host-specific update or reload behavior.
- `side_effectful_capabilities`: list of tools/hooks requiring opt-in approval.
- `unsupported_capabilities`: list of gated features.

**Validation rules**:

- Audio and image remain unsupported in spec 006.
- A host with no hook lifecycle must declare an alternate boot context trigger.
- Unsupported capabilities must gate affected flows before execution.

## BootContextTrigger

Lifecycle path that builds or reloads deterministic boot context.

**Fields**:

- `trigger_type`: `hook`, `explicit_command`, `first_message`, or `manual`.
- `host_event_name`: host event name if any.
- `command`: tutor CLI command or host command if explicit.
- `input_contract`: JSON/input shape consumed by the trigger.
- `output_contract`: validated boot context or host setup error.
- `fallback`: allowed fallback trigger if primary is unavailable.

**Validation rules**:

- Core boot context rendering remains host-blind.
- Trigger code cannot write learner state except through existing lifecycle/core contracts.

## SetupPackage

Host-owned distribution artifact.

**Fields**:

- `host`: `HostSetupTarget.id`.
- `root_path`: project-relative package/profile root.
- `manifest_paths`: host manifest files.
- `skill_paths`: bundled skill folders if any.
- `hook_paths`: bundled hook files if any.
- `binary_paths`: `bin/` or host tool entry points.
- `config_defaults`: distributable defaults only.
- `excluded_paths`: user-owned path patterns that must not be packaged.
- `verification_command`: package validation or manual verification command.

**Validation rules**:

- Excluded paths include secrets, memories, sessions, SQLite state, logs, local overrides, and machine-local config.
- Package code must call tutor CLI/core contracts, not DAL internals.

## SubagentContextPackage

Main-maintainer handoff before a host subagent starts implementation.

**Fields**:

- `host`: target host.
- `active_spec`: `specs/006-agent-adapter-setup/spec.md`.
- `active_plan`: `specs/006-agent-adapter-setup/plan.md`.
- `constitution`: `.specify/memory/constitution.md`.
- `roadmap`: `docs/ROADMAP.md`.
- `official_source_url`: host source URL.
- `host_contract_path`: expected host setup profile contract path.
- `conformance_contract`: `contracts/conformance-kit.md`.
- `verification_requirements`: automated and manual gates.
- `baseline_notes`: existing Claude baseline or shared host-capability notes.
- `report_path`: expected subagent report path.

**Validation rules**:

- Required before implementation starts for each host.
- Missing context package blocks that host slice.

## SubagentImplementationSlice

One independent host implementation assignment.

**Fields**:

- `host`: target host.
- `owner_agent`: assigned subagent identity.
- `allowed_write_scope`: host-specific package/profile files plus agreed shared contract files.
- `created_profile_contract`: host setup profile path.
- `source_sections_used`: official source sections used.
- `setup_decisions`: source-backed decisions.
- `changed_files_reported`: paths changed by the subagent.
- `verification_performed`: commands or manual checks run.
- `failures`: observed failures.
- `blockers`: unresolved blockers.
- `main_agent_review_status`: `pending`, `passed`, or `failed`.

**Validation rules**:

- Subagent cannot mark work ready until changed files are reported.
- Main agent must review every reported changed file.
- Shared contract conflicts must be resolved centrally.

## ConformanceRun

Shared host-portability verification result.

**Fields**:

- `host`: target host.
- `capability_profile`: capability declaration used.
- `flows`: results for `reading`, `lesson`, `transcript`, `vocab`, `writing`, and `progress`.
- `boot_context_result`: lifecycle/boot verification.
- `feedback_contract_result`: validated `FeedbackEnvelope` behavior.
- `progress_contract_result`: aggregate progress behavior.
- `error_behavior_result`: host-specific setup error behavior.
- `data_ownership_result`: local state and package privacy checks.
- `skipped_flows`: capability-gated skips with rationale.
- `decision`: `pass`, `fail`, or `blocked`.

**Validation rules**:

- All six flows must pass unless skipped through a documented capability gate.
- Any skipped representative flow requires a capability profile limitation and manual install report entry.

## ManualProviderInstallReport

Human-run install/update evidence for one host.

**Fields**:

- `host`: target host.
- `performed_on`: date.
- `host_version`: host version if available.
- `package_ref`: local path, marketplace entry, git URL, or package name tested.
- `install_result`: pass/fail plus evidence.
- `launch_result`: pass/fail plus evidence.
- `capability_check_result`: pass/fail plus declared profile.
- `representative_flow_results`: six Phase 5 text flow results.
- `update_or_reload_result`: pass/fail plus evidence.
- `inspect_result`: pass/fail plus evidence.
- `remove_result`: pass/fail or not applicable.
- `user_data_preservation`: pass/fail plus checked paths.
- `blockers`: unresolved issues.

**Validation rules**:

- Required before feature readiness.
- Readiness is blocked if any representative flow fails without documented capability gating.

## HostSetupFailure

Learner-visible setup failure contract.

**Fields**:

- `host`: target host.
- `phase`: `install`, `launch`, `capability_check`, `boot`, `flow`, `update`, `inspect`, or `remove`.
- `category`: `missing_prerequisite`, `invalid_configuration`, `unsupported_capability`, `permission_required`, `source_changed`, or `unknown`.
- `message`: actionable learner-facing message.
- `remediation`: concrete next step.
- `data_safety`: confirms no learner data was modified or names affected paths.

**Validation rules**:

- Error messages name the host and failed prerequisite/config/capability.
- Failures cannot expose secrets, raw learner answers, or local state contents.
