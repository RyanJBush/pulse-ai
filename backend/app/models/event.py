from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    scores: Mapped[list["AnomalyScore"]] = relationship(back_populates="event", cascade="all, delete-orphan")
