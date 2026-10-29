from enum import Enum

from sqlalchemy import Enum as SAEnum


class BillingInterval(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    VOID = "void"


class PaymentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class LedgerEntryType(str, Enum):
    INVOICE_CREATED = "invoice_created"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILURE = "payment_failure"


def enum_column(enum_cls):
    """Portable (non-native) enum stored as its string value."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=30,
        values_callable=lambda e: [m.value for m in e],
        validate_strings=True,
    )
