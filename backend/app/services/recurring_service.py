from ..celery_app import celery_app
from ..database import SessionLocal
from ..models.transaction import Transaction, TransactionType, PaymentMethod
from ..models.recurring_template import RecurringTemplate, RecurrencePattern
from ..models.user import User
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.generate_recurring_transactions")
def generate_recurring_transactions():
    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        # Find templates that need to run today
        templates = db.query(RecurringTemplate).filter(
            RecurringTemplate.next_occurrence_date <= datetime.utcnow()
        ).all()
        
        for template in templates:
            # Create the transaction
            transaction = Transaction(
                amount=template.amount,
                date=datetime.utcnow(),
                category_id=template.category_id,
                transaction_type=template.transaction_type,
                payment_method=template.payment_method,
                description=template.description,
                merchant_name=template.merchant_name,
                notes=template.notes,
                goal_id=template.goal_id,
                user_id=template.user_id
            )
            db.add(transaction)
            
            # Calculate next date
            next_date = template.next_occurrence_date
            if template.recurrence_pattern == RecurrencePattern.DAILY:
                next_date += timedelta(days=1)
            elif template.recurrence_pattern == RecurrencePattern.WEEKLY:
                next_date += timedelta(weeks=1)
            elif template.recurrence_pattern == RecurrencePattern.MONTHLY:
                # Simplified monthly: add 30 days or use dateutil.relativedelta
                next_date += timedelta(days=30)
            elif template.recurrence_pattern == RecurrencePattern.YEARLY:
                next_date += timedelta(days=365)
            
            template.next_occurrence_date = next_date
            template.current_occurrences += 1
            
            # Check if we should stop
            if template.end_date and next_date > template.end_date:
                # In a real app, you'd mark the template as 'Expired'
                db.delete(template) 
            elif template.max_occurrences and template.current_occurrences >= template.max_occurrences:
                db.delete(template)
                
            db.commit()
            logger.info(f"Generated recurring transaction for template {template.id}")
            
    except Exception as e:
        logger.error(f"Error generating recurring transactions: {e}")
        db.rollback()
    finally:
        db.close()
