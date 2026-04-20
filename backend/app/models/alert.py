from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert_note import AlertNote
    from app.models.event import Event


ALERT_STATUSES = {"new", "acknowledged", "investigating", "resolved", "suppressed"}


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    anomaly_score_id: Mapped[int | None] = mapped_column(
        ForeignKey("anomaly_scores.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    severity: Mapped[str] = mapped_column(String(32), default="medium", index=True)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)
    assigned_owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    cooldown_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        index=True,
    )
    last_transition_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        index=True,
    )

    event: Mapped["Event"] = relationship(back_populates="alerts")
    notes: Mapped[list["AlertNote"]] = relationship(
        back_populates="alert",
        cascade="all, delete-orphan",
    )
