from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DetectorConfig(Base):
    __tablename__ = "detector_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    signal_type: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    z_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.3)
    isolation_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.3)
    rolling_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)
    seasonal_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.15)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    updated_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )
