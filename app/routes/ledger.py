from fastapi import APIRouter, Depends

from app.dependencies import get_ledger_service
from app.models.enums import LedgerEntryType
from app.schemas.ledger import LedgerEntryRead
from app.services.ledger_service import LedgerService

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("", response_model=list[LedgerEntryRead])
def list_ledger_entries(
    customer_id: int | None = None,
    invoice_id: int | None = None,
    reference_id: str | None = None,
    entry_type: LedgerEntryType | None = None,
    service: LedgerService = Depends(get_ledger_service),
):
    return service.list_entries(
        customer_id=customer_id,
        invoice_id=invoice_id,
        reference_id=reference_id,
        entry_type=entry_type,
    )
