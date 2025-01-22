from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from celery import Celery
import redis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()
celery = Celery()


def create_app(config_object="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    socketio.init_app(app)

    # Initialize Redis
    app.redis = redis.from_url(app.config["REDIS_URL"])

    # Initialize Celery
    celery.conf.update(app.config)

    # Register blueprints
    from .routes import register_routes

    register_routes(app)

    return app
