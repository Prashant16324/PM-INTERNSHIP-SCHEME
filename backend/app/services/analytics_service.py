"""Analytics and aggregation service for administrative dashboard reporting."""

from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.user import User, UserRole
from app.models.student import StudentProfile, StudentSkill
from app.models.company import Company
from app.models.internship import Internship
from app.models.application import Application, ApplicationStatus
from app.models.allocation import Allocation, AllocationStatus
from app.schemas.analytics import (
    AdminDashboardStats,
    ApplicationsByStatusStat,
    InternshipsByIndustryStat,
    SkillDistributionStat,
    SeatUtilizationStat,
    AnalyticsDashboardResponse,
)


class AnalyticsService:
    """Computes administrative dashboard statistics, utilization metrics, and distributions."""

    @classmethod
    def get_dashboard_analytics(cls, db: Session) -> AnalyticsDashboardResponse:
        """Compute full suite of analytics for the administrator dashboard."""
        # 1. Total counts
        total_students = db.query(func.count(StudentProfile.id)).scalar() or 0
        total_companies = db.query(func.count(Company.id)).scalar() or 0
        total_internships = db.query(func.count(Internship.id)).scalar() or 0
        total_applications = db.query(func.count(Application.id)).scalar() or 0

        # Seat calculations
        total_seats = db.query(func.sum(Internship.total_seats)).scalar() or 0
        available_seats = db.query(func.sum(Internship.available_seats)).scalar() or 0
        allocated_seats = total_seats - available_seats

        allocated_students = db.query(func.count(Allocation.id)).filter(
            Allocation.status.in_([AllocationStatus.PROVISIONAL, AllocationStatus.CONFIRMED])
        ).scalar() or 0

        pending_applications = db.query(func.count(Application.id)).filter(
            Application.status.in_([ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW])
        ).scalar() or 0

        utilization_rate = round((allocated_seats / total_seats * 100.0), 2) if total_seats > 0 else 0.0

        summary = AdminDashboardStats(
            total_students=total_students,
            total_companies=total_companies,
            total_internships=total_internships,
            total_applications=total_applications,
            total_seats=total_seats,
            available_seats=available_seats,
            allocated_students=allocated_students,
            pending_applications=pending_applications,
            overall_seat_utilization_rate=utilization_rate
        )

        # 2. Applications by Status distribution
        status_counts = db.query(
            Application.status, func.count(Application.id)
        ).group_by(Application.status).all()

        app_status_dist = [
            ApplicationsByStatusStat(status=st.value, count=cnt)
            for st, cnt in status_counts
        ]

        # 3. Industry distribution
        industry_counts = db.query(
            Internship.industry,
            func.count(Internship.id),
            func.sum(Internship.total_seats)
        ).group_by(Internship.industry).all()

        industry_dist = [
            InternshipsByIndustryStat(industry=ind, internship_count=icnt, total_seats=tseats or 0)
            for ind, icnt, tseats in industry_counts
        ]

        # 4. Top student skills distribution
        top_skills = db.query(
            StudentSkill.skill_name,
            func.count(StudentSkill.id)
        ).group_by(StudentSkill.skill_name)\
         .order_by(desc(func.count(StudentSkill.id)))\
         .limit(10)\
         .all()

        skill_dist = [
            SkillDistributionStat(skill_name=sname, student_count=cnt)
            for sname, cnt in top_skills
        ]

        # 5. Internship seat utilization
        internships = db.query(Internship).order_by(desc(Internship.total_seats)).limit(10).all()
        seat_util = []
        for i in internships:
            filled = max(0, i.total_seats - i.available_seats)
            rate = round((filled / i.total_seats * 100.0), 1) if i.total_seats > 0 else 0.0
            seat_util.append(
                SeatUtilizationStat(
                    internship_id=i.id,
                    title=i.title,
                    company_name=i.company.company_name if i.company else "Partner Company",
                    total_seats=i.total_seats,
                    allocated_seats=filled,
                    utilization_percentage=rate
                )
            )

        return AnalyticsDashboardResponse(
            summary=summary,
            applications_by_status=app_status_dist,
            industry_distribution=industry_dist,
            top_skills_distribution=skill_dist,
            seat_utilization=seat_util
        )
