from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from ..models.transaction import PaymentMethod, TransactionType

class TransactionCreate(BaseModel):
    amount: float
    date: datetime
    category_id: int
    transaction_type: TransactionType
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    goal_id: Optional[int] = None
    tags: List[int] = []

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[datetime] = None
    category_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    goal_id: Optional[int] = None
    tags: Optional[List[int]] = None

class TransactionResponse(BaseModel):
    id: int
    amount: float
    date: datetime
    category_id: int
    transaction_type: TransactionType
    payment_method: Optional[PaymentMethod]
    description: Optional[str]
    merchant_name: Optional[str]
    receipt_url: Optional[str]
    notes: Optional[str]
    goal_id: Optional[int]
    
    class Config:
        from_attributes = True
