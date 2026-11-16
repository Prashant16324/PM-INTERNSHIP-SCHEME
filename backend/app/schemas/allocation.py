"""Smart allocation engine schemas and summaries."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.allocation import AllocationStatus
from app.schemas.internship import InternshipOut
from app.schemas.student import StudentProfileOut


class RunAllocationRequest(BaseModel):
    """Parameters for initiating an automated allocation round."""
    allocation_round: int = Field(default=1, ge=1, description="Allocation round sequence (e.g. 1, 2, 3)")
    min_score_threshold: float = Field(default=40.0, ge=0.0, le=100.0, description="Minimum match score required for allocation")
    auto_confirm: bool = Field(default=False, description="Whether to automatically set status to CONFIRMED instead of PROVISIONAL")


class AllocationStatusUpdate(BaseModel):
    status: AllocationStatus
    reason: Optional[str] = Field(None, max_length=500)


class AllocationOut(BaseModel):
    id: int
    application_id: int
    student_profile_id: int
    internship_id: int
    allocation_round: int
    allocated_by_user_id: Optional[int] = None
    allocation_score: float
    status: AllocationStatus
    allocation_reason: Optional[str] = None
    allocated_at: datetime
    confirmed_at: Optional[datetime] = None
    internship: Optional[InternshipOut] = None
    student_profile: Optional[StudentProfileOut] = None

    model_config = {
        "from_attributes": True
    }


class AllocationSummaryResponse(BaseModel):
    round: int
    total_applications_evaluated: int
    total_allocated_in_round: int
    total_seats_filled: int
    execution_time_seconds: float
    allocations: List[AllocationOut]
