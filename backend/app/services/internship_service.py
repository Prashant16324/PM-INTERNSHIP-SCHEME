"""Internship management and rule-based eligibility validation service."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from fastapi import HTTPException, status

from app.models.internship import Internship, InternshipSkill, InternshipStatus
from app.models.student import StudentProfile
from app.models.company import Company
from app.schemas.internship import (
    InternshipCreate,
    InternshipUpdate,
    InternshipEligibilityOut
)


class InternshipService:
    """Service handling internship CRUD, search filters, and eligibility assessment."""

    @staticmethod
    def create_internship(db: Session, data: InternshipCreate) -> Internship:
        """Create a new internship opportunity with required skills."""
        company = db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={data.company_id} does not exist"
            )

        internship = Internship(
            company_id=data.company_id,
            title=data.title.strip(),
            description=data.description.strip(),
            location=data.location.strip(),
            industry=data.industry.strip(),
            duration_weeks=data.duration_weeks,
            stipend=data.stipend,
            total_seats=data.total_seats,
            available_seats=data.total_seats,
            min_cgpa=data.min_cgpa,
            preferred_education=data.preferred_education,
            eligibility_criteria=data.eligibility_criteria,
            application_deadline=data.application_deadline,
            status=data.status
        )
        db.add(internship)
        db.flush()

        # Add required skills
        if data.skills:
            for s in data.skills:
                skill_record = InternshipSkill(
                    internship_id=internship.id,
                    skill_name=s.skill_name.strip(),
                    is_mandatory=s.is_mandatory,
                    weight=s.weight
                )
                db.add(skill_record)

        db.commit()
        db.refresh(internship)
        return internship

    @staticmethod
    def update_internship(db: Session, internship_id: int, data: InternshipUpdate) -> Internship:
        """Update an existing internship record."""
        internship = db.query(Internship).filter(Internship.id == internship_id).first()
        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Internship id={internship_id} not found"
            )

        update_dict = data.model_dump(exclude_unset=True)
        skills_data = update_dict.pop("skills", None)

        for field, value in update_dict.items():
            setattr(internship, field, value)

        # Replace skills if explicitly provided
        if skills_data is not None:
            db.query(InternshipSkill).filter(InternshipSkill.internship_id == internship.id).delete()
            for s in skills_data:
                skill_record = InternshipSkill(
                    internship_id=internship.id,
                    skill_name=s["skill_name"].strip(),
                    is_mandatory=s.get("is_mandatory", True),
                    weight=s.get("weight", 1.0)
                )
                db.add(skill_record)

        db.commit()
        db.refresh(internship)
        return internship

    @staticmethod
    def delete_internship(db: Session, internship_id: int) -> None:
        """Delete an internship record."""
        internship = db.query(Internship).filter(Internship.id == internship_id).first()
        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Internship id={internship_id} not found"
            )
        db.delete(internship)
        db.commit()

    @staticmethod
    def get_internship(db: Session, internship_id: int) -> Internship:
        """Retrieve internship with skills and company relation."""
        internship = db.query(Internship).filter(Internship.id == internship_id).first()
        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Internship id={internship_id} not found"
            )
        return internship

    @staticmethod
    def list_internships(
        db: Session,
        search: Optional[str] = None,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        min_stipend: Optional[float] = None,
        status_filter: Optional[InternshipStatus] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Internship], int]:
        """Search and filter internships with pagination."""
        query = db.query(Internship)

        if status_filter:
            query = query.filter(Internship.status == status_filter)

        if industry:
            query = query.filter(Internship.industry.ilike(f"%{industry}%"))

        if location:
            query = query.filter(Internship.location.ilike(f"%{location}%"))

        if min_stipend is not None:
            query = query.filter(Internship.stipend >= min_stipend)

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Internship.title.ilike(search_pattern),
                    Internship.description.ilike(search_pattern),
                    Internship.location.ilike(search_pattern),
                    Internship.industry.ilike(search_pattern)
                )
            )

        total = query.count()
        items = query.order_by(desc(Internship.created_at))\
                     .offset((page - 1) * page_size)\
                     .limit(page_size)\
                     .all()

        return items, total

    @classmethod
    def evaluate_eligibility(cls, profile: StudentProfile, internship: Internship) -> InternshipEligibilityOut:
        """Rule-based eligibility verification between a student profile and an internship."""
        reasons = []
        is_eligible = True

        # 1. Deadline verification
        now = datetime.now(timezone.utc)
        deadline_valid = True
        if internship.application_deadline:
            # Handle timezone-aware or naive datetimes gracefully
            deadline = internship.application_deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            if now > deadline:
                deadline_valid = False
                is_eligible = False
                reasons.append("Application deadline for this internship has passed.")

        # 2. Minimum CGPA threshold
        cgpa_satisfied = True
        if internship.min_cgpa > 0:
            student_cgpa = profile.cgpa or 0.0
            if student_cgpa < internship.min_cgpa:
                cgpa_satisfied = False
                is_eligible = False
                reasons.append(f"Requires minimum CGPA of {internship.min_cgpa}; student profile has {student_cgpa}.")

        # 3. Education / Degree matching
        education_satisfied = True
        if internship.preferred_education and profile.degree:
            pref_edu = [e.strip().lower() for e in internship.preferred_education.split(",")]
            student_deg = profile.degree.strip().lower()
            if not any(pref in student_deg or student_deg in pref for pref in pref_edu):
                education_satisfied = False
                # Soft requirement or warning unless configured strictly
                reasons.append(f"Preferred degrees are: {internship.preferred_education}. Student degree is: {profile.degree}.")

        # 4. Mandatory skills check
        student_skill_names = {s.skill_name.lower().strip() for s in profile.skills}
        matched_mandatory = []
        missing_mandatory = []

        for req_skill in internship.skills:
            if req_skill.is_mandatory:
                if req_skill.skill_name.lower().strip() in student_skill_names:
                    matched_mandatory.append(req_skill.skill_name)
                else:
                    missing_mandatory.append(req_skill.skill_name)

        if missing_mandatory:
            is_eligible = False
            reasons.append(f"Missing mandatory skills: {', '.join(missing_mandatory)}.")

        # 5. Seat availability check
        if internship.available_seats <= 0:
            is_eligible = False
            reasons.append("No seats currently available for this internship.")

        if is_eligible and not reasons:
            reasons.append("Student satisfies all mandatory eligibility criteria for this internship.")

        return InternshipEligibilityOut(
            internship_id=internship.id,
            is_eligible=is_eligible,
            reasons=reasons,
            missing_mandatory_skills=missing_mandatory,
            matched_mandatory_skills=matched_mandatory,
            cgpa_satisfied=cgpa_satisfied,
            education_satisfied=education_satisfied,
            deadline_valid=deadline_valid
        )
