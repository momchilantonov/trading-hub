from datetime import datetime
from decimal import Decimal
import pytest
from flask import Flask
from app import db
from app.models import User, TradingPlan, Trade, Strategy, Journal, Performance
from app.utils.validators import ValidationError


def test_complete_trading_workflow(app: Flask) -> None:
    """
    Test complete trading workflow:
    1. Create user and trading plan
    2. Create strategy
    3. Execute trades with images and fees
    4. Record journal entries with images
    5. Track performance
    """
    with app.app_context():
        # 1. Create User and Trading Plan
        user = User(email='trader@example.com', username='trader')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Create trading plan with images
        plan = TradingPlan(user_id=user.id,
                           name="Forex Day Trading",
                           type="day_trading",
                           risk_management={
                               "max_risk_per_trade": 0.02,
                               "max_daily_risk": 0.06,
                               "max_drawdown": 0.10
                           },
                           entry_rules={
                               "setup_types": ["breakout",
                                               "pullback"],
                               "timeframes": ["H1",
                                              "H4"],
                               "min_risk_reward": 2.0
                           },
                           markets=["EUR/USD",
                                    "GBP/USD",
                                    "USD/JPY"],
                           plan_images=[{
                               "url":
                               "/static/plans/risk_management.png",
                               "section":
                               "risk_management",
                               "description":
                               "Risk management rules",
                               "upload_date":
                               datetime.utcnow().isoformat()
                           }])
        db.session.add(plan)
        db.session.commit()

        # 2. Create Strategy with images
        strategy = Strategy(name="Breakout Strategy",
                            description="Trade breakouts with momentum",
                            parameters={
                                "lookback_period": 20,
                                "volatility_factor": 1.5,
                                "min_volume": 100000
                            },
                            strategy_image_url="/static/strategy/main.png",
                            example_images=[{
                                "url":
                                "/static/strategy/example1.png",
                                "description":
                                "Perfect breakout setup",
                                "pattern_type":
                                "breakout",
                                "upload_date":
                                datetime.utcnow().isoformat()
                            }])
        db.session.add(strategy)
        db.session.commit()

        # 3. Execute Multiple Trades with fees and images
        # Winning trade
        trade1 = Trade(trading_plan_id=plan.id,
                       strategy_id=strategy.id,
                       entry_price=Decimal('1.2000'),
                       exit_price=Decimal('1.2100'),
                       entry_time=datetime(2025,
                                           1,
                                           1,
                                           10,
                                           0),
                       exit_time=datetime(2025,
                                          1,
                                          1,
                                          14,
                                          0),
                       symbol='EURUSD',
                       position_size=Decimal('100000'),
                       timeframe='H1',
                       entry_fee=Decimal('5.00'),
                       exit_fee=Decimal('5.00'),
                       entry_image_url="/static/trades/entry1.png",
                       exit_image_url="/static/trades/exit1.png")

        # Losing trade
        trade2 = Trade(trading_plan_id=plan.id,
                       strategy_id=strategy.id,
                       entry_price=Decimal('1.2150'),
                       exit_price=Decimal('1.2100'),
                       entry_time=datetime(2025,
                                           1,
                                           2,
                                           10,
                                           0),
                       exit_time=datetime(2025,
                                          1,
                                          2,
                                          13,
                                          0),
                       symbol='EURUSD',
                       position_size=Decimal('100000'),
                       timeframe='H1',
                       entry_fee=Decimal('5.00'),
                       exit_fee=Decimal('5.00'),
                       entry_image_url="/static/trades/entry2.png",
                       exit_image_url="/static/trades/exit2.png")

        db.session.add_all([trade1, trade2])
        db.session.commit()

        # 4. Create Journal Entries with images
        journal1 = Journal(trade_id=trade1.id,
                           trading_plan_id=plan.id,
                           notes="Strong breakout with volume confirmation",
                           emotions="Confident",
                           market_conditions={
                               "trend": "bullish",
                               "volatility": "medium",
                               "volume": "high"
                           },
                           plan_adherence={
                               "followed_rules": True,
                               "position_sizing_correct": True,
                               "proper_entry": True,
                               "proper_exit": True
                           },
                           images=[{
                               "url": "/static/journal/analysis1.png",
                               "description": "Trade analysis",
                               "type": "analysis",
                               "upload_date": datetime.utcnow().isoformat()
                           }])

        journal2 = Journal(trade_id=trade2.id,
                           trading_plan_id=plan.id,
                           notes="Entered too late, missed optimal entry",
                           emotions="Hesitant",
                           market_conditions={
                               "trend": "bullish",
                               "volatility": "low",
                               "volume": "decreasing"
                           },
                           plan_adherence={
                               "followed_rules":
                               False,
                               "position_sizing_correct":
                               True,
                               "proper_entry":
                               False,
                               "proper_exit":
                               True,
                               "lessons_learned":
                               "Wait for proper setup confirmation"
                           },
                           images=[{
                               "url": "/static/journal/analysis2.png",
                               "description": "Missed entry analysis",
                               "type": "analysis",
                               "upload_date": datetime.utcnow().isoformat()
                           }])

        db.session.add_all([journal1, journal2])
        db.session.commit()

        # 5. Track Performance
        performance = Performance(
            strategy_id=strategy.id,
            trading_plan_id=plan.id,
            metrics={
                "summary": {
                    "total_trades": 2,
                    "win_rate": 50.0,
                    "profit_factor": 1.2,
                    "average_win": 100.0,
                    "average_loss": 50.0,
                    "largest_win": 100.0,
                    "largest_loss": 50.0,
                    "total_fees": 20.0
                },
                "plan_adherence": {
                    "rule_following_rate": 50.0,
                    "areas_for_improvement":
                    ["entry_timing",
                     "setup_confirmation"]
                }
            },
            timeframe="daily",
            period="2025-01")
        db.session.add(performance)
        db.session.commit()

        # Verify the complete workflow
        # 1. Verify Trading Plan
        plan = db.session.get(TradingPlan, plan.id)
        assert len(plan.trades) == 2
        assert len(plan.plan_images) == 1
        assert plan.plan_images[0]["section"] == "risk_management"

        # 2. Verify Strategy
        strategy = db.session.get(Strategy, strategy.id)
        assert len(strategy.trades) == 2
        assert len(strategy.performances) == 1
        assert strategy.strategy_image_url == "/static/strategy/main.png"
        assert len(strategy.example_images) == 1

        # 3. Verify Trades
        trade1 = db.session.get(Trade, trade1.id)
        assert trade1.entry_fee == Decimal('5.00')
        assert trade1.entry_image_url == "/static/trades/entry1.png"
        assert trade1.exit_image_url == "/static/trades/exit1.png"

        # 4. Verify Journal Entries
        journal1 = db.session.get(Journal, journal1.id)
        assert len(journal1.images) == 1
        assert journal1.images[0]["type"] == "analysis"

        # 5. Verify Performance
        performance = db.session.get(Performance, performance.id)
        assert performance.metrics["summary"]["total_trades"] == 2
        assert performance.metrics["summary"]["win_rate"] == 50.0
        assert performance.metrics["summary"]["total_fees"] == 20.0


