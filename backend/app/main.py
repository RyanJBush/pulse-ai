from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.anomaly import score_event
from app.database import Base, engine, get_db
from app.models import Alert, AnomalyScore, Event
from app.schemas import (
    AlertRead,
    AnomalyScoreRead,
    AnomalyScoreRequest,
    EventCreate,
    EventRead,
    MetricsSummary,
)

app = FastAPI(title="Pulse AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/events", response_model=EventRead)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> Event:
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/api/events", response_model=list[EventRead])
def list_events(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Event]:
    events = db.scalars(
        select(Event).order_by(desc(Event.created_at)).limit(limit).offset(offset)
    ).all()
    return list(events)


@app.post("/api/anomaly/score", response_model=AnomalyScoreRead)
def score_anomaly(payload: AnomalyScoreRequest, db: Session = Depends(get_db)) -> AnomalyScoreRead:
    event = db.get(Event, payload.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")

    try:
        score, alert = score_event(db, event, threshold=payload.threshold)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.commit()
    db.refresh(score)

    output = AnomalyScoreRead.model_validate(score)
    output.alert_id = alert.id if alert else None
    return output


@app.get("/api/anomaly/{event_id}", response_model=AnomalyScoreRead)
def get_latest_event_score(event_id: int, db: Session = Depends(get_db)) -> AnomalyScoreRead:
    score = db.scalars(
        select(AnomalyScore)
        .where(AnomalyScore.event_id == event_id)
        .order_by(desc(AnomalyScore.created_at))
        .limit(1)
    ).first()
    if score is None:
        raise HTTPException(status_code=404, detail="anomaly score not found")

    output = AnomalyScoreRead.model_validate(score)
    output.alert_id = score.alert.id if score.alert else None
    return output


@app.get("/api/alerts", response_model=list[AlertRead])
def list_alerts(status: str | None = None, db: Session = Depends(get_db)) -> list[Alert]:
    query = select(Alert).order_by(desc(Alert.created_at))
    if status:
        query = query.where(Alert.status == status)
    return list(db.scalars(query).all())


@app.get("/api/alerts/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: int, db: Session = Depends(get_db)) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert not found")
    return alert


@app.get("/api/metrics/summary", response_model=MetricsSummary)
def metrics_summary(db: Session = Depends(get_db)) -> MetricsSummary:
    total_events = db.scalar(select(func.count(Event.id))) or 0
    total_scores = db.scalar(select(func.count(AnomalyScore.id))) or 0
    total_alerts = db.scalar(select(func.count(Alert.id))) or 0
    open_alerts = db.scalar(select(func.count(Alert.id)).where(Alert.status == "open")) or 0
    avg_combined_score = db.scalar(select(func.avg(AnomalyScore.combined_score))) or 0.0

    cutoff = datetime.utcnow() - timedelta(hours=1)
    events_last_hour = (
        db.scalar(select(func.count(Event.id)).where(Event.created_at >= cutoff)) or 0
    )

    top_sources_rows = db.execute(
        select(Event.source_id, func.count(Event.id).label("count"))
        .group_by(Event.source_id)
        .order_by(desc("count"))
        .limit(5)
    ).all()

    return MetricsSummary(
        total_events=total_events,
        total_scores=total_scores,
        total_alerts=total_alerts,
        open_alerts=open_alerts,
        avg_combined_score=round(float(avg_combined_score), 6),
        events_last_hour=events_last_hour,
        top_sources=[{"source_id": row.source_id, "count": row.count} for row in top_sources_rows],
    )
