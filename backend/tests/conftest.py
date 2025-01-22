import sys
import os
import pytest

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

from app import create_app, db
from app.models.user import User
from config.testing import TestingConfig  # Direct import of TestingConfig


@pytest.fixture
def app():
    """Create test app instance"""
    app = create_app(
        TestingConfig)  # Pass the class directly instead of string

    # Create test profile pictures directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('static/profile_pictures'):
        os.makedirs('static/profile_pictures')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create test user"""
    with app.app_context():
        user = User(email='test@example.com', username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user
