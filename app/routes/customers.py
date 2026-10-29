from fastapi import APIRouter, Depends

from app.dependencies import get_customer_service
from app.schemas.customer import CustomerCreate, CustomerRead
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(payload: CustomerCreate, service: CustomerService = Depends(get_customer_service)):
    return service.create_customer(payload)


@router.get("", response_model=list[CustomerRead])
def list_customers(service: CustomerService = Depends(get_customer_service)):
    return service.list_customers()


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    return service.get_customer(customer_id)
