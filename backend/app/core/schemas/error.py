# RFC 7807 Problem Details Schema
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ValidationError(BaseModel):
    """Individual validation error detail."""
    field: str = Field(..., description="The field that failed validation")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Error code for programmatic handling")


class ProblemDetail(BaseModel):
    """
    RFC 7807 Problem Details response schema.
    
    Standard format for error responses across the API.
    """
    type: str = Field(
        ...,
        description="URI reference that identifies the problem type",
        json_schema_extra={"example": "https://api.foodstore.com/errors/not-found"}
    )
    title: str = Field(
        ...,
        description="Human-readable summary of the problem",
        json_schema_extra={"example": "Not Found"}
    )
    status: int = Field(
        ...,
        description="HTTP status code",
        json_schema_extra={"example": 404}
    )
    detail: str = Field(
        ...,
        description="Human-readable explanation specific to this occurrence of the problem",
        json_schema_extra={"example": "Product with ID 123 not found"}
    )
    errors: Optional[List[ValidationError]] = Field(
        default=None,
        description="Array of validation errors (used for 422 responses)"
    )

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "type": "https://api.foodstore.com/errors/not-found",
            "title": "Not Found",
            "status": 404,
            "detail": "Product with ID 123 not found"
        }
    })


def create_problem_response(
    status_code: int,
    title: str,
    detail: str,
    error_type: Optional[str] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Helper function to create a Problem Details response dictionary.
    
    Args:
        status_code: HTTP status code
        title: Human-readable title
        detail: Specific error message
        error_type: URI reference for error type
        errors: List of validation errors
        
    Returns:
        Dictionary with RFC 7807 Problem Details format
    """
    if error_type is None:
        error_type = f"https://api.foodstore.com/errors/{title.lower().replace(' ', '-')}"
    
    response = {
        "type": error_type,
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    
    if errors:
        response["errors"] = errors
        
    return response