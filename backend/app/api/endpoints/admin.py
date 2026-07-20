"""
Admin router module for SecureData Web.
Exposes endpoints for user management and login audit trails (admin only).
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from pydantic import BaseModel

from app.db import get_session
from app.models.user import User, UserResponse, LoginAudit, LoginAuditResponse
from app.services.auth import get_current_user

logger = logging.getLogger("app.api.endpoints.admin")

router = APIRouter()

class UserStatusUpdate(BaseModel):
    """
    Pydantic schema to update active status.
    """
    is_active: bool

class UserRoleUpdate(BaseModel):
    """
    Pydantic schema to update user roles.
    """
    role: str

class UserListResponse(BaseModel):
    """
    Pydantic schema for paginated user list.
    """
    items: List[UserResponse]
    total: int

class LoginAuditListResponse(BaseModel):
    """
    Pydantic schema for paginated login audit list.
    """
    items: List[LoginAuditResponse]
    total: int

@router.get("/users", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve list of users with pagination. Admin-only access.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin yang dapat mengakses manajemen user."
        )
    
    offset = (page - 1) * limit
    
    # Get total count
    count_stmt = select(func.count(User.id))
    total = session.exec(count_stmt).one() or 0
    
    # Get items
    stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    users = session.exec(stmt).all()
    
    return UserListResponse(items=users, total=total)

@router.put("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle a user's is_active status. Admin-only access.
    Prevents self-lockout if the admin is the only active admin in the system.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin yang dapat mengubah status user."
        )
        
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan."
        )
        
    # Prevent self-deactivation if only active admin
    if user.id == current_user.id and not status_update.is_active:
        active_admins_stmt = select(func.count(User.id)).where(User.role == "admin").where(User.is_active == True)
        active_admins_count = session.exec(active_admins_stmt).one() or 0
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tidak dapat menonaktifkan akun Anda sendiri karena Anda adalah satu-satunya admin aktif yang tersisa."
            )
            
    user.is_active = status_update.is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    
    logger.info(f"User {user.email} status updated to is_active={user.is_active} by admin {current_user.email}")
    return user

@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Promote or demote a user's role. Admin-only access.
    Prevents self-demotion if the admin is the only active admin in the system.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin yang dapat mengubah peran user."
        )
        
    if role_update.role not in ["admin", "auditor", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Peran tidak valid. Gunakan 'admin', 'auditor', atau 'user'."
        )
        
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan."
        )
        
    # Prevent self-demotion if only active admin
    if user.id == current_user.id and role_update.role != "admin":
        active_admins_stmt = select(func.count(User.id)).where(User.role == "admin").where(User.is_active == True)
        active_admins_count = session.exec(active_admins_stmt).one() or 0
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tidak dapat menurunkan peran Anda sendiri karena Anda adalah satu-satunya admin aktif yang tersisa."
            )
            
    user.role = role_update.role
    session.add(user)
    session.commit()
    session.refresh(user)
    
    logger.info(f"User {user.email} role updated to {user.role} by admin {current_user.email}")
    return user

@router.get("/login-audits", response_model=LoginAuditListResponse)
def list_login_audits(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Query paginated history of logins. Filterable by status ("SUCCESS" / "FAILED"). Admin-only access.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin yang dapat melihat riwayat login audit."
        )
        
    offset = (page - 1) * limit
    
    count_stmt = select(func.count(LoginAudit.id))
    if status_filter:
        count_stmt = count_stmt.where(LoginAudit.status == status_filter)
    total = session.exec(count_stmt).one() or 0
    
    stmt = select(LoginAudit).order_by(LoginAudit.created_at.desc())
    if status_filter:
        stmt = stmt.where(LoginAudit.status == status_filter)
    stmt = stmt.offset(offset).limit(limit)
    
    items = session.exec(stmt).all()
    return LoginAuditListResponse(items=items, total=total)
