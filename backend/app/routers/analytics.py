"""Administrative analytics, reporting, and dashboard metrics router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.analytics import AnalyticsDashboardResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Admin Analytics & Reporting"])


@router.get("/dashboard", response_model=APIResponse[AnalyticsDashboardResponse])
def get_admin_dashboard_metrics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve comprehensive platform metrics, distributions, seat utilization, and reporting data."""
    data = AnalyticsService.get_dashboard_analytics(db)
    return APIResponse(
        success=True,
        message="Analytics dashboard data retrieved successfully",
        data=data
    )
