from typing import Generic, List, Optional, TypeVar, Type
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
OwnerIdType = int

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
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

    def get_many_with_owner(self, db: Session, owner_id: OwnerIdType, skip: int=0, limit: int=100) -> List[ModelType]:
        return self.get_many(db, skip=skip, limit=limit, owner_id=owner_id)

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_update: UpdateSchemaType) -> ModelType:
        """
        Updates a record in the database.
        """
        obj_update_data = obj_update.model_dump(exclude_unset=True)
        for field, value in obj_update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

