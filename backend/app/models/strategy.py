from .base import BaseModel, GUID
from app import db


class Strategy(BaseModel):
    __tablename__ = 'strategies'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.JSON)
    performance_metrics = db.Column(db.JSON)

    # Relationships
    trades = db.relationship('Trade', back_populates='strategy', lazy=True)
    performances = db.relationship('Performance',
                                   back_populates='strategy',
                                   lazy=True,
                                   cascade='all, delete-orphan')
