"""SQLAlchemy models registration and exports."""

from app.database import Base
from app.models.base import TimestampMixin
from app.models.user import User, UserRole
from app.models.student import StudentProfile, StudentSkill
from app.models.company import Company
from app.models.internship import Internship, InternshipSkill, InternshipStatus
from app.models.application import Application, ApplicationStatus
from app.models.allocation import Allocation, AllocationStatus, Recommendation
from app.models.audit_log import AuditLog, ResumeFile

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "UserRole",
    "StudentProfile",
    "StudentSkill",
    "Company",
    "Internship",
    "InternshipSkill",
    "InternshipStatus",
    "Application",
    "ApplicationStatus",
    "Allocation",
    "AllocationStatus",
    "Recommendation",
    "AuditLog",
    "ResumeFile",
]
