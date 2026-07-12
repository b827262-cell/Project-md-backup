"""Tests for the Telegram notifier."""

from __future__ import annotations

import io
from urllib.error import HTTPError

from backend.notifiers.telegram import TelegramNotifier


class _DummyResponse:
    def __init__(self, body: str, code: int = 200) -> None:
        self._body = body
        self._code = code

    def read(self) -> bytes:
        return self._body.encode("utf-8")

    def getcode(self) -> int:
        return self._code

    def __enter__(self) -> _DummyResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_send_message_succeeds(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")
    monkeypatch.setattr(
        "backend.notifiers.telegram.urlopen",
        lambda *args, **kwargs: _DummyResponse('{"ok": true, "result": {}}'),
    )

    assert notifier.send_message("hello world") is True


def test_send_message_handles_http_error(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")

    def fake_urlopen(*args, **kwargs):
        raise HTTPError(
            url="https://api.telegram.org/bottoken/sendMessage",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=io.BytesIO(b'{"ok": false, "description": "Too Many Requests"}'),
        )

    monkeypatch.setattr("backend.notifiers.telegram.urlopen", fake_urlopen)

    assert notifier.send_message("hello world") is False


def test_send_message_respects_cooldown(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")
    notifier.cooldown_seconds = 60
    monkeypatch.setattr(
        "backend.notifiers.telegram.urlopen",
        lambda *args, **kwargs: _DummyResponse('{"ok": true, "result": {}}'),
    )

    assert notifier.send_message("first") is True
    assert notifier.send_message("second") is False
