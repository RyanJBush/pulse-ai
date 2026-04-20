from datetime import datetime

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    event_type: str = Field(..., min_length=1, max_length=255)
    payload: dict = Field(default_factory=dict)
    value: float | None = None
    entity_id: str = Field(default="global", min_length=1, max_length=255)
    signal_type: str | None = Field(default=None, min_length=1, max_length=255)
    event_timestamp: datetime | None = None


class EventRead(BaseModel):
    id: int
    source: str
    event_type: str
    signal_type: str
    entity_id: str
    payload: dict
    value: float
    event_timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class EventIngestResponse(BaseModel):
    event: EventRead
    z_score: float
    isolation_score: float
    rolling_score: float
    seasonal_score: float
    combined_score: float
    dynamic_threshold: float
    confidence_score: float
    severity: str
    reason_codes: list[str]
    is_anomalous: bool
    alert_id: int | None


class ReplayRequest(BaseModel):
    seed: int = 42
    count: int = Field(default=120, ge=1, le=1000)
    source: str = "demo-stream"
    event_type: str = "latency"
    entity_id: str = "entity-demo-1"
    signal_type: str = "latency"
    start_at: datetime | None = None
    interval_seconds: int = Field(default=30, ge=1, le=3600)
    inject_spike_every: int = Field(default=25, ge=0, le=500)
    allow_out_of_order: bool = True


class ReplayResponse(BaseModel):
    ingested: int
    anomalous: int
    alerts_created: int
    suppressed_alerts: int
