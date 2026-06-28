from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class BudgetPeriod(enum.Enum):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    period = Column(Enum(BudgetPeriod), nullable=False)
    is_active = Column(Boolean, default=True)
    enable_rollover = Column(Boolean, default=False)
    rollover_amount = Column(Float, default=0.0)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True) # Null means overall budget
    
    user = relationship("User")
    category = relationship("Category")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
