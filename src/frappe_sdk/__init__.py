"""Frappe Python SDK - Modern Python Client for Frappe & ERPNext."""

from frappe_sdk.client import FrappeClient, AsyncFrappeClient
from frappe_sdk.query import QueryBuilder
from frappe_sdk.exceptions import (
    FrappeException,
    AuthenticationError,
    PermissionDeniedError,
    DocTypeNotFoundError,
    DocumentNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)
from frappe_sdk.models import FrappeBaseDoc, CustomerDoc, ItemDoc, FileAttachment

__version__ = "1.2.0"
__all__ = [
    "FrappeClient",
    "AsyncFrappeClient",
    "QueryBuilder",
    "FrappeException",
    "AuthenticationError",
    "PermissionDeniedError",
    "DocTypeNotFoundError",
    "DocumentNotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "FrappeBaseDoc",
    "CustomerDoc",
    "ItemDoc",
    "FileAttachment",
]
