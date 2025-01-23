from .base import BaseModel, GUID
from app import db
from app.utils.validators import ImageValidator


class Strategy(BaseModel):
    __tablename__ = 'strategies'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.JSON)
    performance_metrics = db.Column(db.JSON)

    # Image fields
    strategy_image_url = db.Column(
        db.String(255))  # Main strategy illustration
    example_images = db.Column(db.JSON, default=[])  # Example setups/patterns

    # Relationships
    trades = db.relationship('Trade', back_populates='strategy', lazy=True)
    performances = db.relationship('Performance',
                                   back_populates='strategy',
                                   lazy=True,
                                   cascade='all, delete-orphan')

    def __setattr__(self, name, value):
        """Validate images before setting"""
        if name == 'strategy_image_url' and value is not None:
            ImageValidator.validate_image_url(value)
        elif name == 'example_images' and value is not None:
            ImageValidator.validate_image_list(value)
        super().__setattr__(name, value)
