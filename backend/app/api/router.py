from fastapi import APIRouter

from app.api.routers import ai, alerts, evaluation, events, governance, incidents, metrics, scoring

api_router = APIRouter()
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

api_router.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])
api_router.include_router(governance.router, prefix="/governance", tags=["governance"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
