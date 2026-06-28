from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.savings_goal import GoalStatus

class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: Optional[datetime] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class SavingsGoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    status: Optional[GoalStatus] = None

class SavingsGoalResponse(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    target_date: Optional[datetime]
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    status: GoalStatus
    
    # Calculated fields
    remaining_amount: float = 0.0
    progress_percentage: float = 0.0
    projected_completion_date: Optional[datetime] = None

    class Config:
        from_attributes = True
