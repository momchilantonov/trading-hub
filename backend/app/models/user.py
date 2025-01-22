from .base import BaseModel
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    profile_picture_updated_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')
    last_login = db.Column(db.DateTime)

    # Relationships
    trading_plans = db.relationship('TradingPlan',
                                    back_populates='user',
                                    lazy=True,
                                    cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return f"/static/profile_pictures/{self.profile_picture}"
        return "/static/profile_pictures/default.png"
