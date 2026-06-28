from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class PaymentMethod(enum.Enum):
    CASH = "Cash"
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    UPI = "UPI"
    NET_BANKING = "Net Banking"
    OTHER = "Other"

class TransactionType(enum.Enum):
    EXPENSE = "Expense"
    INCOME = "Income"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    payment_method = Column(Enum(PaymentMethod))
    merchant_name = Column(String)
    receipt_url = Column(String)
    notes = Column(String)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("savings_goals.id"), nullable=True)
    
    user = relationship("User")
    category = relationship("Category")
    goal = relationship("SavingsGoal", back_populates="transactions")
    tags = relationship("Tag", secondary="transaction_tags")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class TransactionTag(Base):
    __tablename__ = "transaction_tags"
    transaction_id = Column(Integer, ForeignKey("transactions.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
