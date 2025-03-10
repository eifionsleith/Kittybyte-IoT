
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session


class CRUDInterface:
    """
    Base Interface for CRUD Operations.
    """
    def __init__(self, model) -> None:
        self._model = model

    def get_one(self, db: Session, *args, **kwargs) -> Optional[BaseModel]:
        """
        Gets the first instance matching given arguments from the given database session.

        *args: filters
        **kwargs: filter-by
        """
        return db.query(self._model) \
                .filter(*args) \
                .filter_by(**kwargs) \
                .first()

    def create(self, db: Session, obj_to_create: BaseModel) -> BaseModel:
        """
        Creates an the given object using the database session.
        """
        obj_to_create_dict = obj_to_create.model_dump(exclude_none=True, exclude_unset=True)
        db_obj = self._model(**obj_to_create_dict)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

