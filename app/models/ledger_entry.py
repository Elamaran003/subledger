from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.exceptions import LedgerImmutableError
from app.models.enums import LedgerEntryType, enum_column
from app.utils import utcnow


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"), index=True, nullable=True)
    entry_type: Mapped[LedgerEntryType] = mapped_column(enum_column(LedgerEntryType), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    # e.g. "invoice:12" or "payment:7" -> traces an entry to the record that caused it
    reference_id: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    customer: Mapped["Customer"] = relationship(back_populates="ledger_entries")
    invoice: Mapped["Invoice | None"] = relationship(back_populates="ledger_entries")


# Append-only enforcement at the ORM layer (in addition to having no update/delete
# methods on LedgerRepository).
@event.listens_for(LedgerEntry, "before_update")
def _block_update(mapper, connection, target):
    raise LedgerImmutableError("Ledger entries are append-only and cannot be updated.")


@event.listens_for(LedgerEntry, "before_delete")
def _block_delete(mapper, connection, target):
    raise LedgerImmutableError("Ledger entries are append-only and cannot be deleted.")
