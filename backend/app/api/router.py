from fastapi import APIRouter

from app.api.routers import alerts, events, scoring

api_router = APIRouter()
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
