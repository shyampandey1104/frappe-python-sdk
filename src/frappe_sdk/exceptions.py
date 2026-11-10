"""Custom exceptions for Frappe Python SDK."""

from typing import Any, Optional


class FrappeException(Exception):
    """Base exception for all Frappe SDK errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(FrappeException):
    """Raised when authentication fails (invalid API key/secret or session)."""
    pass


class PermissionDeniedError(FrappeException):
    """Raised when user lacks permission to access or modify a resource (403)."""
    pass


class DocTypeNotFoundError(FrappeException):
    """Raised when the specified DocType does not exist (404)."""
    pass


class DocumentNotFoundError(FrappeException):
    """Raised when a specific document name/ID is not found (404)."""
    pass


class ValidationError(FrappeException):
    """Raised when Frappe validation or mandatory field rule fails (417/400)."""
    pass


class RateLimitError(FrappeException):
    """Raised when Frappe rate limits the request (429)."""
    pass


class ServerError(FrappeException):
    """Raised when Frappe encounters an internal server error (500)."""
    pass
