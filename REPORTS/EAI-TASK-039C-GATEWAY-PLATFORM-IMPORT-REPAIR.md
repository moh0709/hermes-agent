# EAI-TASK-039C — Hermes gateway platform import repair

## Status

Completed and validated locally against the live Hermes gateway host, with a follow-up deterministic regression correction for the Slack-disabled case.

## Root cause

The gateway could not satisfy a legacy import path used by the live runtime:

- `gateway.platforms.slack` was referenced, but the real Slack adapter now lives under `plugins.platforms.slack.adapter`.
- This caused the live send path to fail before delivery with:
  - `No module named 'gateway.platforms.slack'`

## Fix

Added a small compatibility shim at:

- `gateway/platforms/slack.py`

Behavior:

- keeps the legacy module path importable;
- does not eagerly load the Slack plugin at gateway startup;
- forwards `register(ctx)` to the plugin entry point;
- exposes the expected Slack symbols lazily for compatibility;
- translates a missing Slack adapter import into a clear Slack-specific runtime error.

## Tests added

- `tests/gateway/test_slack_compat_module.py`

Covers:

- import of `gateway.platforms.slack` without eagerly loading the Slack plugin;
- `register()` forwarding to `plugins.platforms.slack.adapter.register()`;
- deterministic failure when the Slack adapter is unavailable, with a clear Slack-specific error;
- another platform path (`gateway.platforms.webhook`) remaining importable after the Slack-specific failure.

## Live gateway verification

- Service: `hermes-gateway.service`
- Main PID after restart: `3384618`
- Start timestamp: `Thu 2026-07-16 23:07:43 CEST`
- Current process command:
  - `/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run`

Observed gateway log evidence after restart:

- `gateway.platforms.webhook` forced the `github-ready-issues` route away from Telegram delivery and into log delivery.
- Telegram connect path started cleanly.

## Live send evidence

Successful Telegram delivery after restart:

```json
{
  "success": true,
  "platform": "telegram",
  "chat_id": "5088875211",
  "message_id": "2161",
  "note": "Sent to telegram home channel (chat_id: 5088875211)",
  "mirrored": true
}
```

Command used:

```bash
hermes send --json --to telegram "EAI-TASK-039C verification: gateway.platforms.slack import path is available."
```

## Validation

Command:

```bash
scripts/run_tests.sh tests/gateway/test_slack_compat_module.py tests/gateway/test_webhook_dynamic_routes.py tests/gateway/test_webhook_adapter.py tests/gateway/test_webhook_deliver_only.py tests/skills/test_watch_github_runtime_mode.py -- -o addopts='' -q
```

Result:

- 5 files
- 120 tests passed
- 0 failed

Also verified:

- `git diff --check` clean
- `gateway.platforms.slack` imports successfully in-process
- `hermes send --json --to telegram ...` succeeds
- the new deterministic regression test for Slack-unavailable behavior passes

## Rollback procedure

If needed, revert the shim and test with:

```bash
git revert <commit>
systemctl restart hermes-gateway
```

If the gateway process must be preserved, re-enable the previous version only after confirming the legacy import path is no longer needed.

## Remaining limitations

- Slack still depends on the real plugin when actually enabled.
- This fix restores the legacy import path and prevents unrelated startup failures; it does not change Slack business logic.

## Files changed

- `gateway/platforms/slack.py`
- `tests/gateway/test_slack_compat_module.py`
- `.hermes/state.json`

## Final pushed SHA

- `867c15917be2e7bfb4f6f7a5b4d19cb4cc8b0f1f`
