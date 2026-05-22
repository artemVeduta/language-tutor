# Host Setup Profile: Hermes

**Host ID**: `hermes`
**Schema Version**: `1`
**Owner Subagent**: `hermes-adapter-subagent`
**Official Source Checked**: `2026-05-22`
**Status**: `blocked`

## Official Sources

- URL: `https://github.com/synesthesias/hermes`
- Retrieved date: `2026-05-22`
- Source sections used: Profile distributions; `distribution.yaml` manifest;
  profile prompt (`SOUL.md`) and `config.yaml`; `env_requires` / `.env.EXAMPLE`;
  `hermes profile install`/`update`/`info`/`list`/`delete`; update preservation
  and hard exclusions.
- Facts copied into this profile:
  - Hermes profiles are git-backed whole-agent distributions described by a
    `distribution.yaml` manifest plus a `SOUL.md` prompt and a `config.yaml`.
  - Optional `skills/`, `cron/`, and `mcp.json` are supported; this profile
    reuses the repository root `skills/` surface instead of shipping its own.
  - Install/update/inspect/remove use `hermes profile install`,
    `hermes profile update`, `hermes profile info` / `hermes profile list`, and
    `hermes profile delete`.
  - `env_requires` declares required env vars; secrets stay in the operator's
    own `.env` (documented via `.env.EXAMPLE`) and are never bundled.
  - Updates preserve operator-owned local state; the distribution hard-excludes
    secrets, auth, memories, sessions, state DBs, logs, workspaces, caches, and
    `local/`.
- Unsupported assumptions rejected: no SessionStart/SessionEnd hooks were
  assumed (Hermes uses an explicit tutor command for boot); no audio/image
  capability assumed.
- Ambiguities or blockers: the `hermes` CLI is not installed on the
  implementation machine, so live install/update verification is blocked
  (see Verification Expectations and the subagent report Blockers).

## Package Model

Hermes uses the **profile distribution** model: a git-backed, whole-agent
package. The implementation follows it with `hermes-profile/distribution.yaml`
(manifest), `hermes-profile/SOUL.md` (profile prompt), and
`hermes-profile/config.yaml` (defaults). Tutor skills are reused from the
repository root `skills/` surface rather than duplicated into the profile.

## Package Files

Required:

- `hermes-profile/distribution.yaml`
- `hermes-profile/SOUL.md`
- `hermes-profile/config.yaml`

Optional (intentionally omitted): a profile-local `hermes-profile/skills/`,
`cron/`, and `mcp.json`. This profile reuses the root `skills/` surface.

## Prerequisites

- Hermes host with the `hermes` CLI available.
- Git (distributions are git-backed).
- Operator-supplied env values (`ANTHROPIC_API_KEY`) in the operator's own
  untracked `.env`. Never bundled.

## Install Flow

1. `hermes profile install` against the git-backed `hermes-profile/`
   distribution.
2. Provide required env values from the operator's local `.env` (per
   `env_requires` / `.env.EXAMPLE`); no secrets are bundled.

## Launch Flow

1. After install, launch the Hermes agent with the installed profile.
2. Build boot context via the explicit tutor boot command (no SessionStart
   hook); the tutor core renders boot sections from persisted learner data.

## Inspect Flow

1. `hermes profile list` to confirm the profile is installed.
2. `hermes profile info language-tutor` to inspect manifest, prompt, and
   config defaults.

## Update Or Reload Flow

1. `hermes profile update` re-pulls the git-backed distribution.
2. Update preserves operator-owned local state; only distribution-owned
   manifest/prompt/config defaults change.

## Remove Flow

1. `hermes profile delete language-tutor` removes the installed profile.
2. Operator-owned local state (secrets, memories, sessions, DB, logs) is not
   part of the distribution and is not removed by deleting the profile.

## User-Owned Data Boundary

Must never be packaged, copied, overwritten, logged, or published:

- API keys, auth tokens, credentials, and `.env` files
- Learner memories and conversation sessions
- SQLite state, `*.db`, WAL/SHM files, and local event data
- Logs, traces, generated workspaces, caches, scratch plans
- `local/` and machine-local config / local overrides

These mirror the Hermes hard exclusions and `PRIVACY_EXCLUDED_PATTERNS`. This
list may be extended host-side but never weakened.

## Capability Profile

Mirrors `src/language_tutor/adapters/registry.py` (`HostId.HERMES`):

- Text support: `supported`
- Audio / image support: `unsupported`
- Lifecycle start: `explicit_command`
- Lifecycle end: `not_available`
- Boot context trigger: `explicit_tutor_command`
- Setup entry point: `hermes profile install`
- Update behavior: `hermes profile update`
- Side-effectful capabilities: none
- Unsupported capabilities: `audio`, `image`
- Flow gates: none (all six representative text flows supported)

