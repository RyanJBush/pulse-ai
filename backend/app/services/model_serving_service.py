from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeModel:
    name: str
    version: str


class ModelServingService:
    """Small in-process model registry for online prediction serving."""

    def __init__(self) -> None:
        self._models: dict[str, RuntimeModel] = {
            "mean_baseline": RuntimeModel(name="mean_baseline", version="1.0.0"),
            "weighted_sum": RuntimeModel(name="weighted_sum", version="1.0.0"),
        }
        self._active_model = "weighted_sum"

    def available_models(self) -> list[str]:
        return sorted(self._models.keys())

    def active_model(self) -> str:
        return self._active_model

    def predict(self, features: list[float], model_name: str | None = None) -> dict:
        selected_model = model_name or self._active_model
        if selected_model not in self._models:
            raise ValueError(f"unknown model '{selected_model}'")

        if selected_model == "mean_baseline":
            prediction = sum(features) / len(features)
        else:
            weighted_total = sum(value * (idx + 1) for idx, value in enumerate(features))
            prediction = weighted_total / sum(range(1, len(features) + 1))

        runtime = self._models[selected_model]
        return {
            "model_name": runtime.name,
            "prediction": round(float(prediction), 6),
            "metadata": {
                "model_version": runtime.version,
                "feature_count": len(features),
                "active_model": self._active_model,
            },
        }


model_serving_service = ModelServingService()
