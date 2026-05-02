from fastapi import APIRouter, HTTPException

from app.schemas.serving import PredictRequest, PredictResponse, ServingHealthResponse
from app.services.model_serving_service import model_serving_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    try:
        result = model_serving_service.predict(
            features=payload.features,
            model_name=payload.model_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictResponse(
        model_name=result["model_name"],
        prediction=result["prediction"],
        metadata=result["metadata"],
    )


@router.get("/health", response_model=ServingHealthResponse)
def serving_health() -> ServingHealthResponse:
    return ServingHealthResponse(
        active_model=model_serving_service.active_model(),
        active_models=model_serving_service.available_models(),
    )
