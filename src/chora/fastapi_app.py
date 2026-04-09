"""FastAPI application for the Songs API.

This module provides a simple REST API for songwriting workspace management.
"""

from pathlib import Path
from typing import Final

from fastapi import FastAPI
from fastapi.responses import FileResponse
from loguru import logger

from chora.router import (
    artist_write_router,
    auth_router,
    health_router,
    shutdown_router,
    song_router,
    song_write_router,
)

# Instanz der App erstellen
app = FastAPI(title="Songs API", description="Songwriting Workspace", version="1.0.0")

# --------------------------------------------------------------------------------------
# R E S T
# --------------------------------------------------------------------------------------
app.include_router(artist_write_router, prefix="/rest/artists")
app.include_router(song_router, prefix="/rest/artists")
app.include_router(song_write_router, prefix="/rest/artists")
app.include_router(auth_router, prefix="/auth")
app.include_router(health_router, prefix="/health")
app.include_router(shutdown_router, prefix="/admin")

if dev_db_populate:
    app.include_router(db_populate_router, prefix="/dev")
if dev_keycloak_populate:
    app.include_router(keycloak_populate_router, prefix="/dev")


# --------------------------------------------------------------------------------------
# G r a p h Q L
# --------------------------------------------------------------------------------------
# app.include_router(graphql_router, prefix="/graphql")


# --------------------------------------------------------------------------------------
# F a v i c o n
# --------------------------------------------------------------------------------------
@app.get("/favicon.ico")
def favicon() -> FileResponse:
    """facicon.ico ermitteln.

    :return: Response-Objekt mit favicon.ico
    :rtype: FileResponse
    """
    src_path: Final = Path("src")
    file_name: Final = "favicon.ico"
    favicon_path: Final = Path("patient") / "static" / file_name
    file_path: Final = src_path / favicon_path if src_path.is_dir() else favicon_path
    logger.debug("file_path={}", file_path)
    return FileResponse(
        path=file_path,
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )
