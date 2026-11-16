"""Unit and integration tests for AI matching engine and skill gap analysis."""

from app.models.user import User, UserRole
from app.models.company import Company
from app.models.student import StudentProfile, StudentSkill
from app.models.internship import Internship, InternshipSkill, InternshipStatus
from app.schemas.matching import MatchWeightConfig
from app.services.matching_service import MatchingEngine
from app.routers.matching import (
    get_student_recommendations,
    get_internship_skill_gap,
    recompute_my_recommendations,
)


def setup_matching_scenario(db_session):
    """Setup a sample scenario with companies, internships, and a student candidate."""
    # 1. Company
    company = Company(
        company_name="Digital India Innovations",
        industry="Information Technology",
        location="Bangalore",
        is_verified=True
    )
    db_session.add(company)
    db_session.flush()

    # 2. Perfect match internship
    intern1 = Internship(
        company_id=company.id,
        title="Full Stack Python Developer",
        description="Build scalable APIs using Python, FastAPI, and PostgreSQL with React frontends.",
        location="Bangalore",
        industry="Information Technology",
        duration_weeks=10,
        stipend=20000.0,
        total_seats=3,
        available_seats=3,
        min_cgpa=7.0,
        preferred_education="B.Tech, BCA",
        status=InternshipStatus.OPEN
    )
    db_session.add(intern1)
    db_session.flush()

    db_session.add(InternshipSkill(internship_id=intern1.id, skill_name="Python", is_mandatory=True))
    db_session.add(InternshipSkill(internship_id=intern1.id, skill_name="FastAPI", is_mandatory=True))
    db_session.add(InternshipSkill(internship_id=intern1.id, skill_name="PostgreSQL", is_mandatory=False))

    # 3. Partial match internship (requires skills student doesn't have)
    intern2 = Internship(
        company_id=company.id,
        title="Cloud DevOps Engineer",
        description="Deploy cloud infrastructure using Kubernetes, Terraform, and AWS.",
        location="Pune",
        industry="Cloud Computing",
        duration_weeks=12,
        stipend=18000.0,
        total_seats=2,
        available_seats=2,
        min_cgpa=8.5,  # higher threshold
        preferred_education="B.Tech",
        status=InternshipStatus.OPEN
    )
    db_session.add(intern2)
    db_session.flush()

    db_session.add(InternshipSkill(internship_id=intern2.id, skill_name="Kubernetes", is_mandatory=True))
    db_session.add(InternshipSkill(internship_id=intern2.id, skill_name="AWS", is_mandatory=True))

    # 4. Student
    student_user = User(
        email="candidate.ai@test.edu.in",
        hashed_password="hash",
        full_name="Pooja Sharma",
        role=UserRole.STUDENT
    )
    db_session.add(student_user)
    db_session.flush()

    student_profile = StudentProfile(
        user_id=student_user.id,
        degree="B.Tech",
        branch="Information Technology",
        cgpa=8.0,
        preferred_locations=["Bangalore"],
        preferred_industries=["Information Technology"]
    )
    db_session.add(student_profile)
    db_session.flush()

    # Student skills: Python, FastAPI, Docker
    db_session.add(StudentSkill(student_profile_id=student_profile.id, skill_name="Python"))
    db_session.add(StudentSkill(student_profile_id=student_profile.id, skill_name="FastAPI"))
    db_session.add(StudentSkill(student_profile_id=student_profile.id, skill_name="Docker"))

    db_session.commit()
    return student_user, student_profile, intern1, intern2


def test_evaluate_match_high_vs_low(db_session):
    student_user, student_profile, intern1, intern2 = setup_matching_scenario(db_session)

    # Evaluate intern1 (High match)
    score1, skill_s1, edu_s1, loc_s1, ind_s1, is_elig1, matched1, missing1, expl1 = (
        MatchingEngine.evaluate_match(student_profile, intern1)
    )

    assert is_elig1 is True
    assert "Python" in matched1
    assert "FastAPI" in matched1
    assert "PostgreSQL" in missing1
    assert loc_s1 == 100.0  # Bangalore matches preferred location
    assert ind_s1 == 100.0  # IT matches preferred industry
    assert score1 >= 75.0   # High composite score

    # Evaluate intern2 (Ineligible due to missing mandatory skills & CGPA)
    score2, skill_s2, edu_s2, loc_s2, ind_s2, is_elig2, matched2, missing2, expl2 = (
        MatchingEngine.evaluate_match(student_profile, intern2)
    )

    assert is_elig2 is False
    assert "Kubernetes" in missing2
    assert "Ineligible" in expl2
    assert score2 < score1


def test_recommendations_ranking(db_session):
    student_user, student_profile, intern1, intern2 = setup_matching_scenario(db_session)

    res = get_student_recommendations(current_user=student_user, db=db_session)
    assert res.success is True
    assert res.data.total_recommendations == 2

    # Verify top ranked recommendation is the eligible, high scoring one
    top_rec = res.data.recommendations[0]
    assert top_rec.internship_id == intern1.id
    assert top_rec.is_eligible is True
    assert top_rec.overall_score > res.data.recommendations[1].overall_score


def test_skill_gap_analysis(db_session):
    student_user, student_profile, intern1, intern2 = setup_matching_scenario(db_session)

    gap_res = get_internship_skill_gap(internship_id=intern2.id, current_user=student_user, db=db_session)
    assert gap_res.success is True
    data = gap_res.data
    assert "Kubernetes" in data.missing_skills
    assert "AWS" in data.missing_skills
    assert data.skill_match_percentage == 0.0

    # Verify actionable learning recommendations are populated
    assert len(data.learning_recommendations) >= 2
    k8s_rec = next(r for r in data.learning_recommendations if r.skill_name == "Kubernetes")
    assert len(k8s_rec.suggested_topics) > 0
    assert any("Pod" in t or "Deploy" in t for t in k8s_rec.suggested_topics)


def test_recompute_recommendations(db_session):
    student_user, student_profile, intern1, intern2 = setup_matching_scenario(db_session)

    res = recompute_my_recommendations(current_user=student_user, db=db_session)
    assert res.success is True
    assert res.data.total_recommendations >= 1
