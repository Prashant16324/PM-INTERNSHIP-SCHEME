"""Base model and reusable timestamp mixins for SQLAlchemy."""

from datetime import datetime
from sqlalchemy import Column, DateTime, func


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Record creation timestamp"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last record update timestamp"
    )
