"""Student profile, skills, and resume management router."""

import os
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_student
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.student import (
    StudentProfileOut,
    StudentProfileUpdate,
    StudentSkillCreate,
    StudentSkillOut,
    ResumeExtractResponse,
)
from app.services.student_service import StudentService
from app.services.resume_service import ResumeService
from app.models.audit_log import ResumeFile

router = APIRouter(prefix="/students", tags=["Student Profile & Resume"])


@router.get("/me/profile", response_model=APIResponse[StudentProfileOut])
def get_my_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Retrieve the current student's full profile including skills and completion percentage."""
    profile = StudentService.get_profile_by_user(db, current_user)
    return APIResponse(
        success=True,
        message="Student profile retrieved successfully",
        data=StudentProfileOut.model_validate(profile)
    )


@router.put("/me/profile", response_model=APIResponse[StudentProfileOut])
def update_my_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Update profile details (education, preferences, bio) and update completion percentage."""
    profile = StudentService.get_profile_by_user(db, current_user)
    updated = StudentService.update_profile(db, profile, payload)
    return APIResponse(
        success=True,
        message="Student profile updated successfully",
        data=StudentProfileOut.model_validate(updated)
    )


@router.post("/me/skills", response_model=APIResponse[StudentSkillOut], status_code=status.HTTP_201_CREATED)
def add_skill(
    payload: StudentSkillCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Add a new technical or soft skill to the student profile."""
    profile = StudentService.get_profile_by_user(db, current_user)
    skill = StudentService.add_skill(db, profile, payload, source="MANUAL")
    return APIResponse(
        success=True,
        message="Skill added successfully",
        data=StudentSkillOut.model_validate(skill)
    )


@router.delete("/me/skills/{skill_id}", response_model=APIResponse[None])
def remove_skill(
    skill_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Remove a skill from the student profile."""
    profile = StudentService.get_profile_by_user(db, current_user)
    StudentService.remove_skill(db, profile, skill_id)
    return APIResponse(
        success=True,
        message="Skill removed successfully"
    )


@router.post("/me/skills/confirm-batch", response_model=APIResponse[List[StudentSkillOut]])
def confirm_extracted_skills(
    skills: List[str],
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Review and confirm extracted resume skills to append them to the profile."""
    profile = StudentService.get_profile_by_user(db, current_user)
    added = StudentService.batch_add_skills(db, profile, skills, source="RESUME_EXTRACTED")
    return APIResponse(
        success=True,
        message=f"Added {len(added)} confirmed skills to your profile.",
        data=[StudentSkillOut.model_validate(s) for s in added]
    )


@router.post("/me/resume", response_model=APIResponse[ResumeExtractResponse])
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Upload a PDF resume, validate file size/type, extract text and detect candidate skills."""
    profile = StudentService.get_profile_by_user(db, current_user)
    resume_rec, detected_skills, detected_degree, preview = ResumeService.process_and_save_resume(
        db, profile, file
    )

    return APIResponse(
        success=True,
        message="Resume uploaded and processed successfully. Please review detected skills before confirming.",
        data=ResumeExtractResponse(
            filename=resume_rec.original_filename,
            file_size_bytes=resume_rec.file_size_bytes,
            extracted_text_preview=preview,
            detected_skills=detected_skills,
            detected_education=detected_degree,
            message=f"Found {len(detected_skills)} skills and detected degree '{detected_degree or 'Not specified'}'."
        )
    )


@router.get("/me/resume/download")
def download_resume(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Download the currently uploaded resume PDF file."""
    profile = StudentService.get_profile_by_user(db, current_user)
    resume_rec = db.query(ResumeFile).filter(
        ResumeFile.student_profile_id == profile.id
    ).order_by(ResumeFile.uploaded_at.desc()).first()

    if not resume_rec or not os.path.exists(resume_rec.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No uploaded resume file found for this profile"
        )

    return FileResponse(
        path=resume_rec.file_path,
        media_type="application/pdf",
        filename=resume_rec.original_filename
    )
