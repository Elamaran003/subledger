from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.models import Invoice
from app.models.enums import InvoiceStatus
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository):
    def create(self, **fields) -> Invoice:
        return self._add(Invoice(**fields))

    def get(self, invoice_id: int, for_update: bool = False) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        if for_update:  # row lock on Postgres; no-op on SQLite
            stmt = stmt.with_for_update()
        return self.db.scalars(stmt).first()

    def get_by_period(self, subscription_id: int, start: date, end: date) -> Invoice | None:
        stmt = select(Invoice).where(
            Invoice.subscription_id == subscription_id,
            Invoice.period_start == start,
            Invoice.period_end == end,
        )
        return self.db.scalars(stmt).first()

    def list(
        self,
        customer_id: int | None = None,
        subscription_id: int | None = None,
        status: InvoiceStatus | None = None,
    ) -> list[Invoice]:
        stmt = select(Invoice).order_by(Invoice.id)
        if customer_id is not None:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if subscription_id is not None:
            stmt = stmt.where(Invoice.subscription_id == subscription_id)
        if status is not None:
            stmt = stmt.where(Invoice.status == status)
        return list(self.db.scalars(stmt))

    def update_payment_state(
        self, invoice: Invoice, amount_paid: Decimal, status: InvoiceStatus
    ) -> Invoice:
        invoice.amount_paid = amount_paid
        invoice.status = status
        return self.save(invoice)
