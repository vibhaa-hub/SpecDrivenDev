from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.budget import BudgetPeriod

class BudgetBase(BaseModel):
    amount: float = Field(..., gt=0)
    period: BudgetPeriod
    is_active: bool = True
    enable_rollover: bool = False
    category_id: Optional[int] = None # Null means overall budget

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[BudgetPeriod] = None
    is_active: Optional[bool] = None
    enable_rollover: Optional[bool] = None
    category_id: Optional[int] = None

class BudgetResponse(BudgetBase):
    id: int
    rollover_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
