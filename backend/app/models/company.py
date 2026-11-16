"""Company organization profile model."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Company(Base, TimestampMixin):
    """Company / Organization profile offering internships under the scheme."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    location = Column(String(150), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="company")
    internships = relationship("Internship", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company id={self.id} name='{self.company_name}' industry='{self.industry}'>"
