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

_SLACK_ADAPTER_IMPORT = "plugins.platforms.slack.adapter"


def _load_slack_plugin() -> Any:
    try:
        from plugins.platforms.slack.adapter import (  # local import on purpose
            SLACK_AVAILABLE,
            SlackAdapter,
            _standalone_send,
            check_slack_requirements,
            interactive_setup,
            register as plugin_register,
        )
    except ImportError as exc:
        missing_name = getattr(exc, "name", "") or ""
        missing_text = str(exc)
        if missing_name.startswith("plugins.platforms.slack") or _SLACK_ADAPTER_IMPORT in missing_text:
            raise RuntimeError(
                "Slack platform is enabled, but its adapter module could not be "
                f"imported ({_SLACK_ADAPTER_IMPORT}). Disable Slack or install the "
                "Slack adapter dependencies before enabling the platform."
            ) from exc
        raise

    return {
        "SlackAdapter": SlackAdapter,
        "SLACK_AVAILABLE": SLACK_AVAILABLE,
        "check_slack_requirements": check_slack_requirements,
        "interactive_setup": interactive_setup,
        "_standalone_send": _standalone_send,
        "register": plugin_register,
    }


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    return _load_slack_plugin()[name]


def register(ctx) -> None:
    """Forward the legacy gateway entry point to the bundled Slack plugin."""
    plugin_register = _load_slack_plugin()["register"]
    plugin_register(ctx)


def __dir__() -> list[str]:
    return sorted(__all__)
