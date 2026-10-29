from sqlalchemy import select

from app.models import Plan
from app.repositories.base import BaseRepository


class PlanRepository(BaseRepository):
    def create(self, **fields) -> Plan:
        return self._add(Plan(**fields))

    def get(self, plan_id: int) -> Plan | None:
        return self.db.get(Plan, plan_id)

    def get_by_name(self, name: str) -> Plan | None:
        return self.db.scalars(select(Plan).where(Plan.name == name)).first()

    def list(self, active_only: bool = False) -> list[Plan]:
        stmt = select(Plan).order_by(Plan.id)
        if active_only:
            stmt = stmt.where(Plan.is_active.is_(True))
        return list(self.db.scalars(stmt))
