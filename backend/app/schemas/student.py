"""Student profile and skill schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserOut


class StudentSkillBase(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    proficiency_level: str = Field(default="INTERMEDIATE", description="BEGINNER, INTERMEDIATE, or ADVANCED")
    source: str = Field(default="MANUAL", description="MANUAL or RESUME_EXTRACTED")


class StudentSkillCreate(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    proficiency_level: Optional[str] = "INTERMEDIATE"


class StudentSkillOut(StudentSkillBase):
    id: int
    student_profile_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class StudentProfileUpdate(BaseModel):
    phone_number: Optional[str] = Field(None, max_length=20)
    college_name: Optional[str] = Field(None, max_length=255)
    degree: Optional[str] = Field(None, max_length=100)
    branch: Optional[str] = Field(None, max_length=100)
    graduation_year: Optional[int] = Field(None, ge=2020, le=2035)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0, description="Cumulative Grade Point Average on 10.0 scale")
    preferred_locations: Optional[List[str]] = Field(default=None)
    preferred_industries: Optional[List[str]] = Field(default=None)
    bio: Optional[str] = Field(None, max_length=2000)


class StudentProfileOut(BaseModel):
    id: int
    user_id: int
    phone_number: Optional[str] = None
    college_name: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    profile_completion_percentage: int
    preferred_locations: List[str] = []
    preferred_industries: List[str] = []
    resume_url: Optional[str] = None
    bio: Optional[str] = None
    skills: List[StudentSkillOut] = []
    user: Optional[UserOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ResumeExtractResponse(BaseModel):
    filename: str
    file_size_bytes: int
    extracted_text_preview: str
    detected_skills: List[str]
    detected_education: Optional[str] = None
    message: str
