from datetime import datetime

from pydantic import BaseModel, Field


class RCASuggestion(BaseModel):
    cause: str
    confidence: float
    evidence: list[str] = Field(default_factory=list)


class AlertRead(BaseModel):
    id: int
    event_id: int
    workspace_id: str
    incident_id: int | None = None
    anomaly_score_id: int | None = None
    severity: str
    message: str
    metric: str | None = None
    anomaly_score: float | None = None
    anomaly_timestamp: datetime | None = None
    explanation: str | None = None
    rca_suggestions: list[RCASuggestion] = Field(default_factory=list)
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


class AlertSuppressRequest(BaseModel):
    workspace_id: str = Field(default="default", min_length=1, max_length=64)
    metric: str = Field(..., min_length=1, max_length=255)
    duration_minutes: int = Field(default=15, ge=1, le=1440)


class AlertSuppressResponse(BaseModel):
    metric: str
    suppressed_until: str
