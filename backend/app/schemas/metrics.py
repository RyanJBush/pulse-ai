from datetime import datetime

from pydantic import BaseModel


class KpiSummary(BaseModel):
    anomaly_rate: float
    alert_count: int
    throughput_per_minute: float
    high_severity_anomalies: int
    avg_scoring_latency_ms: float


class EntityDrilldownMetrics(BaseModel):
    entity_id: str
    total_events: int
    anomalous_events: int
    anomaly_rate: float
    active_alerts: int
    avg_combined_score: float
    last_event_at: datetime | None
    severity_distribution: dict[str, int]
    reason_code_distribution: dict[str, int]
