from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnomalyScore(Base):
    __tablename__ = "anomaly_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    z_score: Mapped[float] = mapped_column(Float, nullable=False)
    isolation_score: Mapped[float] = mapped_column(Float, nullable=False)
    combined_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    is_anomalous: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event: Mapped["Event"] = relationship(back_populates="scores")
