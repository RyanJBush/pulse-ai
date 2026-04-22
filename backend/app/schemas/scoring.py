from pydantic import BaseModel


class ScoreRequest(BaseModel):
    source: str
    workspace_id: str = "default"
    event_type: str
    payload: dict
    entity_id: str = "global"
    signal_type: str | None = None


class ScoreResponse(BaseModel):
    z_score: float
    isolation_score: float
    rolling_score: float
    seasonal_score: float
    detector_scores: dict[str, float]
    selected_detector: str
    combined_score: float
    dynamic_threshold: float
    confidence_score: float
    severity: str
    reason_codes: list[str]
    is_anomalous: bool
    explanation: str
