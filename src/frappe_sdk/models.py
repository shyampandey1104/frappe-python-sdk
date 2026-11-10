"""Pydantic data models for Frappe documents and responses."""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class FrappeBaseDoc(BaseModel):
    """Base model for Frappe documents."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: Optional[str] = None
    owner: Optional[str] = None
    creation: Optional[datetime] = None
    modified: Optional[datetime] = None
    modified_by: Optional[str] = None
    docstatus: int = Field(default=0, description="0=Draft, 1=Submitted, 2=Cancelled")
    doctype: Optional[str] = None

    def to_frappe_payload(self) -> Dict[str, Any]:
        """Convert model into dictionary suitable for Frappe REST API."""
        return self.model_dump(exclude_unset=True, exclude_none=True)


class CustomerDoc(FrappeBaseDoc):
    """ERPNext Customer DocType representation."""
    customer_name: str
    customer_type: str = "Company"
    customer_group: Optional[str] = "All Customer Groups"
    territory: Optional[str] = "All Territories"
    email_id: Optional[str] = None
    mobile_no: Optional[str] = None


class ItemDoc(FrappeBaseDoc):
    """ERPNext Item DocType representation."""
    item_code: str
    item_name: Optional[str] = None
    item_group: Optional[str] = "All Item Groups"
    stock_uom: str = "Nos"
    is_stock_item: int = 1
    standard_rate: float = 0.0


class FileAttachment(BaseModel):
    """Model representing an uploaded file in Frappe."""
    file_name: str
    file_url: str
    attached_to_doctype: Optional[str] = None
    attached_to_name: Optional[str] = None
    is_private: int = 1


class PaginationMeta(BaseModel):
    """Metadata for paginated query results."""
    page: int = 1
    page_size: int = 20
    total_records: Optional[int] = None
    has_next: bool = False


class QueryResult(BaseModel, Generic[T]):
    """Standardized response container for list queries."""
    data: List[T]
    meta: PaginationMeta
