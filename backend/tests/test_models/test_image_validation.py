from flask import Flask
from datetime import datetime
import pytest
from marshmallow.exceptions import ValidationError
from app import db
from app.models import Trade, Journal, Strategy, TradingPlan
from app.utils.validators import ImageValidator
from decimal import Decimal


def test_valid_image_url(app: Flask):
    """Test valid image URL validation"""
    with app.app_context():
        valid_urls = [
            '/static/trades/image1.png',
            '/static/journal/analysis_1.jpg',
            '/static/strategy/example-1.jpeg',
            '/static/plans/risk-management.gif'
        ]

        for url in valid_urls:
            assert ImageValidator.validate_image_url(url) is True


def test_invalid_image_url(app: Flask):
    """Test invalid image URL validation"""
    with app.app_context():
        invalid_urls = [
            'http://external-site.com/image.png',  # External URL
            '/static/image.bmp',                   # Invalid extension
            'static/image.png',                    # Missing leading slash
            '/static/invalid<chars>.png',          # Invalid characters
            'a' * 256                              # Too long
        ]

        for url in invalid_urls:
            with pytest.raises(ValidationError):
                ImageValidator.validate_image_url(url)


def test_valid_image_list(app: Flask):
    """Test valid image list validation"""
    with app.app_context():
        valid_images = [{
            'url': '/static/test/image1.png',
            'description': 'Test image',
            'upload_date': datetime.utcnow().isoformat()
        }]

        assert ImageValidator.validate_image_list(valid_images) is True


def test_invalid_image_list(app: Flask):
    """Test invalid image list validation"""
    with app.app_context():
        # Missing required field
        with pytest.raises(ValidationError):
            ImageValidator.validate_image_list([{
                'url': '/static/test/image1.png',
                'description': 'Test image'
                # missing upload_date
            }])

        # Invalid URL in list
        with pytest.raises(ValidationError):
            ImageValidator.validate_image_list([{
                'url':
                'invalid-url',
                'description':
                'Test image',
                'upload_date':
                datetime.utcnow().isoformat()
            }])

        # Invalid date format
        with pytest.raises(ValidationError):
            ImageValidator.validate_image_list([{
                'url': '/static/test/image1.png',
                'description': 'Test image',
                'upload_date': 'invalid-date'
            }])


def test_model_image_validation(app: Flask, test_setup):
    """Test image validation in models"""
    with app.app_context():
        plan = db.session.get(TradingPlan, test_setup['plan_id'])

        # Test Trade model validation
        with pytest.raises(ValidationError):
            trade = Trade(
                trading_plan_id=plan.id,
                entry_price=Decimal('1.2000'),
                entry_time=datetime.utcnow(),
                symbol='EURUSD',
                position_size=Decimal('100000'),
                entry_image_url='invalid-url'  # Invalid URL
            )

        # Test Journal model validation
        with pytest.raises(ValidationError):
            journal = Journal(
                trade_id=test_setup['trade_id'],
                trading_plan_id=plan.id,
                images=[{
                    'url': '/static/test/image1.png',
                    'description': 'Test image'
                    # Missing upload_date
                }])

        # Test Strategy model validation
        with pytest.raises(ValidationError):
            strategy = Strategy(
                name="Test Strategy",
                strategy_image_url=
                'http://external-site.com/image.png'  # Invalid external URL
            )

        # Test TradingPlan model validation
        with pytest.raises(ValidationError):
            plan = TradingPlan(
                user_id=test_setup['user_id'],
                name="Test Plan",
                type="day_trading",
                plan_images=[{
                    'url': '/static/test/image1.bmp',  # Invalid extension
                    'description': 'Test image',
                    'upload_date': datetime.utcnow().isoformat()
                }]
            )
