from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import require_role
from app.db.session import get_db
from app.schemas.governance import (
    AuditLogRead,
    DetectorConfigRead,
    DetectorConfigUpdate,
    SuppressionRuleCreate,
    SuppressionRuleRead,
)
from app.services.governance_service import GovernanceService

router = APIRouter()


@router.get(
    "/detectors",
    response_model=list[DetectorConfigRead],
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def list_detectors(db: Session = Depends(get_db)) -> list[DetectorConfigRead]:
    return GovernanceService(db).list_detector_configs()


@router.put(
    "/detectors",
    response_model=DetectorConfigRead,
    dependencies=[Depends(require_role("admin", "operator"))],
)
def upsert_detector(
    payload: DetectorConfigUpdate, db: Session = Depends(get_db)
) -> DetectorConfigRead:
    try:
        return GovernanceService(db).upsert_detector_config(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/audit-logs",
    response_model=list[AuditLogRead],
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def list_audit_logs(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[AuditLogRead]:
    return GovernanceService(db).list_audit_logs(limit=limit)


@router.post(
    "/suppression-rules",
    response_model=SuppressionRuleRead,
    dependencies=[Depends(require_role("admin", "operator"))],
    status_code=201,
)
def add_suppression_rule(
    payload: SuppressionRuleCreate,
    db: Session = Depends(get_db),
) -> SuppressionRuleRead:
    return GovernanceService(db).add_suppression_rule(payload)


@router.get(
    "/suppression-rules",
    response_model=list[SuppressionRuleRead],
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def list_suppression_rules(
    workspace_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[SuppressionRuleRead]:
    return GovernanceService(db).list_suppression_rules(workspace_id=workspace_id)
