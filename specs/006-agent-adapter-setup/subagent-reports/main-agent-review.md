# Main-Agent Changed-File Review

Reviewer: main maintainer (orchestrating agent)
Date: 2026-05-22
Spec: 006-agent-adapter-setup

Each host slice was implemented by exactly one primary sub-agent (US2). This
file records the review decision for every changed file reported by those
sub-agents (T050) and the `SKILL.md` creation gate result (T051).

## SKILL.md Creation Gate (T051)

**Result: PASS — not triggered.** No sub-agent created or edited any `SKILL.md`.
All hosts reuse the existing root `skills/` surface. `git status` confirms zero
`SKILL.md` changes, so the local writing-skills helper / pressure-evidence gate
does not apply to this feature.

## Per-Host Review

### Hermes (owner: hermes-adapter-subagent)

| File | Decision | Notes |
|------|----------|-------|
| `hermes-profile/distribution.yaml` | PASS | Distribution metadata only; reuses `../skills`; hard exclude list present. |
| `hermes-profile/SOUL.md` | PASS | Profile prompt; defers pedagogy/state to core. |
| `hermes-profile/config.yaml` | PASS | Capability/command defaults; no bundled secrets. |
| `contracts/host-setup-profiles/hermes.md` | PASS | Loads + validates as `hermes`; capability values match registry. |
| `subagent-reports/hermes.md` | PASS | All required headings; blocker recorded. |

Blocker (accepted): `hermes` CLI not installed → manual install/update/inspect/remove
verification BLOCKED. Profile status `blocked` is correct.

### OpenClaw (owner: openclaw-adapter-subagent)

| File | Decision | Notes |
|------|----------|-------|
| `openclaw-plugin/package.json` | PASS | ESM (`type=module`), `engines.node>=22`. |
| `openclaw-plugin/openclaw.plugin.json` | PASS | Plugin manifest; side-effectful tool marked opt-in. |
| `openclaw-plugin/src/index.ts` | PASS | Focused `openclaw/plugin-sdk/<subpath>` imports; `definePluginEntry`. |
| `openclaw-plugin/tsconfig.json` | PASS | NodeNext strict ESM config. |
| `contracts/host-setup-profiles/openclaw.md` | PASS | Loads + validates as `openclaw`. |
| `subagent-reports/openclaw.md` | PASS | All required headings. |

Blockers (accepted): `clawhub` not installed → publish dry-run BLOCKED; `tsc`/SDK
peer dep unavailable → `pnpm check` cannot complete type-check locally. Both are
environmental manual-provider steps, not defects in scope.

### Claude (owner: claude-adapter-subagent)

| File | Decision | Notes |
|------|----------|-------|
| `contracts/host-setup-profiles/claude.md` | PASS | Loads + validates as `claude`; documents real baseline files. |
| `subagent-reports/claude.md` | PASS | All required headings; baseline validate findings recorded. |

Baseline preserved — no `.claude-plugin/`, `hooks/`, `skills/`, `agents/`, or
`bin/` files modified.

**Baseline modernization (resolved post-review, maintainer-authorized):**
`claude plugin validate . --strict` (CLI v2.1.148) initially reported three
pre-existing baseline schema errors — `author` string (newer CLI expects object),
`hooks.*.hooks` nested-array shape, and `agents/tutor-judge.md` missing
frontmatter. The maintainer authorized fixing these. All three are now corrected
(`.claude-plugin/plugin.json`, `hooks/hooks.json`, `agents/tutor-judge.md`);
`--strict` passes with only one benign warning (repo-root `CLAUDE.md` is dev
instructions, not plugin context — intentionally retained). Claude package and
plugin-surface tests, and `tutor doctor`, remain green after the change.

### Codex (owner: codex-adapter-subagent)

| File | Decision | Notes |
|------|----------|-------|
| `.codex-plugin/plugin.json` | PASS | References `./skills/`; `plugin_hooks=false` (opt-in preserved); cache-safe. |
| `.agents/plugins/marketplace.json` | PASS | Repo-local marketplace entry referencing the plugin. |
| `contracts/host-setup-profiles/codex.md` | PASS | Loads + validates as `codex`. |
| `subagent-reports/codex.md` | PASS | All required headings. |

No blockers. Codex CLI present (0.130.0) but has no standalone validator;
marketplace add/restart/visibility recorded as manual checks.

## Cross-Cutting Checks

- Antigravity scan: only exclusion notes found (forbidden/out-of-scope/rejected
  context). No Antigravity artifact. PASS.
- Privacy scan of package roots: no `.env`, `*.sqlite*`, `*.db`, or `*.log`
  files. PASS.
- Shared-contract conflicts: none. No sub-agent edited `schemas.py`,
  `adapters/base.py`, `adapters/registry.py`, or `tests/**`.
- US2 gate `tests/packaging/*` + `test_host_setup_profiles.py`: 33 passed.

## Overall Decision

**PASS** for all four host slices. One item flagged for a follow-up,
out-of-scope baseline decision (Claude plugin manifest schema vs newer CLI).
