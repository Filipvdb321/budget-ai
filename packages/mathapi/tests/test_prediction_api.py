import pytest
from datetime import datetime, timedelta
import calendar
from app.prediction_api import (
    calculate_initial_balance,
    initialize_daily_projection,
    add_future_transactions_to_projection,
    calculate_running_balance,
    add_simulations_to_projection,
    process_need_categories,
    process_need_category,
    apply_need_category_spending
)

@pytest.fixture
def base_projection():
    """Fixture to create a base projection for testing."""
    today = datetime.now().date()
    days_ahead = 365
    end_date = today + timedelta(days=days_ahead)
    
    projection = {}
    current_date = today
    
    while current_date <= end_date:
        date_str = current_date.isoformat()
        projection[date_str] = {
            "date": date_str,
            "changes": [],
            "balance": 0
        }
        current_date += timedelta(days=1)
    
    return projection

# ... [bestaande tests behouden] ...

# Nieuwe tests voor extra branches
def test_current_month_with_target_month(base_projection):
    """Test current month handling when it matches the target month."""
    today = datetime.now().date()
    
    category = {
        "name": "Target This Month",
        "target": {
            "goal_type": "NEED",
            "goal_target": 100000,  # €100
            "goal_cadence": 1,
            "goal_cadence_frequency": 1,
            "goal_day": 15,
            "goal_target_month": today.replace(day=1).isoformat()  # Set target to current month
        }
    }
    
    apply_need_category_spending(
        base_projection,
        category,
        category["target"],
        0,  # current_balance
        100.0,  # target_amount
        30,  # days_ahead
        100.0  # global_overall_left
    )
    
    # Check if target amount was applied
    target_date = today.replace(day=15).isoformat()
    changes = [c for c in base_projection[target_date]["changes"] 
              if c["category"] == "Target This Month"]
    
    assert len(changes) == 1
    assert changes[0]["amount"] == -100.0
    assert changes[0]["reason"] == "Target Due This Month"

def test_current_month_with_global_left(base_projection):
    """Test current month handling with remaining global amount."""
    today = datetime.now().date()
    next_month = (today + timedelta(days=32)).replace(day=1)
    
    category = {
        "name": "Global Amount Category",
        "target": {
            "goal_type": "NEED",
            "goal_target": 100000,  # €100
            "goal_cadence": 1,
            "goal_cadence_frequency": 1,
            "goal_day": 15,
            "goal_target_month": next_month.isoformat()  # Set target to next month
        }
    }
    
    apply_need_category_spending(
        base_projection,
        category,
        category["target"],
        0,  # current_balance
        100.0,  # target_amount
        30,  # days_ahead
        75.0  # global_overall_left - different from target amount
    )
    
    # Check if global amount was applied
    target_date = today.replace(day=15).isoformat()
    changes = [c for c in base_projection[target_date]["changes"] 
              if c["category"] == "Global Amount Category"]
    
    assert len(changes) == 1
    assert changes[0]["amount"] == -75.0
    assert changes[0]["reason"] == "Remaining Target Amount"

def test_no_target_month_current_month(base_projection):
    """Test handling of current month when no target month is specified."""
    today = datetime.now().date()
    
    category = {
        "name": "No Target Month Category",
        "target": {
            "goal_type": "NEED",
            "goal_target": 100000,  # €100
            "goal_cadence": 1,
            "goal_cadence_frequency": 1,
            "goal_day": 15
        }
    }
    
    apply_need_category_spending(
        base_projection,
        category,
        category["target"],
        0,  # current_balance
        100.0,  # target_amount
        30,  # days_ahead
        100.0  # global_overall_left
    )
    
    # Check if target amount was applied
    target_date = today.replace(day=15).isoformat()
    changes = [c for c in base_projection[target_date]["changes"] 
              if c["category"] == "No Target Month Category"]
    
    assert len(changes) == 1
    assert changes[0]["amount"] == -100.0
    assert changes[0]["reason"] == "Remaining Target Amount"

def test_cadence_calculation_edge_cases(base_projection):
    """Test edge cases in cadence calculations."""
    base_date = datetime.now().date()
    
    # Test case where target month is December and next cadence is in next year
    december = base_date.replace(month=12, day=1)
    
    category = {
        "name": "Year End Category",
        "target": {
            "goal_type": "NEED",
            "goal_target": 100000,  # €100
            "goal_cadence": 3,  # Quarterly
            "goal_cadence_frequency": 1,
            "goal_target_month": december.isoformat(),
            "goal_day": 15
        }
    }
    
    apply_need_category_spending(
        base_projection,
        category,
        category["target"],
        0,  # current_balance
        100.0,  # target_amount
        365,  # days_ahead
        100.0  # global_overall_left
    )
    
    # Check December payment
    december_date = december.replace(day=15).isoformat()
    december_changes = [c for c in base_projection[december_date]["changes"] 
                       if c["category"] == "Year End Category"]
    assert len(december_changes) == 1
    assert december_changes[0]["amount"] == -100.0
    
    # Check March payment (next quarter)
    next_year_march = december.replace(year=december.year + 1, month=3, day=15)
    march_date = next_year_march.isoformat()
    
    if march_date in base_projection:
        march_changes = [c for c in base_projection[march_date]["changes"] 
                        if c["category"] == "Year End Category"]
        assert len(march_changes) == 1
        assert march_changes[0]["amount"] == -100.0
        assert march_changes[0]["reason"] == "Recurring Spending (Quarterly every 1)"

def test_invalid_goal_day(base_projection):
    """Test handling of invalid goal days (e.g., day 31 in a 30-day month)."""
    today = datetime.now().date()
    
    category = {
        "name": "Invalid Day Category",
        "target": {
            "goal_type": "NEED",
            "goal_target": 100000,  # €100
            "goal_cadence": 1,
            "goal_cadence_frequency": 1,
            "goal_day": 31  # This will be invalid for some months
        }
    }
    
    apply_need_category_spending(
        base_projection,
        category,
        category["target"],
        0,  # current_balance
        100.0,  # target_amount
        60,  # days_ahead
        100.0  # global_overall_left
    )
    
    # Find a month with 30 days in our projection
    current_date = today
    while current_date < today + timedelta(days=60):
        if calendar.monthrange(current_date.year, current_date.month)[1] == 30:
            test_month = current_date
            break
        current_date += timedelta(days=32)
        current_date = current_date.replace(day=1)
    
    if 'test_month' in locals():
        # For months with 30 days, the payment should be on the last day
        last_day = test_month.replace(day=30).isoformat()
        changes = [c for c in base_projection[last_day]["changes"] 
                  if c["category"] == "Invalid Day Category"]
        assert len(changes) == 1
        assert changes[0]["amount"] == -100.0