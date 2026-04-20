import math
from statistics import mean, pstdev

from sklearn.ensemble import IsolationForest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.event import Event
from app.schemas.scoring import ScoreRequest, ScoreResponse


class ScoringService:
    """Computes anomaly scores using Z-score + Isolation Forest."""

    def __init__(self, db: Session):
        self.db = db

    def _extract_value(self, payload: dict) -> float:
        raw = payload.get("value", 0.0)
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    def _load_history(self, limit: int = 500) -> list[float]:
        stmt = select(Event.value).order_by(Event.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def _z_score(self, value: float, history: list[float]) -> float:
        if len(history) < 2:
            return 0.0
        mu = mean(history)
        sigma = pstdev(history)
        if sigma == 0:
            return 0.0
        return (value - mu) / sigma

    def _isolation_score(self, value: float, history: list[float]) -> float:
        if len(history) < 20:
            return 0.0
        training = [[item] for item in history]
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(training)
        # Higher positive number means more anomalous for our API.
        raw = -float(model.score_samples([[value]])[0])
        return min(max(raw, 0.0), 1.0)

    def score_payload(self, payload: ScoreRequest) -> ScoreResponse:
        value = self._extract_value(payload.payload)
        history = self._load_history()
        z_value = self._z_score(value, history)
        z_score = min(abs(z_value) / 3.0, 1.0)
        iso_score = self._isolation_score(value, history)
        combined = round((0.6 * z_score) + (0.4 * iso_score), 4)
        is_anomalous = combined >= settings.ANOMALY_THRESHOLD or abs(z_value) >= 3.0

        return ScoreResponse(
            z_score=round(z_score, 4),
            isolation_score=round(iso_score, 4),
            combined_score=combined,
            is_anomalous=is_anomalous,
            explanation=(
                f"value={value:.3f}; z={z_value:.3f}; "
                f"threshold={settings.ANOMALY_THRESHOLD}; combined={combined:.3f}"
            ),
        )


def score_severity(combined_score: float) -> str:
    if combined_score >= 0.9:
        return "critical"
    if combined_score >= 0.8:
        return "high"
    if combined_score >= 0.6:
        return "medium"
    return "low"
