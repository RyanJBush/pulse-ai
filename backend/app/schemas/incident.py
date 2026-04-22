from datetime import datetime

from pydantic import BaseModel, Field


class IncidentRead(BaseModel):
    id: int
    workspace_id: str
    group_key: str
    status: str
    severity: str
    title: str
    assigned_owner: str | None = None
    suppressed_alerts_count: int
    evidence: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentStatusUpdate(BaseModel):
    status: str = Field(..., min_length=2, max_length=32)
    actor: str = Field(default="system", min_length=1, max_length=120)
    assigned_owner: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=1000)


class IncidentNoteCreate(BaseModel):
    author: str = Field(default="system", min_length=1, max_length=120)
    note: str = Field(..., min_length=1, max_length=2000)


class IncidentNoteRead(BaseModel):
    id: int
    incident_id: int
    author: str
    note: str
    created_at: datetime

    model_config = {"from_attributes": True}
