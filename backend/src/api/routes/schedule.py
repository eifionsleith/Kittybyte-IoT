from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, get_db
from src.crud.schedule import schedule_crud_interface
from src.models.user import User
from src.schemas.schedule import ScheduleCreate, ScheduleOut, ScheduleUpdate

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


@router.put("/{schedule_id}")
def update_my_schedule(current_user: Annotated[User, Depends(get_current_user)],
                       db: Annotated[Session, Depends(get_db)],
                       schedule_update: ScheduleUpdate,
                       schedule_id: UUID
                       ) -> ScheduleOut:
    """
    Allows a user to update a schedule, assuming they are the owner 
    of said schedule.
    """
    schedule = schedule_crud_interface.get_by_id(db, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Schedule not found.")

    if schedule.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User can't do this.")

    schedule = schedule_crud_interface.update(db, schedule, schedule_update)
    return schedule

