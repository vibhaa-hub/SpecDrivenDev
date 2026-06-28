from celery import shared_task
from ..database import SessionLocal
from ..models.user import User
from ..models.notification import Notification
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_weekly_digest():
    db = SessionLocal()
    try:
        # Find users who opted in (we assume a 'opt_in_digest' field on User, though not explicitly in model)
        # For now, we'll send to all users for demo purposes
        users = db.query(User).all()
        
        last_week = datetime.utcnow() - timedelta(days=7)
        
        for user in users:
            # logic to calculate summary for the last week
            # ... (similar to analytics_service)
            
            # Create an in-app notification as a placeholder for the email
            notification = Notification(
                title="Your Weekly Digest is Ready!",
                message="Check your email for your weekly financial summary.",
                user_id=user.id
            )
            db.add(notification)
        
        db.commit()
        logger.info("Weekly digest task completed successfully.")
    except Exception as e:
        logger.error(f"Error in send_weekly_digest: {e}")
    finally:
        db.close()
