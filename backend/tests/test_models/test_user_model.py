import sys
import os
import pytest

# Add the backend directory to the Python path
sys.path.insert(
    0,
    os.path.abspath(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__)))))

from app import db
from app.models.user import User


def test_create_user(app):
    """Test user creation"""
    with app.app_context():
        user = User(email='new@example.com', username='newuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.email == 'new@example.com'
        assert user.username == 'newuser'
        assert user.check_password('password123')
        assert user.profile_picture_url == '/static/profile_pictures/default.png'


def test_user_profile_picture(app):
    """Test profile picture functionality"""
    with app.app_context():
        user = User(email='pic@example.com',
                    username='picuser',
                    profile_picture='test.jpg')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        assert user.profile_picture == 'test.jpg'
        assert user.profile_picture_url == '/static/profile_pictures/test.jpg'
