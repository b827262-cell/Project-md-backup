"""Tests for the production collector loop entry point."""

from __future__ import annotations

from types import SimpleNamespace

from backend.collectors import main as collector_main


class _FakeStopEvent:
    def __init__(self, wait_results: list[bool]) -> None:
        self.wait_results = list(wait_results)
        self.wait_calls: list[float] = []
        self.cleared = False
        self.set_called = False

    def clear(self) -> None:
        self.cleared = True
        self.set_called = False

    def set(self) -> None:
        self.set_called = True

    def is_set(self) -> bool:
        return self.set_called

    def wait(self, timeout: float) -> bool:
        self.wait_calls.append(timeout)
        if self.wait_results:
            return self.wait_results.pop(0)
        return True


class _FakeCollector:
    def __init__(self, **kwargs) -> None:
        self.database_path = kwargs["database_path"]
        self.cursor_position_file = kwargs["cursor_path"]
        self.notifier = kwargs.get("notifier")
        self.collect_calls: list[str] = []
        self._outcomes = [RuntimeError("transient failure"), (1, 1)]

    def collect_from_file(self, log_file_path: str) -> tuple[int, int]:
        self.collect_calls.append(log_file_path)
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_install_signal_handlers_registers_sigterm_and_sigint(monkeypatch) -> None:
    calls: list[tuple[int, object]] = []

    def fake_signal(signum, handler):
        calls.append((signum, handler))

    monkeypatch.setattr(collector_main.signal, "signal", fake_signal)

    collector_main._install_signal_handlers()

    assert [signum for signum, _handler in calls] == [
        collector_main.signal.SIGTERM,
        collector_main.signal.SIGINT,
    ]
    assert calls[0][1] is calls[1][1]


def test_run_collector_loop_continues_after_recoverable_error_and_uses_min_interval(
    monkeypatch, tmp_path
) -> None:
    log_path = tmp_path / "auth.log"
    log_path.write_text(
        "Jul 10 17:30:45 host sshd[1]: Failed password for root from "
        "192.0.2.1 port 22 ssh2\n",
        encoding="utf-8",
    )

    settings = SimpleNamespace(
        database_path=tmp_path / "secmon.db",
        ssh_cursor_path=tmp_path / "cursor.position",
        ssh_log_path=log_path,
        collect_interval_seconds=0.1,
        log_level="INFO",
        telegram_enabled=False,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )
    fake_stop_event = _FakeStopEvent([False, True])
    fake_collector = _FakeCollector(
        database_path=settings.database_path,
        cursor_path=settings.ssh_cursor_path,
        notifier=None,
    )

    monkeypatch.setattr(collector_main, "get_settings", lambda: settings)
    monkeypatch.setattr(collector_main, "_STOP_EVENT", fake_stop_event)
    monkeypatch.setattr(collector_main, "_install_signal_handlers", lambda: None)
    monkeypatch.setattr(collector_main, "SSHCollector", lambda **kwargs: fake_collector)

    result = collector_main.run_collector_loop()

    assert result == 0
    assert fake_stop_event.cleared is True
    assert fake_collector.collect_calls == [str(log_path), str(log_path)]
    assert len(fake_stop_event.wait_calls) == 2
    assert all(timeout >= 0.5 for timeout in fake_stop_event.wait_calls)


def test_run_collector_loop_returns_nonzero_when_initialization_fails(
    monkeypatch, tmp_path
) -> None:
    log_path = tmp_path / "auth.log"
    log_path.write_text(
        "Jul 10 17:30:45 host sshd[1]: Failed password for root from "
        "192.0.2.1 port 22 ssh2\n",
        encoding="utf-8",
    )

    settings = SimpleNamespace(
        database_path=tmp_path / "secmon.db",
        ssh_cursor_path=tmp_path / "cursor.position",
        ssh_log_path=log_path,
        collect_interval_seconds=5.0,
        log_level="INFO",
        telegram_enabled=True,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )

    monkeypatch.setattr(collector_main, "get_settings", lambda: settings)
    monkeypatch.setattr(collector_main, "_STOP_EVENT", _FakeStopEvent([True]))
    monkeypatch.setattr(collector_main, "_install_signal_handlers", lambda: None)

    result = collector_main.run_collector_loop()

    assert result == 1


def test_missing_log_is_recoverable_and_each_round_calls_collector(
    monkeypatch, tmp_path
) -> None:
    missing_log = tmp_path / "missing-auth.log"
    settings = SimpleNamespace(
        database_path=tmp_path / "secmon.db",
        ssh_cursor_path=tmp_path / "cursor.position",
        ssh_log_path=missing_log,
        collect_interval_seconds=5.0,
        log_level="INFO",
        telegram_enabled=False,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )
    fake_stop_event = _FakeStopEvent([False, True])
    fake_collector = _FakeCollector(
        database_path=settings.database_path,
        cursor_path=settings.ssh_cursor_path,
        notifier=None,
    )

    monkeypatch.setattr(collector_main, "get_settings", lambda: settings)
    monkeypatch.setattr(collector_main, "_STOP_EVENT", fake_stop_event)
    monkeypatch.setattr(collector_main, "_install_signal_handlers", lambda: None)
    monkeypatch.setattr(collector_main, "SSHCollector", lambda **kwargs: fake_collector)

    assert collector_main.run_collector_loop() == 0
    assert fake_collector.collect_calls == [str(missing_log), str(missing_log)]
    assert all(
        timeout >= collector_main._MIN_SLEEP_SECONDS for timeout in fake_stop_event.wait_calls
    )


def test_production_loop_rejects_repository_var_paths(monkeypatch, tmp_path) -> None:
    settings = SimpleNamespace(
        environment="production",
        database_path="./var/secmon.db",
        ssh_cursor_path="./var/cursor.position",
        ssh_log_path=tmp_path / "auth.log",
        collect_interval_seconds=5.0,
        log_level="INFO",
        telegram_enabled=False,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )
    monkeypatch.setattr(collector_main, "get_settings", lambda: settings)
    monkeypatch.setattr(collector_main, "_STOP_EVENT", _FakeStopEvent([True]))
    monkeypatch.setattr(collector_main, "_install_signal_handlers", lambda: None)

    assert collector_main.run_collector_loop() == 1
