"""Allocation decisions and AI recommendation models."""

import enum
from sqlalchemy import Column, Integer, Float, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Enum, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class AllocationStatus(str, enum.Enum):
    PROVISIONAL = "PROVISIONAL"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    REJECTED_BY_STUDENT = "REJECTED_BY_STUDENT"


class Allocation(Base, TimestampMixin):
    """Final or provisional seat allocation result for a candidate in an internship."""
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True)
    allocation_round = Column(Integer, default=1, nullable=False)
    allocated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    allocation_score = Column(Float, nullable=False)
    status = Column(
        Enum(AllocationStatus, name="allocation_status_enum", native_enum=False),
        default=AllocationStatus.PROVISIONAL,
        nullable=False,
        index=True
    )
    allocation_reason = Column(Text, nullable=True)
    allocated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    application = relationship("Application", back_populates="allocation")
    student_profile = relationship("StudentProfile", back_populates="allocations")
    internship = relationship("Internship", back_populates="allocations")
    allocated_by_user = relationship("User", foreign_keys=[allocated_by_user_id])

    def __repr__(self) -> str:
        return f"<Allocation id={self.id} student_id={self.student_profile_id} internship_id={self.internship_id} score={self.allocation_score}>"


class Recommendation(Base, TimestampMixin):
    """Explainable AI-generated recommendation cache linking student to internship."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    skill_score = Column(Float, default=0.0, nullable=False)
    education_score = Column(Float, default=0.0, nullable=False)
    location_score = Column(Float, default=0.0, nullable=False)
    industry_score = Column(Float, default=0.0, nullable=False)
    is_eligible = Column(Boolean, default=True, nullable=False)
    explanation = Column(Text, nullable=True)
    matched_skills = Column(JSON, default=list, nullable=False)
    missing_skills = Column(JSON, default=list, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_profile_id", "internship_id", name="uq_student_internship_rec"),
    )

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="recommendations")
    internship = relationship("Internship", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<Recommendation student_id={self.student_profile_id} internship_id={self.internship_id} score={self.overall_score}>"
