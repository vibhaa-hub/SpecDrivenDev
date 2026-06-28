import pytest
from unittest.mock import MagicMock
from app.services.budget_service import check_budget_thresholds, perform_budget_rollover
from app.models.budget import Budget, BudgetPeriod
from app.models.transaction import Transaction, TransactionType
from datetime import datetime, timedelta

def test_check_budget_thresholds_triggers_notification():
    mock_db = MagicMock()
    user_id = 1
    category_id = 10
    date = datetime.utcnow()

    mock_budget = Budget(
        id=1,
        amount=100.0,
        period=BudgetPeriod.MONTHLY,
        user_id=user_id,
        category_id=category_id,
        is_active=True
    )
    # 90% spent — should trigger the 80% threshold notification
    mock_txs = [Transaction(amount=90.0, category_id=category_id)]

    def query_side_effect(model):
        q = MagicMock()
        if model is Budget:
            q.filter.return_value.all.return_value = [mock_budget]
        else:
            q.filter.return_value.all.return_value = mock_txs
        return q

    mock_db.query.side_effect = query_side_effect

    check_budget_thresholds(mock_db, user_id, category_id, date)

    args, kwargs = mock_db.add.call_args
    assert args[0].__class__.__name__ == "Notification"
    assert "80%" in args[0].message

def test_perform_budget_rollover():
    mock_db = MagicMock()
    mock_budget = Budget(
        id=1,
        amount=100.0,
        rollover_amount=0.0,
        enable_rollover=True,
        is_active=True,
        period=BudgetPeriod.MONTHLY,
        user_id=1
    )
    # 70 spent in previous period → 30 unspent should roll over
    mock_txs = [Transaction(amount=70.0)]

    def query_side_effect(model):
        q = MagicMock()
        if model is Budget:
            q.filter.return_value.all.return_value = [mock_budget]
        else:
            q.filter.return_value.all.return_value = mock_txs
        return q

    mock_db.query.side_effect = query_side_effect

    perform_budget_rollover(mock_db)

    assert mock_budget.rollover_amount == 30.0
