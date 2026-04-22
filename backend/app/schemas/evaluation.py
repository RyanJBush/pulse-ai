from pydantic import BaseModel, Field

from app.schemas.event import ReplayRequest


class EvaluationRequest(BaseModel):
    replay: ReplayRequest
    benchmark_name: str = Field(default="seeded-replay", min_length=3, max_length=120)


class EvaluationResponse(BaseModel):
    benchmark_name: str
    total_events: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    false_positive_rate: float
    mean_alert_latency_seconds: float
    time_to_first_detect_seconds: float | None
    detector_breakdown: dict[str, int]


class EvaluationSliceRequest(BaseModel):
    workspace_id: str = "default"
    source: str
    signal_type: str
    entity_id: str


class ThresholdTuningRequest(EvaluationSliceRequest):
    thresholds: list[float] = Field(default_factory=lambda: [0.55, 0.65, 0.75, 0.85, 0.9])


class ThresholdPoint(BaseModel):
    threshold: float
    precision: float
    recall: float
    false_positive_rate: float


class ThresholdTuningResponse(BaseModel):
    workspace_id: str
    source: str
    signal_type: str
    entity_id: str
    points: list[ThresholdPoint]
    recommended_threshold: float | None


class DetectorComparisonPoint(BaseModel):
    detector: str
    samples: int
    true_positive_rate: float
    false_positive_rate: float


class DetectorComparisonResponse(BaseModel):
    workspace_id: str
    source: str
    signal_type: str
    entity_id: str
    detectors: list[DetectorComparisonPoint]
