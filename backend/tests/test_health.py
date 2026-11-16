"""Direct tests for API health check and diagnostic endpoints."""

from app.routers.health import check_health


def test_health_check_endpoint(db_session):
    """Verify health check returns healthy status and DB connectivity."""
    data = check_health(db=db_session)
    assert data["status"] == "online"
    assert data["database"] == "healthy"
    assert "PM Internship Scheme" in data["app_name"]
