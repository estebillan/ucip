"""
Custom exceptions and error handlers for the Universal Consultant Intelligence Platform.

Provides comprehensive error handling with structured responses,
logging, and proper HTTP status codes.
"""

import traceback
from typing import Any, Dict, Optional

import structlog
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.core.config import settings

logger = structlog.get_logger(__name__)


class ConsultantPlatformException(Exception):
    """Base exception for all application-specific errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.correlation_id = correlation_id
        super().__init__(self.message)


class ValidationException(ConsultantPlatformException):
    """Exception for input validation errors."""
    
    def __init__(
        self,
        message: str = "Validation error",
        field_errors: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self.field_errors = field_errors or {}
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field_errors": self.field_errors},
            **kwargs
        )


class NotFoundError(ConsultantPlatformException):
    """Exception for resource not found errors."""
    
    def __init__(
        self,
        resource: str,
        resource_id: Any = None,
        **kwargs
    ):
        message = f"{resource} not found"
        if resource_id is not None:
            message += f" (ID: {resource_id})"
        
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "resource_id": resource_id},
            **kwargs
        )


class AuthenticationError(ConsultantPlatformException):
    """Exception for authentication errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )


class AuthorizationError(ConsultantPlatformException):
    """Exception for authorization errors."""
    
    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"resource": resource, "action": action},
            **kwargs
        )


class RateLimitError(ConsultantPlatformException):
    """Exception for rate limiting errors."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[str] = None,
        reset_time: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"limit": limit, "reset_time": reset_time},
            **kwargs
        )


class ExternalServiceError(ConsultantPlatformException):
    """Exception for external service errors."""
    
    def __init__(
        self,
        service: str,
        message: str = "External service error",
        service_status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message=f"{service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={
                "service": service,
                "service_status_code": service_status_code,
            },
            **kwargs
        )


class BusinessLogicError(ConsultantPlatformException):
    """Exception for business logic violations."""
    
    def __init__(
        self,
        message: str,
        business_rule: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"business_rule": business_rule},
            **kwargs
        )


class DatabaseError(ConsultantPlatformException):
    """Exception for database-related errors."""
    
    def __init__(
        self,
        message: str = "Database error",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation, "table": table},
            **kwargs
        )


class ConfigurationError(ConsultantPlatformException):
    """Exception for configuration errors."""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"config_key": config_key},
            **kwargs
        )


# Exception handlers
async def consultant_platform_exception_handler(
    request: Request,
    exc: ConsultantPlatformException
) -> JSONResponse:
    """Handle application-specific exceptions."""
    
    # Get correlation ID from request
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    # Log the exception
    logger.error(
        "Application exception",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        correlation_id=correlation_id,
        exc_info=settings.debug
    )
    
    # Prepare response
    response_data = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "status_code": exc.status_code,
        }
    }
    
    # Add details in debug mode or for validation errors
    if settings.debug or isinstance(exc, ValidationException):
        response_data["error"]["details"] = exc.details
    
    # Add correlation ID if available
    if correlation_id:
        response_data["correlation_id"] = correlation_id
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors."""
    
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    # Process validation errors
    field_errors = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        field_errors[field_path] = error["msg"]
    
    logger.warning(
        "Validation error",
        field_errors=field_errors,
        correlation_id=correlation_id
    )
    
    response_data = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": {
                "field_errors": field_errors
            }
        }
    }
    
    if correlation_id:
        response_data["correlation_id"] = correlation_id
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )


async def http_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle all other exceptions."""
    
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    # Handle HTTPException
    if isinstance(exc, HTTPException):
        logger.warning(
            "HTTP exception",
            status_code=exc.status_code,
            detail=exc.detail,
            correlation_id=correlation_id
        )
        
        response_data = {
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        }
        
        if correlation_id:
            response_data["correlation_id"] = correlation_id
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    # Handle unexpected exceptions
    logger.error(
        "Unexpected exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        correlation_id=correlation_id,
        exc_info=True
    )
    
    # Prepare error response
    if settings.debug:
        response_data = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "details": {
                    "exception_type": type(exc).__name__,
                    "traceback": traceback.format_exc()
                }
            }
        }
    else:
        response_data = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        }
    
    if correlation_id:
        response_data["correlation_id"] = correlation_id
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )


# Utility functions for raising common exceptions
def raise_not_found(resource: str, resource_id: Any = None) -> None:
    """Raise a not found exception."""
    raise NotFoundError(resource=resource, resource_id=resource_id)


def raise_validation_error(message: str, field_errors: Dict[str, Any] = None) -> None:
    """Raise a validation exception."""
    raise ValidationException(message=message, field_errors=field_errors)


def raise_business_error(message: str, business_rule: str = None) -> None:
    """Raise a business logic exception."""
    raise BusinessLogicError(message=message, business_rule=business_rule)


def raise_external_service_error(
    service: str,
    message: str,
    status_code: int = None
) -> None:
    """Raise an external service exception."""
    raise ExternalServiceError(
        service=service,
        message=message,
        service_status_code=status_code
    )