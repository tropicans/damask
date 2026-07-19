from fastapi import APIRouter
from app.api.endpoints import preview, mask

api_router = APIRouter()
api_router.include_router(preview.router, tags=["preview"])
api_router.include_router(mask.router, tags=["mask"])
