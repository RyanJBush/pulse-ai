from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    source_id: str = Field(min_length=1, max_length=120)
    event_type: str = Field(min_length=1, max_length=120)
    value: float | None = None
    payload: dict = Field(default_factory=dict)


class EventRead(EventCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnomalyScoreRequest(BaseModel):
    event_id: int
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class AnomalyScoreRead(BaseModel):
    id: int
    event_id: int
    z_score: float
    isolation_forest_score: float
    combined_score: float
    model_version: str
    details: dict
    created_at: datetime
    alert_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class AlertRead(BaseModel):
    id: int
    event_id: int
    anomaly_score_id: int
    severity: str
    status: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricsSummary(BaseModel):
    total_events: int
    total_scores: int
    total_alerts: int
    open_alerts: int
    avg_combined_score: float
    events_last_hour: int
    top_sources: list[dict]
