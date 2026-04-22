from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SuppressionRule(Base):
    __tablename__ = "suppression_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(64), index=True, default="default")
    entity_id: Mapped[str] = mapped_column(String(255), index=True)
    signal_type: Mapped[str] = mapped_column(String(255), index=True)
    reason: Mapped[str] = mapped_column(String(255), default="manual suppression")
    created_by: Mapped[str] = mapped_column(String(120), default="system")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True
    )
