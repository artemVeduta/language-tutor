# Tasks: provider-install-smoke-harness

## 1. Harness Contract

- [ ] 1.1 Define provider list and managed-file expectations in one reusable script data block.
- [ ] 1.2 Define report JSON fields and decision rules.
- [ ] 1.3 Define cleanup behavior: delete on all-pass, keep on failure, always keep with `--keep-workdir`.

## 2. Script Implementation

- [ ] 2.1 Add `scripts/provider-smoke.sh` with `--provider <host>` repeated and `--keep-workdir`.
- [ ] 2.2 Create temp workdir with `home/`, `package/`, `reports/`, `logs/`, and `wheel/`.
- [ ] 2.3 Force `HOME`, XDG paths, and secret sentinel into the isolated environment for every command.
- [ ] 2.4 Install the current package into a clean environment before running provider checks.
- [ ] 2.5 Run the shared per-provider sequence for all selected providers.
- [ ] 2.6 Write `reports/<host>.json` for each selected provider.
- [ ] 2.7 Print concise pass/fail summary and kept workdir path when applicable.

## 3. Tests

- [ ] 3.1 Add tests for argument parsing and default all-provider selection.
- [ ] 3.2 Add tests proving success deletes the workdir unless `--keep-workdir` is set.
- [ ] 3.3 Add tests proving failure keeps the workdir and reports the path.
- [ ] 3.4 Add tests proving provider reports include command evidence, managed files, doctor status, secret-leak result, and host CLI status.
- [ ] 3.5 Add tests proving invalid providers are rejected before running any provider check.

## 4. Documentation

- [ ] 4.1 Update `docs/internal/pr12-merge-checklist.md` to point per-provider smoke testing at `scripts/provider-smoke.sh`.
- [ ] 4.2 Document the difference between provider smoke and live manual provider verification.
- [ ] 4.3 Add troubleshooting notes for preserved temp workdirs.

## 5. Verification

- [ ] 5.1 Run `rtk scripts/provider-smoke.sh --provider claude --keep-workdir` locally.
- [ ] 5.2 Run `rtk scripts/provider-smoke.sh` locally.
- [ ] 5.3 Run `rtk uv run pytest` for related tests.
- [ ] 5.4 Run `rtk uv run pyright`.
- [ ] 5.5 Run `rtk uv run ruff check .`.
- [ ] 5.6 Run `rtk openspec validate provider-install-smoke-harness --strict`.
