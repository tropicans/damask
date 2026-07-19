"""
Main module for the SecureData Web FastAPI application.
Initializes the API app, CORS middleware, and includes API routers.
"""

import logging
import secrets
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.api import api_router
from app.db import init_db
from app.services.auth import AuthException
from app.core.limiter import limiter

setup_logging()
logger = logging.getLogger("app.main")

app = FastAPI(title=settings.PROJECT_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude safe methods from verification, but set CSRF cookie if not present
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            response = await call_next(request)
            if not request.cookies.get("secure_data_csrf"):
                csrf_token = secrets.token_urlsafe(32)
                response.set_cookie(
                    key="secure_data_csrf",
                    value=csrf_token,
                    httponly=False,  # Accessible to client JS
                    secure=settings.COOKIE_SECURE,
                    samesite="lax",
                    max_age=86400,
                    domain=None
                )
            return response

        # Exclude public auth routes from validation
        if request.url.path.rstrip('/') in ["/api/auth/login", "/api/auth/register"]:
            return await call_next(request)

        # Validate CSRF token for mutating methods only if session cookie is present (cookie-based auth)
        if request.cookies.get("secure_data_session"):
            csrf_cookie = request.cookies.get("secure_data_csrf")
            csrf_header = request.headers.get("X-CSRF-Token")

            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token validation failed."}
                )

        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    response = JSONResponse(
        status_code=401,
        content={"detail": exc.detail}
    )
    response.delete_cookie(
        key="secure_data_session",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=None
    )
    return response

# Register CSRFMiddleware before CORSMiddleware
app.add_middleware(CSRFMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    """
    Simple health check endpoint to verify backend status.
    Returns:
        dict: Success message status.
    """
    return {"status": "success"}

@app.on_event("startup")
def startup_event():
    """
    App startup event handler. Logs configuration and initializes the SQLite database.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} backend server...")
    logger.info(f"CORS origins configured: {settings.cors_origins}")
    logger.info("Initializing database...")
    init_db()

