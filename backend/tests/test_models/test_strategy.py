import pytest
from decimal import Decimal
from datetime import datetime
from app.models import Strategy, Trade, Performance, TradingPlan, User
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


def test_create_strategy(app):
    """Test basic strategy creation"""
    with app.app_context():
        strategy = Strategy(name="Moving Average Crossover",
                            description="A strategy based on MA crossovers",
                            parameters={
                                "fast_ma": 9,
                                "slow_ma": 21,
                                "timeframe": "H1",
                                "risk_percent": 1.0
                            },
                            performance_metrics={
                                "win_rate": 65.5,
                                "profit_factor": 1.8,
                                "max_drawdown": 12.3,
                                "avg_win_loss": 1.5
                            })

        db.session.add(strategy)
        db.session.commit()

        # Refresh from database
        strategy = db.session.get(Strategy, strategy.id)

        assert strategy.id is not None
        assert strategy.name == "Moving Average Crossover"
        assert strategy.parameters["fast_ma"] == 9
        assert strategy.performance_metrics["win_rate"] == 65.5


def test_strategy_with_trades(app, test_plan):
    """Test strategy relationship with trades"""
    with app.app_context():
        plan = db.session.merge(test_plan)

        strategy = Strategy(name="RSI Strategy",
                            description="RSI-based mean reversion",
                            parameters={
                                "rsi_period": 14,
                                "overbought": 70,
                                "oversold": 30
                            })

        db.session.add(strategy)
        db.session.commit()

        # Create trades using this strategy
        trades = [
            Trade(trading_plan_id=plan.id,
                  strategy_id=strategy.id,
                  entry_price=Decimal('100.00'),
                  entry_time=datetime.utcnow(),
                  symbol='EURUSD',
                  position_size=Decimal('1.0')),
            Trade(trading_plan_id=plan.id,
                  strategy_id=strategy.id,
                  entry_price=Decimal('101.00'),
                  entry_time=datetime.utcnow(),
                  symbol='EURUSD',
                  position_size=Decimal('1.0'))
        ]

        db.session.add_all(trades)
        db.session.commit()

        # Refresh strategy from database
        strategy = db.session.get(Strategy, strategy.id)

        assert len(strategy.trades) == 2
        assert all(trade.strategy_id == strategy.id
                   for trade in strategy.trades)


def test_strategy_performance_metrics(app, test_plan):
    """Test strategy performance metrics tracking"""
    with app.app_context():
        plan = db.session.merge(test_plan)

        strategy = Strategy(name="Breakout Strategy",
                            description="Volatility breakout strategy")

        db.session.add(strategy)
        db.session.commit()

        # Create performance records
        performance = Performance(strategy_id=strategy.id,
                                  trading_plan_id=plan.id,
                                  metrics={
                                      "period_1": {
                                          "trades": 50,
                                          "win_rate": 68.0,
                                          "profit_factor": 2.1,
                                          "sharpe_ratio": 1.8
                                      },
                                      "period_2": {
                                          "trades": 45,
                                          "win_rate": 71.0,
                                          "profit_factor": 2.3,
                                          "sharpe_ratio": 1.9
                                      }
                                  },
                                  timeframe="daily",
                                  period="Q1-2025")

        db.session.add(performance)
        db.session.commit()

        # Refresh from database
        strategy = db.session.get(Strategy, strategy.id)

        assert len(strategy.performances) == 1
        assert strategy.performances[0].metrics["period_1"]["win_rate"] == 68.0
        assert strategy.performances[0].timeframe == "daily"


def test_strategy_json_fields(app):
    """Test complex JSON field handling in strategy"""
    with app.app_context():
        complex_parameters = {
            "entry_rules": {
                "indicators": {
                    "rsi": {
                        "period": 14,
                        "level": 30
                    },
                    "macd": {
                        "fast": 12,
                        "slow": 26,
                        "signal": 9
                    },
                    "bollinger": {
                        "period": 20,
                        "std_dev": 2
                    }
                },
                "filters": {
                    "time_ranges": ["08:00-16:00",
                                    "20:00-24:00"],
                    "min_volatility": 0.5,
                    "max_spread": 3
                },
                "conditions": ["price_action",
                               "volume_confirmation"]
            },
            "exit_rules": {
                "take_profit": {
                    "type": "atr_multiple",
                    "value": 3
                },
                "stop_loss": {
                    "type": "fixed_pips",
                    "value": 50
                },
                "trailing_stop": {
                    "enabled": True,
                    "activation": 1.5
                }
            },
            "risk_management": {
                "position_sizing": {
                    "type": "risk_percent",
                    "value": 1
                },
                "max_daily_trades": 5,
                "max_open_positions": 3
            }
        }

        strategy = Strategy(name="Complex Strategy",
                            description="Strategy with complex parameters",
                            parameters=complex_parameters)

        db.session.add(strategy)
        db.session.commit()

        # Refresh from database
        strategy = db.session.get(Strategy, strategy.id)

        # Test nested JSON structure
        assert strategy.parameters["entry_rules"]["indicators"]["rsi"][
            "period"] == 14
        assert strategy.parameters["exit_rules"]["trailing_stop"][
            "enabled"] is True
        assert strategy.parameters["risk_management"]["max_daily_trades"] == 5


def test_strategy_validation(app):
    """Test strategy validation"""
    with app.app_context():
        # Test missing required name
        with pytest.raises(Exception):
            strategy = Strategy(description="Test")
            db.session.add(strategy)
            db.session.commit()


def test_strategy_relationships_cleanup(app, test_plan):
    """Test cleanup behavior when strategy is deleted"""
    with app.app_context():
        plan = db.session.merge(test_plan)

        strategy = Strategy(name="Test Strategy",
                            description="Strategy to test deletion")

        db.session.add(strategy)
        db.session.commit()

        # Create a trade using this strategy
        trade = Trade(trading_plan_id=plan.id,
                      strategy_id=strategy.id,
                      entry_price=Decimal('100.00'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('1.0'))

        db.session.add(trade)
        db.session.commit()

        trade_id = trade.id
        strategy_id = strategy.id

        # Delete strategy
        db.session.delete(strategy)
        db.session.commit()

        # Verify trade still exists but no longer references strategy
        trade = db.session.get(Trade, trade_id)
        assert trade is not None
        assert trade.strategy_id is None
        assert db.session.get(Strategy, strategy_id) is None
