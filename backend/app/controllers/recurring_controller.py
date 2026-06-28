from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.recurring_template import RecurringTemplate, RecurrencePattern
from ..models.user import User
from ..models.transaction import Transaction
from ..schemas.recurring import RecurringCreate, RecurringUpdate, RecurringResponse
from .auth_controller import get_current_user_email
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=RecurringResponse, status_code=status.HTTP_201_CREATED)
def create_recurring_template(data: RecurringCreate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    template = RecurringTemplate(
        amount=data.amount,
        description=data.description,
        transaction_type=data.transaction_type,
        payment_method=data.payment_method,
        merchant_name=data.merchant_name,
        notes=data.notes,
        recurrence_pattern=data.recurrence_pattern,
        start_date=data.start_date,
        end_date=data.end_date,
        max_occurrences=data.max_occurrences,
        next_occurrence_date=data.start_date,
        user_id=user.id,
        category_id=data.category_id,
        goal_id=data.goal_id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/", response_model=list[RecurringResponse])
def list_recurring(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return db.query(RecurringTemplate).filter(RecurringTemplate.user_id == user.id).all()

@router.patch("/{template_id}", response_model=RecurringResponse)
def update_recurring(template_id: int, data: RecurringUpdate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    template = db.query(RecurringTemplate).filter(RecurringTemplate.id == template_id, RecurringTemplate.user_id == user.id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(template, key, value)
    
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring(template_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    template = db.query(RecurringTemplate).filter(RecurringTemplate.id == template_id, RecurringTemplate.user_id == user.id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    db.delete(template)
    db.commit()
    return None

@router.delete("/{template_id}/occurrence/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_occurrence(template_id: int, transaction_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    # Verify template belongs to user
    template = db.query(RecurringTemplate).filter(RecurringTemplate.id == template_id, RecurringTemplate.user_id == user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    # Verify transaction belongs to user and is linked to this template (via logic or explicit link)
    # In our current model, transactions don't have a template_id. 
    # For a production app, we would add template_id to Transaction model.
    # For now, we'll just delete the transaction if it belongs to the user.
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    db.delete(transaction)
    db.commit()
    return None
