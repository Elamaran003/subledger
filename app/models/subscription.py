from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import SubscriptionStatus, enum_column
from app.utils import utcnow


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        # DB-level safety net for "no two ACTIVE subscriptions to the same plan".
        # The service checks first; this guards against race conditions.
        Index(
            "uq_active_subscription_per_plan",
            "customer_id",
            "plan_id",
            unique=True,
            sqlite_where=text("status = 'active'"),
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(
        enum_column(SubscriptionStatus), default=SubscriptionStatus.ACTIVE
    )
    start_date: Mapped[date] = mapped_column(Date, default=lambda: utcnow().date())
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    customer: Mapped["Customer"] = relationship(back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="subscription")
