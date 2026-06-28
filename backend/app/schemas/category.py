from pydantic import BaseModel
from ..models.category import CategoryType
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    type: CategoryType

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    type: Optional[CategoryType] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    color: Optional[str]
    type: CategoryType
    user_id: Optional[int]

    class Config:
        from_attributes = True
