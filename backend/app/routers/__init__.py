"""API routers registration."""

from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.students import router as students_router
from app.routers.companies import router as companies_router
from app.routers.internships import router as internships_router
from app.routers.matching import router as matching_router
from app.routers.applications import router as applications_router
from app.routers.allocations import router as allocations_router
from app.routers.analytics import router as analytics_router

__all__ = [
    "health_router",
    "auth_router",
    "students_router",
    "companies_router",
    "internships_router",
    "matching_router",
    "applications_router",
    "allocations_router",
    "analytics_router",
]
