"""Application lifecycle and status state machine service."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.student import StudentProfile
from app.models.user import User, UserRole
from app.schemas.application import ApplicationCreate
from app.services.matching_service import MatchingEngine


class ApplicationService:
    """Service handling application submission, duplicate prevention, and state transitions."""

    @classmethod
    def apply_for_internship(
        cls,
        db: Session,
        profile: StudentProfile,
        data: ApplicationCreate
    ) -> Application:
        """Submit a new internship application after verifying eligibility and duplicate guards."""
        internship = db.query(Internship).filter(Internship.id == data.internship_id).first()
        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Internship id={data.internship_id} not found"
            )

        if internship.status != InternshipStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This internship is not accepting applications at this time."
            )

        if internship.available_seats <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available seats remaining for this internship."
            )

        # Check deadline
        if internship.application_deadline:
            deadline = internship.application_deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > deadline:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Application deadline for this internship has passed."
                )

        # Duplicate check: student cannot reapply unless previous was withdrawn
        existing_app = db.query(Application).filter(
            Application.student_profile_id == profile.id,
            Application.internship_id == internship.id
        ).first()

        if existing_app:
            if existing_app.status == ApplicationStatus.WITHDRAWN:
                # Reopen application
                existing_app.status = ApplicationStatus.SUBMITTED
                existing_app.cover_letter = data.cover_letter
                existing_app.applied_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(existing_app)
                return existing_app
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"You have already applied for this internship (Status: {existing_app.status.value})."
                )

        # Compute AI match score for record
        overall_score, _, _, _, _, is_eligible, _, _, _ = MatchingEngine.evaluate_match(profile, internship)

        new_application = Application(
            student_profile_id=profile.id,
            internship_id=internship.id,
            status=ApplicationStatus.SUBMITTED,
            match_score=overall_score,
            cover_letter=data.cover_letter
        )
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        return new_application

    @classmethod
    def withdraw_application(
        cls,
        db: Session,
        profile: StudentProfile,
        application_id: int
    ) -> Application:
        """Allow candidate to withdraw an application if not already allocated."""
        app_record = db.query(Application).filter(
            Application.id == application_id,
            Application.student_profile_id == profile.id
        ).first()

        if not app_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found on this profile"
            )

        if app_record.status == ApplicationStatus.ALLOCATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot withdraw an application that has already been allocated."
            )

        app_record.status = ApplicationStatus.WITHDRAWN
        db.commit()
        db.refresh(app_record)
        return app_record

    @classmethod
    def update_application_status(
        cls,
        db: Session,
        application_id: int,
        new_status: ApplicationStatus,
        actor: User
    ) -> Application:
        """Update candidate application status with role-based permission validation."""
        app_record = db.query(Application).filter(Application.id == application_id).first()
        if not app_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application id={application_id} not found"
            )

        # If actor is COMPANY, verify ownership of internship
        if actor.role == UserRole.COMPANY:
            if app_record.internship.company.user_id != actor.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only manage applications for internships posted by your company"
                )

        app_record.status = new_status
        db.commit()
        db.refresh(app_record)
        return app_record

    @classmethod
    def list_student_applications(cls, db: Session, profile: StudentProfile) -> List[Application]:
        """Fetch all applications submitted by a student."""
        return db.query(Application)\
                 .filter(Application.student_profile_id == profile.id)\
                 .order_by(desc(Application.applied_at))\
                 .all()

    @classmethod
    def list_internship_applications(
        cls,
        db: Session,
        internship_id: int,
        status_filter: Optional[ApplicationStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Application], int]:
        """Paginated list of applications for a specific internship posting."""
        query = db.query(Application).filter(Application.internship_id == internship_id)

        if status_filter:
            query = query.filter(Application.status == status_filter)

        total = query.count()
        items = query.order_by(desc(Application.match_score), desc(Application.applied_at))\
                     .offset((page - 1) * page_size)\
                     .limit(page_size)\
                     .all()

        return items, total
