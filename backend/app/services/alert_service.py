import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.schemas.alert import AlertRead

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, event_id: int, severity: str, message: str) -> Alert:
        alert = Alert(event_id=event_id, severity=severity, message=message)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        logger.warning("alert_created event_id=%s severity=%s alert_id=%s", event_id, severity, alert.id)
        return alert

    def list_alerts(self, limit: int = 50) -> list[AlertRead]:
        stmt = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
        return [AlertRead.model_validate(item) for item in self.db.scalars(stmt).all()]
