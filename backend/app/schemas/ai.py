from datetime import date

from pydantic import BaseModel


class AnomalySummaryRead(BaseModel):
    anomaly_score_id: int
    summary: str
    explanation: str
    suggested_next_steps: list[str]


class DailyBriefingRead(BaseModel):
    day: date
    total_events: int
    anomalies: int
    alerts: int
    high_severity_alerts: int
    top_entities: list[dict[str, int | str]]
    repeated_patterns: list[dict[str, int | str]]
    briefing: str


class IncidentWrapUpRead(BaseModel):
    incident_id: int
    wrap_up: str
    timeline_points: list[str]
    recommended_followups: list[str]
