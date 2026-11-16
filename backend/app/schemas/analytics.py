"""Analytics, dashboard metric cards, and chart distribution schemas."""

from typing import List, Dict, Any
from pydantic import BaseModel


class AdminDashboardStats(BaseModel):
    total_students: int
    total_companies: int
    total_internships: int
    total_applications: int
    total_seats: int
    available_seats: int
    allocated_students: int
    pending_applications: int
    overall_seat_utilization_rate: float


class ApplicationsByStatusStat(BaseModel):
    status: str
    count: int


class InternshipsByIndustryStat(BaseModel):
    industry: str
    internship_count: int
    total_seats: int


class SkillDistributionStat(BaseModel):
    skill_name: str
    student_count: int


class SeatUtilizationStat(BaseModel):
    internship_id: int
    title: str
    company_name: str
    total_seats: int
    allocated_seats: int
    utilization_percentage: float


class AnalyticsDashboardResponse(BaseModel):
    summary: AdminDashboardStats
    applications_by_status: List[ApplicationsByStatusStat]
    industry_distribution: List[InternshipsByIndustryStat]
    top_skills_distribution: List[SkillDistributionStat]
    seat_utilization: List[SeatUtilizationStat]
