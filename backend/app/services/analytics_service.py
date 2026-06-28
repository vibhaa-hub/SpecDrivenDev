from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..models.transaction import Transaction, TransactionType
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_monthly_summary(db: Session, user_id: int):
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == TransactionType.INCOME,
        Transaction.date >= start_of_month
    ).scalar() or 0.0
    
    expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.date >= start_of_month
    ).scalar() or 0.0
    
    net_savings = income - expenses
    savings_rate = (net_savings / income * 100) if income > 0 else 0.0
    
    return {
        "total_income": income,
        "total_expenses": expenses,
        "net_savings": net_savings,
        "savings_rate": savings_rate
    }

def get_category_breakdown(db: Session, user_id: int):
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    results = db.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.date >= start_of_month
    ).group_by(Transaction.category_id).all()
    
    # Convert to a more useful format for donut charts
    breakdown = []
    for row in results:
        breakdown.append({"category_id": row.category_id, "amount": row.total})
        
    return breakdown

def get_spending_trends(db: Session, user_id: int):
    now = datetime.utcnow()
    twelve_months_ago = now - relativedelta(months=12)
    
    # This is a simplified trend: total per month
    # In a real app, we'd ensure every month is present even if 0
    results = db.query(
        func.date_trunc('month', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.date >= twelve_months_ago
    ).group_by('month').order_by('month').all()
    
    return [{"month": row.month, "amount": row.total} for row in results]

def get_top_categories(db: Session, user_id: int, limit=5):
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    results = db.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.date >= start_of_month
    ).group_by(Transaction.category_id).order_by(desc("total")).limit(limit).all()
    
    return [{"category_id": row.category_id, "amount": row.total} for row in results]
