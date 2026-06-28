from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.analytics_service import get_monthly_summary, get_category_breakdown, get_spending_trends, get_top_categories
from .auth_controller import get_current_user_email
from ..models.user import User

router = APIRouter()

@router.get("/summary")
def get_summary(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return get_monthly_summary(db, user.id)

@router.get("/breakdown")
def get_breakdown(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return get_category_breakdown(db, user.id)

@router.get("/trends")
def get_trends(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return get_spending_trends(db, user.id)

@router.get("/top-categories")
def get_top_categories(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return get_top_categories(db, user.id)
