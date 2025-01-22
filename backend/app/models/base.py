from datetime import datetime
import uuid
from app import db
from sqlalchemy.types import TypeDecorator, String


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses String(36) for SQLite and PostgreSQL
    """
    impl = String
    cache_ok = True

    def __init__(self, length=36, **kwargs):
        super(GUID, self).__init__(length, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, str):
            return str(uuid.UUID(value))
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class BaseModel(db.Model):
    """Base model class that includes GUID column"""
    __abstract__ = True

    id = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)
