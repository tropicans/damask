"""
User models module for SecureData Web.
Contains SQLModel definitions for database representation and Pydantic models for request/response schemas.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field as PydanticField
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    """
    SQLModel representation of the 'users' table.
    Stores registered user details with secure password hashes.
    """
    __tablename__ = "users"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        nullable=False
    )
    username: str = Field(index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(default="user", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class UserLogin(BaseModel):
    """
    Pydantic schema used for user login authentication requests.
    """
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """
    Pydantic schema for returning user profiles to the frontend.
    Omits secure password hashes for data protection.
    """
    id: str
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    """
    Pydantic schema returned upon successful user authentication.
    Contains the JWT access token and logged-in user profile.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """
    Pydantic schema representation of the decoded JWT payload data.
    """
    user_id: Optional[str] = None


class UserRegister(BaseModel):
    """
    Pydantic schema used for user registration requests.
    Validates password length and format of email address.
    """
    username: str = PydanticField(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = PydanticField(..., min_length=8, description="Password must be at least 8 characters long")
    role: Optional[str] = "user"
    invite_token: Optional[str] = None  # Required for invite-based registration


class Invite(SQLModel, table=True):
    """
    SQLModel representation of the 'invites' table.
    Stores admin-generated one-time registration invite tokens.
    """
    __tablename__ = "invites"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        nullable=False
    )
    token: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        unique=True,
        index=True,
        nullable=False
    )
    created_by: str = Field(foreign_key="users.id", nullable=False)
    used_by: Optional[str] = Field(default=None, foreign_key="users.id", nullable=True)
    expires_at: datetime = Field(nullable=False)
    is_used: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class InviteResponse(BaseModel):
    """
    Pydantic schema returned upon invite creation.
    Contains the invite token, the full registration URL, and metadata.
    """
    id: str
    token: str
    invite_url: str
    expires_at: datetime
    is_used: bool
    created_at: datetime

