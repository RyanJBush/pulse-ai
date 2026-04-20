from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.scoring import ScoreRequest, ScoreResponse
from app.services.scoring_service import ScoringService

router = APIRouter()


@router.post("/anomaly", response_model=ScoreResponse)
def score_anomaly(payload: ScoreRequest, db: Session = Depends(get_db)) -> ScoreResponse:
    return ScoringService(db).score_payload(payload)
