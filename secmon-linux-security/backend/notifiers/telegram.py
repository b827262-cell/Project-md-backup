"""Telegram Bot API notifier for SecMon alerts."""

from __future__ import annotations

import argparse
import json
import logging
import socket
import sys
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import SecretStr

from backend.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _TelegramResponse:
    status_code: int
    payload: dict[str, Any] | None


class TelegramNotifier:
    """Send SecMon notifications to a Telegram chat."""

    max_message_length = 3500

    def __init__(
        self,
        bot_token: str | SecretStr,
        chat_id: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        token = (
            bot_token.get_secret_value()
            if isinstance(bot_token, SecretStr)
            else bot_token
        )
        if not token or not token.strip():
            raise ValueError("bot_token is required")
        if not chat_id or not chat_id.strip():
            raise ValueError("chat_id is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self._bot_token = token.strip()
        self.chat_id = chat_id.strip()
        self.timeout_seconds = timeout_seconds
        self.cooldown_seconds = 0
        self._last_sent_monotonic: float | None = None

    def send_message(self, text: str) -> bool:
        """Send a plain-text message to Telegram."""
        message = self._normalize_text(text)
        if not message:
            logger.warning("Telegram message is empty after normalization")
            return False

        if self._is_in_cooldown():
            logger.info("Telegram notification suppressed by cooldown")
            return False

        api_url = self._api_url()
        if not api_url.startswith("https://"):
            logger.warning("Telegram notification refused a non-HTTPS endpoint")
            return False

        request = Request(
            api_url,
            data=json.dumps(
                {
                    "chat_id": self.chat_id,
                    "text": message,
                    "disable_web_page_preview": True,
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            response = self._perform_request(request)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            logger.warning("Telegram sendMessage failed: %s", self._describe_error(exc))
            return False

        if not 200 <= response.status_code < 300:
            logger.warning("Telegram API request failed with HTTP status %s", response.status_code)
            return False

        if response.payload is None:
            logger.warning("Telegram API returned malformed JSON (status=%s)", response.status_code)
            return False

        if response.payload.get("ok") is not True:
            logger.warning("Telegram API reported failure (status=%s)", response.status_code)
            return False

        self._last_sent_monotonic = time.monotonic()
        return True

    def _perform_request(self, request: Request) -> _TelegramResponse:
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8", errors="replace")
                status_code = int(response.getcode() or 200)
        except HTTPError as exc:
            raw_body = exc.read().decode("utf-8", errors="replace")
            status_code = int(exc.code)
            return _TelegramResponse(
                status_code=status_code,
                payload=self._decode_payload(raw_body),
            )
        except TimeoutError:
            raise
        except URLError:
            raise
        except OSError:
            raise

        return _TelegramResponse(
            status_code=status_code,
            payload=self._decode_payload(raw_body),
        )

    @staticmethod
    def _decode_payload(raw_body: str) -> dict[str, Any] | None:
        try:
            decoded = json.loads(raw_body)
        except json.JSONDecodeError:
            return None
        return decoded if isinstance(decoded, dict) else None

    def _is_in_cooldown(self) -> bool:
        if self.cooldown_seconds <= 0:
            return False
        if self._last_sent_monotonic is None:
            return False
        return (time.monotonic() - self._last_sent_monotonic) < self.cooldown_seconds

    def _api_url(self) -> str:
        return f"https://api.telegram.org/bot{self._bot_token}/sendMessage"

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if len(normalized) > TelegramNotifier.max_message_length:
            normalized = normalized[: TelegramNotifier.max_message_length].rstrip()
        return normalized

    @staticmethod
    def _describe_error(exc: Exception) -> str:
        if isinstance(exc, HTTPError):
            return f"HTTP {exc.code}"
        if isinstance(exc, URLError):
            reason = getattr(exc, "reason", None)
            return f"network error: {reason}" if reason else "network error"
        if isinstance(exc, TimeoutError):
            return "timeout"
        if isinstance(exc, socket.gaierror):
            return "dns error"
        return exc.__class__.__name__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SecMon Telegram notifier")
    parser.add_argument("--test", action="store_true", help="Send a test notification")
    args = parser.parse_args(argv)

    settings = get_settings()
    settings_dict = vars(settings) if not isinstance(settings, Settings) else None

    def _setting_value(name: str, default: Any) -> Any:
        if isinstance(settings, Settings):
            return getattr(settings, name)
        assert settings_dict is not None
        return settings_dict.get(name, default)

    if not bool(_setting_value("telegram_enabled", False)):
        print("Telegram notifications are disabled.", file=sys.stderr)
        return 1

    bot_token = _setting_value("telegram_bot_token", None)
    chat_id = _setting_value("telegram_chat_id", None)
    if not bot_token or not chat_id:
        print("Missing Telegram bot token or chat id.", file=sys.stderr)
        return 1

    token_value = (
        bot_token.get_secret_value()
        if isinstance(bot_token, SecretStr)
        else str(bot_token)
    )
    notifier = TelegramNotifier(
        token_value,
        str(chat_id),
        timeout_seconds=float(_setting_value("telegram_timeout_seconds", 5.0)),
    )
    notifier.cooldown_seconds = int(_setting_value("telegram_cooldown_seconds", 60))

    if args.test:
        message = (
            "✅ SecMon Telegram notification test\n"
            f"Host: {socket.gethostname()}\n"
            "Status: connected"
        )
        if notifier.send_message(message):
            print("Telegram test notification sent.")
            return 0
        print("Telegram test notification failed.", file=sys.stderr)
        return 1

    print("No action specified. Use --test.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
