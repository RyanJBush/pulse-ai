from datetime import datetime

from pydantic import BaseModel, Field


class AlertRead(BaseModel):
    id: int
    event_id: int
    anomaly_score_id: int | None = None
    severity: str
    message: str
    status: str
    assigned_owner: str | None = None
    updated_at: datetime
    last_transition_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertStatusUpdate(BaseModel):
    status: str = Field(..., min_length=2, max_length=32)
    author: str = Field(default="system", min_length=1, max_length=120)
    note: str | None = Field(default=None, max_length=1000)


class AlertNoteCreate(BaseModel):
    note: str = Field(..., min_length=1, max_length=2000)
    author: str = Field(default="system", min_length=1, max_length=120)


class AlertNoteRead(BaseModel):
    id: int
    alert_id: int
    author: str
    note: str
    created_at: datetime

    model_config = {"from_attributes": True}
