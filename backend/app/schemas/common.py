"""Common API response and pagination schemas."""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized top-level API envelope."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None


class PaginationParams(BaseModel):
    """Pagination query parameter validation."""
    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination wrapper for list endpoints."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
