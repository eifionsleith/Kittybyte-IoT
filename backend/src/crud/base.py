from typing import Generic, List, Optional, Type, TypeVar
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

    def get_many(self, db: Session, *args, skip: int = 0, limit: int = 100, **kwargs) -> List[ModelType]:
        return (
                db.query(self._model)
                .filter(*args)
                .filter_by(**kwargs)
                .offset(skip)
                .limit(limit)
                .all()
                )
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj  # Maybe refactor to raise exception on conflict?

    def update(self, db: Session, obj_to_update: ModelType, obj_update: UpdateSchemaType) -> ModelType:
        obj_update_data = obj_update.model_dump(exclude_unset=True)
        for field, value in obj_update_data.items():
            setattr(obj_to_update, field, value)

        db.add(obj_to_update)
        db.commit()
        db.refresh(obj_to_update)
        return obj_to_update  # Maybe refactor to raise exception on conflict?

    def delete(self, db: Session, db_obj: ModelType) -> ModelType:
        db.delete(db_obj)
        db.commit()
        return db_obj

