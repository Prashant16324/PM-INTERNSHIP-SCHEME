"""Smart allocation engine with concurrency-safe seat management and duplicate prevention."""

import time
import logging
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from fastapi import HTTPException, status

from app.models.allocation import Allocation, AllocationStatus
from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.student import StudentProfile
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.allocation import AllocationOut, AllocationSummaryResponse
from app.services.internship_service import InternshipService

logger = logging.getLogger(__name__)


class AllocationEngine:
    """Core allocation engine managing fair seat assignment and transaction integrity."""

    @classmethod
    def run_allocation(
        cls,
        db: Session,
        admin_user: User,
        round_number: int = 1,
        min_score_threshold: float = 40.0,
        auto_confirm: bool = False
    ) -> AllocationSummaryResponse:
        """Execute the smart allocation algorithm with row locking and duplicate allocation prevention."""
        start_time = time.time()
        logger.info(f"Starting Allocation Round {round_number} initiated by user {admin_user.email}...")

        # Find all eligible candidates currently with active applications
        candidate_apps = db.query(Application).filter(
            Application.status.in_([
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.UNDER_REVIEW,
                ApplicationStatus.SHORTLISTED
            ]),
            Application.match_score >= min_score_threshold
        ).order_by(desc(Application.match_score)).all()

        total_evaluated = len(candidate_apps)
        allocated_records: List[Allocation] = []

        # Track students allocated across this run to prevent duplicate assignments
        already_allocated_student_ids = {
            a.student_profile_id for a in db.query(Allocation).filter(
                Allocation.status.in_([AllocationStatus.PROVISIONAL, AllocationStatus.CONFIRMED])
            ).all()
        }

        # Process applications in merit/compatibility order
        for app in candidate_apps:
            # Duplicate allocation guard
            if app.student_profile_id in already_allocated_student_ids:
                continue

            profile = app.student_profile

            # Concurrency control: Lock the internship row
            internship = db.query(Internship)\
                           .filter(Internship.id == app.internship_id)\
                           .with_for_update()\
                           .first()

            if not internship:
                continue

            # Check seat availability
            if internship.available_seats <= 0 or internship.status != InternshipStatus.OPEN:
                continue

            # Strict Eligibility Validation
            eligibility = InternshipService.evaluate_eligibility(profile, internship)
            if not eligibility.is_eligible:
                logger.info(f"Skipping allocation for student {profile.id} in internship {internship.id}: {eligibility.reasons}")
                continue

            # Assign seat
            alloc_status = AllocationStatus.CONFIRMED if auto_confirm else AllocationStatus.PROVISIONAL
            allocation_reason = (
                f"Round {round_number}: Ranked merit match score {app.match_score}%. "
                f"Eligible candidate allocated to available seat ({internship.available_seats}/{internship.total_seats})."
            )

            new_alloc = Allocation(
                application_id=app.id,
                student_profile_id=profile.id,
                internship_id=internship.id,
                allocation_round=round_number,
                allocated_by_user_id=admin_user.id,
                allocation_score=app.match_score,
                status=alloc_status,
                allocation_reason=allocation_reason,
                allocated_at=datetime.now(timezone.utc),
                confirmed_at=datetime.now(timezone.utc) if auto_confirm else None
            )
            db.add(new_alloc)

            # Decrement seats and update application status
            internship.available_seats -= 1
            app.status = ApplicationStatus.ALLOCATED

            # Mark student as allocated in this session
            already_allocated_student_ids.add(profile.id)
            allocated_records.append(new_alloc)

        # Audit log entry for administrative transparency
        audit = AuditLog(
            user_id=admin_user.id,
            action="RUN_SMART_ALLOCATION",
            target_type="ALLOCATION_ROUND",
            target_id=round_number,
            details={
                "round": round_number,
                "total_evaluated": total_evaluated,
                "total_allocated": len(allocated_records),
                "threshold": min_score_threshold,
                "auto_confirm": auto_confirm
            }
        )
        db.add(audit)
        db.commit()

        # Refresh all created allocation records with relationships loaded
        for alloc in allocated_records:
            db.refresh(alloc)

        execution_duration = round(time.time() - start_time, 3)
        logger.info(f"Allocation Round {round_number} completed in {execution_duration}s: {len(allocated_records)} seats assigned.")

        return AllocationSummaryResponse(
            round=round_number,
            total_applications_evaluated=total_evaluated,
            total_allocated_in_round=len(allocated_records),
            total_seats_filled=len(allocated_records),
            execution_time_seconds=execution_duration,
            allocations=[AllocationOut.model_validate(a) for a in allocated_records]
        )

    @classmethod
    def confirm_allocation(cls, db: Session, allocation_id: int, admin: User) -> Allocation:
        """Admin manually confirms a provisional allocation."""
        alloc = db.query(Allocation).filter(Allocation.id == allocation_id).first()
        if not alloc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allocation record id={allocation_id} not found"
            )

        alloc.status = AllocationStatus.CONFIRMED
        alloc.confirmed_at = datetime.now(timezone.utc)

        db.add(AuditLog(
            user_id=admin.id,
            action="CONFIRM_ALLOCATION",
            target_type="ALLOCATION",
            target_id=alloc.id,
            details={"previous_status": "PROVISIONAL", "new_status": "CONFIRMED"}
        ))
        db.commit()
        db.refresh(alloc)
        return alloc

    @classmethod
    def cancel_allocation(cls, db: Session, allocation_id: int, admin: User, reason: Optional[str] = None) -> Allocation:
        """Cancel an allocation, restore 1 available seat to the internship, and revert application."""
        alloc = db.query(Allocation).filter(Allocation.id == allocation_id).first()
        if not alloc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allocation record id={allocation_id} not found"
            )

        if alloc.status == AllocationStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Allocation is already cancelled"
            )

        # Restore seat
        internship = db.query(Internship).filter(Internship.id == alloc.internship_id).with_for_update().first()
        if internship:
            internship.available_seats = min(internship.total_seats, internship.available_seats + 1)

        # Revert application status
        if alloc.application:
            alloc.application.status = ApplicationStatus.UNDER_REVIEW

        alloc.status = AllocationStatus.CANCELLED
        alloc.allocation_reason = f"Cancelled by admin: {reason or 'No reason provided'}."

        db.add(AuditLog(
            user_id=admin.id,
            action="CANCEL_ALLOCATION",
            target_type="ALLOCATION",
            target_id=alloc.id,
            details={"restored_seats_to_internship": alloc.internship_id, "reason": reason}
        ))
        db.commit()
        db.refresh(alloc)
        return alloc

    @classmethod
    def list_allocations(
        cls,
        db: Session,
        round_number: Optional[int] = None,
        status_filter: Optional[AllocationStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Allocation], int]:
        """Paginated list of system allocations."""
        query = db.query(Allocation)

        if round_number:
            query = query.filter(Allocation.allocation_round == round_number)

        if status_filter:
            query = query.filter(Allocation.status == status_filter)

        total = query.count()
        items = query.order_by(desc(Allocation.allocated_at))\
                     .offset((page - 1) * page_size)\
                     .limit(page_size)\
                     .all()

        return items, total

    @classmethod
    def generate_csv_report(cls, db: Session, round_number: Optional[int] = None) -> str:
        """Generate a complete CSV report of all allocations."""
        import csv
        import io

        query = db.query(Allocation)
        if round_number:
            query = query.filter(Allocation.allocation_round == round_number)
        allocations = query.order_by(desc(Allocation.allocated_at)).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Allocation ID",
            "Round",
            "Status",
            "Match Score (%)",
            "Student Name",
            "Student Email",
            "College",
            "Degree",
            "Branch",
            "CGPA",
            "Internship Title",
            "Company Name",
            "Location",
            "Allocated At",
            "Confirmed At",
            "Allocation Reason"
        ])

        for a in allocations:
            student = a.student_profile
            user = student.user if student else None
            internship = a.internship
            company = internship.company if internship else None

            writer.writerow([
                a.id,
                a.allocation_round,
                a.status.value,
                a.allocation_score,
                user.full_name if user else "N/A",
                user.email if user else "N/A",
                (student.college_name or "N/A") if student else "N/A",
                (student.degree or "N/A") if student else "N/A",
                (student.branch or "N/A") if student else "N/A",
                student.cgpa if student and student.cgpa is not None else "N/A",
                internship.title if internship else "N/A",
                company.company_name if company else "N/A",
                internship.location if internship else "N/A",
                a.allocated_at.isoformat() if a.allocated_at else "",
                a.confirmed_at.isoformat() if a.confirmed_at else "",
                a.allocation_reason or ""
            ])

        return output.getvalue()
