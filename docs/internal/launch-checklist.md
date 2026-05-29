# OSS launch checklist (assets)

Every item below is **launch-blocking** for the public announcement of `lingo-loop` v0.1. They are *not* merge-blocking for the `oss-baseline` change — placeholders shipped via `<!-- TODO(oss-baseline-assets): ... -->` comments in the docs.

Internal tracking only; safe to delete once everything is filled.

## README

- [ ] `docs/assets/demo.cast` — top-level asciinema cast of a typical tutor session (referenced from README placeholder).
- [ ] `docs/assets/demo.gif` — GIF rendered from `demo.cast` via `agg` / `asciinema-agg` (the in-README visual, since GitHub strips JS).

## Per-host install docs

### Claude (`docs/install/claude.md`)
- [ ] `docs/assets/claude-plugin-enabled.png` — screenshot of the Claude `/plugin` panel showing `language-tutor` enabled.
- [ ] `docs/assets/claude-first-session.cast` — asciinema cast of the first session in Claude Code.

### Codex (`docs/install/codex.md`)
- [ ] `docs/assets/codex-plugin-enabled.png` — screenshot of the Codex marketplace/plugins pane showing `language-tutor` enabled.
- [ ] `docs/assets/codex-first-session.cast` — asciinema cast of the first Codex tutor session.

### Hermes (`docs/install/hermes.md`)
- [ ] `docs/assets/hermes-profile-installed.png` — screenshot of `hermes profile list` output (or UI listing) showing `language-tutor`.
- [ ] `docs/assets/hermes-first-session.cast` — asciinema cast of `hermes run language-tutor` first session.

### OpenClaw (`docs/install/openclaw.md`)
- [ ] `docs/assets/openclaw-plugin-enabled.png` — screenshot of the OpenClaw plugins panel showing `@language-tutor/openclaw-plugin` enabled.
- [ ] `docs/assets/openclaw-first-session.cast` — asciinema cast of the first OpenClaw tutor session.

## Verification dates

Each install doc's header currently reads `Verification pending` (no date is asserted until a real host CLI release is confirmed). On first verification, replace it with a `Last verified: YYYY-MM-DD against <Host> vX.Y` line; refresh on each release. A future CI check (planned in `publish-pypi`) will warn if any date is older than 90 days.

- [ ] `docs/install/claude.md` — verify against current Claude Code release, update header.
- [ ] `docs/install/codex.md` — verify against current Codex CLI release, update header.
- [ ] `docs/install/hermes.md` — verify against current Hermes release, update header.
- [ ] `docs/install/openclaw.md` — verify against current OpenClaw release, update header.

## Inline `TODO: verify` markers

Every public doc carries one or more `<!-- TODO: verify -->` markers that must be resolved before the v0.1 announcement. Each must be either confirmed (delete the marker) or fixed (update the surrounding text, then delete the marker). Track them here:

### Host-CLI install syntax (verify against each host's current release)
- [ ] `docs/install/claude.md:3` — Claude Code version pin in `Verification pending` header.
- [ ] `docs/install/claude.md:57` — exact `claude plugin install` invocation.
- [ ] `docs/install/codex.md:3` — Codex CLI version pin in `Verification pending` header.
- [ ] `docs/install/codex.md:53` — exact `codex plugin install` invocation.
- [ ] `docs/install/hermes.md:3` — Hermes version pin in `Verification pending` header.
- [ ] `docs/install/hermes.md:55` — exact `hermes profile install` syntax for git+subdir.
- [ ] `docs/install/openclaw.md:3` — OpenClaw version pin in `Verification pending` header.
- [ ] `docs/install/openclaw.md:35` — exact `openclaw plugins install lingo-loop` syntax (Step 1, by-name); reconcile `plugins` vs `plugin` noun with line 59.
- [ ] `docs/install/openclaw.md:59` — exact `openclaw plugin install` syntax (manual fallback, by-path).

Configuration enum values (`docs/configuration.md` `review_intensity`,
`feedback_verbosity`) were confirmed against `ReviewIntensity` /
`FeedbackVerbosity` in `src/language_tutor/schemas.py` and the markers removed —
no longer tracked here.

A CI guard (added in `.github/workflows/ci.yml`) already fails the build if `rtk` or `Spec N` references leak into public docs; once the items above are resolved, extend the guard to fail on any remaining marker as a release gate. Match the substring `TODO: verify` (every marker uses that exact casing), not the `<!-- -->` wrapper, and exclude `docs/internal/` — e.g. `grep -RInE 'TODO: verify' README.md docs/ | grep -v docs/internal/`.

## Public-issue mirror

Once the repo announcement is imminent, mirror this checklist into a pinned GitHub issue titled **"Launch-blocking assets"** (per `tasks.md` 8.4) so external contributors can claim items.
