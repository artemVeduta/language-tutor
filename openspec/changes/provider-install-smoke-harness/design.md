# Design: provider-install-smoke-harness

## Context
The current distribution baseline has three automated layers:

- unit/integration tests for provider installer behavior
- release tests proving the wheel bundles provider assets
- adapter conformance tests proving host-visible tutor contracts

Those layers do not answer one operational question: "Can I run one command on my laptop that installs the packaged CLI into a disposable environment and checks each provider path without touching my real config?"

This change adds that missing operational smoke layer.

## Command Boundary

The harness is a script under `scripts/` because it orchestrates package build/install, environment variables, CLI invocations, and report files. It does not belong inside the tutor runtime. The shipped `tutor` CLI remains the product surface; the script is maintainer tooling.

Expected command:

```bash
scripts/provider-smoke.sh [--provider <host>] [--keep-workdir]
```

Supported providers are exactly the existing `HostId` values: `claude`, `codex`, `hermes`, and `openclaw`.

## Execution Model

```text
┌──────────────────────────────┐
│ scripts/provider-smoke.sh    │
└───────────────┬──────────────┘
                │
                ▼
        ┌──────────────┐
        │ temp workdir │
        └──────┬───────┘
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
  fake HOME  package   reports/logs
      │        │        │
      └────────┼────────┘
               ▼
      tutor init --provider <host> --yes --json
      tutor init --provider <host> --dry-run --json
      tutor doctor --json
```

## Per-Provider Checks

Every selected provider runs the same reusable sequence:

1. Create provider config root under fake `HOME`.
2. Install the current package into a clean environment.
3. Run `tutor init --provider <host> --yes --json`.
4. Run `tutor init --provider <host> --dry-run --json`.
5. Run `tutor doctor --json`.
6. Assert the provider's managed file exists under fake `HOME`.
7. Assert a sentinel secret is not present in reports, logs, or files under fake `HOME`.
8. Record host CLI availability and safe validation result when available.

Managed file expectations mirror the provider installer profiles:

| Provider | Managed file |
|---|---|
| `claude` | `.claude/plugins/lingo-loop/plugin.json` |
| `codex` | `.codex/plugins/lingo-loop/plugin.json` |
| `hermes` | `.hermes/profiles/lingo-loop/distribution.yaml` |
| `openclaw` | `.openclaw/plugins/lingo-loop/package.json` |

## Host CLI Policy

The harness must not require every host CLI to be installed. Provider install smoke remains useful even if a live host is missing.

| Host CLI state | Result |
|---|---|
| CLI missing | `host_cli.status = "skipped"` with reason `missing_cli` |
| CLI present and safe command known | run command, record pass/fail |
| CLI present but validation is interactive/ambiguous | `host_cli.status = "manual_needed"` |

The provider smoke decision is separate from live manual verification. A provider can pass install smoke while still requiring manual live-host checks before release readiness.

## Report Shape

Each selected provider writes a JSON report under `reports/<host>.json`:

```json
{
  "schema_version": 1,
  "host": "claude",
  "decision": "pass",
  "workdir": "/tmp/lingo-loop-provider-smoke.x",
  "fake_home": "/tmp/lingo-loop-provider-smoke.x/home",
  "commands": [
    {"argv": ["tutor", "init", "--provider", "claude", "--yes", "--json"], "exit_code": 0}
  ],
  "managed_files": [
    {"path": ".claude/plugins/lingo-loop/plugin.json", "exists": true}
  ],
  "doctor_status": "ok",
  "secret_leak_check": "pass",
  "host_cli": {"status": "skipped", "reason": "missing_cli"}
}
```

The aggregate command exits non-zero if any selected provider report has `decision != "pass"`.

## Cleanup Semantics

Cleanup behavior must be deterministic:

- all providers pass and `--keep-workdir` absent: delete workdir
- any provider fails: keep workdir and print path
- `--keep-workdir` present: keep workdir and print path

## Open Questions

None for v1. Docker and interactive live-host automation are intentionally deferred.
