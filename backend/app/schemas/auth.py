"""Authentication requests, tokens, and registration schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserOut
from app.models.user import UserRole


class Token(BaseModel):
    """JWT response structure."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenData(BaseModel):
    """Extracted payload from validated JWT token."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(BaseModel):
    """JSON credentials payload for login."""
    email: EmailStr
    password: str = Field(min_length=1)


class StudentRegisterRequest(BaseModel):
    """Public registration request specifically for students."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100, description="Minimum 8 characters")
    full_name: str = Field(min_length=2, max_length=150)
    phone_number: Optional[str] = Field(None, max_length=20)
    college_name: Optional[str] = Field(None, max_length=255)
    degree: Optional[str] = Field(None, max_length=100, description="e.g. B.Tech, BCA, MCA")
    branch: Optional[str] = Field(None, max_length=100, description="e.g. Computer Science, AI & DS")
    graduation_year: Optional[int] = Field(None, ge=2020, le=2035)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
