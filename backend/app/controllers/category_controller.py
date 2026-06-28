from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.category import Category
from ..models.transaction import Transaction
from ..models.user import User
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from .auth_controller import get_current_user_email
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=list[CategoryResponse])
def list_categories(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db.query(Category).filter((Category.user_id == None) | (Category.user_id == user.id)).all()

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    new_category = Category(
        name=category_data.name,
        icon=category_data.icon,
        color=category_data.color,
        type=category_data.type,
        user_id=user.id
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, update_data: CategoryUpdate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this category")
    
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this category")
    if category.user_id is None:
        raise HTTPException(status_code=403, detail="System categories cannot be deleted")
        
    # Check for associated transactions
    has_transactions = db.query(Transaction).filter(Transaction.category_id == category_id).first() is not None
    if has_transactions:
        raise HTTPException(status_code=409, detail="Cannot delete category with associated transactions. Reassign transactions first.")
    
    db.delete(category)
    db.commit()
    return None
