from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[str] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    scores: Mapped[list["AnomalyScore"]] = relationship(back_populates="event")


class AnomalyScore(Base):
    __tablename__ = "anomaly_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    z_score: Mapped[float] = mapped_column(Float)
    isolation_forest_score: Mapped[float] = mapped_column(Float)
    combined_score: Mapped[float] = mapped_column(Float, index=True)
    model_version: Mapped[str] = mapped_column(String(40), default="mvp-v1")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    event: Mapped[Event] = relationship(back_populates="scores")
    alert: Mapped["Alert | None"] = relationship(back_populates="anomaly_score", uselist=False)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    anomaly_score_id: Mapped[int] = mapped_column(ForeignKey("anomaly_scores.id"), index=True)
    severity: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    anomaly_score: Mapped[AnomalyScore] = relationship(back_populates="alert")
