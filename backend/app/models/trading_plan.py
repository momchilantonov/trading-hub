from .base import BaseModel, GUID
from app import db
from app.utils.validators import ImageValidator


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

    # Image fields
    plan_images = db.Column(db.JSON, default=[])  # Documentation images

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

    def __setattr__(self, name, value):
        """Validate images before setting"""
        if name == 'plan_images' and value is not None:
            ImageValidator.validate_image_list(value)
        super().__setattr__(name, value)
