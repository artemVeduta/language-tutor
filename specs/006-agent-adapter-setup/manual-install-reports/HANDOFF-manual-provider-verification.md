# Handoff: Manual Provider Verification (Blocked Items)

Spec 006 automated layer is complete and green (schemas, contracts, packaging
privacy, adapter conformance, host text flows, pyright, ruff). What remains is
**live, in-host manual provider verification** — installing each host package
into the real host and running the six representative tutor flows. This requires
host CLIs and/or interactive sessions that were unavailable on the build machine.

This doc tells the next operator exactly what to install and run to clear each
blocked item. Update the matching `manual-install-reports/<host>.md` with results.

## Environment expectations

- macOS or Linux local dev machine.
- `uv` (tutor Python runtime), `python 3.12+`, `git`.
- A throwaway learner home (`export TUTOR_HOME="$(mktemp -d)"`) so production
  learner data is never touched.
- The six flows to run in every host: **reading, lesson, transcript, vocab,
  writing, progress**.

## Tool availability on the build machine (2026-05-22)

| Tool | Status | Affects |
|------|--------|---------|
| `claude` | present (v2.1.148) | Claude — only interactive `/reload-plugins` run pending |
| `codex` | present (0.130.0) | Codex — interactive marketplace install pending |
| `pnpm` / `node` | present (node v25.6.1) | OpenClaw build checks |
| `hermes` | **MISSING** | Hermes — all install/update/inspect/remove blocked |
| `clawhub` | **MISSING** | OpenClaw — publish dry-run blocked |
| `tsc` + OpenClaw SDK peer dep | **MISSING** | OpenClaw — `pnpm check` type-check blocked |

---

## Hermes — BLOCKED (no `hermes` CLI)

Install the Hermes CLI (git-backed profile manager), then:

```bash
export TUTOR_HOME="$(mktemp -d)"
rtk hermes profile install ./hermes-profile --name language-tutor-test --alias
rtk hermes profile info language-tutor-test
rtk hermes profile update language-tutor-test
rtk hermes profile delete language-tutor-test
```

Verify and record in `manual-install-reports/hermes.md`:
- `distribution.yaml`, `SOUL.md`, `config.yaml` install correctly.
- Required `env_requires` are prompted/sourced from operator-local `.env` (never bundled).
- Six tutor flows run inside the Hermes session.
- After install/update/delete: `.env`, memories, sessions, state DBs, logs,
  caches, and `local/` are untouched (user-owned).
- Set the profile `Status` and report `Decision` to `pass` once green.

## OpenClaw — BLOCKED (no `clawhub`; no `tsc`/SDK peer dep)

Install Node >=22 (present), the OpenClaw CLI + ClawHub, and the plugin SDK
dev deps, then:

```bash
cd openclaw-plugin
rtk pnpm install            # pulls openclaw/plugin-sdk + typescript
rtk pnpm check              # type-check (needs tsc + SDK peer dep)
rtk pnpm test
rtk clawhub package publish <org>/language-tutor --dry-run
rtk openclaw plugins install <package-name>
```

Verify and record in `manual-install-reports/openclaw.md`:
- `package.json` ESM (`type=module`), `engines.node>=22`.
- `openclaw.plugin.json` manifest, focused `openclaw/plugin-sdk/<subpath>` imports.
- Side-effectful tool stays opt-in (user allowlist) — confirm it is NOT auto-enabled.
- Six tutor flows run; first-message boot trigger fires.
- No `.env`/SQLite/logs in the published package.

## Claude — interactive `/reload-plugins` run pending

CLI present. `claude plugin validate . --strict` now passes (manifest/hooks/agent
errors fixed in this session). Remaining step is a live interactive run:

```bash
rtk claude --plugin-dir .
# inside the session:
/reload-plugins
# then run the six tutor flows and confirm tutor skills/agents/hooks load
```

Record in `manual-install-reports/claude.md`. Note: `--strict` still emits ONE
benign warning — the repo-root `CLAUDE.md` is dev instructions, not plugin
context (tutor ships context via `skills/`). This is expected and not a defect.

## Codex — interactive marketplace install pending

CLI present (0.130.0); no documented standalone validator. Manual steps:

1. Confirm `.codex-plugin/plugin.json` references `./skills/` and that
   `[features].plugin_hooks` is **false** (opt-in only).
2. Add/point the marketplace entry: `.agents/plugins/marketplace.json`.
3. Restart Codex.
4. Install/enable the plugin from the marketplace.
5. Confirm tutor skills are visible.
6. Run the six tutor flows.

Record in `manual-install-reports/codex.md`. Keep hooks disabled unless
intentionally enabling `plugin_hooks`.

---

## Definition of done

Feature readiness requires every `manual-install-reports/<host>.md` to record a
`pass` decision (or a documented, capability-gated skip) for install, launch,
the six flows, update/reload, inspect, remove, and user-data preservation. Until
then those hosts remain `blocked` in their reports and in `dogfood.md`.
