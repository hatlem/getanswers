import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.database import close_db
from app.core.exceptions import AppException
from app.core.logging import setup_logging, log_request, log_error
from app.api import auth, queue, gmail, outlook, smtp, stats, conversations, billing, admin, organizations, lead_magnets
from app.api.platform import leads as platform_leads

# Initialize logging
logger = setup_logging(environment=settings.ENVIRONMENT, log_level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and logging
    logger.info("Starting GetAnswers API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: {settings.VERSION}")

    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                traces_sample_rate=0.1,
                release=settings.VERSION,
            )
            logger.info("Sentry integration enabled")
        except ImportError:
            logger.warning("Sentry DSN configured but sentry_sdk not installed")

    logger.info("Database migrations handled by Alembic on startup")

    yield

    # Shutdown: Close connections
    logger.info("Shutting down GetAnswers API...")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}", exc_info=True)


app = FastAPI(
    title="GetAnswers API",
    description="Agent-First Mailbox - Mission Control Backend",
    version=settings.VERSION,
    lifespan=lifespan,
)

# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    request_id = getattr(request.state, "request_id", None)
    user_id = getattr(request.state, "user_id", None)

    log_error(
        f"Application error: {exc.message}",
        error=exc,
        request_id=request_id,
        user_id=user_id,
        path=request.url.path,
        status_code=exc.status_code
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "request_id": request_id
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    request_id = getattr(request.state, "request_id", None)
    user_id = getattr(request.state, "user_id", None)

    log_error(
        f"Unhandled exception: {str(exc)}",
        error=exc,
        request_id=request_id,
        user_id=user_id,
        path=request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id
        }
    )


# ============================================================================
# Middleware
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    These headers help protect against common web vulnerabilities:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Enables browser XSS protection
    - Strict-Transport-Security: Forces HTTPS (production only)
    - Content-Security-Policy: Restricts resource loading (production only)
    - Referrer-Policy: Controls referrer information
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Only add HSTS in production (requires HTTPS)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Content Security Policy - strict security policy
        # Note: Modern frameworks like React/Vue may require nonces or hashes for inline scripts
        # If needed, use nonce-based CSP instead of unsafe-inline
        if settings.is_production:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Extract user ID if available (set by auth dependency)
        request.state.user_id = None

        # Start timer
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception and re-raise
            duration = time.time() - start_time
            log_error(
                f"Request failed: {request.method} {request.url.path}",
                error=e,
                request_id=request_id,
                duration=duration
            )
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Log request
        log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
            request_id=request_id,
            user_id=getattr(request.state, "user_id", None)
        )

        # Add request ID and response time to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"

        return response


# ============================================================================
# Middleware Configuration (order matters - add in reverse order of execution)
# ============================================================================

# 1. Security headers (outermost)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Request logging
app.add_middleware(RequestLoggingMiddleware)

# 3. Trusted host middleware (only in production)
if settings.is_production:
    # Extract allowed hosts from APP_URL
    # Adjust based on your production domain
    allowed_hosts = ["getanswers.co", "*.getanswers.co", "api.getanswers.co"]
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )

# 4. CORS configuration - allow frontend to make requests
# In production, only allow the specific frontend URL
# In development, allow common localhost ports
cors_origins = [settings.APP_URL]

if settings.is_development:
    cors_origins.extend([
        "http://localhost:5073",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5073",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(gmail.router, prefix="/api", tags=["Gmail OAuth"])
app.include_router(outlook.router, prefix="/api", tags=["Outlook OAuth"])
app.include_router(smtp.router, prefix="/api", tags=["SMTP Email"])
app.include_router(queue.router, prefix="/api/queue", tags=["Review Queue"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin (Super Admin Only)"])
app.include_router(lead_magnets.router, prefix="/api/lead-magnets", tags=["Lead Magnets"])
app.include_router(platform_leads.router, prefix="/api/platform", tags=["Platform Leads"])


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "GetAnswers API",
        "version": settings.VERSION,
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint with service status checks.

    Returns:
        Health status with individual service checks
    """
    from app.core.database import engine
    from app.core.redis import RedisClient

    checks = {
        "api": True,  # API is running if we reach this point
    }

    # Check database connection
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = True
        logger.debug("Database health check: OK")
    except Exception as e:
        checks["database"] = False
        logger.error(f"Database health check failed: {e}")

    # Check Redis connection
    try:
        redis_client = await RedisClient.get_client()
        await redis_client.ping()
        checks["redis"] = True
        logger.debug("Redis health check: OK")
    except Exception as e:
        checks["redis"] = False
        logger.error(f"Redis health check failed: {e}")

    # Overall health
    healthy = all(checks.values())
    status_code = 200 if healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if healthy else "unhealthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "checks": checks,
        }
    )
