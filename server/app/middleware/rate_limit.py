"""Redis-based rate limiting middleware."""
import logging
from typing import Callable

from fastapi import HTTPException, Request, Response, status
from redis import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    
    Limits requests per IP address using a sliding window algorithm.
    """
    
    # Stricter limits for auth endpoints
    AUTH_ENDPOINTS = {"/v1/auth/login", "/v1/auth/signup"}
    AUTH_LIMIT = 10  # requests per minute for auth endpoints
    
    def __init__(self, app, redis_client: Redis | None = None, requests_per_minute: int = 60):
        super().__init__(app)
        self.redis_client = redis_client
        self.requests_per_minute = requests_per_minute
        self.enabled = redis_client is not None
        
        if not self.enabled:
            logger.warning("Rate limiting disabled - Redis client not available")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting if disabled or for health endpoints
        if not self.enabled or request.url.path in ["/health", "/healthz", "/readyz", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier (IP address)
        # TODO: Add X-Forwarded-For support with trusted proxy list
        client_ip = request.client.host if request.client else "unknown"
        
        # Determine limit based on endpoint
        limit = self.AUTH_LIMIT if request.url.path in self.AUTH_ENDPOINTS else self.requests_per_minute
        
        # Create rate limit key including HTTP method
        key = f"rate_limit:{client_ip}:{request.method}:{request.url.path}"
        global_key = f"rate_limit:{client_ip}:global"
        
        try:
            # Check both per-endpoint and global limits
            current = self.redis_client.incr(key)
            global_current = self.redis_client.incr(global_key)
            
            # Set expiry on first request
            if current == 1:
                self.redis_client.expire(key, 60)  # 1 minute window
            if global_current == 1:
                self.redis_client.expire(global_key, 60)
            
            # Check if per-endpoint limit exceeded
            if current > limit:
                ttl = self.redis_client.ttl(key)
                # Clamp negative TTL values (Redis returns -1 or -2 if key doesn't exist or has no expiry)
                ttl = max(0, ttl)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
                    headers={"Retry-After": str(ttl)}
                )
            
            # Check if global limit exceeded (2x the default)
            if global_current > self.requests_per_minute * 2:
                ttl = self.redis_client.ttl(global_key)
                ttl = max(0, ttl)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Global rate limit exceeded. Try again in {ttl} seconds.",
                    headers={"Retry-After": str(ttl)}
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request on error to prevent service disruption
            return await call_next(request)


def get_redis_client() -> Redis | None:
    """Get Redis client for rate limiting."""
    try:
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()  # Test connection
        logger.info(f"Connected to Redis at {settings.redis_url}")
        return client
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}. Rate limiting will be disabled.")
        return None
