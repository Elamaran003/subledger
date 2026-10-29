from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Plan
from app.repositories.plan_repository import PlanRepository
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanService:
    """Owns: plan price > 0, plan name uniqueness, activation state."""

    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo

    def create_plan(self, data: PlanCreate) -> Plan:
        if data.price <= 0:
            raise BusinessRuleError("Plan price must be greater than 0.")
        if self.plan_repo.get_by_name(data.name):
            raise ConflictError(f"A plan named '{data.name}' already exists.")
        plan = self.plan_repo.create(
            name=data.name,
            description=data.description,
            price=data.price,
            currency=data.currency.upper(),
            billing_interval=data.billing_interval,
        )
        self.plan_repo.commit()
        return plan

    def get_plan(self, plan_id: int) -> Plan:
        plan = self.plan_repo.get(plan_id)
        if not plan:
            raise NotFoundError(f"Plan {plan_id} not found.")
        return plan

    def list_plans(self, active_only: bool = False) -> list[Plan]:
        return self.plan_repo.list(active_only=active_only)

    def update_plan(self, plan_id: int, data: PlanUpdate) -> Plan:
        plan = self.get_plan(plan_id)
        if data.price is not None:
            if data.price <= 0:
                raise BusinessRuleError("Plan price must be greater than 0.")
            plan.price = data.price  # existing invoices keep their own snapshot
        if data.description is not None:
            plan.description = data.description
        self.plan_repo.save(plan)
        self.plan_repo.commit()
        return plan

    def set_active(self, plan_id: int, active: bool) -> Plan:
        plan = self.get_plan(plan_id)
        plan.is_active = active
        self.plan_repo.save(plan)
        self.plan_repo.commit()
        return plan
