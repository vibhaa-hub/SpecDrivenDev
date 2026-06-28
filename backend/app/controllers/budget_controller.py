from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.budget import Budget, BudgetPeriod
from ..models.user import User
from ..schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from .auth_controller import get_current_user_email
from ..services.budget_service import get_period_range
from ..models.transaction import Transaction, TransactionType
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(data: BudgetCreate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    # Check if a budget for this category and period already exists for the user
    existing = db.query(Budget).filter(
        Budget.user_id == user.id,
        Budget.category_id == data.category_id,
        Budget.period == data.period
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="A budget for this category and period already exists")
    
    budget = Budget(
        amount=data.amount,
        period=data.period,
        is_active=data.is_active,
        enable_rollover=data.enable_rollover,
        category_id=data.category_id,
        user_id=user.id
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

@router.get("/", response_model=List[dict])
def list_budgets(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    
    results = []
    now = datetime.utcnow()
    for b in budgets:
        start, end = get_period_range(b.period, now)
        spending = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.date >= start,
            Transaction.date <= end
        ).all()
        
        if b.category_id:
            spending = [t for t in spending if t.category_id == b.category_id]
            
        total_spent = sum(t.amount for t in spending)
        
        # Include rollover
        effective_limit = b.amount + b.rollover_amount
        
        budget_data = BudgetResponse.from_orm(b).dict()
        budget_data.update({
            "current_spending": total_spent,
            "effective_limit": effective_limit,
            "progress_percentage": (total_spent / effective_limit * 100) if effective_limit > 0 else 0
        })
        results.append(budget_data)
        
    return results

@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, data: BudgetUpdate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(budget, key, value)
    
    db.commit()
    db.refresh(budget)
    return budget

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    return None
