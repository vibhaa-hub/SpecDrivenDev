from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class GoalStatus(enum.Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ABANDONED = "Abandoned"
    PAUSED = "Paused"

class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime)
    description = Column(String)
    icon = Column(String)
    color = Column(String)
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    transactions = relationship("Transaction", back_populates="goal")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
