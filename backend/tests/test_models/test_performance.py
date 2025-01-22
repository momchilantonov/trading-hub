import pytest
from datetime import datetime
from app.models import Performance, Strategy, TradingPlan, User
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
                            description="Strategy for testing performance")
        db.session.add(strategy)
        db.session.commit()
        return db.session.get(Strategy, strategy.id)


def test_create_performance(app, test_strategy, test_plan):
    """Test basic performance creation"""
    with app.app_context():
        strategy = db.session.merge(test_strategy)
        plan = db.session.merge(test_plan)

        performance = Performance(strategy_id=strategy.id,
                                  trading_plan_id=plan.id,
                                  metrics={
                                      "summary": {
                                          "total_trades": 50,
                                          "win_rate": 65.5,
                                          "profit_factor": 2.1,
                                          "sharpe_ratio": 1.8,
                                          "max_drawdown": 12.5,
                                          "avg_win": 150.75,
                                          "avg_loss": 75.25
                                      },
                                      "monthly_returns": {
                                          "2025-01": 5.2,
                                          "2025-02": 3.8,
                                          "2025-03": -1.2
                                      }
                                  },
                                  timeframe="daily",
                                  period="Q1-2025")

        db.session.add(performance)
        db.session.commit()

        # Refresh from database
        performance = db.session.get(Performance, performance.id)

        assert performance.id is not None
        assert performance.strategy_id == strategy.id
        assert performance.trading_plan_id == plan.id
        assert performance.metrics["summary"]["win_rate"] == 65.5
        assert performance.timeframe == "daily"
        assert performance.period == "Q1-2025"


def test_performance_relationships(app, test_strategy, test_plan):
    """Test performance relationships with strategy and trading plan"""
    with app.app_context():
        strategy = db.session.merge(test_strategy)
        plan = db.session.merge(test_plan)

        performance = Performance(strategy_id=strategy.id,
                                  trading_plan_id=plan.id,
                                  metrics={"basic_metric": 100},
                                  timeframe="weekly",
                                  period="2025-W01")

        db.session.add(performance)
        db.session.commit()

        # Refresh from database
        performance = db.session.get(Performance, performance.id)
        strategy = db.session.get(Strategy, strategy.id)
        plan = db.session.get(TradingPlan, plan.id)

        # Test relationships
        assert performance.strategy == strategy
        assert performance.trading_plan == plan
        assert performance in strategy.performances
        assert performance in plan.performances


def test_performance_complex_metrics(app, test_strategy, test_plan):
    """Test complex metrics data structure"""
    with app.app_context():
        strategy = db.session.merge(test_strategy)
        plan = db.session.merge(test_plan)

        complex_metrics = {
            "overall": {
                "total_trades": 150,
                "winning_trades": 98,
                "losing_trades": 52,
                "win_rate": 65.33,
                "profit_factor": 2.3,
                "expected_value": 45.75
            },
            "risk_metrics": {
                "sharpe_ratio": 1.95,
                "sortino_ratio": 2.15,
                "max_drawdown": {
                    "value": 15.5,
                    "start_date": "2025-01-15",
                    "end_date": "2025-02-01",
                    "duration_days": 17
                },
                "var_95": 8.5,
                "cvar_95": 10.2
            },
            "trade_metrics": {
                "avg_win": 150.25,
                "avg_loss": 65.50,
                "largest_win": 450.00,
                "largest_loss": 200.00,
                "avg_hold_time": {
                    "winning": "5h 30m",
                    "losing": "2h 45m"
                }
            },
            "monthly_breakdown": {
                "2025-01": {
                    "return": 8.5,
                    "trades": 52,
                    "win_rate": 67.3
                },
                "2025-02": {
                    "return": 6.2,
                    "trades": 48,
                    "win_rate": 64.6
                }
            }
        }

        performance = Performance(strategy_id=strategy.id,
                                  trading_plan_id=plan.id,
                                  metrics=complex_metrics,
                                  timeframe="daily",
                                  period="2025-H1")

        db.session.add(performance)
        db.session.commit()

        # Refresh from database
        performance = db.session.get(Performance, performance.id)

        # Test nested JSON structure
        assert performance.metrics["overall"]["win_rate"] == 65.33
        assert performance.metrics["risk_metrics"]["max_drawdown"][
            "duration_days"] == 17
        assert performance.metrics["trade_metrics"]["avg_hold_time"][
            "winning"] == "5h 30m"
        assert performance.metrics["monthly_breakdown"]["2025-01"][
            "trades"] == 52


def test_performance_validation(app, test_strategy, test_plan):
    """Test performance validation"""
    with app.app_context():
        strategy = db.session.merge(test_strategy)
        plan = db.session.merge(test_plan)

        # Test missing required fields
        with pytest.raises(Exception):
            performance = Performance(
                strategy_id=strategy.id)  # Missing trading_plan_id
            db.session.add(performance)
            db.session.commit()

        with pytest.raises(Exception):
            performance = Performance(
                strategy_id=strategy.id,
                trading_plan_id=plan.id,
                # Missing timeframe and period
                metrics={"some_metric": 100})
            db.session.add(performance)
            db.session.commit()


def test_performance_cascading_delete(app, test_strategy, test_plan):
    """Test cascade delete behavior"""
    with app.app_context():
        strategy = db.session.merge(test_strategy)
        plan = db.session.merge(test_plan)

        performance = Performance(strategy_id=strategy.id,
                                  trading_plan_id=plan.id,
                                  metrics={"test_metric": 100},
                                  timeframe="daily",
                                  period="2025-01")

        db.session.add(performance)
        db.session.commit()

        performance_id = performance.id

        # Delete strategy should delete performance
        db.session.delete(strategy)
        db.session.commit()

        # Verify performance is deleted
        assert db.session.get(Performance, performance_id) is None

        # Create another performance for testing plan deletion
        performance2 = Performance(
            strategy_id=test_strategy.id,  # Use a fresh strategy
            trading_plan_id=plan.id,
            metrics={"test_metric": 100},
            timeframe="daily",
            period="2025-01"
        )

        db.session.add(performance2)
        db.session.commit()

        performance2_id = performance2.id

        # Delete plan should delete performance
        db.session.delete(plan)
        db.session.commit()

        # Verify performance is deleted
        assert db.session.get(Performance, performance2_id) is None
