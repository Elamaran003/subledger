from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BillingInterval


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    billing_interval: BillingInterval = BillingInterval.MONTHLY


class PlanUpdate(BaseModel):
    description: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: Decimal
    currency: str
    billing_interval: BillingInterval
    is_active: bool
    created_at: datetime
