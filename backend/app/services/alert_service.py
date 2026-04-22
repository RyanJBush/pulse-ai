import json
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.alert import ALERT_STATUSES, Alert
from app.models.alert_note import AlertNote
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.suppression_rule import SuppressionRule
from app.schemas.alert import AlertNoteRead, AlertRead

logger = get_logger(__name__)


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(
        self,
        event_id: int,
        workspace_id: str,
        anomaly_score_id: int | None,
        severity: str,
        message: str,
        cooldown_key: str | None = None,
        evidence: dict | None = None,
    ) -> Alert | None:
        incident: Incident | None = None
        key_parts = (cooldown_key or "").split(":")
        key_entity = key_parts[0] if len(key_parts) >= 2 else ""
        key_signal = key_parts[-1] if len(key_parts) >= 1 else ""
        suppress_rule = self.db.scalars(
            select(SuppressionRule)
            .where(SuppressionRule.workspace_id == workspace_id)
            .where(SuppressionRule.entity_id == key_entity)
            .where(SuppressionRule.signal_type == key_signal)
            .limit(1)
        ).first()
        if suppress_rule is not None:
            logger.info(
                "alert_suppressed_by_rule workspace=%s event_id=%s rule_id=%s",
                workspace_id,
                event_id,
                suppress_rule.id,
            )
            return None
        if cooldown_key:
            incident = self.db.scalars(
                select(Incident)
                .where(Incident.workspace_id == workspace_id)
                .where(Incident.group_key == cooldown_key)
                .where(Incident.status.in_(("new", "investigating", "suppressed")))
                .order_by(Incident.updated_at.desc())
                .limit(1)
            ).first()
            if incident is None:
                incident = Incident(
                    workspace_id=workspace_id,
                    group_key=cooldown_key,
                    status="new",
                    severity=severity,
                    title=f"Incident for {cooldown_key}",
                    evidence=evidence or {},
                )
                self.db.add(incident)
                self.db.flush()

        if cooldown_key:
            cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
                seconds=settings.ALERT_COOLDOWN_SECONDS
            )
            recent = self.db.scalars(
                select(Alert)
                .where(Alert.workspace_id == workspace_id)
                .where(Alert.cooldown_key == cooldown_key)
                .where(Alert.created_at >= cutoff)
                .where(Alert.status.in_(("new", "acknowledged", "investigating", "suppressed")))
                .order_by(Alert.created_at.desc())
                .limit(1)
            ).first()
            if recent is not None:
                if incident is not None:
                    incident.suppressed_alerts_count += 1
                    incident.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    self.db.add(incident)
                    self.db.commit()
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
            workspace_id=workspace_id,
            incident_id=incident.id if incident is not None else None,
            anomaly_score_id=anomaly_score_id,
            severity=severity,
            message=message,
            status="new",
            cooldown_key=cooldown_key,
            updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            last_transition_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        logger.warning(
            "alert_created event_id=%s severity=%s alert_id=%s incident_id=%s",
            event_id,
            severity,
            alert.id,
            alert.incident_id,
        )
        return alert

    def list_alerts(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        sort_desc: bool = True,
        workspace_id: str | None = None,
    ) -> list[AlertRead]:
        ordering = Alert.created_at.desc() if sort_desc else Alert.created_at.asc()
        stmt = select(Alert).order_by(ordering)
        if status:
            stmt = stmt.where(Alert.status == status)
        if workspace_id:
            stmt = stmt.where(Alert.workspace_id == workspace_id)
        stmt = stmt.offset(offset).limit(limit)
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
        alert.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        alert.last_transition_at = datetime.now(timezone.utc).replace(tzinfo=None)
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
        self.db.add(
            AuditLog(
                actor=author,
                action="alert_status_update",
                resource_type="alert",
                resource_id=str(alert.id),
                details=json.dumps({"from": old_status, "to": alert.status}),
            )
        )
        self.db.commit()
        self.db.refresh(alert)
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
