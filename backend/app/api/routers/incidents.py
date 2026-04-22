from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_role
from app.db.session import get_db
from app.schemas.incident import (
    IncidentNoteCreate,
    IncidentNoteRead,
    IncidentRead,
    IncidentStatusUpdate,
)
from app.services.incident_service import IncidentService

router = APIRouter()


@router.get("", response_model=list[IncidentRead], dependencies=[Depends(require_role("admin", "operator", "analyst"))])
def list_incidents(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0, le=5000),
    status: str | None = Query(default=None),
    sort_desc: bool = Query(default=True),
    workspace_id: str | None = Query(default=None),
) -> list[IncidentRead]:
    return IncidentService(db).list_incidents(
        limit=limit, offset=offset, status=status, sort_desc=sort_desc, workspace_id=workspace_id
    )


@router.patch("/{incident_id}", response_model=IncidentRead, dependencies=[Depends(require_role("admin", "operator"))])
def update_incident(
    incident_id: int,
    payload: IncidentStatusUpdate,
    db: Session = Depends(get_db),
) -> IncidentRead:
    return IncidentService(db).update_incident(
        incident_id=incident_id,
        status=payload.status,
        actor=payload.actor,
        assigned_owner=payload.assigned_owner,
        note=payload.note,
    )


@router.post("/{incident_id}/notes", response_model=IncidentNoteRead, dependencies=[Depends(require_role("admin", "operator", "analyst"))], status_code=201)
def add_incident_note(
    incident_id: int,
    payload: IncidentNoteCreate,
    db: Session = Depends(get_db),
) -> IncidentNoteRead:
    return IncidentService(db).add_note(incident_id=incident_id, author=payload.author, note=payload.note)


@router.get("/{incident_id}/notes", response_model=list[IncidentNoteRead], dependencies=[Depends(require_role("admin", "operator", "analyst"))])
def list_incident_notes(incident_id: int, db: Session = Depends(get_db)) -> list[IncidentNoteRead]:
    return IncidentService(db).list_notes(incident_id=incident_id)
