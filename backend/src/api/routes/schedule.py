from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, get_db
from src.crud.schedule import schedule_crud_interface
from src.models.user import User
from src.schemas.schedule import ScheduleCreate, ScheduleOut

router = APIRouter()

@router.post("/", response_model=ScheduleOut)
def create_schedule_for_user(current_user: Annotated[User, Depends(get_current_user)],
                             db: Annotated[Session, Depends(get_db)],
                             schedule_create: ScheduleCreate
                             ) -> ScheduleOut:
    schedule = schedule_crud_interface.create_with_owner(db, current_user.id, schedule_create)
    return schedule

@router.get("/")
def get_my_schedules(current_user: Annotated[User, Depends(get_current_user)],
                     db: Annotated[Session, Depends(get_db)]
                     ) -> List[ScheduleOut]:
    schedules = schedule_crud_interface.get_many_by_owner_id(db, current_user.id)
    return [ScheduleOut.model_validate(schedule) for schedule in schedules]

