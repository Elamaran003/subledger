from decimal import Decimal

from app.models import LedgerEntry
from app.models.enums import LedgerEntryType
from app.repositories.ledger_repository import LedgerRepository


class LedgerService:
    """Owns: ledger entry creation and the reference_id naming convention.
    Does NOT commit - the calling use case commits so invoice/payment and
    ledger entry succeed or fail together."""

    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def record(
        self,
        *,
        customer_id: int,
        invoice_id: int | None,
        entry_type: LedgerEntryType,
        amount: Decimal,
        currency: str,
        reference_id: str,
        description: str | None = None,
    ) -> LedgerEntry:
        return self.ledger_repo.append(
            customer_id=customer_id,
            invoice_id=invoice_id,
            entry_type=entry_type,
            amount=amount,
            currency=currency,
            reference_id=reference_id,
            description=description,
        )

    def list_entries(self, **filters) -> list[LedgerEntry]:
        return self.ledger_repo.list(**filters)
