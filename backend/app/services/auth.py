import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.core.config import settings
from app.db import get_session
from app.models.user import User

class AuthException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

logger = logging.getLogger("app.services.auth")

security_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": user_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(
    request: Request,
    secure_data_session: Optional[str] = Cookie(None),
    session: Session = Depends(get_session)
) -> User:
    token = secure_data_session
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise AuthException("Token otentikasi tidak ditemukan.")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthException("Token otentikasi tidak valid atau telah kedaluwarsa.")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise AuthException("Token otentikasi tidak valid atau telah kedaluwarsa.")
    
    user = session.get(User, user_id)
    if user is None:
        raise AuthException("User tidak ditemukan.")
    return user
