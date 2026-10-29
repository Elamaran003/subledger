from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Invoice, PaymentAttempt
from app.models.enums import InvoiceStatus, LedgerEntryType, PaymentStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.payment_attempt_repository import PaymentAttemptRepository
from app.schemas.payment import PaymentCreate
from app.services.ledger_service import LedgerService

PAYABLE_STATUSES = {InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID}


class PaymentService:
    """Owns: payment validation, overpayment rule, invoice status transitions,
    'failed payment does not change amount_paid', idempotency by provider_reference."""

    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        payment_attempt_repo: PaymentAttemptRepository,
        ledger_service: LedgerService,
    ):
        self.invoice_repo = invoice_repo
        self.payment_attempt_repo = payment_attempt_repo
        self.ledger_service = ledger_service

    def record_payment(self, data: PaymentCreate) -> tuple[PaymentAttempt, Invoice]:
        invoice = self.invoice_repo.get(data.invoice_id, for_update=True)
        if not invoice:
            raise NotFoundError(f"Invoice {data.invoice_id} not found.")

        if self.payment_attempt_repo.get_by_provider_reference(data.provider_reference):
            raise ConflictError(
                f"provider_reference '{data.provider_reference}' was already recorded."
            )
        if invoice.status not in PAYABLE_STATUSES:
            raise BusinessRuleError(f"Invoice is '{invoice.status.value}' and cannot accept payments.")
        if data.currency.upper() != invoice.currency:
            raise BusinessRuleError(
                f"Payment currency {data.currency.upper()} does not match invoice currency {invoice.currency}."
            )
        if data.status == PaymentStatus.SUCCESS and data.amount > invoice.amount_remaining:
            raise BusinessRuleError(
                f"Payment of {data.amount} exceeds remaining unpaid amount {invoice.amount_remaining}."
            )

        failed = data.status == PaymentStatus.FAILED
        try:
            attempt = self.payment_attempt_repo.create(
                invoice_id=invoice.id,
                amount=data.amount,
                currency=invoice.currency,
                status=data.status,
                provider_reference=data.provider_reference,
                failure_reason=(data.failure_reason or "unspecified") if failed else None,
            )

            if not failed:
                new_paid = invoice.amount_paid + data.amount
                new_status = (
                    InvoiceStatus.PAID
                    if new_paid == invoice.amount_due
                    else InvoiceStatus.PARTIALLY_PAID
                )
                self.invoice_repo.update_payment_state(invoice, new_paid, new_status)

            self.ledger_service.record(
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                entry_type=LedgerEntryType.PAYMENT_FAILURE if failed else LedgerEntryType.PAYMENT_SUCCESS,
                amount=data.amount,
                currency=invoice.currency,
                reference_id=f"payment:{attempt.id}",
                description=attempt.failure_reason if failed else "Payment received",
            )
            self.invoice_repo.commit()
        except Exception:
            self.invoice_repo.rollback()
            raise
        return attempt, invoice

    def list_for_invoice(self, invoice_id: int) -> list[PaymentAttempt]:
        if not self.invoice_repo.get(invoice_id):
            raise NotFoundError(f"Invoice {invoice_id} not found.")
        return self.payment_attempt_repo.list_for_invoice(invoice_id)
