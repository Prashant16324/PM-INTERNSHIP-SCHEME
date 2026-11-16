"""Student internship application model."""

import enum
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, UniqueConstraint, Enum, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    SELECTED = "SELECTED"
    ALLOCATED = "ALLOCATED"
    WITHDRAWN = "WITHDRAWN"


class Application(Base, TimestampMixin):
    """Internship application submitted by a student candidate."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        Enum(ApplicationStatus, name="application_status_enum", native_enum=False),
        default=ApplicationStatus.SUBMITTED,
        nullable=False,
        index=True
    )
    match_score = Column(Float, default=0.0, nullable=False)
    cover_letter = Column(Text, nullable=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_profile_id", "internship_id", name="uq_student_internship_app"),
    )

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="applications")
    internship = relationship("Internship", back_populates="applications")
    allocation = relationship("Allocation", back_populates="application", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Application id={self.id} student_id={self.student_profile_id} internship_id={self.internship_id} status='{self.status}'>"
