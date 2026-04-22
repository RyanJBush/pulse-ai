from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alert import AlertNoteCreate, AlertNoteRead, AlertRead, AlertStatusUpdate
from app.services.alert_service import AlertService

router = APIRouter()


@router.get("", response_model=list[AlertRead])
def list_alerts(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0, le=5000),
    status: str | None = Query(default=None),
    sort_desc: bool = Query(default=True),
    workspace_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AlertRead]:
    return AlertService(db).list_alerts(
        limit=limit,
        offset=offset,
        status=status,
        sort_desc=sort_desc,
        workspace_id=workspace_id,
    )


@router.patch("/{alert_id}/status", response_model=AlertRead)
def update_alert_status(
    alert_id: int,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
) -> AlertRead:
    return AlertService(db).update_status(
        alert_id=alert_id,
        status=payload.status,
        author=payload.author,
        note=payload.note,
    )


@router.post("/{alert_id}/notes", response_model=AlertNoteRead, status_code=201)
def add_alert_note(
    alert_id: int,
    payload: AlertNoteCreate,
    db: Session = Depends(get_db),
) -> AlertNoteRead:
    return AlertService(db).add_note(alert_id=alert_id, author=payload.author, note=payload.note)


@router.get("/{alert_id}/notes", response_model=list[AlertNoteRead])
def list_alert_notes(alert_id: int, db: Session = Depends(get_db)) -> list[AlertNoteRead]:
    return AlertService(db).list_notes(alert_id=alert_id)
