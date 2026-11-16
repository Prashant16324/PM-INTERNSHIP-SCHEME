"""Internship posting and required skills models."""

import enum
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class InternshipStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class Internship(Base, TimestampMixin):
    """Internship opportunity record posted by companies or scheme admins."""
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(150), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    duration_weeks = Column(Integer, default=8, nullable=False)
    stipend = Column(Float, default=0.0, nullable=False)
    total_seats = Column(Integer, default=1, nullable=False)
    available_seats = Column(Integer, default=1, nullable=False)
    min_cgpa = Column(Float, default=0.0, nullable=False)
    preferred_education = Column(String(255), nullable=True)  # e.g., "B.Tech, BCA, MCA"
    eligibility_criteria = Column(Text, nullable=True)
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(InternshipStatus, name="internship_status_enum", native_enum=False), default=InternshipStatus.OPEN, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="internships")
    skills = relationship("InternshipSkill", back_populates="internship", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="internship", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="internship", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="internship", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Internship id={self.id} title='{self.title}' company_id={self.company_id} seats={self.available_seats}/{self.total_seats}>"


class InternshipSkill(Base, TimestampMixin):
    """Normalized technical and foundational skills required for an internship."""
    __tablename__ = "internship_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)

    __table_args__ = (
        UniqueConstraint("internship_id", "skill_name", name="uq_internship_skill"),
    )

    # Relationships
    internship = relationship("Internship", back_populates="skills")

    def __repr__(self) -> str:
        return f"<InternshipSkill id={self.id} internship_id={self.internship_id} skill='{self.skill_name}' mandatory={self.is_mandatory}>"
