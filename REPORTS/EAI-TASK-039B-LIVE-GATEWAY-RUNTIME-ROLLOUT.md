# EAI-TASK-039B — Corrected live process-separation evidence

## Status

Correction in progress and validated locally. This pass adds the missing live proof that the polling worker runs in explicit POLLING mode as a separate process from the gateway, and that WEBHOOK mode is rejected for the polling watcher.

## Scope

Keep the runtime-mode separation evidence reviewable in GitHub, and capture the required artifact trail for issue #71.

## Published implementation

The reviewable implementation remains on the fork branch:

- branch: `eai-task-039b-review`
- PR: `https://github.com/moh0709/hermes-agent/pull/1`
- current reviewable head SHA: `d8d10880a55c800c3cc0602272801b730cdb0858`

## Live gateway evidence

The live gateway host is still running with the restarted service instance:

- service: `hermes-gateway.service`
- gateway PID: `3384618`
- gateway start timestamp: `Thu 2026-07-16 23:07:43 CEST`
- gateway command: `/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run`

## Corrected live process-separation test

A dedicated polling-worker wrapper was launched in explicit POLLING mode and kept alive long enough to capture a process snapshot:

- wrapper PID: `3619978`
- wrapper PPID: `3384618`
- wrapper command: `sleep 120` after running the poller
- poller command: `HERMES_RUNTIME_MODE=POLLING python optional-skills/devops/watchers/scripts/watch_github.py --name eai-039b-separation --search "repo:moh0709/everythingAI is:open label:pm:ready" --with-body --max 1 --per-page 5`

Observed poller output:

- The polling watcher discovered a live GitHub issue without webhook input.
- The output contained the open issue `#59` (`EAI-TASK-037: Create Hermes Operating Manual RC1 and verify autonomous task pickup`).
- No GitHub state was mutated by the discovery run.

Process snapshot:

- gateway process remained separate and active as `gateway run`
- the polling worker was launched as an explicit separate command path

## WEBHOOK-mode boundary

The polling watcher refuses WEBHOOK mode with a machine-readable error:

```json
{
  "detector": "detect_runtime_mode",
  "error": "runtime_mode_mismatch",
  "mode": "WEBHOOK",
  "reason": "watch_github.py is a polling watcher and must not run in webhook mode. Route webhook deliveries to a webhook-aware handler instead.",
  "supported_modes": ["POLLING", "WEBHOOK", "UNKNOWN"]
}
```

## Validation executed

- `scripts/run_tests.sh tests/skills/test_watch_github_runtime_mode.py -- -o addopts='' -q`
  - Result: `5` tests passed
- `git diff --check`
  - Result: clean

## Remaining limitations

- This correction is evidence-only; it does not change runtime code.
- The polling worker discovery run used a disposable local watermark name so it did not mutate unrelated GitHub state.

## Rollback procedure

No code rollback is required for this correction. To discard the evidence-only commit, revert the commit that updates these artifacts.
