import pytest
from unittest.mock import MagicMock, patch
from app.services.analytics_service import get_monthly_summary, get_category_breakdown

def test_get_monthly_summary():
    mock_db = MagicMock()
    # Mock the query for income
    mock_db.query.return_value.filter.return_value.scalar.return_value = 1000.0
    # The same mock is used for expenses, so we need to be careful. 
    # Actually, the service calls it twice.
    # We can use side_effect to return different values.
    mock_db.query.return_value.filter.return_value.scalar.side_effect = [1000.0, 400.0]
    
    result = get_monthly_summary(mock_db, user_id=1)
    
    assert result["total_income"] == 1000.0
    assert result["total_expenses"] == 400.0
    assert result["net_savings"] == 600.0
    assert result["savings_rate"] == 60.0

def test_get_category_breakdown():
    mock_db = MagicMock()
    # Mock the query for category breakdown
    mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [
        MagicMock(category_id=1, total=200.0),
        MagicMock(category_id=2, total=150.0)
    ]
    
    result = get_category_breakdown(mock_db, user_id=1)
    
    assert len(result) == 2
    assert result[0]["category_id"] == 1
    assert result[0]["amount"] == 200.0
