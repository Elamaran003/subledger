from fastapi import APIRouter, Depends

from app.dependencies import get_invoice_service, get_payment_service
from app.models.enums import InvoiceStatus
from app.schemas.invoice import InvoiceGenerate, InvoiceRead
from app.schemas.payment import PaymentAttemptRead
from app.services.invoice_service import InvoiceService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/generate", response_model=InvoiceRead, status_code=201)
def generate_invoice(payload: InvoiceGenerate, service: InvoiceService = Depends(get_invoice_service)):
    return service.generate_invoice(payload)


@router.get("", response_model=list[InvoiceRead])
def list_invoices(
    customer_id: int | None = None,
    subscription_id: int | None = None,
    status: InvoiceStatus | None = None,
    service: InvoiceService = Depends(get_invoice_service),
):
    return service.list_invoices(customer_id=customer_id, subscription_id=subscription_id, status=status)


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: int, service: InvoiceService = Depends(get_invoice_service)):
    return service.get_invoice(invoice_id)


@router.get("/{invoice_id}/payments", response_model=list[PaymentAttemptRead])
def list_invoice_payments(invoice_id: int, service: PaymentService = Depends(get_payment_service)):
    return service.list_for_invoice(invoice_id)
