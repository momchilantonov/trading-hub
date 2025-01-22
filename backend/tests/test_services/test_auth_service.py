from app.services.auth_service import AuthService
from app.utils.exceptions import AuthenticationError
import pytest


def test_register_user_service(app):
    """Test user registration through service"""
    with app.app_context():
        user = AuthService.register_user(email='service@example.com',
                                         username='serviceuser',
                                         password='password123')

        assert user.id is not None
        assert user.email == 'service@example.com'
        assert user.username == 'serviceuser'
        assert user.is_active == True


def test_login_user_service(app, test_user):
    """Test user login through service"""
    with app.app_context():
        auth_data = AuthService.login_user(email='test@example.com',
                                           password='password123')

        assert 'access_token' in auth_data
        assert 'refresh_token' in auth_data
        assert auth_data['user']['email'] == test_user.email


def test_login_invalid_user_service(app):
    """Test login with invalid user through service"""
    with app.app_context():
        with pytest.raises(AuthenticationError):
            AuthService.login_user(email='nonexistent@example.com',
                                   password='password123')
