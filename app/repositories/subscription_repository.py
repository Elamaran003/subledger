from sqlalchemy import select

from app.models import Subscription
from app.models.enums import SubscriptionStatus
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository):
    def create(self, **fields) -> Subscription:
        return self._add(Subscription(**fields))

    def get(self, subscription_id: int) -> Subscription | None:
        return self.db.get(Subscription, subscription_id)

    def find_active(self, customer_id: int, plan_id: int) -> Subscription | None:
        stmt = select(Subscription).where(
            Subscription.customer_id == customer_id,
            Subscription.plan_id == plan_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
        return self.db.scalars(stmt).first()

    def list(self, customer_id: int | None = None) -> list[Subscription]:
        stmt = select(Subscription).order_by(Subscription.id)
        if customer_id is not None:
            stmt = stmt.where(Subscription.customer_id == customer_id)
        return list(self.db.scalars(stmt))
