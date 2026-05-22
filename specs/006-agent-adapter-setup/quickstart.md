# Quickstart: Agent Adapter Setup

## 1. Confirm baseline context

```bash
rtk bin/tutor doctor --json
rtk bin/tutor progress --json '{"window_size":10}'
rtk uv run pytest tests/adapter_contract/test_plugin_surface.py tests/integration/test_text_modality_flow.py tests/integration/test_local_data_ownership.py
```

Expected: existing Claude/plugin surface and Phase 5 text flows still work before host setup changes.

## 2. Create host subagent context packages

For each included host, prepare the context package defined in `specs/006-agent-adapter-setup/contracts/subagent-context-package.md`.

Hosts:

- Hermes
- OpenClaw
- Claude
- Codex

Expected: each host subagent receives the active spec, plan, constitution, roadmap, official source URL, owned host setup profile path, shared conformance expectations, verification requirements, and baseline notes before implementation starts.

## 3. Host subagents create setup profile contracts

Expected files after implementation subagents run:

```text
specs/006-agent-adapter-setup/contracts/host-setup-profiles/hermes.md
specs/006-agent-adapter-setup/contracts/host-setup-profiles/openclaw.md
specs/006-agent-adapter-setup/contracts/host-setup-profiles/claude.md
specs/006-agent-adapter-setup/contracts/host-setup-profiles/codex.md
```

Expected: every profile cites official source sections, package files, install/update/inspect/remove flow, user-owned data boundaries, capability profile, and verification expectations.

## 4. Verify shared contracts

```bash
rtk uv run pytest tests/unit/test_schemas.py tests/adapter_contract/test_host_capability_profile.py tests/adapter_contract/test_lifecycle_contract.py tests/packaging/test_host_setup_profiles.py
```

Expected: host/capability/profile schemas reject missing official sources, Antigravity targets, missing lifecycle alternatives, and missing user-owned data boundaries.

## 5. Run conformance kit

```bash
rtk uv run pytest tests/adapter_contract/test_conformance_kit.py tests/integration/test_host_text_flows.py
```

Expected: Hermes, OpenClaw, Claude, and Codex pass reading, lesson, transcript, vocab, writing, and progress flows, or record source-backed capability gates.

## 6. Check package privacy

```bash
rtk uv run pytest tests/packaging/test_distribution_privacy.py tests/integration/test_local_data_ownership.py
```

Expected: no package/profile/plugin includes secrets, memories, sessions, SQLite state, logs, local overrides, caches, or machine-local config.

## 7. Hermes manual install

```bash
rtk hermes profile install <local-hermes-profile-path> --name language-tutor-test --alias
rtk hermes profile info language-tutor-test
rtk hermes profile update language-tutor-test
rtk hermes profile delete language-tutor-test
```

Expected: install, inspect, update, and remove behavior matches the Hermes setup profile; `.env`, memories, sessions, state DBs, logs, caches, and `local/` stay user-owned.

## 8. OpenClaw package checks

```bash
rtk pnpm test -- <openclaw-plugin-root>
rtk pnpm check
rtk clawhub package publish <org>/<plugin> --dry-run
```

Expected: OpenClaw package metadata, `openclaw.plugin.json`, focused SDK imports, entry point, optional side-effectful tool handling, and tests pass.

## 9. Claude local plugin checks

```bash
rtk claude plugin validate <plugin-root> --strict
rtk claude --plugin-dir <plugin-root>
```

Inside Claude, run `/reload-plugins`, verify skills, agents, hooks, and tutor CLI behavior, then run the six representative text flows.

Expected: existing Claude baseline remains passing.

## 10. Codex local marketplace checks

Codex build docs do not document a standalone CLI validator. Use the manual provider report to record:

- `.codex-plugin/plugin.json` present and valid by inspection/tests
- Repo or personal marketplace entry points to the local plugin
- Codex restart/reload performed
- Plugin appears in the selected marketplace/install surface
- Tutor skills are exposed
- Hooks remain disabled unless `[features].plugin_hooks = true` is intentionally enabled
- Six representative text flows pass or are capability-gated

Expected: Codex recognizes the plugin and supports local iteration without publishing user data outside the workspace boundary.

## 11. Final gates

```bash
rtk uv run pytest
rtk uv run pyright
rtk uv run ruff check .
```

Expected: automated gates pass, all four manual provider install reports are complete, all subagent changed-file reports are reviewed by the main maintainer, and zero Antigravity artifacts exist.
