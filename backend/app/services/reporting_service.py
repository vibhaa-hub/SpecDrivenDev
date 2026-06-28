from sqlalchemy.orm import Session
from ..models.transaction import Transaction, TransactionType
from ..models.notification import Notification
from ..models.user import User
from datetime import datetime, timedelta
import csv
import io
import zipfile
from fastapi.responses import StreamingResponse

def generate_csv_report(user_id: int, start_date: datetime, end_date: datetime):
    # Fetch transactions
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Amount", "Type", "Category", "Merchant", "Description"])
    
    for tx in transactions:
        writer.writerow([tx.date, tx.amount, tx.transaction_type, tx.category_id, tx.merchant_name, tx.description])
        
    return output.getvalue()

# In a real implementation, PDF generation would use a library like ReportLab or WeasyPrint.
# For this implementation, we focus on the service structure.
def generate_pdf_report(user_id: int, start_date: datetime, end_date: datetime):
    # Placeholder for PDF logic
    return f"PDF Report for user {user_id} from {start_date} to {end_date}".encode('utf-8')