def test_trading_workflow_validations(app: Flask) -> None:
    """Test validations in the trading workflow"""
    with app.app_context():
        # Create base user and plan
        user = User(email='trader@example.com', username='trader')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        plan = TradingPlan(user_id=user.id,
                           name="Test Plan",
                           type="day_trading")
        db.session.add(plan)
        db.session.commit()

        # Test trade without required fields
        with pytest.raises(Exception):
            trade = Trade(trading_plan_id=plan.id)
            db.session.add(trade)
            db.session.commit()

        # Test trade with invalid image URL
        with pytest.raises(ValidationError):
            trade = Trade(
                trading_plan_id=plan.id,
                entry_price=Decimal('1.2000'),
                entry_time=datetime.utcnow(),
                symbol='EURUSD',
                position_size=Decimal('100000'),
                entry_image_url="invalid_url"  # Invalid URL format
            )
            db.session.add(trade)
            db.session.commit()

        # Test journal without trade reference
        with pytest.raises(Exception):
            journal = Journal(trading_plan_id=plan.id)
            db.session.add(journal)
            db.session.commit()

        # Test journal with invalid image data
        with pytest.raises(ValidationError):
            journal = Journal(
                trade_id=trade.id,
                trading_plan_id=plan.id,
                images=[{
                    "url": "/static/journal/image.png"
                    # Missing required fields
                }])
            db.session.add(journal)
            db.session.commit()

        # Test performance without required fields
        with pytest.raises(Exception):
            performance = Performance(trading_plan_id=plan.id)
            db.session.add(performance)
            db.session.commit()
