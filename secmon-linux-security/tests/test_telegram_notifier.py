"""Tests for the Telegram notifier."""

from __future__ import annotations

import io
import json
from urllib.error import HTTPError, URLError

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


def test_send_message_handles_ok_false(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")
    monkeypatch.setattr(
        "backend.notifiers.telegram.urlopen",
        lambda *args, **kwargs: _DummyResponse(
            '{"ok": false, "description": "Bad Request"}',
            code=400,
        ),
    )

    assert notifier.send_message("hello world") is False


def test_send_message_handles_malformed_json(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")
    monkeypatch.setattr(
        "backend.notifiers.telegram.urlopen",
        lambda *args, **kwargs: _DummyResponse("not-json"),
    )

    assert notifier.send_message("hello world") is False


def test_send_message_handles_timeout(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")

    def fake_urlopen(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr("backend.notifiers.telegram.urlopen", fake_urlopen)

    assert notifier.send_message("hello world") is False


def test_send_message_truncates_long_message(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _DummyResponse('{"ok": true, "result": {}}')

    monkeypatch.setattr("backend.notifiers.telegram.urlopen", fake_urlopen)

    assert notifier.send_message("x" * 5000) is True
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert len(payload["text"]) == TelegramNotifier.max_message_length
    assert captured["timeout"] == notifier.timeout_seconds


def test_send_message_handles_network_error(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")

    def fake_urlopen(*args, **kwargs):
        raise URLError("dns failure")

    monkeypatch.setattr("backend.notifiers.telegram.urlopen", fake_urlopen)

    assert notifier.send_message("hello world") is False
