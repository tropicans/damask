from fastapi import APIRouter
from app.api.endpoints import preview

api_router = APIRouter()
api_router.include_router(preview.router, tags=["preview"])
