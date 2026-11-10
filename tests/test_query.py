"""Unit tests for QueryBuilder."""

import json
from frappe_sdk.query import QueryBuilder


def test_query_builder_params():
    qb = (
        QueryBuilder("Sales Order")
        .fields("name", "customer", "grand_total")
        .filter("docstatus", "=", 1)
        .filter("grand_total", ">", 5000)
        .order_by("grand_total", "desc")
        .limit(10, 20)
    )

    params = qb.to_params()

    assert json.loads(params["fields"]) == ["name", "customer", "grand_total"]
    filters = json.loads(params["filters"])
    assert len(filters) == 2
    assert filters[0] == ["docstatus", "=", 1]
    assert filters[1] == ["grand_total", ">", 5000]
    assert params["order_by"] == "grand_total desc"
    assert params["limit_page_length"] == "10"
    assert params["limit_start"] == "20"


def test_query_builder_filter_dict():
    qb = QueryBuilder("Customer").filter_dict({"customer_group": "Commercial", "disabled": 0})
    params = qb.to_params()
    filters = json.loads(params["filters"])
    assert ["customer_group", "=", "Commercial"] in filters
    assert ["disabled", "=", 0] in filters
