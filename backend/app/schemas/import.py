from pydantic import BaseModel
from typing import Optional

class CSVImportRow(BaseModel):
    amount: float
    date: str
    category: str
    description: Optional[str] = None
    payment_method: str
    merchant: Optional[str] = None
    goal: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
