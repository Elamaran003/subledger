from sqlalchemy import select

from app.models import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository):
    def create(self, **fields) -> Customer:
        return self._add(Customer(**fields))

    def get(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.scalars(select(Customer).where(Customer.email == email)).first()

    def list(self) -> list[Customer]:
        return list(self.db.scalars(select(Customer).order_by(Customer.id)))
