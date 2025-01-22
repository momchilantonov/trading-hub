from .base import BaseModel, GUID
from app import db


class Trade(BaseModel):
    __tablename__ = 'trades'

    trading_plan_id = db.Column(GUID(),
                                db.ForeignKey('trading_plans.id'),
                                nullable=False)
    strategy_id = db.Column(GUID(),
                            db.ForeignKey('strategies.id'),
                            nullable=True)
    entry_price = db.Column(db.Numeric, nullable=False)
    exit_price = db.Column(db.Numeric)
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime)
    symbol = db.Column(db.String(10), nullable=False)
    position_size = db.Column(db.Numeric, nullable=False)
    timeframe = db.Column(db.String(5))

    # Relationships
    trading_plan = db.relationship('TradingPlan', back_populates='trades')
    strategy = db.relationship('Strategy', back_populates='trades')
    journal_entry = db.relationship('Journal',
                                    back_populates='trade',
                                    uselist=False,
                                    cascade='all, delete-orphan')
