"""Authentication and user lifecycle business logic service."""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.schemas.auth import StudentRegisterRequest
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service handling user authentication, student registration, and admin seeding."""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Verify user credentials and return the active User record."""
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def register_student(db: Session, data: StudentRegisterRequest) -> User:
        """Register a new student account and initialize their student profile."""
        email_clean = data.email.lower().strip()
        existing_user = db.query(User).filter(User.email == email_clean).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists"
            )

        hashed_pwd = hash_password(data.password)
        new_user = User(
            email=email_clean,
            hashed_password=hashed_pwd,
            full_name=data.full_name.strip(),
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.flush()  # Obtain new_user.id

        # Calculate initial profile completion percentage
        completion_points = 20  # Base account created
        if data.phone_number:
            completion_points += 10
        if data.college_name:
            completion_points += 10
        if data.degree:
            completion_points += 10
        if data.branch:
            completion_points += 10

        new_profile = StudentProfile(
            user_id=new_user.id,
            phone_number=data.phone_number,
            college_name=data.college_name,
            degree=data.degree,
            branch=data.branch,
            graduation_year=data.graduation_year,
            profile_completion_percentage=completion_points,
            preferred_locations=[],
            preferred_industries=[]
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Successfully registered student user id={new_user.id} ({new_user.email})")
        return new_user

    @staticmethod
    def seed_initial_admin(db: Session) -> User:
        """Seed the system super administrator account if not present."""
        admin_email = settings.INITIAL_ADMIN_EMAIL.lower().strip()
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            return existing_admin

        hashed_pwd = hash_password(settings.INITIAL_ADMIN_PASSWORD)
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_pwd,
            full_name=settings.INITIAL_ADMIN_NAME,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"Initialized default system administrator: {admin_email}")
        return admin_user
