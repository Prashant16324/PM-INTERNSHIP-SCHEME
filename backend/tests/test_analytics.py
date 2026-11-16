"""Unit tests for administrative analytics reporting."""

from app.models.user import User, UserRole
from app.models.company import Company
from app.models.student import StudentProfile
from app.models.internship import Internship
from app.routers.analytics import get_admin_dashboard_metrics


def test_admin_dashboard_analytics(db_session):
    admin_user = User(email="admin_analytics@test.edu.in", hashed_password="h", full_name="Admin", role=UserRole.ADMIN)
    db_session.add(admin_user)

    company = Company(company_name="Wipro", industry="Consulting", location="Hyderabad", is_verified=True)
    db_session.add(company)
    db_session.flush()

    internship = Internship(
        company_id=company.id,
        title="Consulting Intern",
        description="Business analysis.",
        location="Hyderabad",
        industry="Consulting",
        total_seats=4,
        available_seats=4
    )
    db_session.add(internship)
    db_session.commit()

    res = get_admin_dashboard_metrics(current_user=admin_user, db=db_session)
    assert res.success is True
    data = res.data
    assert data.summary.total_companies >= 1
    assert data.summary.total_internships >= 1
    assert data.summary.total_seats >= 4
    assert len(data.industry_distribution) >= 1
    assert any(ind.industry == "Consulting" for ind in data.industry_distribution)