## Verification Expectations

- `load_host_setup_profile("…/hermes.md")` returns `host == "hermes"`.
- `tests/packaging/test_hermes_profile_distribution.py` passes (required files
  present; no user-owned data in `hermes-profile/`).
- `tests/packaging/test_host_setup_profiles.py` passes (contract validates; one
  profile and report per host; no Antigravity artifacts).
- Manual provider install check (`hermes profile install` / `update` / `info` /
  `delete`): BLOCKED — the `hermes` CLI is not installed on this machine.

## Known Limitations

- No SessionStart/SessionEnd hooks; boot context requires an explicit tutor
  command.
- Live Hermes CLI install/update/inspect/remove verification is blocked until
  the `hermes` CLI is available on the target machine.
- Audio and image flows are out of scope (text-only profile).

```json
{
  "host": "hermes",
  "schema_version": 1,
  "official_sources": [
    {
      "source_url": "https://github.com/synesthesias/hermes",
      "retrieved_on": "2026-05-22",
      "source_sections": [
        "Profile distributions",
        "distribution.yaml manifest",
        "SOUL.md and config.yaml",
        "env_requires / .env.EXAMPLE",
        "hermes profile install/update/info/list/delete",
        "Update preservation and hard exclusions"
      ],
      "facts_used": [
        "Hermes profiles are git-backed whole-agent distributions with distribution.yaml, SOUL.md, and config.yaml",
        "Optional skills/, cron/, and mcp.json are supported; this profile reuses the root skills/ surface",
        "Lifecycle uses hermes profile install/update/info/list/delete",
        "env_requires declares required env vars; secrets stay in the operator .env and are never bundled",
        "Updates preserve operator-owned local state and hard-exclude secrets, memories, sessions, state DBs, logs, caches, and local/"
      ],
      "unsupported_assumptions": [
        "No SessionStart/SessionEnd hooks assumed; boot uses an explicit tutor command",
        "No audio or image capability assumed"
      ],
      "source_risk": "stable"
    }
  ],
  "package_model": "profile_distribution",
  "package_files": [
    "hermes-profile/distribution.yaml",
    "hermes-profile/SOUL.md",
    "hermes-profile/config.yaml"
  ],
  "prerequisites": [
    "Hermes host with the hermes CLI available",
    "Git (distributions are git-backed)",
    "Operator-supplied ANTHROPIC_API_KEY in the operator's own untracked .env (never bundled)"
  ],
  "install_flow": [
    "Run hermes profile install against the git-backed hermes-profile/ distribution",
    "Provide required env values from the operator's local .env per env_requires/.env.EXAMPLE; no secrets are bundled"
  ],
  "launch_flow": [
    "Launch the Hermes agent with the installed language-tutor profile",
    "Build boot context via the explicit tutor boot command (no SessionStart hook); the tutor core renders boot sections from persisted learner data"
  ],
  "inspect_flow": [
    "Run hermes profile list to confirm the profile is installed",
    "Run hermes profile info language-tutor to inspect manifest, prompt, and config defaults"
  ],
  "update_or_reload_flow": [
    "Run hermes profile update to re-pull the git-backed distribution",
    "Update preserves operator-owned local state; only distribution-owned defaults change"
  ],
  "remove_flow": [
    "Run hermes profile delete language-tutor to remove the installed profile",
    "Operator-owned local state is not part of the distribution and is not removed"
  ],
  "required_user_values": [
    "ANTHROPIC_API_KEY (operator-supplied via local .env)"
  ],
  "user_owned_boundaries": [
    "API keys, auth tokens, credentials, and .env files (secrets)",
    "Learner memories",
    "Conversation sessions",
    "SQLite state including *.sqlite, *.db, and WAL/SHM files",
    "Logs and traces",
    "Caches and generated workspaces",
    "local/ and machine-local config / local overrides"
  ],
  "capability_profile_path": "schemas/host_capability_profile.schema.json",
  "verification_expectations": [
    "load_host_setup_profile returns host == hermes",
    "tests/packaging/test_hermes_profile_distribution.py passes",
    "tests/packaging/test_host_setup_profiles.py passes",
    "Manual hermes profile install/update/info/delete check (BLOCKED: hermes CLI not installed on this machine)"
  ],
  "known_limitations": [
    "No SessionStart/SessionEnd hooks; boot context requires an explicit tutor command",
    "Live Hermes CLI install/update/inspect/remove verification is blocked until the hermes CLI is available",
    "Audio and image flows are out of scope (text-only profile)"
  ]
}
```
