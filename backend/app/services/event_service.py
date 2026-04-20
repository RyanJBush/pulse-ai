import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.anomaly_score import AnomalyScore
from app.models.event import Event
from app.schemas.event import EventCreate, EventIngestResponse, EventRead
from app.schemas.scoring import ScoreRequest
from app.services.alert_service import AlertService
from app.services.scoring_service import ScoringService, score_severity

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.scoring_service = ScoringService(db)
        self.alert_service = AlertService(db)

    def _extract_value(self, payload: dict) -> float:
        raw = payload.get("value", 0.0)
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    def ingest_event(self, payload: EventCreate) -> EventIngestResponse:
        event = Event(**payload.model_dump(), value=self._extract_value(payload.payload))
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        logger.info("event_ingested id=%s source=%s type=%s", event.id, event.source, event.event_type)

        score = self.scoring_service.score_payload(ScoreRequest(**payload.model_dump()))
        db_score = AnomalyScore(
            event_id=event.id,
            z_score=score.z_score,
            isolation_score=score.isolation_score,
            combined_score=score.combined_score,
            is_anomalous=score.is_anomalous,
        )
        self.db.add(db_score)
        self.db.commit()

        alert_id = None
        if score.is_anomalous:
            severity = score_severity(score.combined_score)
            alert = self.alert_service.create_alert(
                event_id=event.id,
                severity=severity,
                message=f"Anomalous event detected: source={event.source}, type={event.event_type}",
            )
            alert_id = alert.id

        return EventIngestResponse(
            event=EventRead.model_validate(event),
            z_score=score.z_score,
            isolation_score=score.isolation_score,
            combined_score=score.combined_score,
            is_anomalous=score.is_anomalous,
            alert_id=alert_id,
        )

    def list_events(self, limit: int = 100) -> list[EventRead]:
        stmt = select(Event).order_by(Event.created_at.desc()).limit(limit)
        return [EventRead.model_validate(item) for item in self.db.scalars(stmt).all()]
