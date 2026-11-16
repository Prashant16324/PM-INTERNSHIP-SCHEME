"""Unit and integration tests for AI-based smart allocation engine."""

from app.models.user import User, UserRole
from app.models.company import Company
from app.models.student import StudentProfile, StudentSkill
from app.models.internship import Internship, InternshipSkill, InternshipStatus
from app.models.application import Application, ApplicationStatus
from app.models.allocation import Allocation, AllocationStatus
from app.schemas.allocation import RunAllocationRequest
from app.routers.allocations import (
    run_allocation_engine,
    confirm_allocation,
    cancel_allocation,
    list_allocations,
)


def setup_allocation_scenario(db_session):
    admin_user = User(email="admin_alloc@test.edu.in", hashed_password="h", full_name="Super Admin", role=UserRole.ADMIN)
    db_session.add(admin_user)

    company = Company(company_name="Infosys Limited", industry="IT", location="Bangalore", is_verified=True)
    db_session.add(company)
    db_session.flush()

    # 1. Internship with 2 seats requiring Python
    internship = Internship(
        company_id=company.id,
        title="AI Systems Intern",
        description="Develop ML solutions.",
        location="Bangalore",
        industry="IT",
        total_seats=2,
        available_seats=2,
        min_cgpa=7.0,
        status=InternshipStatus.OPEN
    )
    db_session.add(internship)
    db_session.flush()
    db_session.add(InternshipSkill(internship_id=internship.id, skill_name="Python", is_mandatory=True))

    # 2. Eligible candidate 1 (CGPA 8.5, has Python)
    student1 = User(email="s1@test.edu.in", hashed_password="h", full_name="Student One", role=UserRole.STUDENT)
    db_session.add(student1)
    db_session.flush()
    profile1 = StudentProfile(user_id=student1.id, degree="B.Tech", branch="CSE", cgpa=8.5)
    db_session.add(profile1)
    db_session.flush()
    db_session.add(StudentSkill(student_profile_id=profile1.id, skill_name="Python"))

    app1 = Application(
        student_profile_id=profile1.id,
        internship_id=internship.id,
        status=ApplicationStatus.SUBMITTED,
        match_score=85.0
    )
    db_session.add(app1)

    # 3. Eligible candidate 2 (CGPA 7.5, has Python)
    student2 = User(email="s2@test.edu.in", hashed_password="h", full_name="Student Two", role=UserRole.STUDENT)
    db_session.add(student2)
    db_session.flush()
    profile2 = StudentProfile(user_id=student2.id, degree="B.Tech", branch="IT", cgpa=7.5)
    db_session.add(profile2)
    db_session.flush()
    db_session.add(StudentSkill(student_profile_id=profile2.id, skill_name="Python"))

    app2 = Application(
        student_profile_id=profile2.id,
        internship_id=internship.id,
        status=ApplicationStatus.SUBMITTED,
        match_score=75.0
    )
    db_session.add(app2)

    db_session.commit()
    return admin_user, internship, profile1, profile2, app1, app2


def test_allocation_run_and_seat_decrement(db_session):
    admin_user, internship, profile1, profile2, app1, app2 = setup_allocation_scenario(db_session)

    # Run allocation round 1
    req = RunAllocationRequest(allocation_round=1, min_score_threshold=50.0, auto_confirm=False)
    res = run_allocation_engine(payload=req, current_user=admin_user, db=db_session)

    assert res.success is True
    summary = res.data
    assert summary.total_allocated_in_round == 2
    assert summary.total_seats_filled == 2

    # Verify database state
    db_session.refresh(internship)
    assert internship.available_seats == 0  # 2 seats filled

    db_session.refresh(app1)
    assert app1.status == ApplicationStatus.ALLOCATED

    db_session.refresh(app2)
    assert app2.status == ApplicationStatus.ALLOCATED


def test_allocation_confirmation_and_cancellation(db_session):
    admin_user, internship, profile1, profile2, app1, app2 = setup_allocation_scenario(db_session)

    # Run allocation
    req = RunAllocationRequest(allocation_round=1, min_score_threshold=50.0)
    alloc_res = run_allocation_engine(payload=req, current_user=admin_user, db=db_session)
    alloc1 = alloc_res.data.allocations[0]

    # Confirm allocation 1
    conf_res = confirm_allocation(allocation_id=alloc1.id, current_user=admin_user, db=db_session)
    assert conf_res.success is True
    assert conf_res.data.status == AllocationStatus.CONFIRMED

    # Cancel allocation 2
    alloc2 = alloc_res.data.allocations[1]
    cancel_res = cancel_allocation(allocation_id=alloc2.id, reason="Candidate opted out", current_user=admin_user, db=db_session)
    assert cancel_res.success is True
    assert cancel_res.data.status == AllocationStatus.CANCELLED

    # Verify seat was restored
    db_session.refresh(internship)
    assert internship.available_seats == 1


def test_gale_shapley_algorithm(db_session):
    admin_user, internship, profile1, profile2, app1, app2 = setup_allocation_scenario(db_session)
    from app.services.gale_shapley_service import GaleShapleyEngine

    res = GaleShapleyEngine.run_deferred_acceptance(db_session, min_score_threshold=40.0)
    assert res["total_matches"] == 2
    assert res["stability_guarantee"]["blocking_pairs"] == 0
    assert res["stability_guarantee"]["is_stable"] is True


def test_export_allocations_csv(db_session):
    admin_user, internship, profile1, profile2, app1, app2 = setup_allocation_scenario(db_session)
    from app.services.allocation_service import AllocationEngine
    req = RunAllocationRequest(allocation_round=1, min_score_threshold=50.0)
    run_allocation_engine(payload=req, current_user=admin_user, db=db_session)

    csv_text = AllocationEngine.generate_csv_report(db_session, round_number=1)
    assert "Allocation ID" in csv_text
    assert "Student Name" in csv_text
    assert "AI Systems Intern" in csv_text
