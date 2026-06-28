from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class CategoryType(enum.Enum):
    EXPENSE = "Expense"
    INCOME = "Income"
    BOTH = "Both"

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon = Column(String)
    color = Column(String)
    type = Column(Enum(CategoryType), default=CategoryType.BOTH)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Null for system defaults
    
    user = relationship("User")
