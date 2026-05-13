# Exception handlers for FastAPI
import logging
import traceback
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.core.schemas.error import ProblemDetail, create_problem_response, ValidationError

# Configure logging
logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handler for custom application exceptions (AppException and subclasses).
    
    Returns RFC 7807 Problem Details format.
    """
    logger.warning(
        f"App exception: {exc.title} - {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    problem_detail = exc.to_problem_detail()
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_detail,
    )


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    """
    Handler for FastAPI HTTPException.
    
    Converts HTTPException to RFC 7807 format.
    """
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    problem_detail = create_problem_response(
        status_code=exc.status_code,
        title=exc.__class__.__name__,
        detail=exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_detail,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors (RequestValidationError).
    
    Returns RFC 7807 format with detailed field errors.
    """
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    # Convert Pydantic validation errors to our format
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(ValidationError(
            field=field,
            message=error["msg"],
            code=error.get("type", "validation_error")
        ))
    
    problem_detail = create_problem_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        title="Validation Error",
        detail="Request validation failed",
        error_type="https://api.foodstore.com/errors/validation-error",
        errors=[e.model_dump() for e in errors],
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=problem_detail,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.
    
    Returns generic 500 error in production, detailed error in development.
    """
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        }
    )
    
    # In development, include more details
    detail = "An internal server error occurred"
    
    # Check if we're in debug mode (could be added to settings)
    # For now, use generic message for security
    
    problem_detail = create_problem_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title="Internal Server Error",
        detail=detail,
        error_type="https://api.foodstore.com/errors/internal-error",
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem_detail,
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy database errors.
    
    Returns 503 Service Unavailable for database errors.
    """
    logger.error(
        f"Database error: {type(exc).__name__}: {str(exc)}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    problem_detail = create_problem_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        title="Service Unavailable",
        detail="Database service is temporarily unavailable",
        error_type="https://api.foodstore.com/errors/service-unavailable",
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=problem_detail,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Call this in main.py after creating the app instance.
    """
    # Custom application exceptions
    app.add_exception_handler(AppException, app_exception_handler)
    
    # FastAPI built-in exceptions
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)