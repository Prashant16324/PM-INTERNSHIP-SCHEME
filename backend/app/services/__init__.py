"""Business services registration and exports."""

from app.services.auth_service import AuthService
from app.services.student_service import StudentService
from app.services.internship_service import InternshipService
from app.services.resume_service import ResumeService
from app.services.matching_service import MatchingEngine
from app.services.application_service import ApplicationService
from app.services.allocation_service import AllocationEngine
from app.services.analytics_service import AnalyticsService

__all__ = [
    "AuthService",
    "StudentService",
    "InternshipService",
    "ResumeService",
    "MatchingEngine",
    "ApplicationService",
    "AllocationEngine",
    "AnalyticsService",
]
