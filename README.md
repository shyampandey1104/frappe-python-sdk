# ⚡ Frappe Python SDK

[![CI](https://github.com/shyampandey1104/frappe-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/shyampandey1104/frappe-python-sdk/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A modern, high-performance, asynchronous & synchronous Python client SDK for **Frappe Framework** and **ERPNext** REST APIs. Built with type safety, resilient retries, Pydantic v2 validation, a fluent query builder, and a developer CLI.

---

## ✨ Features

- 🚀 **Dual Engine Support**: Includes both `FrappeClient` (synchronous) and `AsyncFrappeClient` (asynchronous `httpx` engine) for high-concurrency microservices.
- 🔍 **Fluent Query Builder**: Construct complex Frappe filters, child queries, pagination, and sorting with a chainable pythonic API.
- 🛡️ **Pydantic v2 Models**: Built-in and extensible DocType models with auto-validation for ERPNext documents (`Customer`, `Item`, `Sales Order`, etc.).
- 🔄 **Resilient Retries**: Automatic exponential backoff retries for transient 500/502/504 errors using `tenacity`.
- 📊 **Developer CLI (`frappe-cli`)**: Inspect doctypes, test connections, and query records right from your shell with rich formatted tables.
- 📦 **Zero-Config DocType CRUD**: Full support for `get_doc`, `get_list`, `insert`, `update`, `delete`, and remote RPC `call()`.

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                   Python Application                   │
│   (FastAPI / Django / Data Pipelines / Microservices)  │
└───────────────────────────┬────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               │    frappe-python-sdk    │
               ├─────────────────────────┤
               │  • Fluent Query Builder │
               │  • Pydantic v2 Schemas  │
               │  • Auto-Retry & Backoff │
               │  • Async / Sync Engine  │
               └────────────┬────────────┘
                            │  HTTPS / REST / RPC
                            ▼
               ┌─────────────────────────┐
               │    ERPNext / Frappe     │
               │      Desk & REST API    │
               └─────────────────────────┘
```

---

## 📦 Installation

```bash
pip install frappe-python-sdk
```

Or install in editable mode with dev dependencies:
```bash
git clone https://github.com/shyampandey1104/frappe-python-sdk.git
cd frappe-python-sdk
pip install -e ".[dev]"
```

---

## 🚀 Quickstart

### 1. Synchronous Client

```python
from frappe_sdk import FrappeClient

# Initialize client with API credentials
client = FrappeClient(
    base_url="https://your-site.frappe.cloud",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Test connection
print("Status:", client.ping())

# Fluent Query Builder
orders = (
    client.query("Sales Order")
    .fields("name", "customer", "grand_total", "status")
    .filter("docstatus", "=", 1)
    .filter("grand_total", ">", 10000)
    .order_by("grand_total", "desc")
    .limit(10)
    .run()
)

for order in orders:
    print(f"Order: {order['name']} | Customer: {order['customer']} | Total: ₹{order['grand_total']}")
```

### 2. High-Concurrency Asynchronous Client

```python
import asyncio
from frappe_sdk import AsyncFrappeClient

async def main():
    async with AsyncFrappeClient(
        base_url="https://your-site.frappe.cloud",
        api_key="your_api_key",
        api_secret="your_api_secret"
    ) as client:
        # Fetch multiple customers concurrently
        tasks = [
            client.get_doc("Customer", "CUST-0001"),
            client.get_doc("Customer", "CUST-0002"),
            client.get_doc("Customer", "CUST-0003"),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print("Fetched docs:", results)

asyncio.run(main())
```

### 3. Creating & Updating Documents

```python
from frappe_sdk import FrappeClient
from frappe_sdk.models import CustomerDoc

client = FrappeClient(base_url="https://your-site.frappe.cloud", api_key="key", api_secret="secret")

# Create Customer
new_customer = client.insert("Customer", {
    "customer_name": "Acme Industrial Solutions",
    "customer_group": "Commercial",
    "territory": "India"
})
print("Created Customer:", new_customer["name"])

# Update Customer
client.update("Customer", new_customer["name"], {
    "mobile_no": "+91 9876543210"
})
```

---

## 💻 Developer CLI

The package comes bundled with `frappe-cli`:

```bash
# Set environment variables (or pass as flags)
export FRAPPE_URL="https://your-site.frappe.cloud"
export FRAPPE_API_KEY="your_api_key"
export FRAPPE_API_SECRET="your_api_secret"

# Test connection
frappe-cli ping

# Query records formatted in a Rich ASCII table
frappe-cli query "Sales Invoice" --fields "name,customer,grand_total,status" --limit 5
```

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

Author: **Shyamkumar Bhupendra Pandey** ([@shyampandey1104](https://github.com/shyampandey1104))
