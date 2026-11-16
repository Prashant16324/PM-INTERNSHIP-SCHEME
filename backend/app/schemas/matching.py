"""AI matching, recommendations, and skill-gap analysis schemas."""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class MatchWeightConfig(BaseModel):
    """Configurable weights for prototype recommendation scoring."""
    skill_weight: float = Field(default=0.50, ge=0.0, le=1.0)
    education_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    location_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    industry_weight: float = Field(default=0.15, ge=0.0, le=1.0)


class LearningTopicSuggestion(BaseModel):
    skill_name: str
    suggested_topics: List[str]
    estimated_hours: int


class SkillGapDetail(BaseModel):
    internship_id: int
    internship_title: str
    company_name: str
    student_skills: List[str]
    required_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    skill_match_percentage: float
    learning_recommendations: List[LearningTopicSuggestion]


class RecommendationOut(BaseModel):
    internship_id: int
    internship_title: str
    company_name: str
    location: str
    industry: str
    stipend: float
    overall_score: float = Field(description="Normalized 0-100 match score")
    skill_score: float = Field(description="Normalized 0-100 skill similarity")
    education_score: float = Field(description="Normalized 0-100 education compatibility")
    location_score: float = Field(description="Normalized 0-100 location preference score")
    industry_score: float = Field(description="Normalized 0-100 industry preference score")
    is_eligible: bool
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str
    generated_at: datetime

    model_config = {
        "from_attributes": True
    }


class StudentRecommendationResponse(BaseModel):
    student_id: int
    total_recommendations: int
    recommendations: List[RecommendationOut]
