#!/usr/bin/env python3
"""Runtime mode detector for GitHub-driven scripts.

Supported outcomes are intentionally narrow:

- POLLING: started by the task-poller path and should poll GitHub directly.
- WEBHOOK: started by a webhook receiver and may inspect a payload source.
- UNKNOWN: the launcher did not provide enough information to choose.

The detector is intentionally explicit. It does *not* infer polling from the
absence of webhook variables. Launchers must state their mode.
"""

from __future__ import annotations

import json
import os
from enum import Enum
from typing import Mapping, Optional


class RuntimeMode(str, Enum):
    POLLING = "POLLING"
    WEBHOOK = "WEBHOOK"
    UNKNOWN = "UNKNOWN"


_TRUE_VALUES = {"1", "true", "yes", "on", "polling", "webhook"}
_FALSE_VALUES = {"0", "false", "no", "off", ""}


def _truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    if normalized in _FALSE_VALUES:
        return False
    if normalized in _TRUE_VALUES:
        return True
    return bool(normalized)


def _mode_from_explicit_value(value: Optional[str]) -> RuntimeMode:
    if value is None:
        return RuntimeMode.UNKNOWN
    normalized = value.strip().upper()
    if normalized == RuntimeMode.POLLING.value:
        return RuntimeMode.POLLING
    if normalized == RuntimeMode.WEBHOOK.value:
        return RuntimeMode.WEBHOOK
    if normalized == RuntimeMode.UNKNOWN.value:
        return RuntimeMode.UNKNOWN
    return RuntimeMode.UNKNOWN


def detect_runtime_mode(env: Mapping[str, str] | None = None) -> RuntimeMode:
    """Detect the runtime mode from explicit startup signals.

    Priority order:
      1. ``HERMES_RUNTIME_MODE`` when set to POLLING/WEBHOOK/UNKNOWN.
      2. Polling launch flags such as ``TASK_POLLER``.
      3. Webhook payload sources such as ``GITHUB_EVENT_PATH``.
      4. UNKNOWN when nothing explicit is present.
    """
    data = os.environ if env is None else env

    explicit_raw = data.get("HERMES_RUNTIME_MODE")
    if explicit_raw is not None:
        return _mode_from_explicit_value(explicit_raw)

    if _truthy(data.get("TASK_POLLER")):
        return RuntimeMode.POLLING

    if data.get("GITHUB_EVENT_PATH") or data.get("HERMES_GITHUB_EVENT_PATH") or data.get("WEBHOOK_PAYLOAD_PATH"):
        return RuntimeMode.WEBHOOK

    if _truthy(data.get("WEBHOOK_RECEIVER")) or _truthy(data.get("HERMES_WEBHOOK_RECEIVER")):
        return RuntimeMode.WEBHOOK

    return RuntimeMode.UNKNOWN


def runtime_mode_error(
    mode: RuntimeMode,
    *,
    reason: str,
    detector: str = "detect_runtime_mode",
) -> str:
    """Return a machine-readable error payload for startup failures."""
    payload = {
        "error": "unknown_runtime_mode" if mode is RuntimeMode.UNKNOWN else "runtime_mode_mismatch",
        "detector": detector,
        "mode": mode.value,
        "reason": reason,
        "supported_modes": [RuntimeMode.POLLING.value, RuntimeMode.WEBHOOK.value, RuntimeMode.UNKNOWN.value],
    }
    return json.dumps(payload, sort_keys=True)
