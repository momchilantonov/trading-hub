from .base import BaseModel, GUID
from app import db
from app.utils.validators import ImageValidator


class Journal(BaseModel):
    __tablename__ = 'journal_entries'

    trade_id = db.Column(GUID(),
                         db.ForeignKey('trades.id',
                                       ondelete='CASCADE'),
                         nullable=False)
    trading_plan_id = db.Column(GUID(),
                                db.ForeignKey('trading_plans.id',
                                              ondelete='CASCADE'),
                                nullable=False)
    notes = db.Column(db.Text)
    emotions = db.Column(db.String(50))
    market_conditions = db.Column(db.JSON)
    plan_adherence = db.Column(db.JSON)

    # Image fields - journal can have multiple images
    images = db.Column(db.JSON,
                       default=[])  # List of image URLs with descriptions
    # Example format:
    # [{
    #    "url": "path/to/image.jpg",
    #    "description": "Chart analysis",
    #    "type": "analysis",  # analysis, setup, result, etc.
    #    "upload_date": "2025-01-23T10:00:00Z"
    # }]

    # TODO: Ask for explanation!
    # Relationships
    trade = db.relationship('Trade', back_populates='journal_entry')
    trading_plan = db.relationship('TradingPlan',
                                   back_populates='journal_entries')

    def __setattr__(self, name, value):
        """Validate images before setting"""
        if name == 'images' and value is not None:
            ImageValidator.validate_image_list(value)
        super().__setattr__(name, value)
