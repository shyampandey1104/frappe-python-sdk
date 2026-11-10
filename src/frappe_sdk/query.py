"""Fluent query builder for Frappe REST API."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
import json

if TYPE_CHECKING:
    from frappe_sdk.client import FrappeClient, AsyncFrappeClient


class QueryBuilder:
    """Fluent query builder for constructing Frappe `get_list` requests."""

    def __init__(self, doctype: str, client: Optional[Union["FrappeClient", "AsyncFrappeClient"]] = None):
        self.doctype = doctype
        self.client = client
        self._fields: List[str] = ["name"]
        self._filters: List[Any] = []
        self._or_filters: List[Any] = []
        self._order_by: Optional[str] = None
        self._limit_start: int = 0
        self._limit_page_length: int = 20

    def fields(self, *fields: str) -> "QueryBuilder":
        """Specify fields to fetch."""
        if len(fields) == 1 and isinstance(fields[0], (list, tuple)):
            self._fields = list(fields[0])
        else:
            self._fields = list(fields)
        return self

    def filter(self, field: str, operator: str, value: Any) -> "QueryBuilder":
        """Add a filter condition (e.g. `filter("status", "=", "Open")`)."""
        self._filters.append([field, operator, value])
        return self

    def filter_dict(self, filters: Dict[str, Any]) -> "QueryBuilder":
        """Add equality filters from a dictionary."""
        for k, v in filters.items():
            self._filters.append([k, "=", v])
        return self

    def or_filter(self, field: str, operator: str, value: Any) -> "QueryBuilder":
        """Add an OR filter condition."""
        self._or_filters.append([field, operator, value])
        return self

    def order_by(self, field: str, direction: str = "desc") -> "QueryBuilder":
        """Set order by clause (e.g. `creation desc`)."""
        self._order_by = f"{field} {direction.lower()}"
        return self

    def limit(self, limit: int, offset: int = 0) -> "QueryBuilder":
        """Set pagination limit and start offset."""
        self._limit_page_length = limit
        self._limit_start = offset
        return self

    def to_params(self) -> Dict[str, str]:
        """Compile query into HTTP GET parameters."""
        params: Dict[str, str] = {
            "fields": json.dumps(self._fields),
            "limit_start": str(self._limit_start),
            "limit_page_length": str(self._limit_page_length),
        }
        if self._filters:
            params["filters"] = json.dumps(self._filters)
        if self._or_filters:
            params["or_filters"] = json.dumps(self._or_filters)
        if self._order_by:
            params["order_by"] = self._order_by
        return params

    def run(self) -> List[Dict[str, Any]]:
        """Execute query synchronously using attached client."""
        if not self.client:
            raise ValueError("Cannot run query without attached FrappeClient")
        return self.client.get_list(self.doctype, **self._build_kwargs())

    async def run_async(self) -> List[Dict[str, Any]]:
        """Execute query asynchronously using attached AsyncFrappeClient."""
        if not self.client:
            raise ValueError("Cannot run async query without attached AsyncFrappeClient")
        return await self.client.get_list(self.doctype, **self._build_kwargs())

    def _build_kwargs(self) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "fields": self._fields,
            "limit_start": self._limit_start,
            "limit_page_length": self._limit_page_length,
        }
        if self._filters:
            kwargs["filters"] = self._filters
        if self._or_filters:
            kwargs["or_filters"] = self._or_filters
        if self._order_by:
            kwargs["order_by"] = self._order_by
        return kwargs
