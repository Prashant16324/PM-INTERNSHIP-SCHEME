"""Unit and integration tests for student profile and skill management."""

from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.schemas.student import StudentProfileUpdate, StudentSkillCreate
from app.routers.students import (
    get_my_profile,
    update_my_profile,
    add_skill,
    remove_skill,
    confirm_extracted_skills,
)


def create_test_student(db_session, email="student1@test.edu.in"):
    user = User(
        email=email,
        hashed_password="hash",
        full_name="Arjun Mehta",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    profile = StudentProfile(
        user_id=user.id,
        phone_number="9876543210",
        college_name="IIT Bombay",
        degree="B.Tech",
        branch="Computer Science",
        graduation_year=2026,
        cgpa=8.5,
        profile_completion_percentage=60,
        preferred_locations=["Bangalore", "Pune"],
        preferred_industries=["Information Technology", "AI"]
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_student_profile(db_session):
    student = create_test_student(db_session, "profile_test@test.edu.in")
    res = get_my_profile(current_user=student, db=db_session)
    assert res.success is True
    assert res.data.college_name == "IIT Bombay"
    assert res.data.cgpa == 8.5
    assert "Bangalore" in res.data.preferred_locations


def test_update_student_profile(db_session):
    student = create_test_student(db_session, "update_test@test.edu.in")
    update_payload = StudentProfileUpdate(
        cgpa=9.1,
        bio="Aspiring machine learning researcher and full stack engineer."
    )
    res = update_my_profile(payload=update_payload, current_user=student, db=db_session)
    assert res.success is True
    assert res.data.cgpa == 9.1
    assert "machine learning" in res.data.bio


def test_add_and_remove_skill(db_session):
    student = create_test_student(db_session, "skill_test@test.edu.in")

    # Add skill
    skill_payload = StudentSkillCreate(skill_name="Python", proficiency_level="ADVANCED")
    add_res = add_skill(payload=skill_payload, current_user=student, db=db_session)
    assert add_res.success is True
    assert add_res.data.skill_name == "Python"
    skill_id = add_res.data.id

    # Verify profile now reflects skill
    profile_res = get_my_profile(current_user=student, db=db_session)
    assert any(s.skill_name == "Python" for s in profile_res.data.skills)

    # Remove skill
    rem_res = remove_skill(skill_id=skill_id, current_user=student, db=db_session)
    assert rem_res.success is True

    # Verify skill is deleted
    profile_res_after = get_my_profile(current_user=student, db=db_session)
    assert not any(s.skill_name == "Python" for s in profile_res_after.data.skills)


def test_confirm_batch_extracted_skills(db_session):
    student = create_test_student(db_session, "batch_skills@test.edu.in")
    extracted_skills = ["FastAPI", "PostgreSQL", "Docker", "Machine Learning"]

    res = confirm_extracted_skills(skills=extracted_skills, current_user=student, db=db_session)
    assert res.success is True
    assert len(res.data) == 4

    # Verify non-duplicate handling on second call
    res_second = confirm_extracted_skills(skills=["FastAPI", "Kubernetes"], current_user=student, db=db_session)
    assert len(res_second.data) == 1  # Only Kubernetes added
