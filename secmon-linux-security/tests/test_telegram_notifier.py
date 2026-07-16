"""Tests for the Telegram notifier."""

from __future__ import annotations

import io
import json
import logging
import socket
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import pytest
from pydantic import SecretStr

from backend.notifiers import telegram as telegram_module
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


@pytest.mark.parametrize("status_code", [400, 401, 429, 500])
def test_send_message_rejects_required_http_statuses(monkeypatch, status_code: int) -> None:
    notifier = TelegramNotifier("token", "-1008350114645")

    def fake_urlopen(*args, **kwargs):
        raise HTTPError(
            url="https://api.telegram.org/bottoken/sendMessage",
            code=status_code,
            msg="Telegram failure",
            hdrs=None,
            fp=io.BytesIO(b'{"ok": false}'),
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


def test_send_message_handles_dns_error_without_secret_logging(caplog, monkeypatch) -> None:
    secret = "token-that-must-not-be-logged"
    notifier = TelegramNotifier(secret, "8350114645")

    def fake_urlopen(*args, **kwargs):
        raise URLError(socket.gaierror("name resolution failed"))

    monkeypatch.setattr("backend.notifiers.telegram.urlopen", fake_urlopen)
    with caplog.at_level(logging.WARNING, logger="backend.notifiers.telegram"):
        assert notifier.send_message("private body") is False

    assert secret not in caplog.text
    assert "api.telegram.org/bot" not in caplog.text
    assert "private body" not in caplog.text


def test_secretstr_is_retrieved_only_by_notifier_constructor() -> None:
    secret = SecretStr("constructor-only-token")
    notifier = TelegramNotifier(secret, "8350114645")

    assert "constructor-only-token" not in repr(notifier)
    assert notifier._api_url().startswith("https://api.telegram.org/bot")


def test_request_uses_https_chat_id_and_timeout(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "-1008350114645", timeout_seconds=2.5)
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _DummyResponse('{"ok": true, "result": {}}')

    monkeypatch.setattr("backend.notifiers.telegram.urlopen", fake_urlopen)

    assert notifier.send_message("hello") is True
    assert str(captured["url"]).startswith("https://")
    assert captured["timeout"] == 2.5
    assert captured["payload"]["chat_id"] == "-1008350114645"


def test_insecure_endpoint_is_rejected_without_network_call(monkeypatch) -> None:
    notifier = TelegramNotifier("token", "8350114645")
    calls = 0

    def fake_urlopen(*args, **kwargs):
        nonlocal calls
        calls += 1
        return _DummyResponse('{"ok": true}')

    monkeypatch.setattr("backend.notifiers.telegram.urlopen", fake_urlopen)
    monkeypatch.setattr(notifier, "_api_url", lambda: "http://api.telegram.org/bottoken/sendMessage")

    assert notifier.send_message("hello") is False
    assert calls == 0


def test_disabled_cli_makes_zero_network_calls(monkeypatch) -> None:
    calls = 0

    def fake_urlopen(*args, **kwargs):
        nonlocal calls
        calls += 1
        return _DummyResponse('{"ok": true}')

    monkeypatch.setattr(telegram_module, "get_settings", lambda: SimpleNamespace(
        telegram_enabled=False,
        telegram_bot_token=SecretStr("disabled-token"),
        telegram_chat_id="8350114645",
    ))
    monkeypatch.setattr(telegram_module, "urlopen", fake_urlopen)

    assert telegram_module.main(["--test"]) == 1
    assert calls == 0
