import csv
import io
from typing import List
from ..models.transaction import Transaction

def generate_transactions_csv(transactions: List[Transaction]) -> io.StringIO:
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["ID", "Date", "Amount", "Type", "Category", "Payment Method", "Merchant", "Description", "Goal", "Notes"])
    
    for t in transactions:
        writer.writerow([
            t.id,
            t.date.strftime("%Y-%m-%d") if t.date else "",
            t.amount,
            t.transaction_type.value if t.transaction_type else "",
            t.category.name if t.category else "",
            t.payment_method.value if t.payment_method else "",
            t.merchant_name or "",
            t.description or "",
            t.goal.name if t.goal else "",
            t.notes or ""
        ])
    
    output.seek(0)
    return output
