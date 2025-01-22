from .base import BaseModel, GUID
from app import db


class Performance(BaseModel):
    __tablename__ = 'performance_metrics'

    strategy_id = db.Column(GUID(),
                            db.ForeignKey('strategies.id',
                                          ondelete='CASCADE'),
                            nullable=False)
    trading_plan_id = db.Column(GUID(),
                                db.ForeignKey('trading_plans.id',
                                              ondelete='CASCADE'),
                                nullable=False)
    metrics = db.Column(db.JSON)
    timeframe = db.Column(db.String(10), nullable=False)
    period = db.Column(db.String(20), nullable=False)

    # Relationships
    strategy = db.relationship('Strategy', back_populates='performances')
    trading_plan = db.relationship('TradingPlan',
                                   back_populates='performances')
