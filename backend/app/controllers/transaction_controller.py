from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.transaction import Transaction, TransactionTag
from ..models.user import User
from ..models.tag import Tag
from ..schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from .auth_controller import get_current_user_email
from ..services.minio_service import upload_receipt, delete_receipt
from ..services.export_service import generate_transactions_csv
import logging
from datetime import datetime
from typing import Optional, List

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_receipt(file: UploadFile):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Only JPEG, PNG, WEBP are accepted.")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transaction = Transaction(
        amount=transaction_data.amount,
        date=transaction_data.date,
        category_id=transaction_data.category_id,
        transaction_type=transaction_data.transaction_type,
        payment_method=transaction_data.payment_method,
        description=transaction_data.description,
        merchant_name=transaction_data.merchant_name,
        receipt_url=transaction_data.receipt_url,
        notes=transaction_data.notes,
        goal_id=transaction_data.goal_id,
        user_id=user.id
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    from ..services.budget_service import check_budget_thresholds
    check_budget_thresholds(db, user.id, transaction.category_id, transaction.date)

    if transaction_data.tags:
        for tag_id in transaction_data.tags:
            tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user.id).first()
            if tag:
                assoc = TransactionTag(transaction_id=transaction.id, tag_id=tag.id)
                db.add(assoc)
        db.commit()

    return transaction

@router.get("/export")
def export_transactions_csv(email: str = Depends(get_current_user_email), db: Session = Depends(get_db),
                            start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    user = db.query(User).filter(User.email == email).first()
    query = db.query(Transaction).filter(Transaction.user_id == user.id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()
    csv_data = generate_transactions_csv(transactions)

    return StreamingResponse(
        iter([csv_data.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )

@router.get("/", response_model=list[TransactionResponse])
def list_transactions(email: str = Depends(get_current_user_email), db: Session = Depends(get_db),
                      start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                      category_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    user = db.query(User).filter(User.email == email).first()
    query = db.query(Transaction).filter(Transaction.user_id == user.id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    return query.offset(skip).limit(limit).all()

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, update_data: TransactionUpdate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        if key == "tags":
            db.query(TransactionTag).filter(TransactionTag.transaction_id == transaction.id).delete()
            for tag_id in value:
                tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user.id).first()
                if tag:
                    db.add(TransactionTag(transaction_id=transaction.id, tag_id=tag.id))
        else:
            setattr(transaction, key, value)

    from ..services.budget_service import check_budget_thresholds
    check_budget_thresholds(db, user.id, transaction.category_id, transaction.date)

    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.query(TransactionTag).filter(TransactionTag.transaction_id == transaction.id).delete()
    db.delete(transaction)
    db.commit()
    return None

@router.post("/{transaction_id}/receipt", response_model=TransactionResponse)
def upload_receipt_to_transaction(transaction_id: int, file: UploadFile = File(...), email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    validate_receipt(file)
    receipt_url = upload_receipt(file)

    transaction.receipt_url = receipt_url
    db.commit()
    db.refresh(transaction)

    return transaction

@router.delete("/{transaction_id}/receipt", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt_from_transaction(transaction_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not transaction.receipt_url:
        raise HTTPException(status_code=404, detail="No receipt found for this transaction")

    try:
        delete_receipt(transaction.receipt_url)
    except Exception as e:
        logger.error(f"Failed to delete receipt {transaction.receipt_url}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete receipt from storage")

    transaction.receipt_url = None
    db.commit()

    return None
