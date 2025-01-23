from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow.exceptions import ValidationError
from app.utils.validators import UserValidator


class PasswordMixin:
    """Mixin for models that require password functionality"""

    password_hash = None  # Must be defined in the model

    def set_password(self, password: str, validate: bool = True):
        """
        Set password with optional validation
        Args:
            password: Password string
            validate: Whether to validate password against rules
        """
        if validate:
            UserValidator.validate_password(password)

        if not hasattr(self, 'password_hash'):
            raise AttributeError(
                f"Model {self.__class__.__name__} must define password_hash column"
            )

        # Use stronger hashing method and more iterations for production
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256:100000'  # More secure hashing
        )

    def check_password(self, password: str) -> bool:
        """Check if provided password matches the hash"""
        if not self.password_hash:
            raise ValidationError("Password not set")
        return check_password_hash(self.password_hash, password)

    def change_password(self, old_password: str, new_password: str):
        """
        Change password with validation
        Args:
            old_password: Current password
            new_password: New password
        """
        if not self.check_password(old_password):
            raise ValidationError("Current password is incorrect")

        self.set_password(new_password)

    @property
    def has_password(self) -> bool:
        """Check if password is set"""
        return bool(self.password_hash)
