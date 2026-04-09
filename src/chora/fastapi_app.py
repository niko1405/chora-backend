"""FastAPI application for the Songs API.

This module provides a simple REST API for songwriting workspace management.
"""

from fastapi import FastAPI

from chora.router.artist_write_router import artist_write_router
from chora.router.song_router import song_router
from chora.router.song_write_router import song_write_router

# Instanz der App erstellen
app = FastAPI(title="Songs API", description="Songwriting Workspace", version="1.0.0")

app.include_router(artist_write_router, prefix="/artists")
app.include_router(song_router, prefix="/artists")
app.include_router(song_write_router, prefix="/artists")


@app.get("/")
def hello_world() -> dict[str, str]:
    """Return a simple Hello World message for testing."""
    return {"message": "Hello World from Songs API"}
