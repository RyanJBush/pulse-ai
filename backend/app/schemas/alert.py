from datetime import datetime

from pydantic import BaseModel


class AlertRead(BaseModel):
    id: int
    event_id: int
    severity: str
    message: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
