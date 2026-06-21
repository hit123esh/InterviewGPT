"""
InterviewGPT — FastAPI Application Entry Point

Main application with CORS, rate limiting, and all API routers.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.config import get_settings
from backend.database.session import init_db, engine
from sqlalchemy import text
import httpx

# Import routers
from backend.auth.router import router as auth_router
from backend.users.router import router as users_router
from backend.resumes.router import router as resumes_router
from backend.interviews.router import router as interviews_router
from backend.analytics.router import router as analytics_router
from backend.reports.router import router as reports_router
from backend.speech.router import router as speech_router
from backend.admin.router import router as admin_router

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 Starting InterviewGPT API...")
    
    # Initialize database tables
    await init_db()
    logger.info("✅ Database initialized")
    # Check Ollama connectivity if enabled
    if settings.USE_OLLAMA:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(settings.OLLAMA_URL.rstrip("/") + "/api/ping")
                if resp.status_code not in (200, 204):
                    logger.warning(f"Ollama ping returned {resp.status_code}; model calls may fail.")
                else:
                    logger.info("✅ Ollama server reachable")
        except Exception:
            logger.warning("Ollama server not reachable; falling back to mock LLM if configured.")
    
    # Create upload directory
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("./reports", exist_ok=True)
    
    logger.info("✅ InterviewGPT API is ready")
    yield
    
    logger.info("👋 Shutting down InterviewGPT API...")


# Create FastAPI app
app = FastAPI(
    title="InterviewGPT API",
    description="AI-Powered Mock Interview Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins = settings.BACKEND_CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    # Quick DB connectivity test
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "detail": "Database unreachable"})

    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# Register all routers under /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(resumes_router, prefix="/api/v1")
app.include_router(interviews_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(speech_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to InterviewGPT API",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }
