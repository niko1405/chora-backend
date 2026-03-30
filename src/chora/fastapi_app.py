"""FastAPI application for the Songs API.

This module provides a simple REST API for songwriting workspace management.
"""

from fastapi import FastAPI

# Instanz der App erstellen
app = FastAPI(title="Songs API", description="Songwriting Workspace", version="1.0.0")


@app.get("/")
def hello_world() -> dict[str, str]:
    """Return a simple Hello World message for testing."""
    return {"message": "Hello World from Songs API"}
