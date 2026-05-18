# FastAPI application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Create FastAPI app instance
app = FastAPI(
    title="Food Store API",
    version="1.0.0",
    description="E-commerce API for Food Store",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
from app.core.handlers import register_exception_handlers
register_exception_handlers(app)

# Register rate limiting
from app.core.middleware.rate_limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Add limiter to app state for slowapi to work
app.state.limiter = limiter

# Register custom rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {"message": "Food Store API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Note: API routes will be mounted at /api/v1 in app/api/__init__.py
# Import and mount the router after app is created to avoid circular imports
from app.api import router as api_router

app.include_router(api_router, prefix="/api/v1")