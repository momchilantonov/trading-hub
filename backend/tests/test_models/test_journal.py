import pytest
from datetime import datetime
from decimal import Decimal
from app.models import User, TradingPlan, Trade, Journal
from app import db


@pytest.fixture
def test_user(app):
    """Create test user"""
    with app.app_context():
        user = User(email='trader@example.com', username='trader')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return db.session.get(User, user.id)


@pytest.fixture
def test_plan(app, test_user):
    """Create test trading plan"""
    with app.app_context():
        user = db.session.merge(test_user)
        plan = TradingPlan(user_id=user.id,
                           name="Test Plan",
                           type="day_trading")
        db.session.add(plan)
        db.session.commit()
        return db.session.get(TradingPlan, plan.id)


@pytest.fixture
def test_trade(app, test_plan):
    """Create test trade"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        trade = Trade(trading_plan_id=plan.id,
                      entry_price=Decimal('100.00'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('1.0'))
        db.session.add(trade)
        db.session.commit()
        return db.session.get(Trade, trade.id)


def test_create_journal_entry(app, test_plan, test_trade):
    """Test basic journal entry creation"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        trade = db.session.merge(test_trade)

        journal = Journal(trade_id=trade.id,
                          trading_plan_id=plan.id,
                          notes="Strong trend continuation setup",
                          emotions="Confident",
                          market_conditions={
                              "trend": "bullish",
                              "volatility": "medium",
                              "key_levels": ["1.1200",
                                             "1.1250"]
                          },
                          plan_adherence={
                              "followed_rules": True,
                              "position_sizing_correct": True,
                              "proper_entry": True,
                              "proper_exit": True,
                              "areas_for_improvement": []
                          })

        db.session.add(journal)
        db.session.commit()

        # Refresh from database
        journal = db.session.get(Journal, journal.id)

        assert journal.id is not None
        assert journal.trade_id == trade.id
        assert journal.trading_plan_id == plan.id
        assert journal.notes == "Strong trend continuation setup"
        assert journal.emotions == "Confident"
        assert journal.market_conditions["trend"] == "bullish"
        assert journal.plan_adherence["followed_rules"] is True


def test_journal_relationships(app, test_plan, test_trade):
    """Test journal relationships with trade and plan"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        trade = db.session.merge(test_trade)

        journal = Journal(trade_id=trade.id,
                          trading_plan_id=plan.id,
                          notes="Test entry")

        db.session.add(journal)
        db.session.commit()

        # Refresh from database
        journal = db.session.get(Journal, journal.id)
        trade = db.session.get(Trade, trade.id)
        plan = db.session.get(TradingPlan, plan.id)

        # Test relationships
        assert journal.trade == trade
        assert journal.trading_plan == plan
        assert trade.journal_entry == journal
        assert journal in plan.journal_entries


def test_journal_json_fields(app, test_plan, test_trade):
    """Test complex JSON field handling"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        trade = db.session.merge(test_trade)

        complex_conditions = {
            "market": {
                "trend": {
                    "direction": "bullish",
                    "strength": 8,
                    "duration": "4h"
                },
                "support_resistance": {
                    "nearest_support": "1.1150",
                    "nearest_resistance": "1.1200",
                    "strength": "strong"
                },
                "indicators": {
                    "rsi": 65,
                    "macd": "bullish",
                    "moving_averages": "aligned"
                }
            },
            "correlations": {
                "dxy": "negative",
                "gold": "positive"
            }
        }

        complex_adherence = {
            "rules": {
                "entry": {
                    "followed": True,
                    "score": 9,
                    "notes": "Perfect setup"
                },
                "exit": {
                    "followed": True,
                    "score": 8,
                    "notes": "Slightly early"
                }
            },
            "psychology": {
                "emotional_state": "calm",
                "confidence": 8,
                "stress_level": 3
            },
            "improvements":
            ["Wait for better exit signal",
             "Increase position size"]
        }

        journal = Journal(trade_id=trade.id,
                          trading_plan_id=plan.id,
                          market_conditions=complex_conditions,
                          plan_adherence=complex_adherence)

        db.session.add(journal)
        db.session.commit()

        # Refresh from database
        journal = db.session.get(Journal, journal.id)

        # Test nested JSON structure
        assert journal.market_conditions["market"]["trend"]["strength"] == 8
        assert journal.market_conditions["correlations"]["dxy"] == "negative"
        assert journal.plan_adherence["rules"]["entry"]["score"] == 9
        assert "Wait for better exit signal" in journal.plan_adherence[
            "improvements"]


def test_journal_validation(app, test_plan, test_trade):
    """Test journal validation requirements"""
    with app.app_context():
        # Test missing required fields
        with pytest.raises(Exception):
            journal = Journal(
            )  # Missing required trade_id and trading_plan_id
            db.session.add(journal)
            db.session.commit()


def test_journal_cascading_delete(app, test_plan, test_trade):
    """Test cascade delete behavior"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        trade = db.session.merge(test_trade)

        journal = Journal(trade_id=trade.id,
                          trading_plan_id=plan.id,
                          notes="Test entry")

        db.session.add(journal)
        db.session.commit()

        journal_id = journal.id

        # Delete trade should delete journal
        db.session.delete(trade)
        db.session.commit()

        # Verify journal is deleted
        assert db.session.get(Journal, journal_id) is None
