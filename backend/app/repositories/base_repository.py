from sqlalchemy.orm import Session
from typing import TypeVar, Type, List, Optional
from .database import Base

T = TypeVar("T", bound=Base)

class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, model: Type[T], id: int) -> Optional[T]:
        return self.db.query(model).filter(model.id == id).first()

    def get_all(self, model: Type[T], skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(model).offset(skip).limit(limit).all()

    def create(self, model: T) -> T:
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def update(self, model: T) -> T:
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete(self, model: T) -> None:
        self.db.delete(model)
        self.db.commit()
