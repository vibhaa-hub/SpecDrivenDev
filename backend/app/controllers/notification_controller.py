from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.notification import Notification
from ..models.user import User
from .auth_controller import get_current_user_email

router = APIRouter()

@router.get("/")
def list_notifications(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()

@router.patch("/{notification_id}/read")
def mark_as_read(notification_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    notification = db.query(Notification).filter(
        Notification.id == notification_id, 
        Notification.user_id == user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    return {"detail": "Notification marked as read"}

@router.patch("/read-all")
def mark_all_read(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    db.query(Notification).filter(
        Notification.user_id == user.id, 
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"detail": "All notifications marked as read"}
