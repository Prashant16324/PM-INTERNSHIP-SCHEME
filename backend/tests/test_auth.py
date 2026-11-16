"""Tests for authentication, authorization, student registration, and security utilities."""

import pytest
from fastapi import HTTPException
from app.config import settings
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from app.schemas.auth import StudentRegisterRequest, LoginRequest
from app.routers.auth import register_student, login, get_current_authenticated_user
from app.models.user import UserRole
from app.dependencies import get_current_user


def test_password_hashing():
    """Verify bcrypt hash generation and validation."""
    raw = "SecureStudentPass123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decode():
    """Verify JWT token encoding and extraction."""
    payload = {"sub": "42", "email": "test@domain.com", "role": "STUDENT"}
    token = create_access_token(payload)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["email"] == "test@domain.com"
    assert decoded["role"] == "STUDENT"


def test_student_registration_success(db_session):
    """Test successful student registration and initial profile creation."""
    payload = StudentRegisterRequest(
        email="rahul.sharma@example.edu.in",
        password="Password123@",
        full_name="Rahul Sharma",
        phone_number="9876543210",
        college_name="Delhi Technological University",
        degree="B.Tech",
        branch="Computer Science & Engineering",
        graduation_year=2026
    )
    res = register_student(payload=payload, db=db_session)
    assert res.success is True
    assert res.data.email == "rahul.sharma@example.edu.in"
    assert res.data.role == UserRole.STUDENT
    assert res.data.is_active is True


def test_duplicate_registration_rejected(db_session):
    """Verify duplicate email registration is rejected with 409 Conflict."""
    payload = StudentRegisterRequest(
        email="duplicate@example.edu.in",
        password="Password123@",
        full_name="Aman Verma"
    )
    res = register_student(payload=payload, db=db_session)
    assert res.success is True

    # Second attempt with same email
    with pytest.raises(HTTPException) as exc_info:
        register_student(payload=payload, db=db_session)
    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


def test_student_login_success(db_session):
    """Verify student login issues valid JWT token and authenticates properly."""
    reg_payload = StudentRegisterRequest(
        email="sneha.patel@example.edu.in",
        password="SnehaSecure2026!",
        full_name="Sneha Patel"
    )
    register_student(payload=reg_payload, db=db_session)

    login_payload = LoginRequest(
        email="sneha.patel@example.edu.in",
        password="SnehaSecure2026!"
    )
    token_response = login(payload=login_payload, db=db_session)
    assert token_response.access_token is not None
    assert token_response.token_type == "bearer"
    assert token_response.user.email == "sneha.patel@example.edu.in"

    # Verify token decoding through get_current_user dependency
    user = get_current_user(token=token_response.access_token, db=db_session)
    assert user.email == "sneha.patel@example.edu.in"

    # Verify /me endpoint
    me_res = get_current_authenticated_user(current_user=user)
    assert me_res.success is True
    assert me_res.data.full_name == "Sneha Patel"


def test_login_invalid_password(db_session):
    """Verify invalid password raises 401 Unauthorized."""
    reg_payload = StudentRegisterRequest(
        email="vikram@example.edu.in",
        password="CorrectPassword123",
        full_name="Vikram Singh"
    )
    register_student(payload=reg_payload, db=db_session)

    bad_login = LoginRequest(
        email="vikram@example.edu.in",
        password="WrongPassword999"
    )
    with pytest.raises(HTTPException) as exc_info:
        login(payload=bad_login, db=db_session)
    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in exc_info.value.detail


def test_initial_super_admin_login(db_session):
    """Verify that seeded super admin account can authenticate immediately."""
    admin_login = LoginRequest(
        email=settings.INITIAL_ADMIN_EMAIL,
        password=settings.INITIAL_ADMIN_PASSWORD
    )
    token_response = login(payload=admin_login, db=db_session)
    assert token_response.user.role == UserRole.ADMIN
    assert token_response.user.email == settings.INITIAL_ADMIN_EMAIL
