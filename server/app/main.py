import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .config import settings
from .middleware import RequestLoggingMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware, get_redis_client
from .routes import (
    auth_router,
    sites_router,
    social_router,
    search_router,
    moderation_router,
    fact_check_router,
    feed_preference_router,
)
from .routes.health import router as health_router

# Configure logging
# For production, consider using python-json-logger for structured JSON logs
# Current format includes structured fields when available via middleware
class StructuredFormatter(logging.Formatter):
    """Custom formatter that includes extra fields if present."""
    def format(self, record):
        # Build base message
        msg = super().format(record)
        
        # Append extra fields if present
        extras = []
        for key in ['request_id', 'method', 'path', 'status_code', 'duration_ms', 'client_ip']:
            if hasattr(record, key):
                value = getattr(record, key)
                if value is not None:
                    extras.append(f"{key}={value}")
        
        if extras:
            msg = f"{msg} | {' | '.join(extras)}"
        
        return msg

handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter(
    '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

logging.basicConfig(level=logging.INFO, handlers=[handler])


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Truth Net - Verified Knowledge Platform"
    )

    # Add middleware (order matters - first added is outermost)
    # Security headers (outermost - applies to all responses)
    app.add_middleware(
        SecurityHeadersMiddleware,
        enable_hsts=(settings.environment == "production")
    )
    
    # Rate limiting (check limits early)
    redis_client = get_redis_client()
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client, requests_per_minute=60)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host validation (production)
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts if hasattr(settings, 'allowed_hosts') else ["*"]
        )

    # Register routers
    app.include_router(health_router)  # Health endpoints at root level
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(sites_router, prefix=settings.api_v1_prefix)
    app.include_router(social_router, prefix=settings.api_v1_prefix)
    app.include_router(search_router, prefix=settings.api_v1_prefix)
    app.include_router(moderation_router, prefix=settings.api_v1_prefix)
    app.include_router(fact_check_router, prefix=settings.api_v1_prefix)
    app.include_router(feed_preference_router, prefix=settings.api_v1_prefix)

    @app.get("/")
    def read_root():
        return {
            "status": "ok",
            "message": "Truth Net server online",
            "version": "0.1.0",
            "docs": "/docs"
        }

    return app


app = create_app()
