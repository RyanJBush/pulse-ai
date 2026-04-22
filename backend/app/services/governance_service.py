from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.detector_config import DetectorConfig
from app.models.suppression_rule import SuppressionRule
from app.schemas.governance import (
    AuditLogRead,
    DetectorConfigRead,
    DetectorConfigUpdate,
    SuppressionRuleCreate,
    SuppressionRuleRead,
)


class GovernanceService:
    def __init__(self, db: Session):
        self.db = db

    def list_detector_configs(self) -> list[DetectorConfigRead]:
        stmt = select(DetectorConfig).order_by(DetectorConfig.signal_type.asc())
        return [DetectorConfigRead.model_validate(row) for row in self.db.scalars(stmt).all()]

    def upsert_detector_config(self, payload: DetectorConfigUpdate) -> DetectorConfigRead:
        total_weight = (
            payload.z_weight
            + payload.isolation_weight
            + payload.rolling_weight
            + payload.seasonal_weight
        )
        if total_weight <= 0:
            raise ValueError("detector weights must sum to greater than 0")

        stmt = select(DetectorConfig).where(
            DetectorConfig.signal_type == payload.signal_type.strip().lower()
        )
        existing = self.db.scalars(stmt).first()
        if existing is None:
            existing = DetectorConfig(signal_type=payload.signal_type.strip().lower())

        existing.z_weight = payload.z_weight
        existing.isolation_weight = payload.isolation_weight
        existing.rolling_weight = payload.rolling_weight
        existing.seasonal_weight = payload.seasonal_weight
        existing.enabled = payload.enabled
        existing.updated_by = payload.actor
        existing.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        self.db.add(existing)
        self.db.flush()

        self.db.add(
            AuditLog(
                actor=payload.actor,
                action="detector_config_upsert",
                resource_type="detector_config",
                resource_id=str(existing.id),
                details=json.dumps(
                    {
                        "signal_type": existing.signal_type,
                        "enabled": existing.enabled,
                        "weights": {
                            "z": existing.z_weight,
                            "isolation": existing.isolation_weight,
                            "rolling": existing.rolling_weight,
                            "seasonal": existing.seasonal_weight,
                        },
                    }
                ),
            )
        )

        self.db.commit()
        self.db.refresh(existing)
        return DetectorConfigRead.model_validate(existing)

    def list_audit_logs(self, limit: int = 100) -> list[AuditLogRead]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        return [AuditLogRead.model_validate(row) for row in self.db.scalars(stmt).all()]

    def add_suppression_rule(self, payload: SuppressionRuleCreate) -> SuppressionRuleRead:
        rule = SuppressionRule(
            workspace_id=payload.workspace_id,
            entity_id=payload.entity_id,
            signal_type=payload.signal_type,
            reason=payload.reason,
            created_by=payload.actor,
        )
        self.db.add(rule)
        self.db.flush()
        self.db.add(
            AuditLog(
                actor=payload.actor,
                action="suppression_rule_created",
                resource_type="suppression_rule",
                resource_id=str(rule.id),
                details=json.dumps(
                    {
                        "workspace_id": rule.workspace_id,
                        "entity_id": rule.entity_id,
                        "signal_type": rule.signal_type,
                    }
                ),
            )
        )
        self.db.commit()
        self.db.refresh(rule)
        return SuppressionRuleRead.model_validate(rule)

    def list_suppression_rules(self, workspace_id: str | None = None) -> list[SuppressionRuleRead]:
        stmt = select(SuppressionRule).order_by(SuppressionRule.created_at.desc())
        if workspace_id:
            stmt = stmt.where(SuppressionRule.workspace_id == workspace_id)
        return [SuppressionRuleRead.model_validate(row) for row in self.db.scalars(stmt).all()]
