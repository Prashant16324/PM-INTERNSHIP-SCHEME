"""User account and profile Pydantic validation schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100, description="Minimum 8 characters password")
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
