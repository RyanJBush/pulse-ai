from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_role
from app.db.session import get_db
from app.schemas.evaluation import (
    DetectorComparisonResponse,
    EvaluationRequest,
    EvaluationResponse,
    EvaluationSliceRequest,
    ThresholdTuningRequest,
    ThresholdTuningResponse,
)
from app.services.evaluation_service import EvaluationService

router = APIRouter()


@router.post(
    "/seeded-benchmark",
    response_model=EvaluationResponse,
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def run_seeded_benchmark(
    payload: EvaluationRequest,
    db: Session = Depends(get_db),
) -> EvaluationResponse:
    return EvaluationService(db).run_seeded_benchmark(payload)


@router.post(
    "/threshold-tuning",
    response_model=ThresholdTuningResponse,
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def threshold_tuning(
    payload: ThresholdTuningRequest,
    db: Session = Depends(get_db),
) -> ThresholdTuningResponse:
    return EvaluationService(db).tune_thresholds(payload)


@router.post(
    "/detector-comparison",
    response_model=DetectorComparisonResponse,
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def detector_comparison(
    payload: EvaluationSliceRequest,
    db: Session = Depends(get_db),
) -> DetectorComparisonResponse:
    return EvaluationService(db).detector_comparison(payload)
