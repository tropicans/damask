import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.api import api_router

setup_logging()
logger = logging.getLogger("app.main")

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "success"}

@app.on_event("startup")
def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} backend server...")
    logger.info(f"CORS origins configured: {settings.cors_origins}")
