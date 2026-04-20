import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine
from app.models import alert, anomaly_score, event  # noqa: F401

configure_logging()
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @application.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        logger.info("database_initialized")

    application.include_router(api_router, prefix=settings.API_PREFIX)

    @application.get("/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_application()
