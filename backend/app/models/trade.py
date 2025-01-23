from .base import BaseModel, GUID
from app import db
from decimal import Decimal
from app.utils.validators import ImageValidator


class Trade(BaseModel):
    __tablename__ = 'trades'

    trading_plan_id = db.Column(GUID(),
                                db.ForeignKey('trading_plans.id'),
                                nullable=False)
    strategy_id = db.Column(GUID(),
                            db.ForeignKey('strategies.id'),
                            nullable=True)

    # Core trade data
    entry_price = db.Column(db.Numeric, nullable=False)
    exit_price = db.Column(db.Numeric)
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime)
    symbol = db.Column(db.String(10),
                       nullable=False)  # e.g., 'BTCUSD', 'EURUSD'
    position_size = db.Column(db.Numeric, nullable=False)
    timeframe = db.Column(db.String(5))

    # Fee Structure
    entry_fee = db.Column(db.Numeric, nullable=False, default=0)
    exit_fee = db.Column(db.Numeric, default=0)

    # Image fields
    entry_image_url = db.Column(
        db.String(255))  # URL to entry setup/chart image
    exit_image_url = db.Column(db.String(255))  # URL to exit setup/chart image

    # Relationships
    trading_plan = db.relationship('TradingPlan', back_populates='trades')
    strategy = db.relationship('Strategy', back_populates='trades')
    journal_entry = db.relationship('Journal',
                                    back_populates='trade',
                                    uselist=False,
                                    cascade='all, delete-orphan')

    @property
    def base_currency(self):
        """Get the base currency (first part of the pair)"""
        return self.symbol[:3] if self.symbol else None

    @property
    def quote_currency(self):
        """Get the quote currency (second part of the pair)"""
        return self.symbol[3:] if self.symbol else None

    def __setattr__(self, name, value):
        """Validate image URLs before setting"""
        if name in ['entry_image_url', 'exit_image_url'] and value is not None:
            ImageValidator.validate_image_url(value)
        super().__setattr__(name, value)
