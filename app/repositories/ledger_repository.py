from sqlalchemy import select

from app.models import LedgerEntry
from app.models.enums import LedgerEntryType
from app.repositories.base import BaseRepository


class LedgerRepository(BaseRepository):
    """Append + read only. Intentionally no update/delete methods."""

    def append(self, **fields) -> LedgerEntry:
        return self._add(LedgerEntry(**fields))

    def list(
        self,
        customer_id: int | None = None,
        invoice_id: int | None = None,
        reference_id: str | None = None,
        entry_type: LedgerEntryType | None = None,
    ) -> list[LedgerEntry]:
        stmt = select(LedgerEntry).order_by(LedgerEntry.id)
        if customer_id is not None:
            stmt = stmt.where(LedgerEntry.customer_id == customer_id)
        if invoice_id is not None:
            stmt = stmt.where(LedgerEntry.invoice_id == invoice_id)
        if reference_id is not None:
            stmt = stmt.where(LedgerEntry.reference_id == reference_id)
        if entry_type is not None:
            stmt = stmt.where(LedgerEntry.entry_type == entry_type)
        return list(self.db.scalars(stmt))
