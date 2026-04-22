from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean, pstdev

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.detector_config import DetectorConfig
from app.models.event import Event
from app.schemas.scoring import ScoreRequest, ScoreResponse


def score_severity(combined_score: float) -> str:
    if combined_score >= 0.9:
        return "critical"
    if combined_score >= 0.8:
        return "high"
    if combined_score >= 0.6:
        return "medium"
    return "low"


class ScoringService:
    """Computes multi-detector anomaly scores and dynamic thresholds."""

    _detector_profiles: dict[str, dict[str, float]] = {
        "latency": {"z_score": 0.3, "isolation": 0.35, "rolling": 0.25, "seasonal": 0.1},
        "cpu": {"z_score": 0.35, "isolation": 0.35, "rolling": 0.2, "seasonal": 0.1},
        "error_rate": {"z_score": 0.4, "isolation": 0.25, "rolling": 0.25, "seasonal": 0.1},
        "default": {"z_score": 0.3, "isolation": 0.3, "rolling": 0.25, "seasonal": 0.15},
    }

    def __init__(self, db: Session):
        self.db = db

    def _extract_value(self, payload: dict) -> float:
        raw = payload.get("value", 0.0)
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    def _load_history(
        self, source: str, workspace_id: str, signal_type: str, entity_id: str, limit: int = 500
    ) -> list[tuple[float, datetime]]:
        stmt = (
            select(Event.value, Event.event_timestamp)
            .where(Event.source == source)
            .where(Event.workspace_id == workspace_id)
            .where(Event.signal_type == signal_type)
            .where(Event.entity_id == entity_id)
            .order_by(Event.event_timestamp.desc())
            .limit(limit)
        )
        return [(float(row.value), row.event_timestamp) for row in self.db.execute(stmt).all()]

    def _z_score(self, value: float, history: list[float]) -> tuple[float, float]:
        if len(history) < 2:
            return 0.0, 0.0
        mu = mean(history)
        sigma = pstdev(history)
        if sigma == 0:
            return 0.0, 0.0
        z_value = (value - mu) / sigma
        return z_value, min(abs(z_value) / 3.5, 1.0)

    def _isolation_score(self, value: float, history: list[float]) -> float:
        if len(history) < 20:
            return 0.0
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(np.array(history, dtype=float).reshape(-1, 1))
        raw = -float(model.score_samples(np.array([[value]], dtype=float))[0])
        return min(max(raw, 0.0), 1.0)

    def _rolling_score(self, value: float, history: list[float], window: int = 30) -> float:
        if len(history) < max(5, window // 2):
            return 0.0
        baseline = history[:window]
        high = float(np.percentile(baseline, 90))
        low = float(np.percentile(baseline, 10))
        spread = max(high - low, 1e-6)
        if value > high:
            return min((value - high) / spread, 1.0)
        if value < low:
            return min((low - value) / spread, 1.0)
        return 0.0

    def _seasonal_score(
        self, value: float, history_pairs: list[tuple[float, datetime]], timestamp: datetime
    ) -> float:
        if len(history_pairs) < 24:
            return 0.0
        minute_bucket = timestamp.minute
        seasonal_samples = [
            sample
            for sample, sample_ts in history_pairs
            if abs(sample_ts.minute - minute_bucket) <= 2
        ]
        if len(seasonal_samples) < 5:
            return 0.0
        seasonal_mean = mean(seasonal_samples)
        seasonal_sigma = pstdev(seasonal_samples) if len(seasonal_samples) > 1 else 0.0
        if seasonal_sigma <= 0:
            return 0.0
        return min(abs(value - seasonal_mean) / (3.0 * seasonal_sigma), 1.0)

    def _profile_for(self, signal_type: str) -> tuple[str, dict[str, float]]:
        normalized = signal_type.lower().strip()
        detector_config = self.db.scalars(
            select(DetectorConfig).where(DetectorConfig.signal_type == normalized)
        ).first()
        if detector_config and detector_config.enabled:
            return normalized, {
                "z_score": detector_config.z_weight,
                "isolation": detector_config.isolation_weight,
                "rolling": detector_config.rolling_weight,
                "seasonal": detector_config.seasonal_weight,
            }
        for key, profile in self._detector_profiles.items():
            if key != "default" and key in normalized:
                return key, profile
        return "default", self._detector_profiles["default"]

    def _dynamic_threshold(self, history: list[float], signal_type: str) -> float:
        base = settings.ANOMALY_THRESHOLD
        if len(history) < 10:
            return min(base + 0.05, 0.95)
        history_std = pstdev(history) if len(history) > 1 else 0.0
        history_mean = abs(mean(history)) if history else 1.0
        volatility = min(history_std / max(history_mean, 1e-6), 1.0)
        signal_adjustment = -0.03 if "error" in signal_type.lower() else 0.02
        threshold = base + (0.08 * volatility) + signal_adjustment
        return min(max(threshold, 0.55), 0.95)

    def score_payload(
        self, payload: ScoreRequest, event_timestamp: datetime | None = None
    ) -> ScoreResponse:
        signal_type = (payload.signal_type or payload.event_type).strip()
        value = self._extract_value(payload.payload)
        scored_at = event_timestamp or datetime.now(timezone.utc).replace(tzinfo=None)
        history_pairs = self._load_history(
            source=payload.source,
            workspace_id=payload.workspace_id,
            signal_type=signal_type,
            entity_id=payload.entity_id,
        )
        history = [sample for sample, _ in history_pairs]

        z_value, z_score = self._z_score(value, history)
        isolation_score = self._isolation_score(value, history)
        rolling_score = self._rolling_score(value, history)
        seasonal_score = self._seasonal_score(value, history_pairs, scored_at)

        profile_name, profile = self._profile_for(signal_type)
        detector_scores = {
            "z_score": round(z_score, 4),
            "isolation": round(isolation_score, 4),
            "rolling": round(rolling_score, 4),
            "seasonal": round(seasonal_score, 4),
        }
        weighted_combined = (
            (profile["z_score"] * z_score)
            + (profile["isolation"] * isolation_score)
            + (profile["rolling"] * rolling_score)
            + (profile["seasonal"] * seasonal_score)
        )
        combined = round(max(weighted_combined, max(detector_scores.values()) * 0.85), 4)
        dynamic_threshold = round(self._dynamic_threshold(history, signal_type), 4)
        confidence_score = round(min(1.0, 0.35 + (len(history) / 500) * 0.65), 4)
        is_anomalous = combined >= dynamic_threshold or abs(z_value) >= 3.0 or rolling_score >= 0.9

        reason_codes: list[str] = []
        if abs(z_value) >= 2.5:
            reason_codes.append("HIGH_Z_SCORE")
        if isolation_score >= 0.7:
            reason_codes.append("ISOLATION_OUTLIER")
        if rolling_score >= 0.7:
            reason_codes.append("ROLLING_THRESHOLD_BREACH")
        if seasonal_score >= 0.7:
            reason_codes.append("SEASONAL_BASELINE_SHIFT")
        if is_anomalous:
            reason_codes.append("DYNAMIC_THRESHOLD_BREACH")
        if not reason_codes:
            reason_codes.append("NO_STRONG_SIGNAL")

        severity = score_severity(combined)
        explanation = (
            f"value={value:.3f}; detector={profile_name}; combined={combined:.3f}; "
            f"threshold={dynamic_threshold:.3f}; confidence={confidence_score:.3f}; "
            f"reasons={','.join(reason_codes)}"
        )
        return ScoreResponse(
            z_score=round(z_score, 4),
            isolation_score=round(isolation_score, 4),
            rolling_score=round(rolling_score, 4),
            seasonal_score=round(seasonal_score, 4),
            detector_scores=detector_scores,
            selected_detector=profile_name,
            combined_score=combined,
            dynamic_threshold=dynamic_threshold,
            confidence_score=confidence_score,
            severity=severity,
            reason_codes=reason_codes,
            is_anomalous=is_anomalous,
            explanation=explanation,
        )
