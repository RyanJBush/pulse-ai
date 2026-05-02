import math

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    features: list[float] = Field(min_length=1, description="Numeric feature vector")
    model_name: str | None = Field(default=None, description="Optional model selector")

    @field_validator("features")
    @classmethod
    def validate_finite_features(cls, value: list[float]) -> list[float]:
        if any(not math.isfinite(item) for item in value):
            raise ValueError("features must contain only finite numeric values")
        return value


class PredictResponse(BaseModel):
    status: str = "success"
    model_name: str
    prediction: float
    metadata: dict[str, float | int | str]


class ServingHealthResponse(BaseModel):
    status: str = "ok"
    active_model: str
    active_models: list[str]
