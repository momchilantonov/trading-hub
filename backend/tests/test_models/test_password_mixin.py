from flask import Flask
import pytest
from marshmallow.exceptions import ValidationError
from app import db
from app.models import User


def test_password_hashing(app: Flask):
    """Test basic password hashing functionality"""
    with app.app_context():
        user = User(email='test@example.com', username='testuser')
        password = 'TestPass123!'

        # Set password
        user.set_password(password)
        assert user.password_hash is not None
        assert password not in user.password_hash  # Hash shouldn't contain original password

        # Check password
        assert user.check_password(password) is True
        assert user.check_password('WrongPass123!') is False


def test_password_validation(app: Flask):
    """Test password validation during setting"""
    with app.app_context():
        user = User(email='test@example.com', username='testuser')

        # Test weak passwords
        weak_passwords = [
            'short1!',       # Too short
            'nouppercase1!', # No uppercase
            'NOLOWERCASE1!', # No lowercase
            'NoSpecialChar1' # No special character
        ]

        for password in weak_passwords:
            with pytest.raises(ValidationError):
                user.set_password(password)


def test_password_change(app: Flask):
    """Test password change functionality"""
    with app.app_context():
        user = User(email='test@example.com', username='testuser')
        original_password = 'OriginalPass123!'
        new_password = 'NewPass123!'

        # Set initial password
        user.set_password(original_password)
        assert user.check_password(original_password)

        # Change password
        user.change_password(original_password, new_password)
        assert user.check_password(new_password)
        assert not user.check_password(original_password)

        # Test wrong old password
        with pytest.raises(ValidationError):
            user.change_password('WrongPass123!', 'NewerPass123!')


def test_password_state(app: Flask):
    """Test password state checking"""
    with app.app_context():
        user = User(email='test@example.com', username='testuser')

        # Initial state
        assert not user.has_password

        # After setting password
        user.set_password('TestPass123!')
        assert user.has_password

        # Verify hash is properly stored
        db.session.add(user)
        db.session.commit()

        # Fetch fresh instance
        fresh_user = db.session.get(User, user.id)
        assert fresh_user.has_password


def test_bypass_validation(app: Flask):
    """Test setting password without validation"""
    with app.app_context():
        user = User(email='test@example.com', username='testuser')

        # Set weak password with validation bypassed
        weak_password = 'weak'
        user.set_password(weak_password, validate=False)
        assert user.check_password(weak_password)


def test_multiple_password_changes(app: Flask):
    """Test multiple password changes"""
    with app.app_context():
        user = User(email='test@example.com', username='testuser')
        passwords = ['TestPass123!', 'NewPass123!', 'FinalPass123!']

        for i, password in enumerate(passwords):
            if i == 0:
                user.set_password(password)
            else:
                user.change_password(passwords[i - 1], password)

            assert user.check_password(password)
            db.session.add(user)
            db.session.commit()
