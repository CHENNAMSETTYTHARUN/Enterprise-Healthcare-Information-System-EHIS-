from typing import Generic, TypeVar, Type, Optional, List, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id, self.model.is_active == True).first()

    def get_all(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filters: Optional[dict] = None
    ) -> Tuple[List[ModelType], int]:
        query = db.query(self.model).filter(self.model.is_active == True)

        if filters:
            for field, val in filters.items():
                if val is not None and hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == val)

        if search and search_fields:
            search_conditions = []
            for field_name in search_fields:
                if hasattr(self.model, field_name):
                    column = getattr(self.model, field_name)
                    search_conditions.append(column.ilike(f"%{search}%"))
            if search_conditions:
                query = query.filter(or_(*search_conditions))

        total = query.count()

        if sort_by and hasattr(self.model, sort_by):
            sort_column = getattr(self.model, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
            if hasattr(self.model, "created_at"):
                query = query.order_by(self.model.created_at.desc())

        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total

    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> bool:
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db_obj.is_active = False
            db.commit()
            return True
        return False
