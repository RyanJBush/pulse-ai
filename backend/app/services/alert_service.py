from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.alert import ALERT_STATUSES, Alert
from app.models.alert_note import AlertNote
from app.schemas.alert import AlertNoteRead, AlertRead

logger = get_logger(__name__)


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(
        self,
        event_id: int,
        anomaly_score_id: int | None,
        severity: str,
        message: str,
        cooldown_key: str | None = None,
    ) -> Alert | None:
        if cooldown_key:
            cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(
                seconds=settings.ALERT_COOLDOWN_SECONDS
            )
            recent = self.db.scalars(
                select(Alert)
                .where(Alert.cooldown_key == cooldown_key)
                .where(Alert.created_at >= cutoff)
                .where(Alert.status.in_(("new", "acknowledged", "investigating", "suppressed")))
                .order_by(Alert.created_at.desc())
                .limit(1)
            ).first()
            if recent is not None:
                logger.info(
                    "alert_suppressed event_id=%s severity=%s key=%s recent_alert_id=%s",
                    event_id,
                    severity,
                    cooldown_key,
                    recent.id,
                )
                return None

        alert = Alert(
            event_id=event_id,
            anomaly_score_id=anomaly_score_id,
            severity=severity,
            message=message,
            status="new",
            cooldown_key=cooldown_key,
            updated_at=datetime.now(UTC).replace(tzinfo=None),
            last_transition_at=datetime.now(UTC).replace(tzinfo=None),
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        logger.warning(
            "alert_created event_id=%s severity=%s alert_id=%s",
            event_id,
            severity,
            alert.id,
        )
        return alert

    def list_alerts(self, limit: int = 50, status: str | None = None) -> list[AlertRead]:
        stmt = select(Alert).order_by(Alert.created_at.desc())
        if status:
            stmt = stmt.where(Alert.status == status)
        stmt = stmt.limit(limit)
        return [AlertRead.model_validate(item) for item in self.db.scalars(stmt).all()]

    def update_status(
        self, alert_id: int, status: str, author: str, note: str | None = None
    ) -> AlertRead:
        if status not in ALERT_STATUSES:
            raise HTTPException(status_code=400, detail=f"invalid alert status: {status}")

        alert = self.db.get(Alert, alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="alert not found")

        old_status = alert.status
        alert.status = status
        alert.updated_at = datetime.now(UTC).replace(tzinfo=None)
        alert.last_transition_at = datetime.now(UTC).replace(tzinfo=None)
        self.db.add(alert)

        if note:
            self.db.add(AlertNote(alert_id=alert.id, author=author, note=note))

        self.db.commit()
        self.db.refresh(alert)
        logger.info(
            "alert_status_changed alert_id=%s from=%s to=%s",
            alert.id,
            old_status,
            alert.status,
        )
        return AlertRead.model_validate(alert)

    def add_note(self, alert_id: int, author: str, note: str) -> AlertNoteRead:
        alert = self.db.get(Alert, alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="alert not found")

        db_note = AlertNote(alert_id=alert_id, author=author, note=note)
        self.db.add(db_note)
        self.db.commit()
        self.db.refresh(db_note)
        logger.info("alert_note_added alert_id=%s note_id=%s", alert_id, db_note.id)
        return AlertNoteRead.model_validate(db_note)

    def list_notes(self, alert_id: int) -> list[AlertNoteRead]:
        alert = self.db.get(Alert, alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="alert not found")
        stmt = (
            select(AlertNote)
            .where(AlertNote.alert_id == alert_id)
            .order_by(AlertNote.created_at.asc())
        )
        return [AlertNoteRead.model_validate(item) for item in self.db.scalars(stmt).all()]
