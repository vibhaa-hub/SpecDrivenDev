from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base
from .transaction import PaymentMethod, TransactionType

class RecurrencePattern(enum.Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class RecurringTemplate(Base):
    __tablename__ = "recurring_templates"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    payment_method = Column(Enum(PaymentMethod))
    merchant_name = Column(String)
    notes = Column(String)
    
    recurrence_pattern = Column(Enum(RecurrencePattern), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    max_occurrences = Column(Integer)
    current_occurrences = Column(Integer, default=0)
    next_occurrence_date = Column(DateTime, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("savings_goals.id"), nullable=True)
    
    user = relationship("User")
    category = relationship("Category")
    goal = relationship("SavingsGoal")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
