"""
Authentication router module for SecureData Web.
Exposes endpoints for user registration (invite-based), user login (with lockout),
invite creation (admin-only), logout, and querying active user details.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select

from app.db import get_session
from app.models.user import User, UserRegister, UserLogin, UserResponse, Invite, InviteResponse
from app.services.auth import (
    hash_password, verify_password, create_access_token, get_current_user,
    validate_password_policy, is_ip_locked, record_failed_attempt, clear_failed_attempts,
)
from app.core.config import settings
from app.core.limiter import limiter

logger = logging.getLogger("app.api.endpoints.auth")

router = APIRouter()


@router.post("/invite", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
def create_invite(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Creates a one-time invite registration link. Admin only.
    The returned invite_url contains the token for the frontend registration flow.
    Args:
        request (Request): FastAPI request object.
        current_user (User): Authenticated user (must be admin).
        session (Session): SQLite database session.
    Raises:
        HTTPException 403: If the current user is not an admin.
    Returns:
        InviteResponse: Invite metadata including the full registration URL.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat membuat tautan undangan.",
        )
    expires_at = datetime.utcnow() + timedelta(hours=settings.INVITE_EXPIRE_HOURS)
    invite = Invite(created_by=current_user.id, expires_at=expires_at)
    session.add(invite)
    session.commit()
    session.refresh(invite)

    invite_url = f"{settings.FRONTEND_URL}/register?invite={invite.token}"
    logger.info(f"Invite created by admin {current_user.id}, token={invite.token}, expires={expires_at}")

    return InviteResponse(
        id=invite.id,
        token=invite.token,
        invite_url=invite_url,
        expires_at=invite.expires_at,
        is_used=invite.is_used,
        created_at=invite.created_at,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register_user(
    request: Request,
    user_in: UserRegister,
    response: Response,
    session: Session = Depends(get_session),
):
    """
    Registers a new user in the system using a valid invite token.
    Args:
        request (Request): FastAPI request object for rate limiting.
        user_in (UserRegister): Registration body including username, email, password, and invite_token.
        response (Response): FastAPI response to set cookies.
        session (Session): SQLite database session.
    Raises:
        HTTPException 400: If invite token is missing, invalid, used, or expired.
        HTTPException 400: If the email is already registered.
        HTTPException 422: If the password does not meet the policy requirements.
    Returns:
        UserResponse: The newly created User profile record.
    """
    # Validate invite token
    if not user_in.invite_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pendaftaran memerlukan kode undangan yang valid.",
        )

    invite_stmt = select(Invite).where(Invite.token == user_in.invite_token)
    invite = session.exec(invite_stmt).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode undangan tidak valid.",
        )
    if invite.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode undangan sudah digunakan.",
        )
    if datetime.utcnow() > invite.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode undangan sudah kadaluarsa.",
        )

    # Check if email already exists
    statement = select(User).where(User.email == user_in.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar.",
        )

    # Validate password policy before hashing
    try:
        validate_password_policy(user_in.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Hash password and save new user
    hashed = hash_password(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed,
        role=user_in.role or "user",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Mark invite as used
    invite.is_used = True
    invite.used_by = user.id
    session.add(invite)
    session.commit()

    logger.info(f"New user registered: {user.email} via invite {invite.id}")

    access_token = create_access_token(user_id=user.id)
    response.set_cookie(
        key="secure_data_session",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=86400,
        domain=None,
    )
    return user


@router.post("/login", response_model=UserResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    credentials: UserLogin,
    response: Response,
    session: Session = Depends(get_session),
):
    """
    Authenticates user credentials and sets a JWT access token in HttpOnly cookies.
    Implements brute-force protection: locks out IP after 5 failed attempts for 15 minutes.
    Args:
        request (Request): FastAPI request object for rate limiting and IP extraction.
        credentials (UserLogin): User login credentials containing email and password.
        response (Response): FastAPI response to set cookies.
        session (Session): SQLite database session.
    Raises:
        HTTPException 423: If the IP is temporarily locked due to too many failed attempts.
        HTTPException 400: If credentials are invalid.
    Returns:
        UserResponse: The authenticated user profile details.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Check lockout before processing credentials
    if is_ip_locked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Akun dikunci 15 menit karena terlalu banyak percobaan login. Silakan coba lagi nanti.",
        )

    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        record_failed_attempt(client_ip)
        logger.warning(f"Failed login attempt for email={credentials.email} from IP={client_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau kata sandi salah.",
        )

    # Successful login — clear lockout counter
    clear_failed_attempts(client_ip)
    logger.info(f"User logged in: {user.email} from IP={client_ip}")

    access_token = create_access_token(user_id=user.id)
    response.set_cookie(
        key="secure_data_session",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=86400,
        domain=None,
    )
    return user


@router.post("/logout")
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """
    Clears the HttpOnly session cookie and CSRF cookie to log the user out.
    """
    response.delete_cookie(
        key="secure_data_session",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=None,
    )
    response.delete_cookie(
        key="secure_data_csrf",
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=None,
    )
    return {"message": "Keluar berhasil"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves the currently authenticated user's profile.
    Args:
        current_user (User): Extracted user profile from the validated cookie.
    Returns:
        UserResponse: Current User profile record.
    """
    return current_user
