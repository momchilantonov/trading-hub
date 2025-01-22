from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services.auth_service import AuthService
from app.utils.validators import validate_registration, validate_login
from app.utils.exceptions import AuthenticationError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        validate_registration(data)

        user = AuthService.register_user(email=data['email'],
                                         username=data['username'],
                                         password=data['password'])

        return jsonify({
            'message': 'Registration successful',
            'user_id': str(user.id)
        }), 201

    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        validate_login(data)

        auth_data = AuthService.login_user(email=data['email'],
                                           password=data['password'])

        return jsonify(auth_data), 200

    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'error': 'Token refresh failed'}), 500
