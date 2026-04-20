from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.event import Event


class AnomalyScore(Base):
    __tablename__ = "anomaly_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    z_score: Mapped[float] = mapped_column(Float, nullable=False)
    isolation_score: Mapped[float] = mapped_column(Float, nullable=False)
    rolling_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    seasonal_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    combined_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    is_anomalous: Mapped[bool] = mapped_column(default=False, index=True)
    selected_detector: Mapped[str] = mapped_column(String(64), nullable=False, default="blended")
    dynamic_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.75)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="low", index=True)
    reason_codes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    scoring_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_grouped: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )

    event: Mapped["Event"] = relationship(back_populates="scores")
