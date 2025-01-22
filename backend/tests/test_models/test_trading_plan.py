import pytest
from app.models import User, TradingPlan
from app import db


@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(email='trader@example.com', username='trader')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Get fresh instance using Session.get()
        return db.session.get(User, user.id)


def test_create_trading_plan(app, test_user):
    """Test trading plan creation"""
    with app.app_context():
        # Refresh user from database
        user = db.session.merge(test_user)

        plan = TradingPlan(user_id=user.id,
                           name="Daily Forex Strategy",
                           type="day_trading",
                           risk_management={
                               "max_risk_per_trade": 0.02,
                               "max_daily_risk": 0.06
                           },
                           entry_rules={
                               "min_rr_ratio": 2,
                               "setup_types": ["pin bar",
                                               "engulfing"]
                           },
                           timeframes=["H1",
                                       "H4"],
                           markets=["EUR/USD",
                                    "GBP/USD"],
                           notes="My primary forex strategy")

        db.session.add(plan)
        db.session.commit()

        # Refresh plan from database using Session.get()
        plan = db.session.get(TradingPlan, plan.id)

        assert plan.id is not None
        assert plan.user_id == user.id
        assert plan.name == "Daily Forex Strategy"
        assert plan.type == "day_trading"
        assert plan.risk_management["max_risk_per_trade"] == 0.02
        assert "pin bar" in plan.entry_rules["setup_types"]
        assert plan.is_active is True
        assert plan.version == 1


def test_trading_plan_user_relationship(app, test_user):
    """Test relationship between trading plan and user"""
    with app.app_context():
        # Refresh user from database
        user = db.session.merge(test_user)

        plan = TradingPlan(user_id=user.id,
                           name="Swing Trading Strategy",
                           type="swing_trading")

        db.session.add(plan)
        db.session.commit()

        # Refresh from database using Session.get()
        plan = db.session.get(TradingPlan, plan.id)
        user = db.session.get(User, user.id)

        # Test relationship from plan to user
        assert plan.user == user

        # Test relationship from user to plans
        assert plan in user.trading_plans
        assert len(user.trading_plans) == 1


def test_trading_plan_json_fields(app, test_user):
    """Test JSON fields in trading plan"""
    with app.app_context():
        # Refresh user from database
        user = db.session.merge(test_user)

        complex_rules = {
            "entry": {
                "indicators": {
                    "rsi": {
                        "timeframe": 14,
                        "overbought": 70,
                        "oversold": 30
                    },
                    "moving_averages": ["EMA20",
                                        "SMA50"]
                },
                "conditions": ["price_action",
                               "trend_following"]
            }
        }

        plan = TradingPlan(user_id=user.id,
                           name="Complex Strategy",
                           type="systematic",
                           entry_rules=complex_rules)

        db.session.add(plan)
        db.session.commit()

        # Refresh from database using Session.get()
        plan = db.session.get(TradingPlan, plan.id)

        # Test nested JSON structure
        assert plan.entry_rules["entry"]["indicators"]["rsi"][
            "timeframe"] == 14
        assert "EMA20" in plan.entry_rules["entry"]["indicators"][
            "moving_averages"]


def test_trading_plan_version_control(app, test_user):
    """Test trading plan versioning"""
    with app.app_context():
        # Refresh user from database
        user = db.session.merge(test_user)

        plan = TradingPlan(user_id=user.id,
                           name="Evolving Strategy",
                           type="day_trading",
                           version=1)

        db.session.add(plan)
        db.session.commit()

        # Refresh plan from database using Session.get()
        plan = db.session.get(TradingPlan, plan.id)

        # Update plan
        plan.version += 1
        plan.name = "Evolving Strategy V2"
        db.session.commit()

        # Refresh again using Session.get()
        plan = db.session.get(TradingPlan, plan.id)
        assert plan.version == 2
        assert plan.name == "Evolving Strategy V2"


def test_trading_plan_validation(app, test_user):
    """Test trading plan validation"""
    with app.app_context():
        # Test required fields
        with pytest.raises(Exception):
            plan = TradingPlan(
                user_id=test_user.id)  # Missing required name and type
            db.session.add(plan)
            db.session.commit()


def test_trading_plan_cascading_delete(app, test_user):
    """Test cascade delete behavior"""
    with app.app_context():
        # Refresh user from database
        user = db.session.merge(test_user)

        plan = TradingPlan(user_id=user.id, name="Test Strategy", type="test")
        db.session.add(plan)
        db.session.commit()

        plan_id = plan.id

        # Delete user should cascade to plan
        db.session.delete(user)
        db.session.commit()

        # Verify plan is deleted using Session.get()
        assert db.session.get(TradingPlan, plan_id) is None
