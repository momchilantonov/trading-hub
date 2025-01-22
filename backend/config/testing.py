import os
from datetime import timedelta


class TestingConfig:
    DEBUG = False
    TESTING = True

    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security (simplified for testing)
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Redis and Celery (use eager mode for testing)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False

    # Testing-specific settings
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_ENABLED = False

    # In-memory Redis for testing
    REDIS_URL = "redis://localhost:6379/1"

    # CORS (allow all for testing)
    CORS_ORIGINS = ["*"]

    # Disable logging in tests
    LOG_LEVEL = "ERROR"
