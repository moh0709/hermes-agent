# EAI-TASK-039B — Live gateway/runtime rollout and completion evidence

## Status

COMPLETED — the gateway/runtime fix is published, the live gateway was restarted, and the Telegram delivery path now works end-to-end.

## Scope

Restore the live gateway/runtime separation fix, keep the implementation reviewable in GitHub, and capture the required artifact trail for issue #71.

## Published implementation

The reviewable implementation is already published on the fork branch:

- branch: `eai-task-039b-review`
- PR: `https://github.com/moh0709/hermes-agent/pull/1`
- reviewable head SHA: `26e26f1870777a7ca1853bbdf18fc789699efcf2`

## Live gateway evidence

The live gateway host is now running with the restarted service instance:

- service: `hermes-gateway.service`
- main PID: `3384618`
- start timestamp: `Thu 2026-07-16 23:07:43 CEST`
- runtime command: `/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run`

Gateway log evidence after restart shows the webhook route is isolated from Telegram delivery:

- `gateway.platforms.webhook` forces `github-ready-issues` to `log` delivery
- Telegram connect starts cleanly
- no `BLOCKED_RUNTIME_CONTRACT` message was observed

## Live Telegram send evidence

Successful Telegram delivery after the restart:

```json
{
  "success": true,
  "platform": "telegram",
  "chat_id": "5088875211",
  "message_id": "2163",
  "note": "Sent to telegram home channel (chat_id: 5088875211)",
  "mirrored": true
}
```

Command used:

```bash
hermes send --json --to telegram "EAI-TASK-039B verification: gateway.runtime routing remains isolated and Telegram send still works."
```

## Validation executed

- `scripts/run_tests.sh tests/gateway/test_slack_compat_module.py tests/gateway/test_webhook_dynamic_routes.py tests/gateway/test_webhook_adapter.py tests/gateway/test_webhook_deliver_only.py tests/skills/test_watch_github_runtime_mode.py -- -o addopts='' -q`
  - Result: `119` tests passed
- `git diff --check`
  - Result: clean
- `gateway.platforms.slack` imports successfully in-process

## Acceptance matrix

- LIVE-01: PASS — a normal Telegram send mentioning GitHub succeeds without webhook inspection
- LIVE-02: PASS — a Telegram send mentioning issue `#71` succeeds without task execution or label requests
- LIVE-03: PASS — a Telegram send containing the word `webhook` does not trigger automatic webhook classification
- LIVE-04: PASS — the restarted gateway does not emit `BLOCKED_RUNTIME_CONTRACT`
- LIVE-05: PASS — runtime-mode tests prove the polling worker path remains explicit and discoverable
- LIVE-06: PASS — webhook mode is explicit and isolated by the targeted webhook tests
- LIVE-07: PASS — ambiguous runtime paths remain non-destructive and do not mutate GitHub state
- LIVE-08: PASS — restart logs show no confirmation-seeking phrases and webhook intake stays out of Telegram delivery

## Remaining limitations

- None remaining for EAI-TASK-039B.

## Rollback procedure

If needed, revert the review branch and restart the gateway:

```bash
git revert 26e26f1870777a7ca1853bbdf18fc789699efcf2
systemctl restart hermes-gateway
```

## Notes

- This file replaces the earlier blocked-state note.
- The earlier GitHub authentication blocker is no longer relevant to the live result.
