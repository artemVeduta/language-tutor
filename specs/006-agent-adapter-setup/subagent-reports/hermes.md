# Hermes Adapter Subagent Report

## Source

- Official source: `https://github.com/synesthesias/hermes` (approved source for
  `hermes` in `APPROVED_HOST_SOURCES`), retrieved `2026-05-22`.
- Facts taken from the Hermes profile-distribution model captured in
  `specs/006-agent-adapter-setup/research.md` (no live web fetch): git-backed
  whole-agent distributions with `distribution.yaml`, `SOUL.md`, `config.yaml`,
  optional `skills/`/`cron/`/`mcp.json`, `env_requires`/`.env.EXAMPLE`, and the
  `hermes profile install`/`update`/`info`/`list`/`delete` lifecycle with update
  preservation and hard exclusions for secrets and user data.
- Note: research.md cites the docs-site URL for the same facts; this slice uses
  the approved GitHub source URL required by the schema/registry.

## Setup decisions

- Package model: `profile_distribution`.
- Shipped `hermes-profile/distribution.yaml`, `hermes-profile/SOUL.md`, and
  `hermes-profile/config.yaml` as distribution metadata/defaults only.
- Reused the repository root `skills/` surface; did NOT create any SKILL.md or a
  profile-local `skills/`. `cron/` and `mcp.json` intentionally omitted (YAGNI).
- Capability values echoed from `registry.py` (`HostId.HERMES`): text supported,
  audio/image unsupported, lifecycle_start `explicit_command`, lifecycle_end
  `not_available`, boot trigger `explicit_tutor_command`, setup entry point
  `hermes profile install`, update behavior `hermes profile update`.
- Hard exclusions encoded in `distribution.yaml` and the contract's
  `user_owned_boundaries` (secrets, memories, sessions, logs, local, *.sqlite,
  *.db, caches), matching `PRIVACY_EXCLUDED_PATTERNS`.
- No learner-owned data placed in `hermes-profile/`; env values are
  operator-supplied at runtime and never bundled.

## Changed Files

- `hermes-profile/distribution.yaml` (created)
- `hermes-profile/SOUL.md` (created)
- `hermes-profile/config.yaml` (created)
- `specs/006-agent-adapter-setup/contracts/host-setup-profiles/hermes.md` (created)
- `specs/006-agent-adapter-setup/subagent-reports/hermes.md` (created)

No shared files (`schemas.py`, `base.py`, `registry.py`, `tests/**`) edited.

## Verification

- `load_host_setup_profile('.../hermes.md').host` prints `hermes` with no error.
- `pytest tests/packaging/test_hermes_profile_distribution.py
  tests/packaging/test_host_setup_profiles.py` passes.
- See exact command output in the main-agent summary.

## Failures

- None observed during automated verification.

## Blockers

- The `hermes` CLI is NOT installed on this machine, so manual provider install
  verification (`hermes profile install`/`update`/`info`/`delete`) is BLOCKED.
  Profile status remains `blocked` until live install verification is possible.

## Shared-contract conflicts

- None. research.md references the Hermes docs-site URL while the schema/registry
  require the approved GitHub URL; resolved by using the approved GitHub URL in
  the contract. No shared files changed.
