"""Modul für die Router der Chora-Anwendung einschließlich Validierung."""

from collections.abc import Sequence

from chora.router.artist_router import artist_router, get, get_by_id
from chora.router.artist_write_router import (
    artist_write_router,
    delete,
    patch,
    post,
    put,
)
from chora.router.health_router import router as health_router
from chora.router.shutdown_router import router as shutdown_router
from chora.router.shutdown_router import shutdown
from chora.router.song_router import song_router
from chora.router.song_write_router import song_write_router
from chora.security.auth_router import router as auth_router

__all__: Sequence[str] = [
    "artist_router",
    "artist_write_router",
    "auth_router",
    "delete",
    "get",
    "get_by_id",
    "health_router",
    "patch",
    "post",
    "put",
    "shutdown",
    "shutdown_router",
    "song_router",
    "song_write_router",
]
