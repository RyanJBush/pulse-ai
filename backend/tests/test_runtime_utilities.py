import pytest
from fastapi import HTTPException

import app.main as main_module
from app.core.auth import require_role
from app.core.background_jobs import BackgroundJobRunner
from app.core.cache import TTLCache
from app.db import session as session_module


def test_ttl_cache_set_get_expire_and_invalidate():
    cache = TTLCache[int](ttl_seconds=0)
    cache.set("k1", 7)
    assert cache.get("k1") is None

    cache = TTLCache[int](ttl_seconds=30)
    cache.set("k1", 1)
    cache.set("k2", 2)
    assert cache.get("k1") == 1
    assert cache.get("missing") is None

    cache.invalidate("k1")
    assert cache.get("k1") is None
    assert cache.get("k2") == 2

    cache.invalidate()
    assert cache.get("k2") is None


def test_require_role_validates_and_authorizes():
    guard = require_role("admin", "operator")
    assert guard(" ADMIN ") == "admin"

    with pytest.raises(HTTPException) as invalid:
        guard("unknown-role")
    assert invalid.value.status_code == 400
    assert invalid.value.detail == "invalid role header"

    with pytest.raises(HTTPException) as forbidden:
        guard("viewer")
    assert forbidden.value.status_code == 403
    assert forbidden.value.detail == "insufficient role"


def test_get_db_closes_session(monkeypatch):
    class FakeDB:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(session_module, "SessionLocal", lambda: fake_db)

    generator = session_module.get_db()
    yielded = next(generator)
    assert yielded is fake_db
    generator.close()
    assert fake_db.closed is True


def test_background_job_runner_lifecycle_and_drift_hook(monkeypatch):
    created_threads = []

    class FakeThread:
        def __init__(self, *, target, name, daemon):
            self.target = target
            self.name = name
            self.daemon = daemon
            self.started = False
            self.joined = False
            self.alive = False
            created_threads.append(self)

        def start(self):
            self.started = True
            self.alive = True

        def is_alive(self):
            return self.alive

        def join(self, timeout):
            self.joined = True
            self.alive = False

    class FakeDB:
        def __init__(self):
            self.closed = False
            self.scalar_calls = 0

        def scalar(self, _query):
            self.scalar_calls += 1
            return 3

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    log_messages = []

    monkeypatch.setattr("app.core.background_jobs.threading.Thread", FakeThread)
    monkeypatch.setattr("app.core.background_jobs.SessionLocal", lambda: fake_db)
    monkeypatch.setattr(
        "app.core.background_jobs.logger.info",
        lambda message, *args: log_messages.append(message % args if args else message),
    )

    runner = BackgroundJobRunner(interval_seconds=1)
    runner.start()
    assert len(created_threads) == 1
    assert created_threads[0].started is True
    assert created_threads[0].name == "pulse-background-jobs"
    runner.start()
    assert len(created_threads) == 1

    runner._run_drift_hook()
    assert fake_db.scalar_calls == 1
    assert fake_db.closed is True
    assert any("drift_hook anomalies_total=3" in message for message in log_messages)

    runner.stop()
    assert created_threads[0].joined is True


def test_background_job_runner_loop_and_refresh_hook(monkeypatch):
    runner = BackgroundJobRunner(interval_seconds=1)
    calls = {"refresh": 0, "drift": 0}
    messages = []

    monkeypatch.setattr(runner, "_run_detector_refresh_hook", lambda: calls.__setitem__("refresh", 1))
    monkeypatch.setattr(runner, "_run_drift_hook", lambda: calls.__setitem__("drift", 1))
    monkeypatch.setattr(runner._stop, "wait", lambda _interval: runner._stop.set())
    runner._loop()
    assert calls == {"refresh": 1, "drift": 1}

    monkeypatch.setattr(
        "app.core.background_jobs.logger.info",
        lambda message, *args: messages.append(message % args if args else message),
    )
    runner._run_detector_refresh_hook()
    assert any("detector_refresh_hook status=ok" in message for message in messages)


@pytest.mark.anyio
async def test_lifespan_runs_startup_and_shutdown(monkeypatch):
    create_all_called = False
    start_called = False
    stop_called = False

    def fake_create_all(*, bind):
        nonlocal create_all_called
        create_all_called = bind is main_module.engine

    def fake_start():
        nonlocal start_called
        start_called = True

    def fake_stop():
        nonlocal stop_called
        stop_called = True

    monkeypatch.setattr(main_module.Base.metadata, "create_all", fake_create_all)
    monkeypatch.setattr(main_module.background_jobs, "start", fake_start)
    monkeypatch.setattr(main_module.background_jobs, "stop", fake_stop)

    async with main_module.lifespan(main_module.app):
        assert create_all_called is True
        assert start_called is True
    assert stop_called is True


def test_ready_and_rate_limit_paths(client, monkeypatch):
    main_module._rate_limiter.clear()
    monkeypatch.setattr(main_module.settings, "RATE_LIMIT_PER_MINUTE", 2)

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}

    first = client.get("/health")
    second = client.get("/health")
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.text == "rate limit exceeded"

    main_module._rate_limiter["testclient"] = (100, -1)
    reset = client.get("/health")
    assert reset.status_code == 200
