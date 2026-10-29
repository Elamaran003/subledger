from sqlalchemy import select

from app.models import PaymentAttempt
from app.repositories.base import BaseRepository


class PaymentAttemptRepository(BaseRepository):
    def create(self, **fields) -> PaymentAttempt:
        return self._add(PaymentAttempt(**fields))

    def get_by_provider_reference(self, ref: str) -> PaymentAttempt | None:
        stmt = select(PaymentAttempt).where(PaymentAttempt.provider_reference == ref)
        return self.db.scalars(stmt).first()

    def list_for_invoice(self, invoice_id: int) -> list[PaymentAttempt]:
        stmt = (
            select(PaymentAttempt)
            .where(PaymentAttempt.invoice_id == invoice_id)
            .order_by(PaymentAttempt.id)
        )
        return list(self.db.scalars(stmt))
