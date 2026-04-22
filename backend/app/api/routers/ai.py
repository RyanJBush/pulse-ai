from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_role
from app.db.session import get_db
from app.schemas.ai import AnomalySummaryRead, DailyBriefingRead, IncidentWrapUpRead
from app.services.ai_summary_service import AISummaryService

router = APIRouter()


@router.get(
    "/anomalies/{anomaly_score_id}/summary",
    response_model=AnomalySummaryRead,
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def anomaly_summary(anomaly_score_id: int, db: Session = Depends(get_db)) -> AnomalySummaryRead:
    return AISummaryService(db).anomaly_summary(anomaly_score_id=anomaly_score_id)


@router.get(
    "/daily-briefing",
    response_model=DailyBriefingRead,
    dependencies=[Depends(require_role("admin", "operator", "analyst", "viewer"))],
)
def daily_briefing(
    day: date | None = Query(default=None, description="YYYY-MM-DD, defaults to today UTC"),
    db: Session = Depends(get_db),
) -> DailyBriefingRead:
    return AISummaryService(db).daily_briefing(day=day)


@router.get(
    "/incidents/{incident_id}/wrap-up",
    response_model=IncidentWrapUpRead,
    dependencies=[Depends(require_role("admin", "operator", "analyst"))],
)
def incident_wrap_up(incident_id: int, db: Session = Depends(get_db)) -> IncidentWrapUpRead:
    return AISummaryService(db).incident_wrap_up(incident_id=incident_id)
