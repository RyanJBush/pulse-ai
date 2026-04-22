from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.background_jobs import BackgroundJobRunner
from app.core.config import settings
from app.core.logging import clear_request_id, configure_logging, get_logger, set_request_id
from app.db.base import Base
from app.db.session import engine
from app.models import (
    Alert,
    AlertNote,
    AnomalyScore,
    AuditLog,
    DetectorConfig,
    Event,
    Incident,
    IncidentNote,
    SuppressionRule,
)

configure_logging()
logger = get_logger(__name__)
background_jobs = BackgroundJobRunner(interval_seconds=settings.BACKGROUND_JOB_INTERVAL_SECONDS)
_rate_limiter: dict[str, tuple[int, int]] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    background_jobs.start()
    logger.info(
        "startup_complete app=%s version=%s models=%s",
        settings.APP_NAME,
        settings.APP_VERSION,
        [
            Event.__tablename__,
            AnomalyScore.__tablename__,
            Alert.__tablename__,
            AlertNote.__tablename__,
            DetectorConfig.__tablename__,
            AuditLog.__tablename__,
            Incident.__tablename__,
            IncidentNote.__tablename__,
            SuppressionRule.__tablename__,
        ],
    )
    yield
    background_jobs.stop()


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.middleware("http")
async def trace_request(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    set_request_id(request_id)
    started = perf_counter()
    try:
        response = await call_next(request)
    finally:
        duration_ms = round((perf_counter() - started) * 1000.0, 2)
        logger.info(
            "request method=%s path=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
    response.headers["x-request-id"] = request_id
    clear_request_id()
    return response


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    now_minute = int(perf_counter() // 60)
    key = request.client.host if request.client else "unknown"
    count, minute = _rate_limiter.get(key, (0, now_minute))
    if minute != now_minute:
        count, minute = 0, now_minute
    count += 1
    _rate_limiter[key] = (count, minute)
    if count > settings.RATE_LIMIT_PER_MINUTE:
        return Response(status_code=429, content="rate limit exceeded")
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}
