"""Internship application validation and serialization schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.application import ApplicationStatus
from app.schemas.internship import InternshipOut
from app.schemas.student import StudentProfileOut


class ApplicationCreate(BaseModel):
    internship_id: int
    cover_letter: Optional[str] = Field(None, max_length=2000, description="Optional brief motivation note")


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    note: Optional[str] = Field(None, max_length=500)


class ApplicationOut(BaseModel):
    id: int
    student_profile_id: int
    internship_id: int
    status: ApplicationStatus
    match_score: float
    cover_letter: Optional[str] = None
    applied_at: datetime
    updated_at: datetime
    internship: Optional[InternshipOut] = None
    student_profile: Optional[StudentProfileOut] = None

    model_config = {
        "from_attributes": True
    }
