"""SongWriteRouter: Router fuer feingranulare Song-Bearbeitung je Artist."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from chora.router.dependencies import get_song_write_service
from chora.router.song_model import SongModel
from chora.security.role import Role
from chora.security.roles_required import RolesRequired
from chora.service.song_write_service import SongWriteService

__all__ = ["song_write_router"]


song_write_router: Final = APIRouter(tags=["Schreiben"])


@song_write_router.post(
    "/{artist_id}/songs",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def post_song(
    artist_id: int,
    song_model: SongModel,
    request: Request,
    service: Annotated[SongWriteService, Depends(get_song_write_service)],
) -> Response:
    """Einen Song fuer einen Artist anlegen."""
    logger.debug("artist_id={}, song_model={}", artist_id, song_model)
    song = service.create(artist_id=artist_id, song=song_model.to_song())
    logger.debug("song={}", song)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{song.id}"},
    )


@song_write_router.put(
    "/{artist_id}/songs/{song_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def put_song(
    artist_id: int,
    song_id: int,
    song_model: SongModel,
    service: Annotated[SongWriteService, Depends(get_song_write_service)],
) -> Response:
    """Einen Song eines Artists aktualisieren."""
    logger.debug(
        "artist_id={}, song_id={}, song_model={}",
        artist_id,
        song_id,
        song_model,
    )
    service.update(
        artist_id=artist_id,
        song_id=song_id,
        song=song_model.to_song(),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@song_write_router.delete(
    "/{artist_id}/songs/{song_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def delete_song(
    artist_id: int,
    song_id: int,
    service: Annotated[SongWriteService, Depends(get_song_write_service)],
) -> Response:
    """Einen Song eines Artists loeschen."""
    logger.debug("artist_id={}, song_id={}", artist_id, song_id)
    service.delete(artist_id=artist_id, song_id=song_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
