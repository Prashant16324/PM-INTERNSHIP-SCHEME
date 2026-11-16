"""Internship opportunities and skills schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.internship import InternshipStatus
from app.schemas.company import CompanyOut


class InternshipSkillCreate(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    is_mandatory: bool = True
    weight: float = Field(default=1.0, ge=0.1, le=5.0)


class InternshipSkillOut(BaseModel):
    id: int
    internship_id: int
    skill_name: str
    is_mandatory: bool
    weight: float

    model_config = {
        "from_attributes": True
    }


class InternshipBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    location: str = Field(min_length=2, max_length=150)
    industry: str = Field(min_length=2, max_length=100)
    duration_weeks: int = Field(default=8, ge=2, le=52)
    stipend: float = Field(default=0.0, ge=0.0)
    total_seats: int = Field(default=1, ge=1)
    min_cgpa: float = Field(default=0.0, ge=0.0, le=10.0)
    preferred_education: Optional[str] = Field(None, max_length=255, description="e.g. B.Tech, BCA, MCA")
    eligibility_criteria: Optional[str] = Field(None)
    application_deadline: Optional[datetime] = None
    status: InternshipStatus = InternshipStatus.OPEN


class InternshipCreate(InternshipBase):
    company_id: int
    skills: Optional[List[InternshipSkillCreate]] = []


class InternshipUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    location: Optional[str] = None
    industry: Optional[str] = None
    duration_weeks: Optional[int] = Field(None, ge=2, le=52)
    stipend: Optional[float] = Field(None, ge=0.0)
    total_seats: Optional[int] = Field(None, ge=1)
    available_seats: Optional[int] = Field(None, ge=0)
    min_cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    preferred_education: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    application_deadline: Optional[datetime] = None
    status: Optional[InternshipStatus] = None
    skills: Optional[List[InternshipSkillCreate]] = None


class InternshipOut(InternshipBase):
    id: int
    company_id: int
    available_seats: int
    created_at: datetime
    updated_at: datetime
    skills: List[InternshipSkillOut] = []
    company: Optional[CompanyOut] = None

    model_config = {
        "from_attributes": True
    }


class InternshipEligibilityOut(BaseModel):
    internship_id: int
    is_eligible: bool
    reasons: List[str]
    missing_mandatory_skills: List[str]
    matched_mandatory_skills: List[str]
    cgpa_satisfied: bool
    education_satisfied: bool
    deadline_valid: bool
