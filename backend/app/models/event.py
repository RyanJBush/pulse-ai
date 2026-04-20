from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.anomaly_score import AnomalyScore


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    signal_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False, default="global", index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    scores: Mapped[list["AnomalyScore"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="event", cascade="all, delete-orphan")
