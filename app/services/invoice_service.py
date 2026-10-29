from datetime import date, timedelta

from app.config import get_settings
from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Invoice
from app.models.enums import (
    BillingInterval,
    InvoiceStatus,
    LedgerEntryType,
    SubscriptionStatus,
)
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.invoice import InvoiceGenerate
from app.services.ledger_service import LedgerService
from app.utils import add_months


class InvoiceService:
    """Owns: invoice generation, price snapshot (amount_due), billing period
    calculation, 'subscription must be active' rule, duplicate-period guard."""

    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
        invoice_repo: InvoiceRepository,
        ledger_service: LedgerService,
    ):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.invoice_repo = invoice_repo
        self.ledger_service = ledger_service

    @staticmethod
    def _period_end(start: date, interval: BillingInterval) -> date:
        months = 12 if interval == BillingInterval.YEARLY else 1
        return add_months(start, months)

    def generate_invoice(self, data: InvoiceGenerate) -> Invoice:
        sub = self.subscription_repo.get(data.subscription_id)
        if not sub:
            raise NotFoundError(f"Subscription {data.subscription_id} not found.")
        if sub.status != SubscriptionStatus.ACTIVE:
            raise BusinessRuleError("Cannot generate an invoice for a non-active subscription.")

        plan = self.plan_repo.get(sub.plan_id)
        if not plan:
            raise NotFoundError(f"Plan {sub.plan_id} not found.")

        start = data.period_start or date.today()
        end = data.period_end or self._period_end(start, plan.billing_interval)

        if self.invoice_repo.get_by_period(sub.id, start, end):
            raise ConflictError("An invoice already exists for this subscription and period.")

        try:
            invoice = self.invoice_repo.create(
                subscription_id=sub.id,
                customer_id=sub.customer_id,
                amount_due=plan.price,  # snapshot of price at generation time
                currency=plan.currency,
                status=InvoiceStatus.ISSUED,
                period_start=start,
                period_end=end,
                due_date=start + timedelta(days=get_settings().invoice_due_days),
            )
            self.ledger_service.record(
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                entry_type=LedgerEntryType.INVOICE_CREATED,
                amount=invoice.amount_due,
                currency=invoice.currency,
                reference_id=f"invoice:{invoice.id}",
                description=f"Invoice issued for {start} to {end}",
            )
            self.invoice_repo.commit()
        except Exception:
            self.invoice_repo.rollback()
            raise
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.invoice_repo.get(invoice_id)
        if not invoice:
            raise NotFoundError(f"Invoice {invoice_id} not found.")
        return invoice

    def list_invoices(self, **filters) -> list[Invoice]:
        return self.invoice_repo.list(**filters)
