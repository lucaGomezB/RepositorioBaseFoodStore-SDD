# Custom exception classes for Food Store API
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """
    Base exception class for application-specific errors.
    
    All custom exceptions should inherit from this class.
    Uses RFC 7807 Problem Details format.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        title: Optional[str] = None,
        error_type: Optional[str] = None,
        errors: Optional[list] = None,
    ):
        self.title = title or self._default_title(status_code)
        self.error_type = error_type or f"https://api.foodstore.com/errors/{self._default_type(status_code)}"
        self.errors = errors or []
        super().__init__(status_code=status_code, detail=detail)

    @staticmethod
    def _default_title(status_code: int) -> str:
        """Get default title based on HTTP status code."""
        titles = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            422: "Validation Error",
            500: "Internal Server Error",
            503: "Service Unavailable",
        }
        return titles.get(status_code, "Error")

    @staticmethod
    def _default_type(status_code: int) -> str:
        """Get default error type URI based on HTTP status code."""
        types = {
            400: "bad-request",
            401: "unauthorized",
            403: "forbidden",
            404: "not-found",
            422: "validation-error",
            500: "internal-error",
            503: "service-unavailable",
        }
        return types.get(status_code, "error")

    def to_problem_detail(self) -> Dict[str, Any]:
        """Convert exception to RFC 7807 Problem Details format."""
        result = {
            "type": self.error_type,
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
        }
        if self.errors:
            result["errors"] = self.errors
        return result


class NotFoundException(AppException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found", resource: Optional[str] = None):
        self.resource = resource
        error_type = f"https://api.foodstore.com/errors/not-found"
        if resource:
            error_type = f"https://api.foodstore.com/errors/{resource}-not-found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            title="Not Found",
            error_type=error_type,
        )


class ValidationException(AppException):
    """Exception raised when request validation fails."""

    def __init__(self, detail: str = "Validation failed", errors: Optional[list] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            title="Validation Error",
            error_type="https://api.foodstore.com/errors/validation-error",
            errors=errors,
        )


class UnauthorizedException(AppException):
    """Exception raised when authentication fails."""

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            title="Unauthorized",
            error_type="https://api.foodstore.com/errors/unauthorized",
        )


class ForbiddenException(AppException):
    """Exception raised when user lacks permission."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            title="Forbidden",
            error_type="https://api.foodstore.com/errors/forbidden",
        )


class ServiceUnavailableException(AppException):
    """Exception raised when service is temporarily unavailable."""

    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            title="Service Unavailable",
            error_type="https://api.foodstore.com/errors/service-unavailable",
        )


class BadRequestException(AppException):
    """Exception raised for invalid requests."""

    def __init__(self, detail: str = "Invalid request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            title="Bad Request",
            error_type="https://api.foodstore.com/errors/bad-request",
        )