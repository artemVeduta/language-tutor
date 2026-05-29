## ADDED Requirements

### Requirement: Provider install smoke MUST run through one maintainer executable

The repository MUST provide one maintainer executable that runs provider installation smoke checks for supported hosts. By default, the executable MUST run Claude, Codex, Hermes, and OpenClaw in a deterministic order. It MUST also allow a maintainer to run one provider at a time with `--provider <host>`.

The executable MUST run against an isolated temporary environment, not the maintainer's real host configuration. It MUST create a fake `HOME`, force relevant local state paths into that environment, install the current package into a clean package environment, run provider-specific `tutor init` commands, run `tutor doctor --json`, check each provider's managed files, and verify that a sentinel secret does not leak into reports, logs, or files written under fake `HOME`.

The executable MUST delete the temporary workdir after a fully successful run unless `--keep-workdir` is set. It MUST keep the workdir after any failure and print the retained path.

#### Scenario: Maintainer runs all provider smoke checks

- **WHEN** a maintainer runs `scripts/provider-smoke.sh`
- **THEN** the executable runs smoke checks for `claude`, `codex`, `hermes`, and `openclaw`
- **AND** each provider check uses a fake `HOME` under a temporary workdir
- **AND** each provider check runs `tutor init --provider <host> --yes --json`
- **AND** each provider check runs `tutor init --provider <host> --dry-run --json`
- **AND** the executable runs `tutor doctor --json`
- **AND** the executable writes a per-provider JSON report
- **AND** the executable exits zero only if every selected provider report has decision `pass`

#### Scenario: Maintainer runs one provider smoke check

- **WHEN** a maintainer runs `scripts/provider-smoke.sh --provider codex`
- **THEN** only the Codex provider smoke sequence runs
- **AND** no Claude, Hermes, or OpenClaw managed files are required for the decision

#### Scenario: Successful run purges temporary workdir

- **GIVEN** all selected provider smoke checks pass
- **AND** `--keep-workdir` is not set
- **WHEN** the executable exits
- **THEN** the temporary workdir is deleted

#### Scenario: Failed run preserves temporary workdir

- **GIVEN** at least one selected provider smoke check fails
- **WHEN** the executable exits
- **THEN** the temporary workdir remains on disk
- **AND** stdout or stderr prints the retained workdir path
- **AND** the provider report and command logs are available under that workdir

#### Scenario: Keep-workdir preserves successful run artifacts

- **GIVEN** all selected provider smoke checks pass
- **WHEN** a maintainer runs `scripts/provider-smoke.sh --keep-workdir`
- **THEN** the temporary workdir remains on disk
- **AND** stdout prints the retained workdir path

#### Scenario: Host CLI checks are best-effort

- **GIVEN** a provider's host CLI is not installed on the maintainer laptop
- **WHEN** the provider smoke sequence runs
- **THEN** the report records host CLI validation as `skipped` with reason `missing_cli`
- **AND** the missing host CLI alone does not fail the provider install smoke decision when package install, `tutor init`, `tutor doctor`, managed-file checks, and secret-leak checks pass

#### Scenario: Sentinel secret never leaks

- **GIVEN** the executable sets a sentinel secret in the environment
- **WHEN** selected provider smoke checks complete
- **THEN** the sentinel value is absent from all provider reports
- **AND** the sentinel value is absent from command logs
- **AND** the sentinel value is absent from files written under fake `HOME`
