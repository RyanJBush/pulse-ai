from datetime import datetime

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    event_type: str = Field(..., min_length=1, max_length=255)
    payload: dict


class EventRead(BaseModel):
    id: int
    source: str
    event_type: str
    payload: dict
    value: float
    created_at: datetime

    model_config = {"from_attributes": True}


class EventIngestResponse(BaseModel):
    event: EventRead
    z_score: float
    isolation_score: float
    combined_score: float
    is_anomalous: bool
    alert_id: int | None
