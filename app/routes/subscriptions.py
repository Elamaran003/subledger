from fastapi import APIRouter, Depends

from app.dependencies import get_subscription_service
from app.schemas.subscription import SubscriptionCreate, SubscriptionRead
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("", response_model=SubscriptionRead, status_code=201)
def create_subscription(
    payload: SubscriptionCreate, service: SubscriptionService = Depends(get_subscription_service)
):
    return service.create_subscription(payload)


@router.get("", response_model=list[SubscriptionRead])
def list_subscriptions(
    customer_id: int | None = None, service: SubscriptionService = Depends(get_subscription_service)
):
    return service.list_subscriptions(customer_id=customer_id)


@router.get("/{subscription_id}", response_model=SubscriptionRead)
def get_subscription(subscription_id: int, service: SubscriptionService = Depends(get_subscription_service)):
    return service.get_subscription(subscription_id)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionRead)
def cancel_subscription(subscription_id: int, service: SubscriptionService = Depends(get_subscription_service)):
    return service.cancel_subscription(subscription_id)
