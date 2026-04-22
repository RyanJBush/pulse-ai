from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.anomaly_score import AnomalyScore
from app.models.event import Event
from app.schemas.evaluation import (
    DetectorComparisonPoint,
    DetectorComparisonResponse,
    EvaluationSliceRequest,
    EvaluationRequest,
    EvaluationResponse,
    ThresholdPoint,
    ThresholdTuningRequest,
    ThresholdTuningResponse,
)
from app.services.event_service import EventService


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.event_service = EventService(db)

    def run_seeded_benchmark(self, payload: EvaluationRequest) -> EvaluationResponse:
        run_started = datetime.utcnow()
        replay_result = self.event_service.replay_seeded_stream(payload.replay)

        stmt = (
            select(Event, AnomalyScore)
            .join(AnomalyScore, AnomalyScore.event_id == Event.id)
            .where(Event.source == payload.replay.source)
            .where(Event.workspace_id == payload.replay.workspace_id)
            .where(Event.entity_id == payload.replay.entity_id)
            .where(Event.signal_type == payload.replay.signal_type)
            .where(Event.created_at >= run_started)
        )
        rows = self.db.execute(stmt).all()

        tp = fp = tn = fn = 0
        alert_latencies: list[float] = []
        first_detect_seconds: float | None = None
        detector_breakdown: dict[str, int] = {}

        for event, score in rows:
            injected = bool((event.payload or {}).get("is_injected_anomaly", False))
            predicted = bool(score.is_anomalous)

            if injected and predicted:
                tp += 1
            elif not injected and predicted:
                fp += 1
            elif injected and not predicted:
                fn += 1
            else:
                tn += 1

            if predicted:
                detector_breakdown[score.selected_detector] = (
                    detector_breakdown.get(score.selected_detector, 0) + 1
                )
                latency = (event.created_at - event.event_timestamp).total_seconds()
                alert_latencies.append(max(latency, 0.0))
                if first_detect_seconds is None and event.payload.get("replay_index") is not None:
                    first_detect_seconds = float(
                        event.payload["replay_index"] * payload.replay.interval_seconds
                    )

        precision = 0.0 if (tp + fp) == 0 else round(tp / (tp + fp), 4)
        recall = 0.0 if (tp + fn) == 0 else round(tp / (tp + fn), 4)
        fpr = 0.0 if (fp + tn) == 0 else round(fp / (fp + tn), 4)
        mean_latency = (
            0.0
            if not alert_latencies
            else round(sum(alert_latencies) / len(alert_latencies), 4)
        )

        return EvaluationResponse(
            benchmark_name=payload.benchmark_name,
            total_events=replay_result.ingested,
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            precision=precision,
            recall=recall,
            false_positive_rate=fpr,
            mean_alert_latency_seconds=mean_latency,
            time_to_first_detect_seconds=first_detect_seconds,
            detector_breakdown=detector_breakdown,
        )

    def tune_thresholds(self, payload: ThresholdTuningRequest) -> ThresholdTuningResponse:
        rows = self._load_slice(payload.workspace_id, payload.source, payload.signal_type, payload.entity_id)
        points: list[ThresholdPoint] = []
        best_threshold: float | None = None
        best_f1 = -1.0

        for threshold in payload.thresholds:
            tp = fp = tn = fn = 0
            for event, score in rows:
                injected = bool((event.payload or {}).get("is_injected_anomaly", False))
                predicted = float(score.combined_score) >= float(threshold)
                if injected and predicted:
                    tp += 1
                elif not injected and predicted:
                    fp += 1
                elif injected and not predicted:
                    fn += 1
                else:
                    tn += 1

            precision = 0.0 if (tp + fp) == 0 else tp / (tp + fp)
            recall = 0.0 if (tp + fn) == 0 else tp / (tp + fn)
            fpr = 0.0 if (fp + tn) == 0 else fp / (fp + tn)
            points.append(
                ThresholdPoint(
                    threshold=round(float(threshold), 4),
                    precision=round(precision, 4),
                    recall=round(recall, 4),
                    false_positive_rate=round(fpr, 4),
                )
            )
            f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = float(threshold)

        return ThresholdTuningResponse(
            workspace_id=payload.workspace_id,
            source=payload.source,
            signal_type=payload.signal_type,
            entity_id=payload.entity_id,
            points=points,
            recommended_threshold=round(best_threshold, 4) if best_threshold is not None else None,
        )

    def detector_comparison(self, payload: EvaluationSliceRequest) -> DetectorComparisonResponse:
        rows = self._load_slice(payload.workspace_id, payload.source, payload.signal_type, payload.entity_id)
        stats: dict[str, dict[str, int]] = {}
        for event, score in rows:
            detector = score.selected_detector or "unknown"
            bucket = stats.setdefault(detector, {"tp": 0, "fp": 0, "tn": 0, "fn": 0})
            injected = bool((event.payload or {}).get("is_injected_anomaly", False))
            predicted = bool(score.is_anomalous)
            if injected and predicted:
                bucket["tp"] += 1
            elif not injected and predicted:
                bucket["fp"] += 1
            elif injected and not predicted:
                bucket["fn"] += 1
            else:
                bucket["tn"] += 1

        detectors: list[DetectorComparisonPoint] = []
        for detector, m in stats.items():
            tpr = 0.0 if (m["tp"] + m["fn"]) == 0 else m["tp"] / (m["tp"] + m["fn"])
            fpr = 0.0 if (m["fp"] + m["tn"]) == 0 else m["fp"] / (m["fp"] + m["tn"])
            detectors.append(
                DetectorComparisonPoint(
                    detector=detector,
                    samples=m["tp"] + m["fp"] + m["tn"] + m["fn"],
                    true_positive_rate=round(tpr, 4),
                    false_positive_rate=round(fpr, 4),
                )
            )
        detectors.sort(key=lambda d: d.samples, reverse=True)

        return DetectorComparisonResponse(
            workspace_id=payload.workspace_id,
            source=payload.source,
            signal_type=payload.signal_type,
            entity_id=payload.entity_id,
            detectors=detectors,
        )

    def _load_slice(
        self, workspace_id: str, source: str, signal_type: str, entity_id: str
    ) -> list[tuple[Event, AnomalyScore]]:
        stmt = (
            select(Event, AnomalyScore)
            .join(AnomalyScore, AnomalyScore.event_id == Event.id)
            .where(Event.workspace_id == workspace_id)
            .where(Event.source == source)
            .where(Event.signal_type == signal_type)
            .where(Event.entity_id == entity_id)
            .order_by(Event.created_at.asc())
        )
        return self.db.execute(stmt).all()
