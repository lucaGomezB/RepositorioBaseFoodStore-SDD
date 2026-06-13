# Tests for custom exception classes
from fastapi import status
from app.core.exceptions import (
    AppException,
    NotFoundException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
    ServiceUnavailableException,
    BadRequestException,
)


class TestAppException:
    """Tests for the base AppException class."""

    def test_app_exception_default_values(self):
        """Test AppException has correct default values."""
        exc = AppException(status_code=400, detail="Test error")
        
        assert exc.status_code == 400
        assert exc.detail == "Test error"
        assert exc.title == "Bad Request"
        assert exc.error_type == "https://api.foodstore.com/errors/bad-request"

    def test_app_exception_custom_title(self):
        """Test AppException accepts custom title."""
        exc = AppException(
            status_code=400,
            detail="Test error",
            title="Custom Title"
        )
        
        assert exc.title == "Custom Title"

    def test_app_exception_custom_error_type(self):
        """Test AppException accepts custom error type URI."""
        exc = AppException(
            status_code=400,
            detail="Test error",
            error_type="https://example.com/custom-error"
        )
        
        assert exc.error_type == "https://example.com/custom-error"

    def test_app_exception_with_errors(self):
        """Test AppException can include validation errors."""
        errors = [
            {"field": "email", "message": "Invalid email format"}
        ]
        exc = AppException(
            status_code=422,
            detail="Validation failed",
            errors=errors
        )
        
        assert exc.errors == errors

    def test_to_problem_detail(self):
        """Test AppException.to_problem_detail returns RFC 7807 format."""
        exc = AppException(
            status_code=400,
            detail="Bad request",
            title="Bad Request",
            error_type="https://api.foodstore.com/errors/bad-request"
        )
        
        result = exc.to_problem_detail()
        
        assert result["type"] == "https://api.foodstore.com/errors/bad-request"
        assert result["title"] == "Bad Request"
        assert result["status"] == 400
        assert result["detail"] == "Bad request"

    def test_to_problem_detail_with_errors(self):
        """Test AppException.to_problem_detail includes errors array."""
        errors = [
            {"field": "name", "message": "Required"}
        ]
        exc = AppException(
            status_code=422,
            detail="Validation failed",
            errors=errors
        )
        
        result = exc.to_problem_detail()
        
        assert "errors" in result
        assert result["errors"] == errors


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_not_found_exception_default(self):
        """Test NotFoundException has correct defaults."""
        exc = NotFoundException()
        
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.title == "Not Found"
        assert exc.error_type == "https://api.foodstore.com/errors/not-found"

    def test_not_found_exception_custom_message(self):
        """Test NotFoundException accepts custom message."""
        exc = NotFoundException(detail="Product not found")
        
        assert exc.detail == "Product not found"

    def test_not_found_exception_with_resource(self):
        """Test NotFoundException can specify resource type."""
        exc = NotFoundException(detail="Product 123 not found", resource="product")
        
        assert exc.error_type == "https://api.foodstore.com/errors/product-not-found"


class TestValidationException:
    """Tests for ValidationException."""

    def test_validation_exception_default(self):
        """Test ValidationException has correct defaults."""
        exc = ValidationException()
        
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.title == "Validation Error"
        assert exc.error_type == "https://api.foodstore.com/errors/validation-error"

    def test_validation_exception_with_errors(self):
        """Test ValidationException can include field errors."""
        errors = [
            {"field": "email", "message": "Invalid format", "code": "invalid"},
            {"field": "password", "message": "Too short", "code": "min_length"}
        ]
        exc = ValidationException(detail="Validation failed", errors=errors)
        
        assert exc.errors == errors


class TestUnauthorizedException:
    """Tests for UnauthorizedException."""

    def test_unauthorized_exception_default(self):
        """Test UnauthorizedException has correct defaults."""
        exc = UnauthorizedException()
        
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.title == "Unauthorized"
        assert exc.error_type == "https://api.foodstore.com/errors/unauthorized"

    def test_unauthorized_exception_custom_message(self):
        """Test UnauthorizedException accepts custom message."""
        exc = UnauthorizedException(detail="Please login first")
        
        assert exc.detail == "Please login first"


class TestForbiddenException:
    """Tests for ForbiddenException."""

    def test_forbidden_exception_default(self):
        """Test ForbiddenException has correct defaults."""
        exc = ForbiddenException()
        
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.title == "Forbidden"
        assert exc.error_type == "https://api.foodstore.com/errors/forbidden"


class TestServiceUnavailableException:
    """Tests for ServiceUnavailableException."""

    def test_service_unavailable_exception_default(self):
        """Test ServiceUnavailableException has correct defaults."""
        exc = ServiceUnavailableException()
        
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.title == "Service Unavailable"
        assert exc.error_type == "https://api.foodstore.com/errors/service-unavailable"


class TestBadRequestException:
    """Tests for BadRequestException."""

    def test_bad_request_exception_default(self):
        """Test BadRequestException has correct defaults."""
        exc = BadRequestException()
        
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.title == "Bad Request"
        assert exc.error_type == "https://api.foodstore.com/errors/bad-request"