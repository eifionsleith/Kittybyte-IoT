from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.schedule import Schedule
from src.models.schedule_slot import ScheduleSlot
from src.schemas.schedule import ScheduleCreate, ScheduleUpdate


class CRUDSchedule(CRUDBase[Schedule, ScheduleCreate, ScheduleUpdate]):
    def get_many_by_owner_id(self, db: Session, owner_id: UUID) -> List[Schedule]:
        return self.get_many(db, self.model.owner_id == owner_id)

    def create_with_owner(self, db: Session, owner_id: UUID, obj_in: ScheduleCreate) -> Schedule:
        schedule_data = obj_in.model_dump(exclude={"slots"})
        db_schedule = self.model(**schedule_data, owner_id=owner_id)
        db.add(db_schedule)
        db.flush()

        for slot in obj_in.slots:
            db_slot = ScheduleSlot(**slot.model_dump(), schedule_id=db_schedule.id)
            db.add(db_slot)

        db.commit()
        db.refresh(db_schedule)
        return db_schedule

schedule_crud_interface = CRUDSchedule(Schedule)

