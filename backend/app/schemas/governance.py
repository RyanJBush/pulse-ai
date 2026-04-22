from datetime import datetime

from pydantic import BaseModel, Field


class DetectorConfigRead(BaseModel):
    id: int
    signal_type: str
    z_weight: float
    isolation_weight: float
    rolling_weight: float
    seasonal_weight: float
    enabled: bool
    updated_by: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class DetectorConfigUpdate(BaseModel):
    signal_type: str = Field(..., min_length=1, max_length=128)
    z_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    isolation_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    rolling_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    seasonal_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    enabled: bool = True
    actor: str = Field(default="system", min_length=1, max_length=120)


class AuditLogRead(BaseModel):
    id: int
    actor: str
    action: str
    resource_type: str
    resource_id: str
    details: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SuppressionRuleCreate(BaseModel):
    workspace_id: str = Field(default="default", min_length=1, max_length=64)
    entity_id: str = Field(..., min_length=1, max_length=255)
    signal_type: str = Field(..., min_length=1, max_length=255)
    reason: str = Field(default="manual suppression", min_length=1, max_length=255)
    actor: str = Field(default="system", min_length=1, max_length=120)


class SuppressionRuleRead(BaseModel):
    id: int
    workspace_id: str
    entity_id: str
    signal_type: str
    reason: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}
