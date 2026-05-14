import json
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.alert import ALERT_STATUSES, Alert
from app.models.alert_note import AlertNote
from app.models.anomaly_score import AnomalyScore
from app.models.audit_log import AuditLog
from app.models.event import Event
from app.models.incident import Incident
from app.models.suppression_rule import SuppressionRule
from app.schemas.alert import AlertNoteRead, AlertRead
from app.services.alert_manager import AlertManager
from app.services.rca_service import RCAEngine

logger = get_logger(__name__)


class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_manager = AlertManager()
        self.rca_engine = RCAEngine(db)

    def create_alert(self, event_id: int, workspace_id: str, anomaly_score_id: int | None, severity: str, message: str, cooldown_key: str | None = None, evidence: dict | None = None) -> Alert | None:
        incident: Incident | None = None
        entity_for_dedup = "global"
        signal_for_dedup = "unknown"
        if cooldown_key:
            parts = cooldown_key.split(":")
            entity_for_dedup = parts[0] if len(parts) > 1 else "global"
            signal_for_dedup = parts[-1]
            if self.alert_manager.is_suppressed(workspace_id=workspace_id, metric=signal_for_dedup):
                return None
            if self.alert_manager.is_duplicate(workspace_id=workspace_id, entity_id=entity_for_dedup, signal_type=signal_for_dedup):
                return None
        if cooldown_key:
            incident = self.db.scalars(select(Incident).where(Incident.workspace_id == workspace_id).where(Incident.group_key == cooldown_key).where(Incident.status.in_(("new", "investigating", "suppressed"))).order_by(Incident.updated_at.desc()).limit(1)).first()
            if incident is None:
                incident = Incident(workspace_id=workspace_id, group_key=cooldown_key, status="new", severity=severity, title=f"Incident for {cooldown_key}", evidence=evidence or {})
                self.db.add(incident)
                self.db.flush()

        if cooldown_key:
            cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=settings.ALERT_COOLDOWN_SECONDS)
            recent = self.db.scalars(select(Alert).where(Alert.workspace_id == workspace_id).where(Alert.cooldown_key == cooldown_key).where(Alert.created_at >= cutoff).where(Alert.status.in_(("new", "acknowledged", "investigating", "suppressed"))).order_by(Alert.created_at.desc()).limit(1)).first()
            if recent is not None:
                return None

        alert = Alert(event_id=event_id, workspace_id=workspace_id, incident_id=incident.id if incident is not None else None, anomaly_score_id=anomaly_score_id, severity=severity, message=message, status="new", cooldown_key=cooldown_key, updated_at=datetime.now(timezone.utc).replace(tzinfo=None), last_transition_at=datetime.now(timezone.utc).replace(tzinfo=None))
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        if cooldown_key:
            self.alert_manager.mark_fired(workspace_id=workspace_id, entity_id=entity_for_dedup, signal_type=signal_for_dedup)
        return alert

    def list_alerts(self, limit: int = 50, offset: int = 0, status: str | None = None, sort_desc: bool = True, workspace_id: str | None = None) -> list[AlertRead]:
        ordering = Alert.created_at.desc() if sort_desc else Alert.created_at.asc()
        stmt = select(Alert, Event, AnomalyScore).join(Event, Event.id == Alert.event_id).outerjoin(AnomalyScore, AnomalyScore.id == Alert.anomaly_score_id).order_by(ordering)
        if status:
            stmt = stmt.where(Alert.status == status)
        if workspace_id:
            stmt = stmt.where(Alert.workspace_id == workspace_id)
        rows = self.db.execute(stmt.offset(offset).limit(limit)).all()
        alerts = []
        for alert, event, score in rows:
            alerts.append(AlertRead(id=alert.id, event_id=alert.event_id, workspace_id=alert.workspace_id, incident_id=alert.incident_id, anomaly_score_id=alert.anomaly_score_id, severity=alert.severity, message=alert.message, metric=event.signal_type, anomaly_score=round(float(score.combined_score), 4) if score and score.combined_score is not None else None, anomaly_timestamp=event.event_timestamp, explanation=(score.details or {}).get("explanation") if score and score.details else None, rca_suggestions=self.rca_engine.suggest_causes(event=event, score=score), status=alert.status, assigned_owner=alert.assigned_owner, updated_at=alert.updated_at, last_transition_at=alert.last_transition_at, created_at=alert.created_at))
        return alerts

    def suppress_metric(self, workspace_id: str, metric: str, duration_minutes: int) -> dict:
        return self.alert_manager.suppress_metric(workspace_id=workspace_id, metric=metric, duration_minutes=duration_minutes)

    def list_active_alerts(self, workspace_id: str | None = None) -> list[AlertRead]:
        return [a for a in self.list_alerts(limit=500, workspace_id=workspace_id) if a.status not in ("resolved", "closed") and not (a.metric and self.alert_manager.is_suppressed(workspace_id=a.workspace_id, metric=a.metric))]

    def update_status(self, alert_id: int, status: str, author: str, note: str | None = None) -> AlertRead:
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
        self.db.add(AuditLog(actor=author, action="alert_status_update", resource_type="alert", resource_id=str(alert.id), details=json.dumps({"from": old_status, "to": alert.status})))
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
        return AlertNoteRead.model_validate(db_note)

    def list_notes(self, alert_id: int) -> list[AlertNoteRead]:
        alert = self.db.get(Alert, alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="alert not found")
        stmt = select(AlertNote).where(AlertNote.alert_id == alert_id).order_by(AlertNote.created_at.asc())
        return [AlertNoteRead.model_validate(item) for item in self.db.scalars(stmt).all()]
