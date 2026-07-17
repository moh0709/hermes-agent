# EAI-HERMES-039B — Live Telegram gateway isolation

## Root cause
The live gateway was loading the dynamic webhook route `github-ready-issues` with `deliver: telegram`. That route is a webhook-intake path for GitHub issue automation, but Telegram is a human chat surface. As a result, the gateway could surface webhook-style prompts in Telegram sessions instead of keeping webhook handling isolated.

## Fix
- Added a runtime guard in `gateway/platforms/webhook.py` so GitHub issue intake routes that target Telegram are normalized to `deliver: log` during route reload/validation.
- Added a regression test in `tests/gateway/test_webhook_dynamic_routes.py` to prove the Telegram-delivery GitHub issue route is coerced away from Telegram.
- Updated the `webhook-subscriptions` skill so the GitHub issue example no longer recommends Telegram delivery for autonomous issue runners.

## Runtime/configuration change
- The live gateway restart reloaded the dynamic subscription file and logged the normalization:
  - `github-ready-issues` → forced from `telegram` to `log`
- The gateway was restarted under systemd so the new code path and dynamic-route normalization took effect.

## Verification
- Gateway restart completed and the new process is active.
- Gateway startup log now contains the warning that the GitHub issue route is forced to `log` delivery.
- The webhook adapter still loads the route, but Telegram is no longer the delivery target.

## Git push status
- Local commit: `f89de08123fc09268f7e8861471e0770d2245177`
- Push to upstream `origin/main` was blocked by GitHub permissions (`403`)
- Push to the personal fork was also blocked by GitHub workflow-scoped permissions on the repository

## Remaining limitations
- The webhook route still exists for autonomous issue handling, but it no longer emits into Telegram chat.
- WhatsApp reconnect attempts were still timing out during startup; that is unrelated to this fix.
