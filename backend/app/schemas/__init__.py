"""Pydantic schemas registration and exports."""

from app.schemas.common import APIResponse, PaginationParams, PaginatedResponse
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserOut
from app.schemas.auth import Token, TokenData, LoginRequest, StudentRegisterRequest, PasswordChangeRequest
from app.schemas.student import (
    StudentProfileUpdate,
    StudentProfileOut,
    StudentSkillCreate,
    StudentSkillOut,
    ResumeExtractResponse,
)
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.schemas.internship import (
    InternshipSkillCreate,
    InternshipSkillOut,
    InternshipCreate,
    InternshipUpdate,
    InternshipOut,
    InternshipEligibilityOut,
)
from app.schemas.matching import (
    MatchWeightConfig,
    LearningTopicSuggestion,
    SkillGapDetail,
    RecommendationOut,
    StudentRecommendationResponse,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationOut,
)
from app.schemas.allocation import (
    RunAllocationRequest,
    AllocationStatusUpdate,
    AllocationOut,
    AllocationSummaryResponse,
)
from app.schemas.analytics import (
    AdminDashboardStats,
    ApplicationsByStatusStat,
    InternshipsByIndustryStat,
    SkillDistributionStat,
    SeatUtilizationStat,
    AnalyticsDashboardResponse,
)

__all__ = [
    "APIResponse",
    "PaginationParams",
    "PaginatedResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "Token",
    "TokenData",
    "LoginRequest",
    "StudentRegisterRequest",
    "PasswordChangeRequest",
    "StudentProfileUpdate",
    "StudentProfileOut",
    "StudentSkillCreate",
    "StudentSkillOut",
    "ResumeExtractResponse",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyOut",
    "InternshipSkillCreate",
    "InternshipSkillOut",
    "InternshipCreate",
    "InternshipUpdate",
    "InternshipOut",
    "InternshipEligibilityOut",
    "MatchWeightConfig",
    "LearningTopicSuggestion",
    "SkillGapDetail",
    "RecommendationOut",
    "StudentRecommendationResponse",
    "ApplicationCreate",
    "ApplicationStatusUpdate",
    "ApplicationOut",
    "RunAllocationRequest",
    "AllocationStatusUpdate",
    "AllocationOut",
    "AllocationSummaryResponse",
    "AdminDashboardStats",
    "ApplicationsByStatusStat",
    "InternshipsByIndustryStat",
    "SkillDistributionStat",
    "SeatUtilizationStat",
    "AnalyticsDashboardResponse",
]
