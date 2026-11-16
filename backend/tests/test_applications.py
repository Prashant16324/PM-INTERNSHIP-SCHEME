"""Unit and integration tests for internship applications and state transitions."""

from app.models.user import User, UserRole
from app.models.company import Company
from app.models.student import StudentProfile, StudentSkill
from app.models.internship import Internship, InternshipSkill, InternshipStatus
from app.models.application import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate
from app.routers.applications import (
    apply_to_internship,
    get_my_applications,
    withdraw_my_application,
    update_application_status,
)


def setup_application_scenario(db_session):
    company = Company(company_name="Tata Consultancy Services", industry="IT", location="Mumbai", is_verified=True)
    db_session.add(company)
    db_session.flush()

    internship = Internship(
        company_id=company.id,
        title="Software Engineer Intern",
        description="Develop scalable cloud services.",
        location="Mumbai",
        industry="IT",
        total_seats=2,
        available_seats=2,
        status=InternshipStatus.OPEN
    )
    db_session.add(internship)
    db_session.flush()

    student_user = User(email="applicant@test.edu.in", hashed_password="h", full_name="Ravi Kumar", role=UserRole.STUDENT)
    db_session.add(student_user)
    db_session.flush()

    student_profile = StudentProfile(user_id=student_user.id, degree="B.Tech", branch="CSE", cgpa=8.2)
    db_session.add(student_profile)
    db_session.commit()

    return student_user, student_profile, internship


def test_submit_application_success(db_session):
    student_user, student_profile, internship = setup_application_scenario(db_session)

    payload = ApplicationCreate(internship_id=internship.id, cover_letter="Excited to contribute to TCS projects.")
    res = apply_to_internship(payload=payload, current_user=student_user, db=db_session)

    assert res.success is True
    assert res.data.internship_id == internship.id
    assert res.data.status == ApplicationStatus.SUBMITTED
    assert res.data.match_score > 0.0


def test_duplicate_application_fails(db_session):
    student_user, student_profile, internship = setup_application_scenario(db_session)
    payload = ApplicationCreate(internship_id=internship.id)

    # First succeeds
    apply_to_internship(payload=payload, current_user=student_user, db=db_session)

    # Second fails with 409 Conflict
    import pytest
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        apply_to_internship(payload=payload, current_user=student_user, db=db_session)
    assert exc.value.status_code == 409


def test_withdraw_application(db_session):
    student_user, student_profile, internship = setup_application_scenario(db_session)
    payload = ApplicationCreate(internship_id=internship.id)
    app_res = apply_to_internship(payload=payload, current_user=student_user, db=db_session)
    app_id = app_res.data.id

    withdraw_res = withdraw_my_application(application_id=app_id, current_user=student_user, db=db_session)
    assert withdraw_res.success is True
    assert withdraw_res.data.status == ApplicationStatus.WITHDRAWN


def test_update_application_status(db_session):
    student_user, student_profile, internship = setup_application_scenario(db_session)
    admin_user = User(email="admin_app@test.edu.in", hashed_password="h", full_name="Admin", role=UserRole.ADMIN)

    app_res = apply_to_internship(payload=ApplicationCreate(internship_id=internship.id), current_user=student_user, db=db_session)
    app_id = app_res.data.id

    status_update = ApplicationStatusUpdate(status=ApplicationStatus.SHORTLISTED)
    res = update_application_status(application_id=app_id, payload=status_update, current_user=admin_user, db=db_session)
    assert res.success is True
    assert res.data.status == ApplicationStatus.SHORTLISTED
