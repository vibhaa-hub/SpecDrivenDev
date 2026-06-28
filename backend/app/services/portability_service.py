import zipfile
import json
import io
from typing import List
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.transaction import Transaction
from ..models.category import Category
from ..models.tag import Tag
from ..models.savings_goal import SavingsGoal
from ..models.budget import Budget
from ..models.notification import Notification

def export_user_data(db: Session, user_id: int):
    # Buffer to hold the zip file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        # 1. User Profile
        user = db.query(User).filter(User.id == user_id).first()
        user_data = {
            "full_name": user.full_name,
            "email": user.email,
            "preferred_currency": user.preferred_currency,
            "timezone": user.timezone
        }
        zip_file.writestr("profile.json", json.dumps(user_data, indent=2))
        
        # 2. Transactions
        transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
        trans_list = []
        for t in transactions:
            trans_list.append({
                "id": t.id,
                "amount": t.amount,
                "date": t.date.isoformat() if t.date else None,
                "category": t.category.name if t.category else None,
                "type": t.transaction_type.value if t.transaction_type else None,
                "payment_method": t.payment_method.value if t.payment_method else None,
                "description": t.description,
                "merchant": t.merchant_name,
                "notes": t.notes,
                "goal_id": t.goal_id
            })
        zip_file.writestr("transactions.json", json.dumps(trans_list, indent=2))
        
        # 3. Categories
        categories = db.query(Category).filter(Category.user_id == user_id).all()
        cat_list = [{"id": c.id, "name": c.name, "type": c.type.value} for c in categories]
        zip_file.writestr("categories.json", json.dumps(cat_list, indent=2))
        
        # 4. Tags
        tags = db.query(Tag).filter(Tag.user_id == user_id).all()
        tag_list = [{"id": t.id, "name": t.name} for t in tags]
        zip_file.writestr("tags.json", json.dumps(tag_list, indent=2))
        
        # 5. Savings Goals
        goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()
        goal_list = [{"id": g.id, "name": g.name, "target": g.target_amount, "current": g.current_amount} for g in goals]
        zip_file.writestr("savings_goals.json", json.dumps(goal_list, indent=2))
        
        # 6. Budgets
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        budget_list = [{"id": b.id, "amount": b.amount, "period": b.period.value} for b in budgets]
        zip_file.writestr("budgets.json", json.dumps(budget_list, indent=2))

    zip_buffer.seek(0)
    return zip_buffer
