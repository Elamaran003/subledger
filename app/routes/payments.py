from fastapi import APIRouter, Depends

from app.dependencies import get_payment_service
from app.schemas.payment import PaymentCreate, PaymentResult
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentResult, status_code=201)
def record_payment(payload: PaymentCreate, service: PaymentService = Depends(get_payment_service)):
    attempt, invoice = service.record_payment(payload)
    return PaymentResult(payment_attempt=attempt, invoice=invoice)
