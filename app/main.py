import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import Base, engine, ensure_database_exists
from app.core.middleware import SecurityHeadersMiddleware, RequestLoggingMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.core.exceptions import EHISEXception
from app.api.v1.api import api_router
from seed import seed_database

setup_logging()
logger = logging.getLogger("ehis")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ensure_database_exists()
        Base.metadata.create_all(bind=engine)
        seed_database()
    except Exception as e:
        logger.warning(f"Startup check: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Healthcare Information System — Full Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

@app.exception_handler(EHISEXception)
async def ehis_exception_handler(request: Request, exc: EHISEXception):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An error occurred", "error": str(exc)}
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/metrics", tags=["Health"])
def metrics():
    from app.cache.redis_client import redis_cache
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "redis_available": redis_cache.is_available,
        "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
        "mfa_enabled": settings.MFA_ENABLED,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
