"""Unit and integration tests for internship management and eligibility checks."""

from app.models.user import User, UserRole
from app.models.company import Company
from app.models.student import StudentProfile, StudentSkill
from app.schemas.internship import (
    InternshipCreate,
    InternshipSkillCreate,
    InternshipUpdate
)
from app.routers.internships import (
    create_internship,
    list_internships,
    get_internship_detail,
    update_internship,
    check_my_eligibility
)


def create_test_company(db_session):
    company = Company(
        company_name="Bharat Tech Solutions",
        industry="Information Technology",
        location="Bangalore",
        is_verified=True
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


def test_create_and_list_internships(db_session):
    company = create_test_company(db_session)
    admin_user = User(
        email="admin_internship@test.edu.in",
        hashed_password="hash",
        full_name="Admin",
        role=UserRole.ADMIN
    )

    internship_payload = InternshipCreate(
        company_id=company.id,
        title="AI/ML Research Intern",
        description="Work on cutting edge NLP and recommendation engines for smart governance.",
        location="Bangalore",
        industry="Artificial Intelligence",
        duration_weeks=12,
        stipend=25000.0,
        total_seats=5,
        min_cgpa=7.5,
        preferred_education="B.Tech, M.Tech",
        skills=[
            InternshipSkillCreate(skill_name="Python", is_mandatory=True, weight=2.0),
            InternshipSkillCreate(skill_name="Machine Learning", is_mandatory=True, weight=2.0),
            InternshipSkillCreate(skill_name="Docker", is_mandatory=False, weight=1.0),
        ]
    )

    create_res = create_internship(payload=internship_payload, current_user=admin_user, db=db_session)
    assert create_res.success is True
    assert create_res.data.title == "AI/ML Research Intern"
    assert len(create_res.data.skills) == 3
    internship_id = create_res.data.id

    # Test listing with search
    list_res = list_internships(
        page=1,
        page_size=10,
        search="Research",
        db=db_session
    )
    assert list_res.success is True
    assert list_res.data.total == 1
    assert list_res.data.items[0].id == internship_id


def test_eligibility_evaluation_passes(db_session):
    company = create_test_company(db_session)
    admin_user = User(email="admin_el@test.edu.in", hashed_password="h", full_name="Ad", role=UserRole.ADMIN)

    # 1. Create Internship requiring Python and SQL with min CGPA 7.0
    internship_payload = InternshipCreate(
        company_id=company.id,
        title="Data Analytics Intern",
        description="Analyze public scheme data.",
        location="Delhi",
        industry="Data Analytics",
        total_seats=3,
        min_cgpa=7.0,
        preferred_education="B.Tech, BCA",
        skills=[
            InternshipSkillCreate(skill_name="Python", is_mandatory=True),
            InternshipSkillCreate(skill_name="SQL", is_mandatory=True),
        ]
    )
    internship_res = create_internship(payload=internship_payload, current_user=admin_user, db=db_session)
    internship_id = internship_res.data.id

    # 2. Create Student with Python and SQL and CGPA 8.0
    student_user = User(email="eligible_stud@test.edu.in", hashed_password="h", full_name="Aditi", role=UserRole.STUDENT)
    db_session.add(student_user)
    db_session.flush()

    student_profile = StudentProfile(
        user_id=student_user.id,
        degree="B.Tech",
        branch="Computer Science",
        cgpa=8.0
    )
    db_session.add(student_profile)
    db_session.flush()

    db_session.add(StudentSkill(student_profile_id=student_profile.id, skill_name="Python"))
    db_session.add(StudentSkill(student_profile_id=student_profile.id, skill_name="SQL"))
    db_session.commit()

    # 3. Check Eligibility
    elig_res = check_my_eligibility(internship_id=internship_id, current_user=student_user, db=db_session)
    assert elig_res.success is True
    assert elig_res.data.is_eligible is True
    assert elig_res.data.cgpa_satisfied is True
    assert len(elig_res.data.missing_mandatory_skills) == 0


def test_eligibility_evaluation_fails_on_missing_skill_and_low_cgpa(db_session):
    company = create_test_company(db_session)
    admin_user = User(email="admin_el2@test.edu.in", hashed_password="h", full_name="Ad", role=UserRole.ADMIN)

    # Internship requiring Machine Learning and min CGPA 8.5
    internship_payload = InternshipCreate(
        company_id=company.id,
        title="Deep Learning Intern",
        description="Deep learning research.",
        location="Hyderabad",
        industry="AI",
        total_seats=2,
        min_cgpa=8.5,
        skills=[
            InternshipSkillCreate(skill_name="Machine Learning", is_mandatory=True),
        ]
    )
    internship_res = create_internship(payload=internship_payload, current_user=admin_user, db=db_session)
    internship_id = internship_res.data.id

    # Student with CGPA 7.0 and lacking Machine Learning
    student_user = User(email="ineligible_stud@test.edu.in", hashed_password="h", full_name="Rohan", role=UserRole.STUDENT)
    db_session.add(student_user)
    db_session.flush()

    student_profile = StudentProfile(
        user_id=student_user.id,
        degree="B.Sc",
        cgpa=7.0
    )
    db_session.add(student_profile)
    db_session.flush()
    db_session.add(StudentSkill(student_profile_id=student_profile.id, skill_name="HTML"))
    db_session.commit()

    elig_res = check_my_eligibility(internship_id=internship_id, current_user=student_user, db=db_session)
    assert elig_res.success is True
    assert elig_res.data.is_eligible is False
    assert elig_res.data.cgpa_satisfied is False
    assert "Machine Learning" in elig_res.data.missing_mandatory_skills
