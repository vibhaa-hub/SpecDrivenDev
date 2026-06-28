import csv
import io
from sqlalchemy.orm import Session
from fastapi import UploadFile
from ..models.transaction import Transaction, TransactionType, PaymentMethod, TransactionTag
from ..models.category import Category
from ..models.user import User
from ..models.savings_goal import SavingsGoal
from ..models.tag import Tag
from datetime import datetime

def process_csv_import(db: Session, user: User, file: UploadFile):
    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(content))
    
    results = {"success": 0, "failed": 0, "warnings": []}
    
    for row_idx, row in enumerate(csv_reader, start=1):
        try:
            # Basic mapping from CSV columns to model fields
            # Expected columns: amount, date, category, payment_method, description, merchant, goal, tags, notes
            
            # 1. Resolve Category
            category = db.query(Category).filter(
                (Category.name == row["category"]) & 
                ((Category.user_id == user.id) | (Category.user_id == None))
            ).first()
            
            if not category:
                raise ValueError(f"Category '{row['category']}' not found")
            
            # 2. Resolve Goal
            goal_id = None
            if row.get("goal"):
                goal = db.query(SavingsGoal).filter(
                    SavingsGoal.name == row["goal"], 
                    SavingsGoal.user_id == user.id
                ).first()
                if goal:
                    goal_id = goal.id
                else:
                    results["warnings"].append(f"Row {row_idx}: Goal '{row['goal']}' not found, skipping association")

            # 3. Create Transaction
            transaction = Transaction(
                amount=float(row["amount"]),
                date=datetime.strptime(row["date"], "%Y-%m-%d"),
                category_id=category.id,
                transaction_type=TransactionType.EXPENSE, # Default to expense for bulk import or add a column
                payment_method=PaymentMethod[row["payment_method"].upper().replace(" ", "_")],
                description=row.get("description"),
                merchant_name=row.get("merchant"),
                notes=row.get("notes"),
                goal_id=goal_id,
                user_id=user.id
            )
            
            db.add(transaction)
            db.flush() # Get transaction ID
            
            # 4. Handle Tags
            if row.get("tags"):
                tag_names = [t.strip() for t in row["tags"].split(",")]
                for name in tag_names:
                    tag = db.query(Tag).filter(Tag.name == name, Tag.user_id == user.id).first()
                    if not tag:
                        tag = Tag(name=name, user_id=user.id)
                        db.add(tag)
                        db.flush()
                    
                    assoc = TransactionTag(transaction_id=transaction.id, tag_id=tag.id)
                    db.add(assoc)
            
            db.commit()
            results["success"] += 1
            
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["warnings"].append(f"Row {row_idx}: {str(e)}")
            
    return results
