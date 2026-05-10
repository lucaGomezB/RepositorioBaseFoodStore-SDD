# API router configuration
from fastapi import APIRouter

# Create main API router
router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint for API v1."""
    return {"status": "ok", "service": "food-store-api-v1"}


@router.get("/")
def api_root():
    """API root endpoint."""
    return {"message": "Food Store API v1", "docs": "/docs"}