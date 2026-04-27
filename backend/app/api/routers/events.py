from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.event import (
    BufferEnqueueRequest,
    BufferEnqueueResponse,
    BufferFlushResponse,
    BufferStatsResponse,
    EventCreate,
    EventIngestResponse,
    EventRead,
    ReplayRequest,
    ReplayResponse,
    ScoredEventRead,
)
from app.services.event_service import EventService

router = APIRouter()


@router.post("/ingest", response_model=EventIngestResponse, status_code=201)
def ingest_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventIngestResponse:
    return EventService(db).ingest_event(payload)


@router.get("", response_model=list[EventRead])
def list_events(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0, le=5000),
    sort_desc: bool = Query(default=True),
    workspace_id: str | None = Query(default=None),
) -> list[EventRead]:
    return EventService(db).list_events(
        limit=limit, offset=offset, sort_desc=sort_desc, workspace_id=workspace_id
    )


@router.post("/replay", response_model=ReplayResponse, status_code=201)
def replay_events(payload: ReplayRequest, db: Session = Depends(get_db)) -> ReplayResponse:
    return EventService(db).replay_seeded_stream(payload)


@router.get("/scored", response_model=list[ScoredEventRead])
def list_scored_events(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0, le=5000),
    sort_desc: bool = Query(default=True),
    workspace_id: str | None = Query(default=None),
    anomalous_only: bool = Query(default=False),
) -> list[ScoredEventRead]:
    return EventService(db).list_scored_events(
        limit=limit,
        offset=offset,
        sort_desc=sort_desc,
        workspace_id=workspace_id,
        anomalous_only=anomalous_only,
    )


@router.post("/buffer/enqueue", response_model=BufferEnqueueResponse, status_code=202)
def enqueue_buffer(
    payload: BufferEnqueueRequest, db: Session = Depends(get_db)
) -> BufferEnqueueResponse:
    return EventService(db).buffer_enqueue(payload)


@router.post("/buffer/flush", response_model=BufferFlushResponse)
def flush_buffer(
    limit: int | None = Query(default=None, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> BufferFlushResponse:
    return EventService(db).buffer_flush(limit=limit)


@router.get("/buffer/stats", response_model=BufferStatsResponse)
def buffer_stats(db: Session = Depends(get_db)) -> BufferStatsResponse:
    return EventService(db).buffer_stats()
