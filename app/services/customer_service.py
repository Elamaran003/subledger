from app.exceptions import ConflictError, NotFoundError
from app.models import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate


class CustomerService:
    """Owns: customer email uniqueness."""

    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    def create_customer(self, data: CustomerCreate) -> Customer:
        if self.customer_repo.get_by_email(data.email):
            raise ConflictError(f"A customer with email '{data.email}' already exists.")
        customer = self.customer_repo.create(name=data.name, email=data.email)
        self.customer_repo.commit()
        return customer

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.customer_repo.get(customer_id)
        if not customer:
            raise NotFoundError(f"Customer {customer_id} not found.")
        return customer

    def list_customers(self) -> list[Customer]:
        return self.customer_repo.list()
