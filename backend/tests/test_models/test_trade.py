import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.models import User, TradingPlan, Trade, Strategy
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
def test_strategy(app):
    """Create test strategy"""
    with app.app_context():
        strategy = Strategy(name="Test Strategy",
                            description="Test strategy description",
                            parameters={
                                "rsi_period": 14,
                                "ma_period": 20
                            })
        db.session.add(strategy)
        db.session.commit()
        return db.session.get(Strategy, strategy.id)


def test_create_trade(app, test_plan):
    """Test basic trade creation"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        entry_time = datetime.utcnow()

        trade = Trade(trading_plan_id=plan.id,
                      entry_price=Decimal('100.50'),
                      entry_time=entry_time,
                      symbol='EURUSD',
                      position_size=Decimal('1.0'),
                      timeframe='H1')

        db.session.add(trade)
        db.session.commit()

        # Refresh from database
        trade = db.session.get(Trade, trade.id)

        assert trade.id is not None
        assert trade.trading_plan_id == plan.id
        assert trade.entry_price == Decimal('100.50')
        assert trade.symbol == 'EURUSD'
        assert trade.position_size == Decimal('1.0')
        assert trade.timeframe == 'H1'
        assert trade.exit_price is None
        assert trade.exit_time is None


def test_trade_complete_lifecycle(app, test_plan, test_strategy):
    """Test complete trade lifecycle including entry and exit"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        strategy = db.session.merge(test_strategy)
        entry_time = datetime.utcnow()

        trade = Trade(trading_plan_id=plan.id,
                      strategy_id=strategy.id,
                      entry_price=Decimal('100.00'),
                      entry_time=entry_time,
                      symbol='EURUSD',
                      position_size=Decimal('1.0'),
                      timeframe='H1')

        db.session.add(trade)
        db.session.commit()

        # Add exit details
        trade = db.session.get(Trade, trade.id)
        exit_time = entry_time + timedelta(hours=2)
        trade.exit_price = Decimal('101.00')
        trade.exit_time = exit_time
        db.session.commit()

        # Refresh and verify
        trade = db.session.get(Trade, trade.id)
        assert trade.exit_price == Decimal('101.00')
        assert trade.exit_time == exit_time
        assert trade.strategy_id == strategy.id


def test_trade_relationships(app, test_plan, test_strategy):
    """Test trade relationships with plan and strategy"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        strategy = db.session.merge(test_strategy)

        trade = Trade(trading_plan_id=plan.id,
                      strategy_id=strategy.id,
                      entry_price=Decimal('100.00'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('1.0'))

        db.session.add(trade)
        db.session.commit()

        # Refresh from database
        trade = db.session.get(Trade, trade.id)
        plan = db.session.get(TradingPlan, plan.id)
        strategy = db.session.get(Strategy, strategy.id)

        # Test relationships
        assert trade.trading_plan == plan
        assert trade.strategy == strategy
        assert trade in plan.trades
        assert trade in strategy.trades


def test_trade_validation(app, test_plan):
    """Test trade validation requirements"""
    with app.app_context():
        plan = db.session.merge(test_plan)

        # Test missing required fields
        with pytest.raises(Exception):
            trade = Trade(trading_plan_id=plan.id)  # Missing required fields
            db.session.add(trade)
            db.session.commit()


def test_trade_cascading_delete(app, test_plan, test_strategy):
    """Test cascade delete behavior"""
    with app.app_context():
        plan = db.session.merge(test_plan)
        strategy = db.session.merge(test_strategy)

        trade = Trade(trading_plan_id=plan.id,
                      strategy_id=strategy.id,
                      entry_price=Decimal('100.00'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('1.0'))

        db.session.add(trade)
        db.session.commit()

        trade_id = trade.id

        # Delete plan should cascade to trade
        db.session.delete(plan)
        db.session.commit()

        # Verify trade is deleted
        assert db.session.get(Trade, trade_id) is None

        # But strategy should still exist
        assert db.session.get(Strategy, strategy.id) is not None
