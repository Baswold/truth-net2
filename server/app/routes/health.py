"""Health check and metrics endpoints."""
import time
from typing import Dict

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_session
from ..services.search import search_service

router = APIRouter(tags=["health"])

# Track application start time
_start_time = time.time()


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float


class ReadinessResponse(BaseModel):
    ready: bool
    checks: Dict[str, bool]
    details: Dict[str, str]


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Basic health check - always returns OK if server is running."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        uptime_seconds=round(time.time() - _start_time, 2)
    )


@router.get("/healthz", response_model=HealthResponse)
def healthz():
    """Kubernetes-style liveness probe."""
    return health_check()


@router.get("/readyz", response_model=ReadinessResponse)
def readiness_check(db: Session = Depends(get_session)):
    """Kubernetes-style readiness probe - checks dependencies."""
    checks = {}
    details = {}
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
        details["database"] = "Connected"
    except Exception as e:
        checks["database"] = False
        details["database"] = f"Error: {str(e)[:100]}"
    
    # Check MeiliSearch availability (optional)
    if search_service.is_available():
        checks["search"] = True
        details["search"] = "MeiliSearch available"
    else:
        checks["search"] = False
        details["search"] = "MeiliSearch unavailable (using DB fallback)"
    
    # Overall ready status - database must be up, search is optional
    ready = checks.get("database", False)
    
    return ReadinessResponse(
        ready=ready,
        checks=checks,
        details=details
    )


@router.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """
    Prometheus-compatible metrics endpoint.
    
    Returns metrics in Prometheus text exposition format.
    In production, consider using prometheus_fastapi_instrumentator
    or similar for full metrics integration.
    """
    uptime = time.time() - _start_time
    
    metrics_output = f"""# HELP truthnet_uptime_seconds Application uptime in seconds
# TYPE truthnet_uptime_seconds gauge
truthnet_uptime_seconds {uptime}

# HELP truthnet_info Application information
# TYPE truthnet_info gauge
truthnet_info{{version="0.1.0",environment="{settings.environment}"}} 1
"""
    
    return PlainTextResponse(
        content=metrics_output,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
