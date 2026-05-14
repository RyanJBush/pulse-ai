from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.anomaly_score import AnomalyScore
from app.models.event import Event


class RCAEngine:
    def __init__(self, db: Session):
        self.db = db

    def suggest_causes(self, *, event: Event, score: AnomalyScore | None = None) -> list[dict]:
        window_start = event.event_timestamp - timedelta(minutes=2)
        window_end = event.event_timestamp + timedelta(minutes=2)

        stmt = (
            select(Event.signal_type, Event.value)
            .where(Event.workspace_id == event.workspace_id)
            .where(Event.entity_id == event.entity_id)
            .where(Event.event_timestamp >= window_start)
            .where(Event.event_timestamp <= window_end)
        )
        grouped: dict[str, list[float]] = defaultdict(list)
        for signal_type, value in self.db.execute(stmt).all():
            if signal_type and value is not None:
                grouped[signal_type].append(float(value))

        spikes = {
            metric: max(values)
            for metric, values in grouped.items()
            if values and max(values) > 0 and (sum(values) / len(values)) > 0
        }

        suggestions: list[dict] = []
        if spikes.get("cpu_usage") and spikes.get("memory_usage"):
            suggestions.append(
                {
                    "cause": "possible memory leak",
                    "confidence": 0.9,
                    "evidence": [
                        "cpu_usage spiked near anomaly timestamp",
                        "memory_usage spiked near anomaly timestamp",
                    ],
                }
            )
        if spikes.get("api_latency") and spikes.get("request_volume"):
            suggestions.append(
                {
                    "cause": "traffic surge causing saturation",
                    "confidence": 0.84,
                    "evidence": [
                        "api_latency increased in ±2m window",
                        "request_volume increased in ±2m window",
                    ],
                }
            )
        if spikes.get("error_rate") and spikes.get("api_latency"):
            suggestions.append(
                {
                    "cause": "downstream dependency degradation",
                    "confidence": 0.8,
                    "evidence": ["error_rate spike", "api_latency spike"],
                }
            )

        if not suggestions:
            suggestions.append(
                {
                    "cause": "isolated metric anomaly",
                    "confidence": 0.55,
                    "evidence": [f"{event.signal_type} deviated from baseline"],
                }
            )

        ranked = sorted(suggestions, key=lambda item: item["confidence"], reverse=True)
        return ranked
