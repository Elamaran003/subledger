from fastapi import APIRouter, Depends

from app.dependencies import get_plan_service
from app.schemas.plan import PlanCreate, PlanRead, PlanUpdate
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.post("", response_model=PlanRead, status_code=201)
def create_plan(payload: PlanCreate, service: PlanService = Depends(get_plan_service)):
    return service.create_plan(payload)


@router.get("", response_model=list[PlanRead])
def list_plans(active_only: bool = False, service: PlanService = Depends(get_plan_service)):
    return service.list_plans(active_only=active_only)


@router.get("/{plan_id}", response_model=PlanRead)
def get_plan(plan_id: int, service: PlanService = Depends(get_plan_service)):
    return service.get_plan(plan_id)


@router.patch("/{plan_id}", response_model=PlanRead)
def update_plan(plan_id: int, payload: PlanUpdate, service: PlanService = Depends(get_plan_service)):
    return service.update_plan(plan_id, payload)


@router.post("/{plan_id}/deactivate", response_model=PlanRead)
def deactivate_plan(plan_id: int, service: PlanService = Depends(get_plan_service)):
    return service.set_active(plan_id, False)


@router.post("/{plan_id}/activate", response_model=PlanRead)
def activate_plan(plan_id: int, service: PlanService = Depends(get_plan_service)):
    return service.set_active(plan_id, True)
