from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.incident import INCIDENT_STATUSES, Incident
from app.models.incident_note import IncidentNote
from app.schemas.incident import IncidentNoteRead, IncidentRead


class IncidentService:
    def __init__(self, db: Session):
        self.db = db

    def list_incidents(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        sort_desc: bool = True,
        workspace_id: str | None = None,
    ) -> list[IncidentRead]:
        ordering = Incident.updated_at.desc() if sort_desc else Incident.updated_at.asc()
        stmt = select(Incident).order_by(ordering)
        if status:
            stmt = stmt.where(Incident.status == status)
        if workspace_id:
            stmt = stmt.where(Incident.workspace_id == workspace_id)
        stmt = stmt.offset(offset).limit(limit)
        return [IncidentRead.model_validate(row) for row in self.db.scalars(stmt).all()]

    def update_incident(
        self,
        incident_id: int,
        status: str,
        actor: str,
        assigned_owner: str | None = None,
        note: str | None = None,
    ) -> IncidentRead:
        if status not in INCIDENT_STATUSES:
            raise HTTPException(status_code=400, detail=f"invalid incident status: {status}")

        incident = self.db.get(Incident, incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="incident not found")

        old_status = incident.status
        incident.status = status
        incident.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        if assigned_owner is not None:
            incident.assigned_owner = assigned_owner
        self.db.add(incident)

        if note:
            self.db.add(IncidentNote(incident_id=incident.id, author=actor, note=note))

        self.db.add(
            AuditLog(
                actor=actor,
                action="incident_status_update",
                resource_type="incident",
                resource_id=str(incident.id),
                details=json.dumps({"from": old_status, "to": status}),
            )
        )
        self.db.commit()
        self.db.refresh(incident)
        return IncidentRead.model_validate(incident)

    def add_note(self, incident_id: int, author: str, note: str) -> IncidentNoteRead:
        incident = self.db.get(Incident, incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="incident not found")

        db_note = IncidentNote(incident_id=incident_id, author=author, note=note)
        self.db.add(db_note)
        self.db.commit()
        self.db.refresh(db_note)
        return IncidentNoteRead.model_validate(db_note)

    def list_notes(self, incident_id: int) -> list[IncidentNoteRead]:
        if self.db.get(Incident, incident_id) is None:
            raise HTTPException(status_code=404, detail="incident not found")
        stmt = (
            select(IncidentNote)
            .where(IncidentNote.incident_id == incident_id)
            .order_by(IncidentNote.created_at.asc())
        )
        return [IncidentNoteRead.model_validate(row) for row in self.db.scalars(stmt).all()]
