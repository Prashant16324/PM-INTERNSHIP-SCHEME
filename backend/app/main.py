"""FastAPI Application Entry Point for PM Internship Scheme Smart Allocation Engine."""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base, SessionLocal
import app.models  # Ensure all models are registered with Base.metadata
from app.services.auth_service import AuthService
from app.routers import (
    health_router,
    auth_router,
    students_router,
    companies_router,
    internships_router,
    matching_router,
    applications_router,
    allocations_router,
    analytics_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pm_internship_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events: startup initialization and graceful shutdown."""
    logger.info("Initializing PM Internship Scheme Smart Allocation Backend...")

    # Ensure tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Seed initial super admin if missing
    try:
        db = SessionLocal()
        AuthService.seed_initial_admin(db)
        db.close()
    except Exception as e:
        logger.error(f"Error seeding initial administrator: {e}")

    yield

    logger.info("Shutting down PM Internship Scheme Smart Allocation Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Academic prototype of an AI-powered internship recommendation and smart allocation platform "
        "designed for the PM Internship Scheme. Provides explainable matching scores, role-based "
        "access control, resume skill gap analysis, and fairness-aware seat allocation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred. Please contact the administrator.",
            "error_detail": str(exc) if settings.DEBUG else None
        }
    )


# Root diagnostic endpoint
@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": f"{settings.API_V1_STR}/health",
        "status": "online"
    }


# Mount Routers under API_V1_STR
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(students_router, prefix=settings.API_V1_STR)
app.include_router(companies_router, prefix=settings.API_V1_STR)
app.include_router(internships_router, prefix=settings.API_V1_STR)
app.include_router(matching_router, prefix=settings.API_V1_STR)
app.include_router(applications_router, prefix=settings.API_V1_STR)
app.include_router(allocations_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
