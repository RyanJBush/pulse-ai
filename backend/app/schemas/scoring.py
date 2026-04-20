from pydantic import BaseModel


class ScoreRequest(BaseModel):
    source: str
    event_type: str
    payload: dict


class ScoreResponse(BaseModel):
    z_score: float
    isolation_score: float
    combined_score: float
    is_anomalous: bool
    explanation: str
