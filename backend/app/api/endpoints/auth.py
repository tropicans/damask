"""
Authentication router module for SecureData Web.
Exposes endpoints for user registration, user login, and querying active user details.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from app.db import get_session
from app.models.user import User, UserRegister, UserLogin, UserResponse
from app.services.auth import hash_password, verify_password, create_access_token, get_current_user
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserRegister,
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Registers a new user in the system.
    Args:
        user_in (UserRegister): Registration body containing username, email, and password.
        response (Response): FastAPI response to set cookies.
        session (Session): SQLite database session.
    Raises:
        HTTPException 400: If the email is already registered.
    Returns:
        UserResponse: The newly created User profile record.
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_in.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar."
        )
    
    # Hash password and save new user
    hashed = hash_password(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    access_token = create_access_token(user_id=user.id)
    response.set_cookie(
        key="secure_data_session",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=86400,
        domain=None
    )
    return user

@router.post("/login", response_model=UserResponse)
def login(
    credentials: UserLogin,
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Authenticates user credentials and sets a JWT access token in HttpOnly cookies.
    Args:
        credentials (UserLogin): User login credentials containing email and password.
        response (Response): FastAPI response to set cookies.
        session (Session): SQLite database session.
    Raises:
        HTTPException 400: If credentials are invalid.
    Returns:
        UserResponse: The authenticated user profile details.
    """
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau kata sandi salah."
        )
    
    access_token = create_access_token(user_id=user.id)
    response.set_cookie(
        key="secure_data_session",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=86400,
        domain=None
    )
    return user

@router.post("/logout")
def logout(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """
    Clears the HttpOnly session cookie and CSRF cookie to log the user out.
    """
    response.delete_cookie(
        key="secure_data_session",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=None
    )
    response.delete_cookie(
        key="secure_data_csrf",
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=None
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
