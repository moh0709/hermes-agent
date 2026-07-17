"""Tests for the GitHub watcher runtime-mode detector."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "optional-skills" / "devops" / "watchers" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from runtime_mode import RuntimeMode, detect_runtime_mode, runtime_mode_error  # type: ignore


def test_explicit_polling_wins_over_webhook_payload():
    env = {
        "TASK_POLLER": "1",
        "GITHUB_EVENT_PATH": "/tmp/event.json",
    }
    assert detect_runtime_mode(env) is RuntimeMode.POLLING


def test_webhook_detected_from_payload_path():
    env = {"GITHUB_EVENT_PATH": "/tmp/event.json"}
    assert detect_runtime_mode(env) is RuntimeMode.WEBHOOK


def test_explicit_runtime_mode_overrides_other_signals():
    env = {
        "HERMES_RUNTIME_MODE": "webhook",
        "TASK_POLLER": "1",
        "GITHUB_EVENT_PATH": "/tmp/event.json",
    }
    assert detect_runtime_mode(env) is RuntimeMode.WEBHOOK


def test_unknown_runtime_mode_stays_unknown():
    assert detect_runtime_mode({}) is RuntimeMode.UNKNOWN


def test_unknown_runtime_mode_error_is_machine_readable():
    payload = json.loads(
        runtime_mode_error(
            RuntimeMode.UNKNOWN,
            reason="missing startup signal",
        )
    )
    assert payload == {
        "detector": "detect_runtime_mode",
        "error": "unknown_runtime_mode",
        "mode": "UNKNOWN",
        "reason": "missing startup signal",
        "supported_modes": ["POLLING", "WEBHOOK", "UNKNOWN"],
    }
