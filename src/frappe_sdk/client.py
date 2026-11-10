"""Core Synchronous and Asynchronous Frappe REST API Clients."""

from typing import Any, Dict, List, Optional, Union
import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from frappe_sdk.exceptions import (
    AuthenticationError,
    DocTypeNotFoundError,
    DocumentNotFoundError,
    FrappeException,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from frappe_sdk.query import QueryBuilder


def _handle_error_response(response: httpx.Response) -> None:
    """Parse HTTP error response and raise specific SDK exception."""
    status = response.status_code
    message = response.text
    try:
        data = response.json()
        if isinstance(data, dict):
            if "exception" in data:
                message = data.get("exception", "")
            elif "_server_messages" in data:
                try:
                    msgs = json.loads(data["_server_messages"])
                    message = "; ".join([json.loads(m).get("message", "") for m in msgs])
                except Exception:
                    message = data.get("_server_messages", "")
            elif "message" in data:
                message = str(data["message"])
    except Exception:
        data = None

    if status == 401:
        raise AuthenticationError(f"Authentication failed: {message}", status_code=status, response_data=data)
    elif status == 403:
        raise PermissionDeniedError(f"Access forbidden: {message}", status_code=status, response_data=data)
    elif status == 404:
        raise DocumentNotFoundError(f"Resource not found: {message}", status_code=status, response_data=data)
    elif status in (400, 417):
        raise ValidationError(f"Validation error: {message}", status_code=status, response_data=data)
    elif status == 429:
        raise RateLimitError(f"Rate limit exceeded: {message}", status_code=status, response_data=data)
    elif status >= 500:
        raise ServerError(f"Frappe internal error: {message}", status_code=status, response_data=data)
    else:
        raise FrappeException(f"API Error [{status}]: {message}", status_code=status, response_data=data)


class FrappeClient:
    """Synchronous client for Frappe & ERPNext REST APIs."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if api_key and api_secret:
            headers["Authorization"] = f"token {api_key}:{api_secret}"
        elif token:
            headers["Authorization"] = f"token {token}"

        self._session = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl,
        )

    def __enter__(self) -> "FrappeClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._session.close()

    def query(self, doctype: str) -> QueryBuilder:
        """Create a fluent query builder for this doctype."""
        return QueryBuilder(doctype=doctype, client=self)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(ServerError),
        reraise=True,
    )
    def get_doc(self, doctype: str, name: str) -> Dict[str, Any]:
        """Fetch a single document by its primary name."""
        resp = self._session.get(f"/api/resource/{doctype}/{name}")
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", {})

    def get_list(
        self,
        doctype: str,
        fields: Optional[List[str]] = None,
        filters: Optional[List[Any]] = None,
        or_filters: Optional[List[Any]] = None,
        order_by: Optional[str] = None,
        limit_start: int = 0,
        limit_page_length: int = 20,
    ) -> List[Dict[str, Any]]:
        """List documents matching filter criteria."""
        params: Dict[str, str] = {
            "limit_start": str(limit_start),
            "limit_page_length": str(limit_page_length),
        }
        if fields:
            params["fields"] = json.dumps(fields)
        if filters:
            params["filters"] = json.dumps(filters)
        if or_filters:
            params["or_filters"] = json.dumps(or_filters)
        if order_by:
            params["order_by"] = order_by

        resp = self._session.get(f"/api/resource/{doctype}", params=params)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", [])

    def insert(self, doctype: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new document into Frappe."""
        resp = self._session.post(f"/api/resource/{doctype}", json=doc)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", {})

    def update(self, doctype: str, name: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document."""
        resp = self._session.put(f"/api/resource/{doctype}/{name}", json=doc)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", {})

    def delete(self, doctype: str, name: str) -> bool:
        """Delete a document by name."""
        resp = self._session.delete(f"/api/resource/{doctype}/{name}")
        if not resp.is_success:
            _handle_error_response(resp)
        return True

    def call(self, method: str, **kwargs) -> Any:
        """Call a whitelisted Frappe Python method (e.g. `frappe.client.get_value`)."""
        resp = self._session.post(f"/api/method/{method}", json=kwargs)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("message")

    def ping(self) -> str:
        """Test server connectivity and session validity."""
        return self.call("frappe.ping")


class AsyncFrappeClient:
    """Asynchronous client for high-concurrency Frappe & ERPNext integrations."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if api_key and api_secret:
            headers["Authorization"] = f"token {api_key}:{api_secret}"
        elif token:
            headers["Authorization"] = f"token {token}"

        self._session = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl,
        )

    async def __aenter__(self) -> "AsyncFrappeClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        await self._session.aclose()

    def query(self, doctype: str) -> QueryBuilder:
        return QueryBuilder(doctype=doctype, client=self)

    async def get_doc(self, doctype: str, name: str) -> Dict[str, Any]:
        resp = await self._session.get(f"/api/resource/{doctype}/{name}")
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", {})

    async def get_list(
        self,
        doctype: str,
        fields: Optional[List[str]] = None,
        filters: Optional[List[Any]] = None,
        or_filters: Optional[List[Any]] = None,
        order_by: Optional[str] = None,
        limit_start: int = 0,
        limit_page_length: int = 20,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, str] = {
            "limit_start": str(limit_start),
            "limit_page_length": str(limit_page_length),
        }
        if fields:
            params["fields"] = json.dumps(fields)
        if filters:
            params["filters"] = json.dumps(filters)
        if or_filters:
            params["or_filters"] = json.dumps(or_filters)
        if order_by:
            params["order_by"] = order_by

        resp = await self._session.get(f"/api/resource/{doctype}", params=params)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", [])

    async def insert(self, doctype: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        resp = await self._session.post(f"/api/resource/{doctype}", json=doc)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", {})

    async def update(self, doctype: str, name: str, doc: Dict[str, Any]) -> Dict[str, Any]:
        resp = await self._session.put(f"/api/resource/{doctype}/{name}", json=doc)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("data", {})

    async def delete(self, doctype: str, name: str) -> bool:
        resp = await self._session.delete(f"/api/resource/{doctype}/{name}")
        if not resp.is_success:
            _handle_error_response(resp)
        return True

    async def call(self, method: str, **kwargs) -> Any:
        resp = await self._session.post(f"/api/method/{method}", json=kwargs)
        if not resp.is_success:
            _handle_error_response(resp)
        return resp.json().get("message")
