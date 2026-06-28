from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.savings_goal import SavingsGoal, GoalStatus
from ..models.user import User
from ..models.transaction import Transaction
from ..schemas.savings_goal import SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse
from .auth_controller import get_current_user_email
import logging
from datetime import datetime, timedelta
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

def calculate_goal_metrics(goal: SavingsGoal, db: Session):
    remaining = goal.target_amount - goal.current_amount
    progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
    
    # Projected completion date:
    # Calculate average monthly contribution over the last 3 months
    three_months_ago = datetime.utcnow() - timedelta(days=90)
    contributions = db.query(Transaction).filter(
        Transaction.goal_id == goal.id,
        Transaction.date >= three_months_ago
    ).all()
    
    total_contrib = sum(t.amount for t in contributions)
    avg_monthly = total_contrib / 3
    
    projected_date = None
    if avg_monthly > 0 and remaining > 0:
        months_to_go = remaining / avg_monthly
        projected_date = datetime.utcnow() + timedelta(days=int(months_to_go * 30))
        
    return {
        "remaining_amount": max(0, remaining),
        "progress_percentage": min(100, progress),
        "projected_completion_date": projected_date
    }

@router.post("/", response_model=SavingsGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(data: SavingsGoalCreate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    goal = SavingsGoal(
        name=data.name,
        target_amount=data.target_amount,
        target_date=data.target_date,
        description=data.description,
        icon=data.icon,
        color=data.color,
        user_id=user.id
    )
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    metrics = calculate_goal_metrics(goal, db)
    # We a cheat here by adding attributes to the model instance so Pydantic picks them up
    goal.remaining_amount = metrics["remaining_amount"]
    goal.progress_percentage = metrics["progress_percentage"]
    goal.projected_completion_date = metrics["projected_completion_date"]
    
    return goal

@router.get("/", response_model=list[SavingsGoalResponse])
def list_goals(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user.id).all()
    
    responses = []
    for goal in goals:
        metrics = calculate_goal_metrics(goal, db)
        goal.remaining_amount = metrics["remaining_amount"]
        goal.progress_percentage = metrics["progress_percentage"]
        goal.projected_completion_date = metrics["projected_completion_date"]
        responses.append(goal)
        
    return responses

@router.get("/{goal_id}", response_model=SavingsGoalResponse)
def get_goal(goal_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    metrics = calculate_goal_metrics(goal, db)
    goal.remaining_amount = metrics["remaining_amount"]
    goal.progress_percentage = metrics["progress_percentage"]
    goal.projected_completion_date = metrics["projected_completion_date"]
    
    return goal

@router.patch("/{goal_id}", response_model=SavingsGoalResponse)
def update_goal(goal_id: int, data: SavingsGoalUpdate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(goal, key, value)
    
    db.commit()
    db.refresh(goal)
    
    metrics = calculate_goal_metrics(goal, db)
    goal.remaining_amount = metrics["remaining_amount"]
    goal.progress_percentage = metrics["progress_percentage"]
    goal.projected_completion_date = metrics["projected_completion_date"]
    
    return goal

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return None

@router.post("/{goal_id}/contribute", response_model=SavingsGoalResponse)
def contribute_to_goal(goal_id: int, amount: float, date: datetime, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Find the system-defined 'Savings' category
    from ..models.category import Category
    category = db.query(Category).filter(Category.name == "Savings", Category.user_id == None).first()
    if not category:
        # Fallback: create one if missing (though seed should have it)
        from ..models.category import CategoryType
        category = Category(name="Savings", type=CategoryType.EXPENSE, user_id=None)
        db.add(category)
        db.commit()
        db.refresh(category)
    
    # Create transaction
    from ..models.transaction import Transaction, TransactionType, PaymentMethod
    transaction = Transaction(
        amount=amount,
        date=date,
        category_id=category.id,
        transaction_type=TransactionType.EXPENSE,
        payment_method=PaymentMethod.CASH, # Default for direct contribution
        user_id=user.id,
        goal_id=goal.id
    )
    db.add(transaction)
    
    # Update goal total
    goal.current_amount += amount
    
    # Trigger completion
    if goal.current_amount >= goal.target_amount and goal.status != GoalStatus.COMPLETED:
        goal.status = GoalStatus.COMPLETED
        from ..models.notification import Notification
        notification = Notification(
            title="Goal Completed!",
            message=f"Congratulations! You've reached your target for {goal.name}.",
            user_id=user.id
        )
        db.add(notification)
    
    db.commit()
    db.refresh(goal)
    
    metrics = calculate_goal_metrics(goal, db)
    goal.remaining_amount = metrics["remaining_amount"]
    goal.progress_percentage = metrics["progress_percentage"]
    goal.projected_completion_date = metrics["projected_completion_date"]
    
    return goal
    

@router.post("/{goal_id}/associate/{transaction_id}")
def associate_transaction_to_goal(goal_id: int, transaction_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # If transaction is already linked to a different goal, deduct from that goal
    if transaction.goal_id and transaction.goal_id != goal.id:
        old_goal = db.query(SavingsGoal).filter(SavingsGoal.id == transaction.goal_id).first()
        if old_goal:
            old_goal.current_amount -= transaction.amount
    
    # Link to new goal and update its total
    if transaction.goal_id != goal.id:
        transaction.goal_id = goal.id
        goal.current_amount += transaction.amount
        
        # Trigger completion
        if goal.current_amount >= goal.target_amount and goal.status != GoalStatus.COMPLETED:
            goal.status = GoalStatus.COMPLETED
            from ..models.notification import Notification
            notification = Notification(
                title="Goal Completed!",
                message=f"Congratulations! You've reached your target for {goal.name}.",
                user_id=user.id
            )
            db.add(notification)
            
    db.commit()

    db.refresh(goal)
    
    metrics = calculate_goal_metrics(goal, db)
    goal.remaining_amount = metrics["remaining_amount"]
    goal.progress_percentage = metrics["progress_percentage"]
    goal.projected_completion_date = metrics["projected_completion_date"]
    
    return goal

