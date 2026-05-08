from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.metrics import EntityDrilldownMetrics, EntityMetricTrendResponse, KpiSummary
from app.services.metrics_service import MetricsService

router = APIRouter()


@router.get("/summary", response_model=KpiSummary)
def kpi_summary(db: Session = Depends(get_db)) -> KpiSummary:
    return MetricsService(db).kpi_summary()


@router.get("/entities/{entity_id}", response_model=EntityDrilldownMetrics)
def entity_drilldown(entity_id: str, db: Session = Depends(get_db)) -> EntityDrilldownMetrics:
    return MetricsService(db).entity_drilldown(entity_id=entity_id)


@router.get("/entities/{entity_id}/trends", response_model=EntityMetricTrendResponse)
def entity_metric_trends(
    entity_id: str,
    limit: int = Query(default=180, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> EntityMetricTrendResponse:
    return MetricsService(db).entity_metric_trends(entity_id=entity_id, limit=limit)
