from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token
from app import db
from app.models.user import User
from app.utils.exceptions import AuthenticationError


class AuthService:

    @staticmethod
    def register_user(email, username, password):
        if User.query.filter_by(email=email).first():
            raise AuthenticationError("Email already registered")
        if User.query.filter_by(username=username).first():
            raise AuthenticationError("Username already taken")

        user = User(email=email, username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        user.last_login = datetime.utcnow()
        db.session.commit()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'role': user.role
            }
        }
