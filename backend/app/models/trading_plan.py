from .base import BaseModel, GUID
from app import db


class TradingPlan(BaseModel):
    __tablename__ = 'trading_plans'

    user_id = db.Column(GUID(), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    risk_management = db.Column(db.JSON)
    entry_rules = db.Column(db.JSON)
    exit_rules = db.Column(db.JSON)
    timeframes = db.Column(db.JSON)
    position_sizing = db.Column(db.JSON)
    markets = db.Column(db.JSON)
    notes = db.Column(db.Text)
    version = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    user = db.relationship('User', back_populates='trading_plans')
    trades = db.relationship('Trade',
                             back_populates='trading_plan',
                             lazy=True,
                             cascade='all, delete-orphan')
    journal_entries = db.relationship('Journal',
                                      back_populates='trading_plan',
                                      lazy=True,
                                      cascade='all, delete-orphan')
    performances = db.relationship('Performance',
                                   back_populates='trading_plan',
                                   lazy=True,
                                   cascade='all, delete-orphan')
