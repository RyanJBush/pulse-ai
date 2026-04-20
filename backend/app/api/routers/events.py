from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.event import EventCreate, EventIngestResponse, EventRead
from app.services.event_service import EventService

router = APIRouter()


@router.post("/ingest", response_model=EventIngestResponse, status_code=201)
def ingest_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventIngestResponse:
    return EventService(db).ingest_event(payload)


@router.get("", response_model=list[EventRead])
def list_events(db: Session = Depends(get_db), limit: int = 100) -> list[EventRead]:
    return EventService(db).list_events(limit=limit)
