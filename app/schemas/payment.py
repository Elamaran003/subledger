from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentStatus
from app.schemas.invoice import InvoiceRead


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    status: PaymentStatus
    provider_reference: str = Field(min_length=1, max_length=100)
    failure_reason: str | None = Field(default=None, max_length=255)


class PaymentAttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider_reference: str
    failure_reason: str | None
    created_at: datetime


class PaymentResult(BaseModel):
    payment_attempt: PaymentAttemptRead
    invoice: InvoiceRead
