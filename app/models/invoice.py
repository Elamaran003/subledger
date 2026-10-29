from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import InvoiceStatus, enum_column
from app.utils import utcnow


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("subscription_id", "period_start", "period_end", name="uq_invoice_period"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # plan price snapshot
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[InvoiceStatus] = mapped_column(
        enum_column(InvoiceStatus), default=InvoiceStatus.ISSUED, index=True
    )
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    subscription: Mapped["Subscription"] = relationship(back_populates="invoices")
    payment_attempts: Mapped[list["PaymentAttempt"]] = relationship(back_populates="invoice")
    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="invoice")

    @property
    def amount_remaining(self) -> Decimal:
        return self.amount_due - self.amount_paid
