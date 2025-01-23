from flask import Flask
import pytest
from marshmallow.exceptions import ValidationError
from app import db
from app.models import User
from app.utils.validators import UserValidator


def test_valid_email_formats(app: Flask):
    """Test valid email formats"""
    with app.app_context():
        valid_emails = [
            'user@example.com',
            'user.name@example.com',
            'user+label@example.com',
            'user@subdomain.example.com'
        ]

        for email in valid_emails:
            assert UserValidator.validate_email(email) is True


def test_invalid_email_formats(app: Flask):
    """Test invalid email formats"""
    with app.app_context():
        invalid_emails = [
            '',                    # Empty
            'notanemail',         # No @
            '@nodomain.com',      # No username
            'no spaces@test.com', # Contains space
            'a' * 121 + '@test.com'  # Too long
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError):
                UserValidator.validate_email(email)


def test_valid_username_formats(app: Flask):
    """Test valid username formats"""
    with app.app_context():
        valid_usernames = ['john123', 'john_doe', 'john-doe', 'johndoe']

        for username in valid_usernames:
            assert UserValidator.validate_username(username) is True


def test_invalid_username_formats(app: Flask):
    """Test invalid username formats"""
    with app.app_context():
        invalid_usernames = [
            '',              # Empty
            'ab',           # Too short
            '123john',      # Starts with number
            'john@doe',     # Invalid character
            'a' * 81       # Too long
        ]

        for username in invalid_usernames:
            with pytest.raises(ValidationError):
                UserValidator.validate_username(username)


def test_valid_password_formats(app: Flask):
    """Test valid password formats"""
    with app.app_context():
        valid_passwords = ['Test123!@', 'SecurePass123$', 'MyP@ssw0rd']

        for password in valid_passwords:
            assert UserValidator.validate_password(password) is True


def test_invalid_password_formats(app: Flask):
    """Test invalid password formats"""
    with app.app_context():
        invalid_passwords = [
            '',              # Empty
            'short1!',       # Too short
            'nouppercase1!', # No uppercase
            'NOLOWERCASE1!', # No lowercase
            'NoNumbers!',    # No numbers
            'NoSpecial1',    # No special characters
            'a' * 129       # Too long
        ]

        for password in invalid_passwords:
            with pytest.raises(ValidationError):
                UserValidator.validate_password(password)


def test_user_creation_with_validation(app: Flask):
    """Test user creation with validation"""
    with app.app_context():
        # Valid user creation
        user = User(email='test@example.com', username='testuser')
        user.set_password('SecurePass123!')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.check_password('SecurePass123!')

        # Invalid email
        with pytest.raises(ValidationError):
            User(email='invalid', username='testuser2')

        # Invalid username
        with pytest.raises(ValidationError):
            User(email='test2@example.com', username='123user')

        # Invalid password
        user2 = User(email='test2@example.com', username='testuser2')
        with pytest.raises(ValidationError):
            user2.set_password('weak')


def test_unique_constraints(app: Flask):
    """Test unique constraints for email and username"""
    with app.app_context():
        user1 = User(email='test@example.com', username='testuser')
        user1.set_password('SecurePass123!')
        db.session.add(user1)
        db.session.commit()

        # Try to create user with same email
        with pytest.raises(
                Exception):  # SQLAlchemy will raise an integrity error
            user2 = User(
                email='test@example.com',  # Same email
                username='different'
            )
            user2.set_password('SecurePass123!')
            db.session.add(user2)
            db.session.commit()

        # Try to create user with same username
        with pytest.raises(Exception):
            user3 = User(
                email='different@example.com',
                username='testuser'  # Same username
            )
            user3.set_password('SecurePass123!')
            db.session.add(user3)
            db.session.commit()
