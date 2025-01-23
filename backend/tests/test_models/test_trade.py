from datetime import datetime
from decimal import Decimal
import pytest
from flask import Flask
from app import db
from app.models import Trade, TradingPlan, Strategy


def test_trade_with_fees(app: Flask, test_setup):
    """Test trade creation with entry and exit fees"""
    with app.app_context():
        plan = db.session.get(TradingPlan, test_setup['plan_id'])

        # Create BTC/USD trade
        trade = Trade(trading_plan_id=plan.id,
                      entry_price=Decimal('50000.00'),
                      exit_price=Decimal('51000.00'),
                      entry_time=datetime.utcnow(),
                      exit_time=datetime.utcnow(),
                      symbol='BTCUSD',
                      position_size=Decimal('1.0'),
                      entry_fee=Decimal('25.00'),
                      exit_fee=Decimal('25.50'),
                      timeframe='H1')

        db.session.add(trade)
        db.session.commit()

        # Refresh from database
        trade = db.session.get(Trade, trade.id)

        # Verify fees
        assert trade.entry_fee == Decimal('25.00')
        assert trade.exit_fee == Decimal('25.50')
        assert trade.base_currency == 'BTC'
        assert trade.quote_currency == 'USD'


def test_forex_trade_with_fees(app: Flask, test_setup):
    """Test forex trade with fees"""
    with app.app_context():
        plan = db.session.get(TradingPlan, test_setup['plan_id'])

        # Create EUR/USD trade
        trade = Trade(trading_plan_id=plan.id,
                      entry_price=Decimal('1.2000'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('100000'),
                      entry_fee=Decimal('5.00'),
                      timeframe='H1')

        db.session.add(trade)
        db.session.commit()

        # Refresh from database
        trade = db.session.get(Trade, trade.id)

        # Verify fees and currencies
        assert trade.entry_fee == Decimal('5.00')
        assert trade.exit_fee == 0  # Default value for incomplete trade
        assert trade.base_currency == 'EUR'
        assert trade.quote_currency == 'USD'


def test_trade_without_fees(app: Flask, test_setup):
    """Test trade creation with default fees"""
    with app.app_context():
        plan = db.session.get(TradingPlan, test_setup['plan_id'])

        trade = Trade(trading_plan_id=plan.id,
                      entry_price=Decimal('1.2000'),
                      entry_time=datetime.utcnow(),
                      symbol='EURUSD',
                      position_size=Decimal('100000'))

        db.session.add(trade)
        db.session.commit()

        # Refresh from database
        trade = db.session.get(Trade, trade.id)

        # Verify default fees
        assert trade.entry_fee == 0
        assert trade.exit_fee == 0


def test_trade_fee_precision(app: Flask, test_setup):
    """Test fee decimal precision handling"""
    with app.app_context():
        plan = db.session.get(TradingPlan, test_setup['plan_id'])

        trade = Trade(
            trading_plan_id=plan.id,
            entry_price=Decimal('50000.00'),
            entry_time=datetime.utcnow(),
            symbol='BTCUSD',
            position_size=Decimal('1.0'),
            entry_fee=Decimal('0.00123'),  # Test small fee precision
            exit_fee=Decimal('0.00456')
        )

        db.session.add(trade)
        db.session.commit()

        # Refresh from database
        trade = db.session.get(Trade, trade.id)

        # Verify fee precision is maintained
        assert trade.entry_fee == Decimal('0.00123')
        assert trade.exit_fee == Decimal('0.00456')
