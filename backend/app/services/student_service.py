"""Student profile and skills management service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.student import StudentProfile, StudentSkill
from app.models.user import User
from app.schemas.student import StudentProfileUpdate, StudentSkillCreate


class StudentService:
    """Service handling profile enrichment, completion calculation, and skill management."""

    @staticmethod
    def calculate_completion(profile: StudentProfile) -> int:
        """Dynamically compute profile completion percentage (0-100%)."""
        points = 20  # Base account created

        if profile.phone_number:
            points += 10
        if profile.college_name:
            points += 10
        if profile.degree and profile.branch:
            points += 10
        if profile.cgpa is not None and profile.cgpa > 0:
            points += 10
        if profile.graduation_year:
            points += 10
        if profile.preferred_locations or profile.preferred_industries:
            points += 10
        if profile.skills and len(profile.skills) > 0:
            points += 10
        if profile.resume_url:
            points += 10

        return min(points, 100)

    @classmethod
    def get_profile_by_user(cls, db: Session, user: User) -> StudentProfile:
        """Retrieve student profile belonging to user, creating one if not exists."""
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if not profile:
            profile = StudentProfile(
                user_id=user.id,
                preferred_locations=[],
                preferred_industries=[],
                profile_completion_percentage=20
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @classmethod
    def update_profile(cls, db: Session, profile: StudentProfile, data: StudentProfileUpdate) -> StudentProfile:
        """Update student profile attributes and recalculate completion score."""
        update_dict = data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(profile, field, value)

        profile.profile_completion_percentage = cls.calculate_completion(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @classmethod
    def add_skill(cls, db: Session, profile: StudentProfile, data: StudentSkillCreate, source: str = "MANUAL") -> StudentSkill:
        """Add a new skill to student profile, checking for duplicates."""
        skill_clean = data.skill_name.strip()
        existing = db.query(StudentSkill).filter(
            StudentSkill.student_profile_id == profile.id,
            StudentSkill.skill_name.ilike(skill_clean)
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Skill '{skill_clean}' is already listed in your profile."
            )

        new_skill = StudentSkill(
            student_profile_id=profile.id,
            skill_name=skill_clean,
            proficiency_level=data.proficiency_level or "INTERMEDIATE",
            source=source
        )
        db.add(new_skill)
        profile.profile_completion_percentage = cls.calculate_completion(profile)
        db.commit()
        db.refresh(new_skill)
        return new_skill

    @classmethod
    def remove_skill(cls, db: Session, profile: StudentProfile, skill_id: int) -> None:
        """Remove a skill from student profile and recalculate completion percentage."""
        skill = db.query(StudentSkill).filter(
            StudentSkill.id == skill_id,
            StudentSkill.student_profile_id == profile.id
        ).first()

        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found on this profile"
            )

        db.delete(skill)
        profile.profile_completion_percentage = cls.calculate_completion(profile)
        db.commit()

    @classmethod
    def batch_add_skills(cls, db: Session, profile: StudentProfile, skill_names: List[str], source: str = "RESUME_EXTRACTED") -> List[StudentSkill]:
        """Bulk import non-duplicate skills (e.g. verified from resume extraction)."""
        existing_skills = {
            s.skill_name.lower(): s for s in profile.skills
        }
        added = []

        for name in skill_names:
            name_clean = name.strip()
            if not name_clean or name_clean.lower() in existing_skills:
                continue

            new_skill = StudentSkill(
                student_profile_id=profile.id,
                skill_name=name_clean,
                proficiency_level="INTERMEDIATE",
                source=source
            )
            db.add(new_skill)
            added.append(new_skill)

        if added:
            profile.profile_completion_percentage = cls.calculate_completion(profile)
            db.commit()

        return added
