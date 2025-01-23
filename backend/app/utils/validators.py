from marshmallow import Schema, fields, validate
from datetime import datetime
import re
from typing import List, Dict, Optional
from marshmallow.exceptions import ValidationError
from datetime import datetime


class RegistrationSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True,
                          validate=validate.Length(min=3,
                                                   max=80))
    password = fields.Str(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


def validate_registration(data):
    schema = RegistrationSchema()
    return schema.load(data)


def validate_login(data):
    schema = LoginSchema()
    return schema.load(data)


class ImageValidator:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_URL_LENGTH = 255
    VALID_URL_PATTERN = r'^/static/[a-zA-Z0-9/_-]+\.(png|jpg|jpeg|gif)$'

    @classmethod
    def validate_image_url(cls, url: str) -> bool:
        """Validate a single image URL"""
        if not url or len(url) > cls.MAX_URL_LENGTH:
            raise ValidationError("Image URL is empty or too long")

        if not re.match(cls.VALID_URL_PATTERN, url):
            raise ValidationError("Invalid image URL format")

        extension = url.split('.')[-1].lower()
        if extension not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Invalid image extension. Allowed: {cls.ALLOWED_EXTENSIONS}")

        return True

    @classmethod
    def validate_image_list(cls, images: List[Dict]) -> bool:
        """Validate a list of image objects"""
        if not isinstance(images, list):
            raise ValidationError("Images must be provided as a list")

        for img in images:
            if not isinstance(img, dict):
                raise ValidationError("Each image must be a dictionary")

            required_fields = {'url', 'description', 'upload_date'}
            if not all(field in img for field in required_fields):
                raise ValidationError(
                    f"Image missing required fields: {required_fields}")

            cls.validate_image_url(img['url'])

            # Validate upload date
            try:
                datetime.fromisoformat(img['upload_date'])
            except ValueError:
                raise ValidationError("Invalid upload date format")

        return True

    import re


class UserValidator:
    # Email validation
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    MIN_EMAIL_LENGTH = 5
    MAX_EMAIL_LENGTH = 120

    # Username validation
    USERNAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 80

    # Password validation
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Validate email format and length
        Rules:
        - Must be a valid email format
        - Length between MIN_EMAIL_LENGTH and MAX_EMAIL_LENGTH
        - Must not contain dangerous characters
        """
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required and must be a string")

        if not cls.MIN_EMAIL_LENGTH <= len(email) <= cls.MAX_EMAIL_LENGTH:
            raise ValidationError(
                f"Email must be between {cls.MIN_EMAIL_LENGTH} and {cls.MAX_EMAIL_LENGTH} characters"
            )

        if not re.match(cls.EMAIL_PATTERN, email):
            raise ValidationError("Invalid email format")

        return True

    @classmethod
    def validate_username(cls, username: str) -> bool:
        """
        Validate username format and length
        Rules:
        - Only alphanumeric characters, underscores, and hyphens
        - Length between MIN_USERNAME_LENGTH and MAX_USERNAME_LENGTH
        - Must start with a letter
        """
        if not username or not isinstance(username, str):
            raise ValidationError("Username is required and must be a string")

        if not cls.MIN_USERNAME_LENGTH <= len(
                username) <= cls.MAX_USERNAME_LENGTH:
            raise ValidationError(
                f"Username must be between {cls.MIN_USERNAME_LENGTH} and {cls.MAX_USERNAME_LENGTH} characters"
            )

        if not username[0].isalpha():
            raise ValidationError("Username must start with a letter")

        if not re.match(cls.USERNAME_PATTERN, username):
            raise ValidationError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        return True

    @classmethod
    def validate_password(cls, password: str) -> bool:
        """
        Validate password strength
        Rules:
        - Minimum length of 8 characters
        - Maximum length of 128 characters
        - Must contain at least one uppercase letter
        - Must contain at least one lowercase letter
        - Must contain at least one number
        - Must contain at least one special character
        """
        if not password or not isinstance(password, str):
            raise ValidationError("Password is required and must be a string")

        if not cls.MIN_PASSWORD_LENGTH <= len(
                password) <= cls.MAX_PASSWORD_LENGTH:
            raise ValidationError(
                f"Password must be between {cls.MIN_PASSWORD_LENGTH} and {cls.MAX_PASSWORD_LENGTH} characters"
            )

        if not any(c.isupper() for c in password):
            raise ValidationError(
                "Password must contain at least one uppercase letter")

        if not any(c.islower() for c in password):
            raise ValidationError(
                "Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one number")

        if not any(c in '@$!%*?&' for c in password):
            raise ValidationError(
                "Password must contain at least one special character (@$!%*?&)"
            )

        return True
