import pytest
from unittest.mock import MagicMock, patch
from app.services.recurring_service import generate_recurring_transactions
from app.models.recurring_template import RecurringTemplate, RecurrencePattern
from app.models.transaction import Transaction
from datetime import datetime

def test_generate_recurring_transactions():
    mock_db = MagicMock()
    template = RecurringTemplate(
        id=1,
        amount=50.0,
        recurrence_pattern=RecurrencePattern.DAILY,
        next_occurrence_date=datetime.utcnow().date(),
        user_id=1,
        category_id=10
    )

    def query_side_effect(model):
        q = MagicMock()
        q.filter.return_value.all.return_value = [template]
        return q

    mock_db.query.side_effect = query_side_effect

    with patch('app.services.recurring_service.SessionLocal', return_value=mock_db):
        generate_recurring_transactions()

    args, kwargs = mock_db.add.call_args
    assert args[0].amount == 50.0
    assert args[0].user_id == 1
    assert template.next_occurrence_date > datetime.utcnow().date()
