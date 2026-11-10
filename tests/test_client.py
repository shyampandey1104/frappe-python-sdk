"""Unit tests for Client error handling and mocked responses."""

import pytest
import httpx
from frappe_sdk.client import _handle_error_response
from frappe_sdk.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    DocumentNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)


def make_mock_response(status_code: int, content: dict) -> httpx.Response:
    req = httpx.Request("GET", "http://test.local/api/resource/Customer/CUST-001")
    return httpx.Response(status_code=status_code, json=content, request=req)


def test_auth_error_handling():
    resp = make_mock_response(401, {"message": "Invalid API Key"})
    with pytest.raises(AuthenticationError) as exc_info:
        _handle_error_response(resp)
    assert exc_info.value.status_code == 401


def test_not_found_handling():
    resp = make_mock_response(404, {"message": "Customer CUST-999 not found"})
    with pytest.raises(DocumentNotFoundError) as exc_info:
        _handle_error_response(resp)
    assert exc_info.value.status_code == 404


def test_validation_error_handling():
    resp = make_mock_response(417, {"message": "Mandatory field 'customer_name' missing"})
    with pytest.raises(ValidationError):
        _handle_error_response(resp)


def test_rate_limit_error():
    resp = make_mock_response(429, {"message": "Hourly request quota exceeded"})
    with pytest.raises(RateLimitError):
        _handle_error_response(resp)


def test_server_error_handling():
    resp = make_mock_response(500, {"exception": "OperationalError: MariaDB connection timeout"})
    with pytest.raises(ServerError):
        _handle_error_response(resp)
