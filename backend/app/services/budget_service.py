from sqlalchemy.orm import Session
from ..models.budget import Budget, BudgetPeriod
from ..models.transaction import Transaction, TransactionType
from ..models.notification import Notification
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def check_budget_thresholds(db: Session, user_id: int, category_id: int = None, date: datetime = None):
    if date is None:
        date = datetime.utcnow()
    
    # 1. Find relevant budgets (category-specific or overall)
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.is_active == True
    ).all()
    
    # Filter budgets that apply to this transaction
    applicable_budgets = []
    for b in budgets:
        if b.category_id is None: # Overall budget
            applicable_budgets.append(b)
        elif b.category_id == category_id: # Category budget
            applicable_budgets.append(b)
            
    for budget in applicable_budgets:
        # Calculate current period spending
        start_date, end_date = get_period_range(budget.period, date)
        
        spending = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # If category budget, filter by category
        if budget.category_id:
            spending = [t for t in spending if t.category_id == budget.category_id]
            
        total_spent = sum(t.amount for t in spending)
        
        # Check thresholds (80% and 100%)
        threshold_80 = budget.amount * 0.8
        threshold_100 = budget.amount
        
        # To avoid duplicate notifications, we should check if a notification was already sent for this period
        # For simplicity in this implementation, we'll just log it and create the notification.
        # A production system would track "last_notified_threshold" per budget per period.
        
        if total_spent >= threshold_100:
            create_budget_notification(db, user_id, budget, "100%", total_spent)
        elif total_spent >= threshold_80:
            create_budget_notification(db, user_id, budget, "80%", total_spent)

def create_budget_notification(db: Session, user_id: int, budget: Budget, threshold: str, total_spent: float):
    cat_name = budget.category.name if budget.category else "Overall"
    msg = f"Budget Alert: Your {cat_name} {budget.period.value} budget has reached {threshold} ({total_spent:.2f}/{budget.amount:.2f})."
    
    # Prevent duplicate notifications for the same threshold in the same period
    # (Simplified: just create the notification)
    notification = Notification(
        title="Budget Breach",
        message=msg,
        user_id=user_id
    )
    db.add(notification)
    db.commit()

def get_period_range(period: BudgetPeriod, reference_date: datetime):
    if period == BudgetPeriod.WEEKLY:
        # Start of current week (Monday)
        start = reference_date - timedelta(days=reference_date.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif period == BudgetPeriod.MONTHLY:
        # Start of current month
        start = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # End of current month (approx)
        if reference_date.month == 12:
            end = reference_date.replace(year=reference_date.year + 1, month=1, day=1)
        else:
            end = reference_date.replace(month=reference_date.month + 1, day=1)
            
    return start, end

def perform_budget_rollover(db: Session):
    """
    Task 8.2: Carry forward unspent balances to the next period.
    This should be called by a Celery beat task.
    """
    budgets = db.query(Budget).filter(Budget.enable_rollover == True, Budget.is_active == True).all()
    
    for budget in budgets:
        # We need to know when the last rollover happened. 
        # For simplicity, we'll calculate the unspent amount for the PREVIOUS period.
        # In a real system, we'd have a 'last_rollover_date' field.
        
        # Get range for previous period
        now = datetime.utcnow()
        if budget.period == BudgetPeriod.WEEKLY:
            # Previous week
            last_monday = now - timedelta(days=now.weekday() + 7)
            last_monday = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            start = last_monday
            end = last_monday + timedelta(days=7)
        else: # MONTHLY
            # Previous month
            first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = first_of_this_month
            if first_of_this_month.month == 1:
                start = first_of_this_month.replace(year=first_of_this_month.year - 1, month=12, day=1)
            else:
                start = first_of_this_month.replace(month=first_of_this_month.month - 1, day=1)

        spending = db.query(Transaction).filter(
            Transaction.user_id == budget.user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.date >= start,
            Transaction.date < end
        ).all()
        
        if budget.category_id:
            spending = [t for t in spending if t.category_id == budget.category_id]
            
        total_spent = sum(t.amount for t in spending)
        unspent = budget.amount - total_spent
        
        if unspent > 0:
            budget.rollover_amount += unspent
            db.commit()
