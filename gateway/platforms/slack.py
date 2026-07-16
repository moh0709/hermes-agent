"""Compatibility shim for the Slack gateway module path.

The real Slack adapter lives in ``plugins.platforms.slack.adapter``.  This
module preserves legacy imports like ``import gateway.platforms.slack`` without
pulling the heavy Slack plugin in eagerly at gateway startup.

It is intentionally tiny and lazy:

- importing this module does *not* import the Slack plugin;
- attribute access loads the plugin on demand;
- ``register(ctx)`` forwards to the plugin's registration entry point.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "SlackAdapter",
    "SLACK_AVAILABLE",
    "check_slack_requirements",
    "interactive_setup",
    "register",
    "_standalone_send",
]

_LAZY_EXPORTS = {
    "SlackAdapter",
    "SLACK_AVAILABLE",
    "check_slack_requirements",
    "interactive_setup",
    "_standalone_send",
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from plugins.platforms.slack.adapter import (  # local import on purpose
        SLACK_AVAILABLE,
        SlackAdapter,
        _standalone_send,
        check_slack_requirements,
        interactive_setup,
    )

    exports = {
        "SlackAdapter": SlackAdapter,
        "SLACK_AVAILABLE": SLACK_AVAILABLE,
        "check_slack_requirements": check_slack_requirements,
        "interactive_setup": interactive_setup,
        "_standalone_send": _standalone_send,
    }
    return exports[name]


def register(ctx) -> None:
    """Forward the legacy gateway entry point to the bundled Slack plugin."""
    from plugins.platforms.slack.adapter import register as plugin_register

    plugin_register(ctx)


def __dir__() -> list[str]:
    return sorted(__all__)
