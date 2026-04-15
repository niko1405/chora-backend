"""SongWriteRouter: Router fuer feingranulare Song-Bearbeitung."""

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
    "",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def post_song(
    song_model: SongModel,
    request: Request,
    service: Annotated[SongWriteService, Depends(get_song_write_service)],
) -> Response:
    """Einen Song anlegen."""
    logger.debug("song_model={}", song_model)
    song_id = service.create(
        song=song_model.to_song(),
        artist_ids=song_model.artist_ids,
    )
    logger.debug("song_id={}", song_id)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{song_id}"},
    )


@song_write_router.put(
    "/{song_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def put_song(
    song_id: int,
    song_model: SongModel,
    service: Annotated[SongWriteService, Depends(get_song_write_service)],
) -> Response:
    """Einen Song aktualisieren."""
    logger.debug("song_id={}, song_model={}", song_id, song_model)
    service.update(
        song_id=song_id,
        song=song_model.to_song(),
        artist_ids=song_model.artist_ids,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@song_write_router.delete(
    "/{song_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def delete_song(
    song_id: int,
    service: Annotated[SongWriteService, Depends(get_song_write_service)],
) -> Response:
    """Einen Song loeschen."""
    logger.debug("song_id={}", song_id)
    service.delete(song_id=song_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
