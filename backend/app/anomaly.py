from __future__ import annotations

import math
import statistics

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, AnomalyScore, Event


def _severity(score: float) -> str:
    if score >= 0.95:
        return "critical"
    if score >= 0.85:
        return "high"
    if score >= 0.7:
        return "medium"
    return "low"


def score_event(
    db: Session, event: Event, threshold: float = 0.8
) -> tuple[AnomalyScore, Alert | None]:
    if event.value is None:
        raise ValueError("event value is required for anomaly scoring")

    history_values = db.scalars(
        select(Event.value)
        .where(Event.source_id == event.source_id)
        .where(Event.value.is_not(None))
        .order_by(Event.created_at.desc())
        .limit(500)
    ).all()

    if not history_values:
        history_values = [event.value]

    mu = statistics.fmean(history_values)
    sigma = statistics.pstdev(history_values) if len(history_values) > 1 else 0.0
    z_score = abs((event.value - mu) / sigma) if sigma > 0 else 0.0

    if len(history_values) >= 10:
        model = IsolationForest(contamination="auto", random_state=42)
        arr = np.array(history_values, dtype=float).reshape(-1, 1)
        model.fit(arr)
        decision = float(model.decision_function(np.array([[event.value]], dtype=float))[0])
        isolation_score = 1.0 / (1.0 + math.exp(6 * decision))
    else:
        isolation_score = min(z_score / 6.0, 1.0)

    combined_score = min(1.0, 0.6 * min(z_score / 6.0, 1.0) + 0.4 * isolation_score)

    score = AnomalyScore(
        event_id=event.id,
        z_score=round(z_score, 6),
        isolation_forest_score=round(isolation_score, 6),
        combined_score=round(combined_score, 6),
        details={"mean": mu, "std_dev": sigma, "samples": len(history_values)},
    )
    db.add(score)
    db.flush()

    alert = None
    if score.combined_score >= threshold:
        alert = Alert(
            event_id=event.id,
            anomaly_score_id=score.id,
            severity=_severity(score.combined_score),
            message=f"Anomalous event detected for source {event.source_id}",
        )
        db.add(alert)
        db.flush()

    return score, alert
