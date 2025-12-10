"""Custom exception classes for the application."""

from fastapi import status


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        """
        Initialize an application exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            details: Additional error details (dict)
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """Raised when user lacks permission for an action."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, resource_id: str = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} not found: {resource_id}"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(AppException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class ConflictError(AppException):
    """Raised when a resource conflict occurs (e.g., duplicate email)."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)


class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            "Rate limit exceeded",
            status.HTTP_429_TOO_MANY_REQUESTS,
            {"retry_after": retry_after}
        )


class ExternalServiceError(AppException):
    """Base exception for external service errors."""

    def __init__(self, service: str, message: str):
        super().__init__(
            f"{service} error: {message}",
            status.HTTP_502_BAD_GATEWAY,
            {"service": service}
        )


class GmailAPIError(ExternalServiceError):
    """Raised when Gmail API calls fail."""

    def __init__(self, message: str, details: dict = None):
        super().__init__("Gmail API", message)
        if details:
            self.details.update(details)


class ClaudeAPIError(ExternalServiceError):
    """Raised when Claude API calls fail."""

    def __init__(self, message: str, details: dict = None):
        super().__init__("Claude API", message)
        if details:
            self.details.update(details)


class DatabaseError(AppException):
    """Raised when database operations fail."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RedisError(AppException):
    """Raised when Redis operations fail."""

    def __init__(self, message: str = "Redis operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)
