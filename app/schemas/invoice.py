from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import InvoiceStatus


class InvoiceGenerate(BaseModel):
    subscription_id: int
    period_start: date | None = None
    period_end: date | None = None

    @model_validator(mode="after")
    def check_period(self):
        if self.period_end and not self.period_start:
            raise ValueError("period_start is required when period_end is provided")
        if self.period_start and self.period_end and self.period_end <= self.period_start:
            raise ValueError("period_end must be after period_start")
        return self


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subscription_id: int
    customer_id: int
    amount_due: Decimal
    amount_paid: Decimal
    amount_remaining: Decimal
    currency: str
    status: InvoiceStatus
    period_start: date
    period_end: date
    due_date: date
    created_at: datetime
