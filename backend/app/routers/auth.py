"""Authentication and user session management router."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token, LoginRequest, StudentRegisterRequest
from app.schemas.user import UserOut
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.utils.security import create_access_token
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication & Authorization"])


@router.post("/register", response_model=APIResponse[UserOut], status_code=status.HTTP_201_CREATED)
def register_student(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    """Public registration endpoint for students under the PM Internship Scheme."""
    user = AuthService.register_student(db, payload)
    return APIResponse(
        success=True,
        message="Student registration successful. You can now log in.",
        data=UserOut.model_validate(user)
    )


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Standard JSON login endpoint returning a signed JWT access token."""
    user = AuthService.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    })

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )


@router.post("/token", response_model=Token)
def login_for_swagger_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password form endpoint for Swagger UI authorization button."""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    })

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )


@router.get("/me", response_model=APIResponse[UserOut])
def get_current_authenticated_user(current_user: User = Depends(get_current_user)):
    """Fetch currently logged-in user details and active role."""
    return APIResponse(
        success=True,
        message="User profile retrieved successfully",
        data=UserOut.model_validate(current_user)
    )
