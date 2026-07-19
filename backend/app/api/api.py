from fastapi import APIRouter
from app.api.endpoints import preview, mask, auth, jobs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(preview.router, tags=["preview"])
api_router.include_router(mask.router, tags=["mask"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

