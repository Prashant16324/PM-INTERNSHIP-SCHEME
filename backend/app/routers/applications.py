"""Internship applications and candidate tracking router."""

from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_student, require_admin_or_company, get_current_user
from app.models.user import User
from app.models.application import ApplicationStatus
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationOut,
)
from app.services.application_service import ApplicationService
from app.services.student_service import StudentService

router = APIRouter(prefix="/applications", tags=["Internship Applications"])


@router.post("", response_model=APIResponse[ApplicationOut], status_code=status.HTTP_201_CREATED)
def apply_to_internship(
    payload: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Submit an application to an open internship opportunity."""
    profile = StudentService.get_profile_by_user(db, current_user)
    application = ApplicationService.apply_for_internship(db, profile, payload)
    return APIResponse(
        success=True,
        message="Application submitted successfully",
        data=ApplicationOut.model_validate(application)
    )


@router.get("/me", response_model=APIResponse[List[ApplicationOut]])
def get_my_applications(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """View application history and current statuses for the logged-in student."""
    profile = StudentService.get_profile_by_user(db, current_user)
    applications = ApplicationService.list_student_applications(db, profile)
    return APIResponse(
        success=True,
        message="Applications retrieved successfully",
        data=[ApplicationOut.model_validate(a) for a in applications]
    )


@router.delete("/{application_id}/withdraw", response_model=APIResponse[ApplicationOut])
def withdraw_my_application(
    application_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Withdraw a previously submitted application (if not yet allocated)."""
    profile = StudentService.get_profile_by_user(db, current_user)
    withdrawn = ApplicationService.withdraw_application(db, profile, application_id)
    return APIResponse(
        success=True,
        message="Application withdrawn successfully",
        data=ApplicationOut.model_validate(withdrawn)
    )


@router.get("/internship/{internship_id}", response_model=APIResponse[PaginatedResponse[ApplicationOut]])
def get_internship_applications(
    internship_id: int,
    status_filter: Annotated[Optional[ApplicationStatus], Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(require_admin_or_company),
    db: Session = Depends(get_db)
):
    """View candidate applications for an internship with match scores (Admin / Employer)."""
    items, total = ApplicationService.list_internship_applications(
        db=db,
        internship_id=internship_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )

    return APIResponse(
        success=True,
        message="Applications retrieved successfully",
        data=PaginatedResponse(
            items=[ApplicationOut.model_validate(a) for a in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 1
        )
    )


@router.put("/{application_id}/status", response_model=APIResponse[ApplicationOut])
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(require_admin_or_company),
    db: Session = Depends(get_db)
):
    """Update status of a candidate application (e.g. Under Review, Shortlisted, Rejected)."""
    updated = ApplicationService.update_application_status(
        db=db,
        application_id=application_id,
        new_status=payload.status,
        actor=current_user
    )
    return APIResponse(
        success=True,
        message=f"Application status updated to {payload.status.value}",
        data=ApplicationOut.model_validate(updated)
    )
