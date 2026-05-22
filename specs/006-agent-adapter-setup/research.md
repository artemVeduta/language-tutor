# Research: Agent Adapter Setup

## Decision: Scope includes Hermes, OpenClaw, Claude, and Codex only

**Rationale**: The active spec explicitly includes Hermes, OpenClaw, Claude, and Codex and excludes Antigravity. The roadmap names Phase 6/6.x as the host-capability and adapter rollout phase, so this feature is the documented scope move for selected hosts.

**Alternatives considered**:

- Include Antigravity from the older roadmap: rejected because the active feature says skip, and success criteria require zero Antigravity deliverables.
- Keep Claude-only v1 scope: rejected because the current feature explicitly starts source-backed host setup work while preserving host-independent core boundaries.

## Decision: Use versioned host setup profile contracts as source of truth

**Rationale**: FR-003 and the clarification require source-backed host setup profiles under `specs/006-agent-adapter-setup/contracts/host-setup-profiles/`. Planning defines the common schema/template; each implementation subagent owns its host file after receiving the context package.

**Alternatives considered**:

- Put setup facts only in tasks: rejected because tasks are not durable source-of-truth contracts.
- Put setup facts only in code comments: rejected because official evidence and manual install expectations must be reviewable before implementation.

## Decision: Hermes uses profile distributions

**Rationale**: Official Hermes documentation defines a profile distribution as a git-backed whole-agent package with `distribution.yaml`, `SOUL.md`, `config.yaml`, optional `skills/`, `cron/`, and `mcp.json`. Install/update/inspect/remove flows use `hermes profile install`, `hermes profile update`, `hermes profile info/list`, and `hermes profile delete`. The source also documents `env_requires`, `.env.EXAMPLE`, update preservation, and hard exclusions for secrets and user data.

**Official source**: https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions

**Alternatives considered**:

- Generic archive or manual copy: rejected because Hermes source states distributions are git-backed and update through git-backed install/update commands.
- Sharing user config/state: rejected because the source excludes `.env`, auth, memories, sessions, state DBs, logs, workspaces, caches, and `local/`.

## Decision: OpenClaw uses its documented plugin package model

**Rationale**: Official OpenClaw documentation requires Node >=22, TypeScript ESM, `package.json`, `openclaw.plugin.json`, focused SDK subpath imports, and entry points using `definePluginEntry` or `defineChannelPluginEntry`. Tools register through `api.registerTool`; optional or side-effectful tools use `{ optional: true }` and user allowlists. Verification uses package metadata checks, manifest validation, tests, `pnpm check`, and ClawHub dry-run/publish/install flows.

**Official source**: https://docs.openclaw.ai/plugins/building-plugins#building-plugins

**Alternatives considered**:

- Python-only OpenClaw package: rejected because the documented plugin model is Node/TypeScript with OpenClaw SDK entry points.
- Required side-effectful tools: rejected because the source documents optional tools for side-effectful or binary-dependent capabilities.

## Decision: Claude preserves the existing plugin baseline

**Rationale**: Official Claude docs define a self-contained plugin directory with `.claude-plugin/plugin.json` and root-level components such as `skills/`, `agents/`, `hooks/hooks.json`, `bin/`, settings, MCP, LSP, and monitors. Local verification uses `claude --plugin-dir`, `/reload-plugins`, component checks, and `claude plugin validate`. The current project already follows the Claude plugin shape, so implementation must preserve the existing baseline while adding common host contracts.

**Official source**: https://code.claude.com/docs/en/plugins

**Alternatives considered**:

- Rebuild Claude package around another host model: rejected because the existing Claude baseline must remain passing.
- Store persistent state in plugin root: rejected because plugin roots are versioned/cached package content; persistent/plugin data must stay separate from bundled files.

## Decision: Codex uses Codex plugin packaging and local marketplace verification

**Rationale**: Official OpenAI Codex docs define `.codex-plugin/plugin.json` as the required plugin entry point. The manifest can point to root-level `skills/`, `.app.json`, `.mcp.json`, `hooks/`, and install-surface metadata. Local/repo marketplace files can expose plugins, and installed plugins are cached under Codex's plugin cache. Plugin hooks are off by default and require `[features].plugin_hooks = true`.

**Official source**: https://developers.openai.com/codex/plugins/build

**Alternatives considered**:

- Treat Codex as Claude-compatible without a Codex manifest: rejected because Codex has its own `.codex-plugin/plugin.json` entry point and marketplace/cache behavior.
- Require hooks by default: rejected because Codex plugin hooks are documented as disabled by default in this release.

## Decision: Model host capability and lifecycle availability as separate axes

**Rationale**: The roadmap and spec both identify lifecycle availability as a real risk independent from text support. Capability profiles must declare text support, lifecycle hook availability, alternate boot trigger, update behavior, optional side-effectful capabilities, and unsupported capabilities.

**Alternatives considered**:

- Single boolean `supports_text`: rejected because a text-capable host may still lack SessionStart/SessionEnd hooks.
- Claude-style lifecycle as universal: rejected because the spec requires hosts without Claude-style hooks to build boot context through an explicit alternate trigger.

## Decision: Shared conformance kit covers every Phase 5 text flow

**Rationale**: Clarification requires all Phase 5 text flows: reading, lesson, transcript, vocab, writing, and progress. A shared conformance kit keeps learner-visible behavior host-portable and prevents host-specific setup from changing feedback/progress/data semantics.

**Alternatives considered**:

- One representative flow only: rejected by clarification.
- Host-specific conformance per adapter: rejected because the same tutor contracts must substitute across hosts.

## Decision: One implementation subagent owns each host slice

**Rationale**: FR-012 through FR-014 require one host subagent per included host, a full main-maintainer context package before work starts, subagent-owned setup profile contracts, and main-agent changed-file review before readiness.

**Alternatives considered**:

- Main agent implements all hosts directly: rejected by explicit user requirement and spec.
- Shared subagent for multiple hosts: rejected because each host needs independent source usage, setup decisions, changed-file reports, and verification evidence.

## Decision: Distribution privacy is a blocking verification gate

**Rationale**: FR-017 and the constitution require no packaging, copying, logging, or publishing of user secrets, learner memories, sessions, SQLite state, logs, or local-only config. Hermes official docs also hard-exclude those categories. Packaging privacy tests and manual reports must block readiness if any excluded data appears.

**Alternatives considered**:

- Rely on `.gitignore` only: rejected because not every host package is git-only and privacy must be tested.
- Document exclusions without tests: rejected because data ownership is a constitution gate.
