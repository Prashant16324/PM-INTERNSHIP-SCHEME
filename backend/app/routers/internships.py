"""Internship catalog, search, and eligibility assessment router."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin_or_company, require_student, get_current_user
from app.models.user import User, UserRole
from app.models.internship import InternshipStatus
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.internship import (
    InternshipCreate,
    InternshipUpdate,
    InternshipOut,
    InternshipEligibilityOut,
)
from app.services.internship_service import InternshipService
from app.services.student_service import StudentService

router = APIRouter(prefix="/internships", tags=["Internships & Opportunities"])


@router.get("", response_model=APIResponse[PaginatedResponse[InternshipOut]])
def list_internships(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    min_stipend: Optional[float] = None,
    status_filter: Optional[InternshipStatus] = None,
    db: Session = Depends(get_db)
):
    """Search, filter, and paginate available internships under the scheme."""
    items, total = InternshipService.list_internships(
        db=db,
        search=search,
        industry=industry,
        location=location,
        min_stipend=min_stipend,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )

    return APIResponse(
        success=True,
        message="Internships retrieved successfully",
        data=PaginatedResponse(
            items=[InternshipOut.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 1
        )
    )


@router.get("/{internship_id}", response_model=APIResponse[InternshipOut])
def get_internship_detail(internship_id: int, db: Session = Depends(get_db)):
    """Fetch complete details of an internship including required skills and company info."""
    internship = InternshipService.get_internship(db, internship_id)
    return APIResponse(
        success=True,
        message="Internship retrieved successfully",
        data=InternshipOut.model_validate(internship)
    )


@router.post("", response_model=APIResponse[InternshipOut], status_code=status.HTTP_201_CREATED)
def create_internship(
    payload: InternshipCreate,
    current_user: User = Depends(require_admin_or_company),
    db: Session = Depends(get_db)
):
    """Create a new internship opportunity with required skills (Admin or Employer)."""
    internship = InternshipService.create_internship(db, payload)
    return APIResponse(
        success=True,
        message="Internship created successfully",
        data=InternshipOut.model_validate(internship)
    )


@router.put("/{internship_id}", response_model=APIResponse[InternshipOut])
def update_internship(
    internship_id: int,
    payload: InternshipUpdate,
    current_user: User = Depends(require_admin_or_company),
    db: Session = Depends(get_db)
):
    """Update internship details or required skills."""
    internship = InternshipService.get_internship(db, internship_id)

    # Check company ownership if user is a COMPANY role
    if current_user.role == UserRole.COMPANY and internship.company.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit internships posted by your company"
        )

    updated = InternshipService.update_internship(db, internship_id, payload)
    return APIResponse(
        success=True,
        message="Internship updated successfully",
        data=InternshipOut.model_validate(updated)
    )


@router.delete("/{internship_id}", response_model=APIResponse[None])
def delete_internship(
    internship_id: int,
    current_user: User = Depends(require_admin_or_company),
    db: Session = Depends(get_db)
):
    """Delete an internship opportunity."""
    internship = InternshipService.get_internship(db, internship_id)

    if current_user.role == UserRole.COMPANY and internship.company.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete internships posted by your company"
        )

    InternshipService.delete_internship(db, internship_id)
    return APIResponse(
        success=True,
        message="Internship deleted successfully"
    )


@router.get("/{internship_id}/eligibility", response_model=APIResponse[InternshipEligibilityOut])
def check_my_eligibility(
    internship_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Verify rule-based eligibility between the authenticated student's profile and the internship."""
    profile = StudentService.get_profile_by_user(db, current_user)
    internship = InternshipService.get_internship(db, internship_id)
    result = InternshipService.evaluate_eligibility(profile, internship)

    return APIResponse(
        success=True,
        message="Eligibility evaluation completed",
        data=result
    )
