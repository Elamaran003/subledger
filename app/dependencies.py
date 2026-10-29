"""Dependency wiring (constructor injection). Routes depend on services only."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.customer_repository import CustomerRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.ledger_repository import LedgerRepository
from app.repositories.payment_attempt_repository import PaymentAttemptRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.customer_service import CustomerService
from app.services.invoice_service import InvoiceService
from app.services.ledger_service import LedgerService
from app.services.payment_service import PaymentService
from app.services.plan_service import PlanService
from app.services.subscription_service import SubscriptionService


def get_plan_service(db: Session = Depends(get_db)) -> PlanService:
    return PlanService(PlanRepository(db))


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(CustomerRepository(db))


def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    return SubscriptionService(
        SubscriptionRepository(db), CustomerRepository(db), PlanRepository(db)
    )


def get_ledger_service(db: Session = Depends(get_db)) -> LedgerService:
    return LedgerService(LedgerRepository(db))


def get_invoice_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(
        SubscriptionRepository(db),
        PlanRepository(db),
        InvoiceRepository(db),
        LedgerService(LedgerRepository(db)),
    )


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(
        InvoiceRepository(db),
        PaymentAttemptRepository(db),
        LedgerService(LedgerRepository(db)),
    )
