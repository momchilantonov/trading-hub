from datetime import datetime
from decimal import Decimal
import pytest
from flask import Flask
from app import db
from app.models import Trade, Journal, Strategy, TradingPlan, User


def test_trade_images(app: Flask, test_setup):
    """Test trade image handling"""
    with app.app_context():
        plan = db.session.get(TradingPlan, test_setup['plan_id'])

        trade = Trade(trading_plan_id=plan.id,
                      entry_price=Decimal('1.2000'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('100000'),
                      entry_image_url='/static/trades/entry_1.png',
                      exit_image_url='/static/trades/exit_1.png')

        db.session.add(trade)
        db.session.commit()

        # Refresh from database
        trade = db.session.get(Trade, trade.id)

        assert trade.entry_image_url == '/static/trades/entry_1.png'
        assert trade.exit_image_url == '/static/trades/exit_1.png'


def test_journal_images(app: Flask, test_setup):
    """Test journal image handling"""
    with app.app_context():
        trade = db.session.get(Trade, test_setup['trade_id'])

        images = [{
            "url": "/static/journal/analysis_1.png",
            "description": "Price action analysis",
            "type": "analysis",
            "upload_date": datetime.utcnow().isoformat()
        },
                  {
                      "url": "/static/journal/setup_1.png",
                      "description": "Entry setup",
                      "type": "setup",
                      "upload_date": datetime.utcnow().isoformat()
                  }]

        journal = Journal(trade_id=trade.id,
                          trading_plan_id=trade.trading_plan_id,
                          notes="Test entry",
                          images=images)

        db.session.add(journal)
        db.session.commit()

        # Refresh from database
        journal = db.session.get(Journal, journal.id)

        assert len(journal.images) == 2
        assert journal.images[0]["type"] == "analysis"
        assert journal.images[1]["type"] == "setup"


def test_strategy_images(app: Flask, test_setup):
    """Test strategy image handling"""
    with app.app_context():
        example_images = [{
            "url": "/static/strategy/example_1.png",
            "description": "Perfect breakout setup",
            "pattern_type": "breakout",
            "upload_date": datetime.utcnow().isoformat()
        }]

        strategy = Strategy(name="Breakout Strategy",
                            description="Trading breakouts",
                            strategy_image_url="/static/strategy/main.png",
                            example_images=example_images)

        db.session.add(strategy)
        db.session.commit()

        # Refresh from database
        strategy = db.session.get(Strategy, strategy.id)

        assert strategy.strategy_image_url == "/static/strategy/main.png"
        assert len(strategy.example_images) == 1
        assert strategy.example_images[0]["pattern_type"] == "breakout"


def test_trading_plan_images(app: Flask, test_setup):
    """Test trading plan image handling"""
    with app.app_context():
        user = db.session.get(User, test_setup['user_id'])

        plan_images = [{
            "url": "/static/plans/entry_rules.png",
            "section": "entry_rules",
            "description": "Entry rules diagram",
            "upload_date": datetime.utcnow().isoformat()
        },
                       {
                           "url": "/static/plans/risk_management.png",
                           "section": "risk_management",
                           "description": "Risk management flowchart",
                           "upload_date": datetime.utcnow().isoformat()
                       }]

        plan = TradingPlan(user_id=user.id,
                           name="Test Plan",
                           type="day_trading",
                           plan_images=plan_images)

        db.session.add(plan)
        db.session.commit()

        # Refresh from database
        plan = db.session.get(TradingPlan, plan.id)

        assert len(plan.plan_images) == 2
        assert plan.plan_images[0]["section"] == "entry_rules"
        assert plan.plan_images[1]["section"] == "risk_management"
