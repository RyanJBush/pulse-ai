from fastapi import APIRouter

from app.api.routers import alerts, events, metrics, scoring

api_router = APIRouter()
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
