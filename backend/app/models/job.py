"""
Job models module for SecureData Web.
Contains SQLModel definitions for tracking audit log metadata of masking jobs.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class MaskingJob(SQLModel, table=True):
    """
    SQLModel representation of the 'masking_jobs' table.
    Caches metadata for audit compliance, such as file name, file size, status, and row count.
    Does NOT store the file content itself.
    """
    __tablename__ = "masking_jobs"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: str = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        index=True,
        nullable=False
    )
    file_name: str = Field(nullable=False)
    file_size_bytes: int = Field(nullable=False)
    row_count: Optional[int] = Field(default=None, nullable=True)
    status: str = Field(nullable=False)  # "SUCCESS" or "FAILED"
    error_message: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class JobDetail(SQLModel, table=True):
    """
    SQLModel representation of the 'job_details' table.
    Tracks which column was masked under which strategy/rule for a particular job.
    """
    __tablename__ = "job_details"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        nullable=False
    )
    job_id: str = Field(
        foreign_key="masking_jobs.id",
        ondelete="CASCADE",
        index=True,
        nullable=False
    )
    column_name: str = Field(nullable=False)
    rule_name: str = Field(nullable=False)
