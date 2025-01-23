from datetime import datetime
from decimal import Decimal
import pytest
from flask import Flask
from app import db
from app.models import User, TradingPlan, Trade, Strategy, Journal, Performance


@pytest.fixture
def test_setup(app: Flask):
    """Create a complete test setup with all related objects"""
    with app.app_context():
        # Create user
        user = User(email='trader@example.com', username='trader')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Create trading plan with images
        plan = TradingPlan(user_id=user_id,
                           name="Test Plan",
                           type="day_trading",
                           plan_images=[{
                               "url":
                               "/static/plans/test.png",
                               "section":
                               "rules",
                               "description":
                               "Test image",
                               "upload_date":
                               datetime.utcnow().isoformat()
                           }])
        db.session.add(plan)
        db.session.commit()
        plan_id = plan.id

        # Create strategy with images
        strategy = Strategy(name="Test Strategy",
                            description="Test strategy description",
                            strategy_image_url="/static/strategy/main.png",
                            example_images=[{
                                "url":
                                "/static/strategy/example.png",
                                "description":
                                "Example setup",
                                "pattern_type":
                                "test",
                                "upload_date":
                                datetime.utcnow().isoformat()
                            }])
        db.session.add(strategy)
        db.session.commit()
        strategy_id = strategy.id

        # Create trade with fees and images
        trade = Trade(trading_plan_id=plan_id,
                      strategy_id=strategy_id,
                      entry_price=Decimal('100.00'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('1.0'),
                      entry_fee=Decimal('5.00'),
                      exit_fee=Decimal('5.00'),
                      entry_image_url="/static/trades/entry.png",
                      exit_image_url="/static/trades/exit.png")
        db.session.add(trade)
        db.session.commit()
        trade_id = trade.id

        # Create journal with images
        journal = Journal(trade_id=trade_id,
                          trading_plan_id=plan_id,
                          notes="Test note",
                          images=[{
                              "url": "/static/journal/test.png",
                              "description": "Test analysis",
                              "type": "analysis",
                              "upload_date": datetime.utcnow().isoformat()
                          }])
        db.session.add(journal)
        db.session.commit()
        journal_id = journal.id

        # Create performance
        performance = Performance(strategy_id=strategy_id,
                                  trading_plan_id=plan_id,
                                  metrics={
                                      "test": "data",
                                      "total_fees": 10.0
                                  },
                                  timeframe="daily",
                                  period="2025-01")
        db.session.add(performance)
        db.session.commit()
        performance_id = performance.id

        return {
            'user_id': user_id,
            'plan_id': plan_id,
            'strategy_id': strategy_id,
            'trade_id': trade_id,
            'journal_id': journal_id,
            'performance_id': performance_id
        }


def test_user_deletion_cascade(app: Flask, test_setup):
    """Test cascade behavior when deleting a user"""
    with app.app_context():
        user = db.session.get(User, test_setup['user_id'])
        plan_id = test_setup['plan_id']
        trade_id = test_setup['trade_id']
        journal_id = test_setup['journal_id']

        # Verify initial state including images
        plan = db.session.get(TradingPlan, plan_id)
        assert len(plan.plan_images) == 1

        # Delete user
        db.session.delete(user)
        db.session.commit()

        # Verify cascading deletes
        assert db.session.get(TradingPlan, plan_id) is None
        assert db.session.get(Trade, trade_id) is None
        assert db.session.get(Journal, journal_id) is None


def test_trading_plan_deletion_cascade(app: Flask, test_setup):
    """Test cascade behavior when deleting a trading plan"""
    with app.app_context():
        plan = db.session.get(TradingPlan, test_setup['plan_id'])
        user_id = test_setup['user_id']
        trade_id = test_setup['trade_id']
        journal_id = test_setup['journal_id']
        performance_id = test_setup['performance_id']

        # Verify initial state including images
        assert len(plan.plan_images) == 1

        # Delete trading plan
        db.session.delete(plan)
        db.session.commit()

        # Verify cascading deletes
        assert db.session.get(User, user_id) is not None  # User should remain
        assert db.session.get(Trade, trade_id) is None
        assert db.session.get(Journal, journal_id) is None
        assert db.session.get(Performance, performance_id) is None


def test_strategy_deletion_behavior(app: Flask, test_setup):
    """Test behavior when deleting a strategy"""
    with app.app_context():
        strategy = db.session.get(Strategy, test_setup['strategy_id'])
        trade_id = test_setup['trade_id']
        performance_id = test_setup['performance_id']

        # Verify initial state including images
        assert strategy.strategy_image_url == "/static/strategy/main.png"
        assert len(strategy.example_images) == 1

        # Delete strategy
        db.session.delete(strategy)
        db.session.commit()

        # Verify related records
        trade = db.session.get(Trade, trade_id)
        assert trade is not None
        assert trade.strategy_id is None  # Should be set to NULL
        assert db.session.get(Performance, performance_id) is None


def test_trade_deletion_cascade(app: Flask, test_setup):
    """Test cascade behavior when deleting a trade"""
    with app.app_context():
        trade = db.session.get(Trade, test_setup['trade_id'])
        journal_id = test_setup['journal_id']
        plan_id = test_setup['plan_id']
        strategy_id = test_setup['strategy_id']

        # Verify initial state including images
        assert trade.entry_image_url == "/static/trades/entry.png"
        assert trade.exit_image_url == "/static/trades/exit.png"
        assert trade.entry_fee == Decimal('5.00')
        assert trade.exit_fee == Decimal('5.00')

        # Delete trade
        db.session.delete(trade)
        db.session.commit()

        # Verify cascading deletes
        assert db.session.get(Journal, journal_id) is None
        assert db.session.get(TradingPlan,
                              plan_id) is not None  # Should remain
        assert db.session.get(Strategy,
                              strategy_id) is not None  # Should remain


def test_relationship_updates(app: Flask, test_setup):
    """Test updating relationships between entities"""
    with app.app_context():
        # Get fresh instances
        user = db.session.get(User, test_setup['user_id'])
        trade = db.session.get(Trade, test_setup['trade_id'])
        journal = db.session.get(Journal, test_setup['journal_id'])

        # Create new trading plan with images
        new_plan = TradingPlan(user_id=user.id,
                               name="New Plan",
                               type="swing_trading",
                               plan_images=[{
                                   "url":
                                   "/static/plans/new.png",
                                   "section":
                                   "rules",
                                   "description":
                                   "New plan image",
                                   "upload_date":
                                   datetime.utcnow().isoformat()
                               }])
        db.session.add(new_plan)
        db.session.commit()

        # Move trade to new plan
        trade.trading_plan_id = new_plan.id
        trade.journal_entry.trading_plan_id = new_plan.id
        db.session.commit()

        # Verify relationships
        trade = db.session.get(Trade, trade.id)
        assert trade.trading_plan_id == new_plan.id

        journal = db.session.get(Journal, test_setup['journal_id'])
        assert journal.trading_plan_id == new_plan.id

        # Create new strategy with images
        new_strategy = Strategy(name="New Strategy",
                                description="New strategy description",
                                strategy_image_url="/static/strategy/new.png")
        db.session.add(new_strategy)
        db.session.commit()

        # Move trade to new strategy
        trade.strategy_id = new_strategy.id
        db.session.commit()

        # Verify strategy relationships
        trade = db.session.get(Trade, trade.id)
        new_strategy = db.session.get(Strategy, new_strategy.id)
        assert trade.strategy_id == new_strategy.id
        assert trade in new_strategy.trades


def test_fee_relationships(app: Flask, test_setup):
    """Test fee handling in relationships"""
    with app.app_context():
        trade = db.session.get(Trade, test_setup['trade_id'])

        # Update fees
        trade.entry_fee = Decimal('7.50')
        trade.exit_fee = Decimal('7.50')
        db.session.commit()

        # Create performance record with updated fees
        performance = Performance(strategy_id=test_setup['strategy_id'],
                                  trading_plan_id=test_setup['plan_id'],
                                  metrics={
                                      "total_fees":
                                      float(trade.entry_fee + trade.exit_fee),
                                      "period_data":
                                      "test"
                                  },
                                  timeframe="daily",
                                  period="2025-01")
        db.session.add(performance)
        db.session.commit()

        # Verify fee relationships
        trade = db.session.get(Trade, trade.id)
        assert trade.entry_fee == Decimal('7.50')
        assert trade.exit_fee == Decimal('7.50')
        assert performance.metrics["total_fees"] == 15.0
