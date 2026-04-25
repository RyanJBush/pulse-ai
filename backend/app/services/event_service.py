import math
import random
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.ingestion_buffer import buffer_instance
from app.core.logging import get_logger
from app.models.anomaly_score import AnomalyScore
from app.models.event import Event
from app.schemas.event import (
    BufferEnqueueRequest,
    BufferEnqueueResponse,
    BufferFlushResponse,
    BufferStatsResponse,
    EventCreate,
    EventIngestResponse,
    EventRead,
    ReplayRequest,
    ReplayResponse,
)
from app.schemas.scoring import ScoreRequest
from app.services.alert_service import AlertService
from app.services.scoring_service import ScoringService

logger = get_logger(__name__)


class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.scoring_service = ScoringService(db)
        self.alert_service = AlertService(db)

    def _extract_value(self, payload: dict, fallback_value: float | None) -> float:
        if fallback_value is not None:
            return float(fallback_value)
        raw = payload.get("value", 0.0)
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    def ingest_event(self, payload: EventCreate) -> EventIngestResponse:
        signal_type = payload.signal_type or payload.event_type
        event_timestamp = payload.event_timestamp or datetime.now(timezone.utc).replace(tzinfo=None)
        event = Event(
            source=payload.source,
            workspace_id=payload.workspace_id,
            event_type=payload.event_type,
            signal_type=signal_type,
            entity_id=payload.entity_id,
            payload=payload.payload,
            value=self._extract_value(payload.payload, payload.value),
            event_timestamp=event_timestamp,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        logger.info(
            "event_ingested id=%s source=%s signal=%s entity=%s event_ts=%s",
            event.id,
            event.source,
            event.signal_type,
            event.entity_id,
            event.event_timestamp.isoformat(),
        )

        score_started = time.perf_counter()
        score = self.scoring_service.score_payload(
            ScoreRequest(
                source=event.source,
                workspace_id=event.workspace_id,
                event_type=event.event_type,
                signal_type=event.signal_type,
                entity_id=event.entity_id,
                payload=event.payload,
            ),
            event_timestamp=event.event_timestamp,
        )
        score_latency_ms = round((time.perf_counter() - score_started) * 1000.0, 4)

        drift_hook = (
            "watch" if score.confidence_score > 0.8 and score.combined_score > 0.7 else "stable"
        )
        db_score = AnomalyScore(
            event_id=event.id,
            z_score=score.z_score,
            isolation_score=score.isolation_score,
            rolling_score=score.rolling_score,
            seasonal_score=score.seasonal_score,
            combined_score=score.combined_score,
            is_anomalous=score.is_anomalous,
            selected_detector=score.selected_detector,
            dynamic_threshold=score.dynamic_threshold,
            confidence_score=score.confidence_score,
            severity=score.severity,
            reason_codes=score.reason_codes,
            scoring_latency_ms=score_latency_ms,
            details={"detector_scores": score.detector_scores, "drift_hook": drift_hook},
        )
        self.db.add(db_score)
        self.db.commit()
        self.db.refresh(db_score)

        alert_id = None
        if score.is_anomalous:
            alert = self.alert_service.create_alert(
                event_id=event.id,
                workspace_id=event.workspace_id,
                anomaly_score_id=db_score.id,
                severity=score.severity,
                message=(
                    "Anomalous event detected: "
                    f"source={event.source}, signal={event.signal_type}"
                ),
                cooldown_key=f"{event.entity_id}:{event.signal_type}",
                evidence={
                    "reason_codes": score.reason_codes,
                    "confidence_score": score.confidence_score,
                    "dynamic_threshold": score.dynamic_threshold,
                },
            )
            alert_id = alert.id if alert else None

        return EventIngestResponse(
            event=EventRead.model_validate(event),
            z_score=score.z_score,
            isolation_score=score.isolation_score,
            rolling_score=score.rolling_score,
            seasonal_score=score.seasonal_score,
            combined_score=score.combined_score,
            dynamic_threshold=score.dynamic_threshold,
            confidence_score=score.confidence_score,
            severity=score.severity,
            reason_codes=score.reason_codes,
            is_anomalous=score.is_anomalous,
            alert_id=alert_id,
        )

    def list_events(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_desc: bool = True,
        workspace_id: str | None = None,
    ) -> list[EventRead]:
        ordering = Event.created_at.desc() if sort_desc else Event.created_at.asc()
        stmt = select(Event).order_by(ordering)
        if workspace_id:
            stmt = stmt.where(Event.workspace_id == workspace_id)
        stmt = stmt.offset(offset).limit(limit)
        return [EventRead.model_validate(item) for item in self.db.scalars(stmt).all()]

    def replay_seeded_stream(self, payload: ReplayRequest) -> ReplayResponse:
        base_time = payload.start_at or (
            datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
        )
        rng = random.Random(payload.seed)

        events_to_replay: list[EventCreate] = []
        for idx in range(payload.count):
            ts = base_time + timedelta(seconds=idx * payload.interval_seconds)
            seasonal_component = 10.0 * math.sin(idx / 8.0)
            noise = rng.uniform(-2.0, 2.0)
            value = 60.0 + seasonal_component + noise
            if payload.inject_spike_every > 0 and idx > 0 and idx % payload.inject_spike_every == 0:
                value = value * settings.REPLAY_SPIKE_MULTIPLIER
                is_injected_anomaly = True
            else:
                is_injected_anomaly = False
            events_to_replay.append(
                EventCreate(
                    source=payload.source,
                    workspace_id=payload.workspace_id,
                    event_type=payload.event_type,
                    signal_type=payload.signal_type,
                    entity_id=payload.entity_id,
                    event_timestamp=ts,
                    value=round(value, 4),
                    payload={
                        "value": round(value, 4),
                        "seed": payload.seed,
                        "replay_index": idx,
                        "is_injected_anomaly": is_injected_anomaly,
                    },
                )
            )

        if payload.allow_out_of_order and len(events_to_replay) >= 3:
            for idx in range(0, len(events_to_replay) - 2, 17):
                events_to_replay[idx], events_to_replay[idx + 2] = (
                    events_to_replay[idx + 2],
                    events_to_replay[idx],
                )

        anomalous = 0
        alert_ids: set[int] = set()
        suppressed_alerts = 0
        for replay_event in events_to_replay:
            response = self.ingest_event(replay_event)
            if response.is_anomalous:
                anomalous += 1
            if response.alert_id is not None:
                alert_ids.add(response.alert_id)
            if response.is_anomalous and response.alert_id is None:
                suppressed_alerts += 1

        logger.info(
            "replay_completed seed=%s count=%s anomalous=%s alerts=%s suppressed=%s",
            payload.seed,
            payload.count,
            anomalous,
            len(alert_ids),
            suppressed_alerts,
        )
        return ReplayResponse(
            ingested=payload.count,
            anomalous=anomalous,
            alerts_created=len(alert_ids),
            suppressed_alerts=suppressed_alerts,
        )

    def buffer_enqueue(self, payload: BufferEnqueueRequest) -> BufferEnqueueResponse:
        queued = buffer_instance.enqueue_many(payload.events)
        logger.info("buffer_enqueued accepted=%s queued=%s", len(payload.events), queued)
        return BufferEnqueueResponse(accepted=len(payload.events), queued=queued)

    def buffer_flush(self, limit: int | None = None) -> BufferFlushResponse:
        drained = buffer_instance.drain(limit=limit)
        anomalies = 0
        alerts_created = 0
        for event in drained:
            result = self.ingest_event(event)
            if result.is_anomalous:
                anomalies += 1
            if result.alert_id is not None:
                alerts_created += 1
        logger.info(
            "buffer_flushed processed=%s anomalies=%s alerts_created=%s",
            len(drained),
            anomalies,
            alerts_created,
        )
        return BufferFlushResponse(
            processed=len(drained),
            anomalies=anomalies,
            alerts_created=alerts_created,
        )

    def buffer_stats(self) -> BufferStatsResponse:
        return BufferStatsResponse(**buffer_instance.stats())
