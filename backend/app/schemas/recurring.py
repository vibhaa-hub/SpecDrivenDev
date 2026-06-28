from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.recurring_template import RecurrencePattern, TransactionType, PaymentMethod

class RecurringCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    transaction_type: TransactionType
    payment_method: Optional[PaymentMethod] = None
    merchant_name: Optional[str] = None
    notes: Optional[str] = None
    recurrence_pattern: RecurrencePattern
    start_date: datetime
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None
    category_id: int
    goal_id: Optional[int] = None

class RecurringUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None

class RecurringResponse(BaseModel):
    id: int
    amount: float
    recurrence_pattern: RecurrencePattern
    next_occurrence_date: datetime
    
    class Config:
        from_attributes = True
