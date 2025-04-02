from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    def get_one(self, db: Session, *args, **kwargs) -> Optional[ModelType]:
        return (
                db.query(self._model)
                .filter(*args)
                .filter_by(**kwargs)
                .first()
                )

    def get_many(self, db: Session, *args, skip: int=0, limit: int=100, **kwargs) -> List[ModelType]:
        return (
                db.query(self._model)
                .filter(*args)
                .filter_by(**kwargs)
                .offset(skip)
                .limit(limit)
                .all()
                )

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_update: UpdateSchemaType) -> ModelType:
        obj_upate_data = obj_update.model_dump(exclude_unset=True)
        for field, value in obj_upate_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *args, **kwargs):
        db_obj = self.get_one(db, *args, **kwargs)
        if db_obj:
            db.delete(db_obj)
            return True
        else:
            return False
