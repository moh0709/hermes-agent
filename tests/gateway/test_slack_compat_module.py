"""Regression tests for the legacy ``gateway.platforms.slack`` shim.

The live gateway failure reported by the PM was ``No module named
'gateway.platforms.slack'``.  The gateway must be able to import this legacy
module path even though the real Slack adapter now lives under
``plugins.platforms.slack.adapter``.
"""

from __future__ import annotations

import builtins
import importlib
import sys


class TestGatewaySlackCompatModule:
    def test_import_does_not_eagerly_load_plugin(self, monkeypatch):
        original_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith("plugins.platforms.slack"):
                raise AssertionError("Slack plugin should not be imported during gateway.platforms.slack import")
            return original_import(name, globals, locals, fromlist, level)

        monkeypatch.delitem(sys.modules, "gateway.platforms.slack", raising=False)
        monkeypatch.setattr(builtins, "__import__", fake_import)

        module = importlib.import_module("gateway.platforms.slack")

        assert module.__name__ == "gateway.platforms.slack"
        assert "register" in module.__all__

    def test_register_forwards_to_slack_plugin(self, monkeypatch):
        module = importlib.import_module("gateway.platforms.slack")

        calls = []

        class FakeCtx:
            def register_platform(self, **kwargs):
                calls.append(kwargs)

        module.register(FakeCtx())

        assert calls, "register() should forward to the plugin and register slack"
        assert calls[0]["name"] == "slack"
        assert calls[0]["label"] == "Slack"
