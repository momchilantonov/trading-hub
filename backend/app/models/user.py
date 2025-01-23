from .mixins import PasswordMixin
from .base import BaseModel
from app.utils.validators import UserValidator
from app import db


class User(BaseModel, PasswordMixin):
    __tablename__ = 'users'

    email = db.Column(db.String(UserValidator.MAX_EMAIL_LENGTH),
                      unique=True,
                      nullable=False)
    username = db.Column(db.String(UserValidator.MAX_USERNAME_LENGTH),
                         unique=True,
                         nullable=False)
    password_hash = db.Column(db.String(256),
                              nullable=False)  # Required for PasswordMixin
    profile_picture = db.Column(db.String(255), nullable=True)
    profile_picture_updated_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')
    last_login = db.Column(db.DateTime)

    trading_plans = db.relationship('TradingPlan',
                                    back_populates='user',
                                    lazy=True)

    def __init__(self, **kwargs):
        if 'email' in kwargs:
            UserValidator.validate_email(kwargs['email'])
        if 'username' in kwargs:
            UserValidator.validate_username(kwargs['username'])
        super().__init__(**kwargs)
