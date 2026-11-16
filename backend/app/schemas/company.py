"""Company profile Pydantic validation schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    industry: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=5000)
    website: Optional[str] = Field(None, max_length=255)
    location: str = Field(min_length=2, max_length=150)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=255)
    industry: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    is_verified: Optional[bool] = None


class CompanyOut(CompanyBase):
    id: int
    user_id: Optional[int] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
