# Rate limiting middleware using slowapi
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.schemas.error import create_problem_response


# Initialize limiter with IP-based rate limiting
limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_key(request: Request) -> str:
    """Get the rate limit key based on client IP."""
    return get_remote_address(request)


@limiter.limit(f"{settings.RATE_LIMIT_LOGIN_REQUESTS}/minute")
async def login_rate_limit(request: Request):
    """Rate limit decorator for login endpoint."""
    pass  # The decorator handles the limiting


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    Returns RFC 7807 Problem Details format.
    """
    return JSONResponse(
        status_code=429,
        content=create_problem_response(
            status_code=429,
            title="Too Many Requests",
            detail=f"Rate limit exceeded. Try again in {settings.RATE_LIMIT_LOGIN_WINDOW} minutes.",
            error_type="https://api.foodstore.com/errors/rate-limit-exceeded",
        ),
        headers={
            "X-RateLimit-Limit": str(settings.RATE_LIMIT_LOGIN_REQUESTS),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(settings.RATE_LIMIT_LOGIN_WINDOW * 60),
        },
    )


def init_rate_limiting(app: FastAPI) -> None:
    """
    Initialize rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Add limiter to app state
    app.state.limiter = limiter
    
    # Add SlowAPIMiddleware — reads limiter from app.state.limiter
    app.add_middleware(SlowAPIMiddleware)
    
    # Register custom rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


def add_rate_limit_headers(response, request: Request, limit: str) -> None:
    """
    Add rate limit headers to response.
    
    Args:
        response: FastAPI response
        request: Request object
        limit: Rate limit string (e.g., "5/minute")
    """
    # Get current limiter from app state
    if hasattr(request.app.state, "limiter"):
        # This would need actual implementation to get current counts
        # For now, we'll set reasonable defaults
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_LOGIN_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(max(0, settings.RATE_LIMIT_LOGIN_REQUESTS - 1))
        response.headers["X-RateLimit-Reset"] = str(settings.RATE_LIMIT_LOGIN_WINDOW * 60)