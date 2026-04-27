from __future__ import annotations

import threading
from datetime import datetime, timezone

from sqlalchemy import func, select

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.anomaly_score import AnomalyScore

logger = get_logger(__name__)


class BackgroundJobRunner:
    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, name="pulse-background-jobs", daemon=True
        )
        self._thread.start()
        logger.info("background_jobs_started interval_seconds=%s", self.interval_seconds)

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        logger.info("background_jobs_stopped")

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._run_detector_refresh_hook()
            self._run_drift_hook()
            self._stop.wait(self.interval_seconds)

    def _run_detector_refresh_hook(self) -> None:
        logger.info("detector_refresh_hook status=ok at=%s", datetime.now(timezone.utc).isoformat())

    def _run_drift_hook(self) -> None:
        db = SessionLocal()
        try:
            last_hour = datetime.now(timezone.utc).replace(tzinfo=None)
            anomalous_count = db.scalar(
                select(func.count(AnomalyScore.id)).where(AnomalyScore.is_anomalous.is_(True))
            )
            logger.info("drift_hook anomalies_total=%s ts=%s", anomalous_count or 0, last_hour)
        finally:
            db.close()
