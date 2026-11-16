"""Student profile and student skills models."""

from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class StudentProfile(Base, TimestampMixin):
    """Detailed academic and professional profile of a student."""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    college_name = Column(String(255), nullable=True)
    degree = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    cgpa = Column(Float, nullable=True)
    profile_completion_percentage = Column(Integer, default=0, nullable=False)
    preferred_locations = Column(JSON, default=list, nullable=False)
    preferred_industries = Column(JSON, default=list, nullable=False)
    resume_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    skills = relationship("StudentSkill", back_populates="student_profile", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student_profile", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student_profile", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="student_profile", cascade="all, delete-orphan")
    resume_files = relationship("ResumeFile", back_populates="student_profile", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudentProfile id={self.id} user_id={self.user_id} degree='{self.degree}'>"


class StudentSkill(Base, TimestampMixin):
    """Normalized technical and soft skills attached to a student profile."""
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    proficiency_level = Column(String(50), default="INTERMEDIATE", nullable=False)  # BEGINNER, INTERMEDIATE, ADVANCED
    source = Column(String(50), default="MANUAL", nullable=False)  # MANUAL, RESUME_EXTRACTED

    # Unique constraint per student and skill
    __table_args__ = (
        UniqueConstraint("student_profile_id", "skill_name", name="uq_student_skill"),
    )

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="skills")

    def __repr__(self) -> str:
        return f"<StudentSkill id={self.id} student_id={self.student_profile_id} skill='{self.skill_name}'>"
