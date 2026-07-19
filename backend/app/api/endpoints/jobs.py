from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from pydantic import BaseModel

from app.db import get_session
from app.models.user import User
from app.services.auth import get_current_user
from app.models.job import MaskingJob, JobDetail

router = APIRouter()

class JobStatsResponse(BaseModel):
    total_files: int
    total_rows: int
    success_rate: float

@router.get("/", response_model=List[MaskingJob])
def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get paginated history of masking jobs for the current logged-in user.
    """
    statement = (
        select(MaskingJob)
        .where(MaskingJob.user_id == current_user.id)
        .order_by(MaskingJob.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    results = session.exec(statement).all()
    return results

@router.get("/stats", response_model=JobStatsResponse)
def get_jobs_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get aggregate stats of masking jobs for the current logged-in user.
    """
    # Total files processed successfully
    success_stmt = (
        select(func.count(MaskingJob.id))
        .where(MaskingJob.user_id == current_user.id)
        .where(MaskingJob.status == "SUCCESS")
    )
    total_files = session.exec(success_stmt).one() or 0

    # Total rows sanitized successfully
    rows_stmt = (
        select(func.sum(MaskingJob.row_count))
        .where(MaskingJob.user_id == current_user.id)
        .where(MaskingJob.status == "SUCCESS")
    )
    total_rows = session.exec(rows_stmt).one() or 0

    # Success rate
    total_stmt = (
        select(func.count(MaskingJob.id))
        .where(MaskingJob.user_id == current_user.id)
    )
    total_jobs = session.exec(total_stmt).one() or 0

    if total_jobs > 0:
        success_rate = (total_files / total_jobs) * 100.0
    else:
        success_rate = 100.0

    return JobStatsResponse(
        total_files=total_files,
        total_rows=total_rows,
        success_rate=round(success_rate, 2)
    )

@router.get("/{job_id}/details", response_model=List[JobDetail])
def get_job_details(
    job_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get masking details (masked columns and their rules) for a specific job.
    Asserts ownership of the job.
    """
    # Fetch job first to check ownership
    job = session.get(MaskingJob, job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Pekerjaan penyamaran tidak ditemukan."
        )
    
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Anda tidak memiliki akses ke data pekerjaan penyamaran ini."
        )

    statement = select(JobDetail).where(JobDetail.job_id == job_id)
    details = session.exec(statement).all()
    return details
