"""Command Line Interface for Frappe SDK."""

import json
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
import os

app = typer.Typer(help="Frappe & ERPNext CLI tool for developers and sysadmins.")
console = Console()


def get_client(url: Optional[str] = None, api_key: Optional[str] = None, api_secret: Optional[str] = None):
    from frappe_sdk.client import FrappeClient
    base_url = url or os.environ.get("FRAPPE_URL", "http://localhost:8000")
    key = api_key or os.environ.get("FRAPPE_API_KEY")
    secret = api_secret or os.environ.get("FRAPPE_API_SECRET")
    return FrappeClient(base_url=base_url, api_key=key, api_secret=secret)


@app.command()
def ping(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Frappe instance URL"),
    api_key: Optional[str] = typer.Option(None, "--key", "-k", help="Frappe API key"),
    api_secret: Optional[str] = typer.Option(None, "--secret", "-s", help="Frappe API secret"),
):
    """Test connection with Frappe / ERPNext server."""
    client = get_client(url, api_key, api_secret)
    try:
        res = client.ping()
        console.print(f"[bold green]✓ Connected successfully![/] Server responded: [cyan]{res}[/]")
    except Exception as e:
        console.print(f"[bold red]✗ Connection failed:[/] {e}")
        raise typer.Exit(code=1)


@app.command()
def query(
    doctype: str = typer.Argument(..., help="DocType to query (e.g. Customer, Item, User)"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="Comma-separated field list"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of records to fetch"),
    url: Optional[str] = typer.Option(None, "--url", "-u"),
):
    """Query records from a DocType and display as a formatted table."""
    client = get_client(url)
    field_list = [f.strip() for f in fields.split(",")] if fields else ["name", "owner", "modified"]
    try:
        records = client.query(doctype).fields(*field_list).limit(limit).run()
        if not records:
            console.print(f"[yellow]No records found for DocType '{doctype}'[/yellow]")
            return

        table = Table(title=f"DocType: {doctype} ({len(records)} records)")
        for col in field_list:
            table.add_column(col, style="cyan")

        for row in records:
            table.add_row(*[str(row.get(col, "")) for col in field_list])

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Query failed:[/] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
