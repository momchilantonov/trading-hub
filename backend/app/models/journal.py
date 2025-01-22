from .base import BaseModel, GUID
from app import db


class Journal(BaseModel):
    __tablename__ = 'journal_entries'

    trade_id = db.Column(GUID(),
                         db.ForeignKey('trades.id',
                                       ondelete='CASCADE'),
                         nullable=False)
    trading_plan_id = db.Column(GUID(),
                                db.ForeignKey('trading_plans.id'),
                                nullable=False)
    notes = db.Column(db.Text)
    emotions = db.Column(db.String(50))
    market_conditions = db.Column(db.JSON)
    plan_adherence = db.Column(db.JSON)

    # Relationships
    trade = db.relationship('Trade', back_populates='journal_entry')
    trading_plan = db.relationship('TradingPlan',
                                   back_populates='journal_entries')
