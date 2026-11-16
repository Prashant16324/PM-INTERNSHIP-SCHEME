"""AI matching, recommendation ranking, and skill gap analysis router."""

from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_student, require_admin
from app.models.user import User
from app.models.student import StudentProfile
from app.schemas.common import APIResponse
from app.schemas.matching import (
    MatchWeightConfig,
    RecommendationOut,
    SkillGapDetail,
    StudentRecommendationResponse,
)
from app.services.matching_service import MatchingEngine
from app.services.student_service import StudentService
from app.services.internship_service import InternshipService

router = APIRouter(prefix="/matching", tags=["AI Recommendation & Matching"])


@router.get("/recommendations", response_model=APIResponse[StudentRecommendationResponse])
def get_student_recommendations(
    skill_weight: Annotated[float, Query(ge=0.0, le=1.0)] = 0.50,
    education_weight: Annotated[float, Query(ge=0.0, le=1.0)] = 0.20,
    location_weight: Annotated[float, Query(ge=0.0, le=1.0)] = 0.15,
    industry_weight: Annotated[float, Query(ge=0.0, le=1.0)] = 0.15,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Fetch AI-ranked internship recommendations for the authenticated student with explainable scoring."""
    profile = StudentService.get_profile_by_user(db, current_user)
    weights = MatchWeightConfig(
        skill_weight=skill_weight,
        education_weight=education_weight,
        location_weight=location_weight,
        industry_weight=industry_weight
    )

    recs = MatchingEngine.generate_recommendations_for_student(
        db=db,
        profile=profile,
        weights=weights,
        limit=limit
    )

    return APIResponse(
        success=True,
        message="AI recommendations generated successfully",
        data=StudentRecommendationResponse(
            student_id=profile.id,
            total_recommendations=len(recs),
            recommendations=recs
        )
    )


@router.get("/skill-gap/{internship_id}", response_model=APIResponse[SkillGapDetail])
def get_internship_skill_gap(
    internship_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Retrieve fine-grained skill gap analysis between student's profile and an internship."""
    profile = StudentService.get_profile_by_user(db, current_user)
    internship = InternshipService.get_internship(db, internship_id)
    gap_analysis = MatchingEngine.get_skill_gap_analysis(profile, internship)

    return APIResponse(
        success=True,
        message="Skill gap analysis completed",
        data=gap_analysis
    )


@router.post("/recompute", response_model=APIResponse[StudentRecommendationResponse])
def recompute_my_recommendations(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Force recompute of recommendations following profile, skill, or resume updates."""
    profile = StudentService.get_profile_by_user(db, current_user)
    recs = MatchingEngine.generate_recommendations_for_student(
        db=db,
        profile=profile,
        weights=MatchWeightConfig(),
        limit=20
    )

    return APIResponse(
        success=True,
        message="Recommendations recomputed and cache updated",
        data=StudentRecommendationResponse(
            student_id=profile.id,
            total_recommendations=len(recs),
            recommendations=recs
        )
    )


@router.get("/admin/student/{student_id}", response_model=APIResponse[StudentRecommendationResponse])
def get_recommendations_for_student_admin(
    student_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Administrator inspection endpoint to review AI matching scores for any registered student."""
    profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile with id={student_id} not found"
        )

    recs = MatchingEngine.generate_recommendations_for_student(
        db=db,
        profile=profile,
        weights=MatchWeightConfig(),
        limit=50
    )

    return APIResponse(
        success=True,
        message=f"Recommendations generated for student id={student_id}",
        data=StudentRecommendationResponse(
            student_id=profile.id,
            total_recommendations=len(recs),
            recommendations=recs
        )
    )
