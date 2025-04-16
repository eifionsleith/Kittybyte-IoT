from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.base import BaseDatabaseModel
from src.models.user import User


ModelType = TypeVar("ModelType", bound=BaseDatabaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_one(self, db: Session, *args, **kwargs) -> Optional[ModelType]:
        return (
                db.query(self.model)
                .filter(*args)
                .filter_by(**kwargs)
                .first()
                )

    def get_many(self, db: Session, *args, skip: int=0, limit: int=100, **kwargs) -> List[ModelType]:
        return (
                db.query(self.model)
                .filter(*args)
                .filter_by(**kwargs)
                .offset(skip)
                .limit(limit)
                .all()
                )

    def get_by_id(self, db: Session, id: UUID) -> Optional[User]:
        return self.get_one(db, self.model.id == id)

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self,
               db: Session,
               db_obj: ModelType,
               obj_update: UpdateSchemaType
               ) -> ModelType:
        obj_update_data = obj_update.model_dump(exclude_unset=True)
        for field, value in obj_update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: UUID) -> Optional[ModelType]:
        obj = self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return obj
        return None

