"""AI-assisted allocation process, seat assignment, and approval router."""

from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin, require_student, get_current_user
from app.models.user import User
from app.models.allocation import Allocation, AllocationStatus
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.allocation import (
    RunAllocationRequest,
    AllocationOut,
    AllocationSummaryResponse,
    AllocationStatusUpdate,
)
from app.services.allocation_service import AllocationEngine
from app.services.gale_shapley_service import GaleShapleyEngine
from app.services.student_service import StudentService

router = APIRouter(prefix="/allocations", tags=["Smart Allocation Engine"])


@router.post("/run", response_model=APIResponse[AllocationSummaryResponse])
def run_allocation_engine(
    payload: RunAllocationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Initiate an AI-based automated allocation round across eligible candidate applications (Admin only)."""
    summary = AllocationEngine.run_allocation(
        db=db,
        admin_user=current_user,
        round_number=payload.allocation_round,
        min_score_threshold=payload.min_score_threshold,
        auto_confirm=payload.auto_confirm
    )
    return APIResponse(
        success=True,
        message=f"Allocation Round {payload.allocation_round} executed successfully. Assigned {summary.total_allocated_in_round} seats.",
        data=summary
    )


@router.get("", response_model=APIResponse[PaginatedResponse[AllocationOut]])
def list_allocations(
    round_number: Annotated[Optional[int], Query(ge=1)] = None,
    status_filter: Annotated[Optional[AllocationStatus], Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """View all system allocations with round and status filters (Admin only)."""
    items, total = AllocationEngine.list_allocations(
        db=db,
        round_number=round_number,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )

    return APIResponse(
        success=True,
        message="Allocations retrieved successfully",
        data=PaginatedResponse(
            items=[AllocationOut.model_validate(a) for a in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 1
        )
    )


@router.get("/gale-shapley")
def run_gale_shapley_simulation(
    min_score_threshold: Annotated[float, Query(ge=0.0, le=100.0)] = 35.0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Execute Gale-Shapley Student-Proposing Deferred Acceptance simulation and return stability metrics."""
    result = GaleShapleyEngine.run_deferred_acceptance(db, min_score_threshold)
    return APIResponse(
        success=True,
        message="Gale-Shapley Deferred Acceptance algorithm executed successfully",
        data=result
    )


@router.get("/export")
def export_allocations_csv(
    round_number: Annotated[Optional[int], Query(ge=1)] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Export all allocations as a downloadable CSV report (Admin only)."""
    csv_content = AllocationEngine.generate_csv_report(db, round_number)
    filename = f"pm_internship_allocations_round_{round_number or 'all'}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.put("/{allocation_id}/confirm", response_model=APIResponse[AllocationOut])
def confirm_allocation(
    allocation_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Manually approve and confirm a provisional internship allocation."""
    confirmed = AllocationEngine.confirm_allocation(db, allocation_id, current_user)
    return APIResponse(
        success=True,
        message="Allocation confirmed successfully",
        data=AllocationOut.model_validate(confirmed)
    )


@router.put("/{allocation_id}/cancel", response_model=APIResponse[AllocationOut])
def cancel_allocation(
    allocation_id: int,
    reason: Optional[str] = Query(None, description="Reason for cancelling the seat allocation"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cancel an allocation, restore 1 seat to the internship, and revert candidate application."""
    cancelled = AllocationEngine.cancel_allocation(db, allocation_id, current_user, reason)
    return APIResponse(
        success=True,
        message="Allocation cancelled and internship seat restored",
        data=AllocationOut.model_validate(cancelled)
    )


@router.get("/my", response_model=APIResponse[Optional[AllocationOut]])
def get_my_allocation(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Check if the currently authenticated student has been provisionally or definitively allocated a seat."""
    profile = StudentService.get_profile_by_user(db, current_user)
    allocation = db.query(Allocation).filter(
        Allocation.student_profile_id == profile.id,
        Allocation.status.in_([AllocationStatus.PROVISIONAL, AllocationStatus.CONFIRMED])
    ).first()

    return APIResponse(
        success=True,
        message="Allocation status retrieved",
        data=AllocationOut.model_validate(allocation) if allocation else None
    )
