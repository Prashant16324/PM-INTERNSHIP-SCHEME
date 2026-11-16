"""Company organization management router."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.dependencies import require_admin_or_company, get_current_user
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut

router = APIRouter(prefix="/companies", tags=["Companies & Employers"])


@router.get("", response_model=APIResponse[PaginatedResponse[CompanyOut]])
def list_companies(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all registered partner companies with optional name/industry search."""
    query = db.query(Company)
    if search:
        query = query.filter(Company.company_name.ilike(f"%{search.strip()}%"))

    total = query.count()
    items = query.order_by(desc(Company.created_at))\
                 .offset((page - 1) * page_size)\
                 .limit(page_size)\
                 .all()

    return APIResponse(
        success=True,
        message="Companies retrieved successfully",
        data=PaginatedResponse(
            items=[CompanyOut.model_validate(c) for c in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 1
        )
    )


@router.get("/{company_id}", response_model=APIResponse[CompanyOut])
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Retrieve company details by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id={company_id} not found"
        )
    return APIResponse(
        success=True,
        message="Company retrieved successfully",
        data=CompanyOut.model_validate(company)
    )


@router.post("", response_model=APIResponse[CompanyOut], status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    current_user: User = Depends(require_admin_or_company),
    db: Session = Depends(get_db)
):
    """Create a new partner company profile."""
    company = Company(
        user_id=current_user.id if current_user.role == UserRole.COMPANY else None,
        company_name=payload.company_name.strip(),
        industry=payload.industry.strip(),
        description=payload.description,
        website=payload.website,
        location=payload.location.strip(),
        is_verified=True if current_user.role == UserRole.ADMIN else False
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return APIResponse(
        success=True,
        message="Company created successfully",
        data=CompanyOut.model_validate(company)
    )


@router.put("/{company_id}", response_model=APIResponse[CompanyOut])
def update_company(
    company_id: int,
    payload: CompanyUpdate,
    current_user: User = Depends(require_admin_or_company),
    db: Session = Depends(get_db)
):
    """Update company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id={company_id} not found"
        )

    # If role is COMPANY, verify ownership
    if current_user.role == UserRole.COMPANY and company.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own company profile"
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return APIResponse(
        success=True,
        message="Company updated successfully",
        data=CompanyOut.model_validate(company)
    )
