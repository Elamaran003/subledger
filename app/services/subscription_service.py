from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Subscription
from app.models.enums import SubscriptionStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription import SubscriptionCreate
from app.utils import utcnow


class SubscriptionService:
    """Owns: inactive-plan rule, one-active-subscription-per-plan rule, cancellation."""

    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        customer_repo: CustomerRepository,
        plan_repo: PlanRepository,
    ):
        self.subscription_repo = subscription_repo
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo

    def create_subscription(self, data: SubscriptionCreate) -> Subscription:
        if not self.customer_repo.get(data.customer_id):
            raise NotFoundError(f"Customer {data.customer_id} not found.")
        plan = self.plan_repo.get(data.plan_id)
        if not plan:
            raise NotFoundError(f"Plan {data.plan_id} not found.")
        if not plan.is_active:
            raise BusinessRuleError("Cannot subscribe to an inactive plan.")
        if self.subscription_repo.find_active(data.customer_id, data.plan_id):
            raise ConflictError("Customer already has an active subscription to this plan.")

        sub = self.subscription_repo.create(
            customer_id=data.customer_id,
            plan_id=data.plan_id,
            status=SubscriptionStatus.ACTIVE,
        )
        self.subscription_repo.commit()
        return sub

    def get_subscription(self, subscription_id: int) -> Subscription:
        sub = self.subscription_repo.get(subscription_id)
        if not sub:
            raise NotFoundError(f"Subscription {subscription_id} not found.")
        return sub

    def list_subscriptions(self, customer_id: int | None = None) -> list[Subscription]:
        return self.subscription_repo.list(customer_id=customer_id)

    def cancel_subscription(self, subscription_id: int) -> Subscription:
        sub = self.get_subscription(subscription_id)
        if sub.status == SubscriptionStatus.CANCELLED:
            raise BusinessRuleError("Subscription is already cancelled.")
        sub.status = SubscriptionStatus.CANCELLED
        sub.cancelled_at = utcnow()
        self.subscription_repo.save(sub)
        self.subscription_repo.commit()
        return sub
