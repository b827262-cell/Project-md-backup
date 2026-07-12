"""Production loop for the SecMon SSH collector."""

from __future__ import annotations

import logging
import signal
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import TypeVar, cast

from backend.collectors.ssh_collector import SSHCollector
from backend.config import Settings, get_settings
from backend.notifiers import TelegramNotifier

logger = logging.getLogger(__name__)
_STOP_EVENT = Event()
_MIN_SLEEP_SECONDS = 0.5
T = TypeVar("T")


def _configure_logging(level_name: str) -> None:
    if logging.getLogger().handlers:
        logging.getLogger().setLevel(level_name)
        return
    logging.basicConfig(
        level=level_name,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _setting_value(settings: object, name: str, default: T) -> T:
    if isinstance(settings, Settings):
        return cast(T, getattr(settings, name))
    return cast(T, vars(settings).get(name, default))


def _install_signal_handlers() -> None:
    def _handle_signal(signum: int, _frame: object) -> None:
        logger.info("Received signal %s, stopping collector loop", signum)
        _STOP_EVENT.set()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)


def _build_notifier(settings: Settings) -> TelegramNotifier | None:
    if not bool(_setting_value(settings, "telegram_enabled", False)):
        return None
    bot_token = _setting_value(settings, "telegram_bot_token", None)
    chat_id = _setting_value(settings, "telegram_chat_id", None)
    if not bot_token or not chat_id:
        raise ValueError("Telegram is enabled but bot token or chat id is missing")
    notifier = TelegramNotifier(
        str(bot_token),
        str(chat_id),
        timeout_seconds=float(_setting_value(settings, "telegram_timeout_seconds", 5.0)),
    )
    notifier.cooldown_seconds = int(_setting_value(settings, "telegram_cooldown_seconds", 60))
    return notifier


def run_collector_loop() -> int:
    settings = get_settings()
    _configure_logging(str(_setting_value(settings, "log_level", "INFO")))
    _STOP_EVENT.clear()
    _install_signal_handlers()

    try:
        notifier = _build_notifier(settings)
        collector = SSHCollector(
            notifier=notifier,
            cursor_path=Path(
                _setting_value(
                    settings,
                    "ssh_cursor_path",
                    "./var/ssh_cursor.position",
                )
            ),
            database_path=Path(_setting_value(settings, "database_path", "./var/secmon.db")),
        )
    except Exception:
        logger.exception("Failed to initialize the SSH collector")
        return 1

    poll_interval = max(
        float(_setting_value(settings, "collect_interval_seconds", 5.0)),
        _MIN_SLEEP_SECONDS,
    )
    log_path = Path(_setting_value(settings, "ssh_log_path", "/var/log/auth.log"))

    logger.info(
        "Starting SecMon SSH collector loop (log_path=%s, db=%s, cursor=%s, interval=%.1fs)",
        log_path,
        collector.database_path,
        collector.cursor_position_file,
        poll_interval,
    )

    while not _STOP_EVENT.is_set():
        round_start = time.monotonic()
        started_at = datetime.now().isoformat(timespec="seconds")
        try:
            if not log_path.exists():
                logger.warning("SSH log file not found at %s", log_path)
                new_events = 0
                new_attackers = 0
            else:
                new_events, new_attackers = collector.collect_from_file(str(log_path))
            duration = time.monotonic() - round_start
            next_poll = max(poll_interval - duration, _MIN_SLEEP_SECONDS)
            logger.info(
                "SSH collection round start=%s new_events=%d new_attackers=%d "
                "duration=%.3fs next_poll=%.3fs",
                started_at,
                new_events,
                new_attackers,
                duration,
                next_poll,
            )
        except (sqlite3.Error, ValueError) as exc:
            logger.exception("Unrecoverable collector error: %s", exc)
            return 1
        except Exception as exc:
            logger.warning("Recoverable collection error: %s", exc, exc_info=True)
            duration = time.monotonic() - round_start
            next_poll = max(poll_interval - duration, _MIN_SLEEP_SECONDS)

        if _STOP_EVENT.wait(next_poll):
            break

    logger.info("SecMon SSH collector loop stopped")
    return 0


def main() -> int:
    return run_collector_loop()


if __name__ == "__main__":
    raise SystemExit(main())
