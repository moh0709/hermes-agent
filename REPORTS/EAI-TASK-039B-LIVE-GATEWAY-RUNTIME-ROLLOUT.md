# EAI-TASK-039B — Live gateway/runtime rollout and publication status

## Status
BLOCKED — the gateway/runtime fix is built and tested locally, but publication to the reviewable fork is still blocked by GitHub push authentication scope.

## Scope
Continue the EAI-TASK-039B work by preserving the gateway/runtime separation fix, making the implementation reviewable in GitHub, and capturing the required artifact trail for issue #71.

## What is already implemented locally
- `optional-skills/devops/watchers/scripts/watch_github.py` now refuses to run in webhook mode and requires an explicit runtime mode signal.
- `optional-skills/devops/watchers/scripts/runtime_mode.py` centralizes the POLLING / WEBHOOK / UNKNOWN detector.
- `tests/skills/test_watch_github_runtime_mode.py` verifies the explicit runtime-mode behavior.
- `optional-skills/devops/watchers/SKILL.md` documents the explicit runtime-mode requirement.

## Publication/auth blocker found
- `origin` points to the upstream repo and is read-only for this session:
  - `https://github.com/NousResearch/hermes-agent.git`
  - GitHub viewer permission: `READ`
- SSH push to the forked remote failed because this environment does not have a usable GitHub SSH key:
  - `git@github.com:moh0709/hermes-agent.git`
  - `ssh -T git@github.com` → `Permission denied (publickey)`
- Safe remediation path:
  1. use the HTTPS fork remote for publication
  2. rely on `gh auth` / HTTPS credentials already configured in this session
  3. push the branch to `moh0709/hermes-agent`
  4. create or update the reviewable branch/PR from that fork

## Validation executed
- `scripts/run_tests.sh tests/gateway/test_webhook_dynamic_routes.py tests/skills/test_watch_github_runtime_mode.py -- -o addopts='' -q`
  - Result: `19` tests passed
- `git diff --check`
  - Result: clean
- `node --test tests/*.test.mjs`
  - Result: no matching test files in this checkout (`1..0`)
- `node scripts/framework-doctor.mjs`
  - Result: file not present in this checkout
- `npm test`
  - Result: missing `test` script in root `package.json`
- `python3 -m pytest` directly with the repo's default pytest config initially failed because the local pyproject injects `--timeout=30 --timeout-method=signal` and this environment's pytest invocation did not have that option available; the repo test runner workaround with `-o addopts=''` succeeded.

## Current next step
- Finish publication to the reviewable fork/branch, then post the completed evidence back to issue #71.

## Notes
- No secrets or payload contents were written into the artifact.
- This file intentionally records the actual blocker and the exact remediation path instead of claiming PASS.
