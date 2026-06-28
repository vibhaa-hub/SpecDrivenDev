from pydantic import BaseModel
from typing import Optional

class TagCreate(BaseModel):
    name: str

class TagUpdate(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        from_attributes = True
