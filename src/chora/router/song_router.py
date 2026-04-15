"""SongGetRouter fuer die Songverwaltung."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from chora.repository.pageable import Pageable
from chora.repository.slice import Slice
from chora.router.dependencies import get_song_service
from chora.router.page import Page
from chora.service.song_dto import SongDTO
from chora.service.song_service import SongService

__all__ = ["song_router"]


song_router: Final = APIRouter(tags=["Lesen"])


@song_router.get("")
def get(
    request: Request,
    service: Annotated[SongService, Depends(get_song_service)],
    artist_id: int | None = None,
) -> JSONResponse:
    """Songs mit Pagination lesen, optional nach Artist gefiltert."""
    query_params: Final = request.query_params
    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    songs_slice: Final = service.find(artist_id=artist_id, pageable=pageable)
    result: Final = _song_slice_to_page(songs_slice=songs_slice, pageable=pageable)
    return JSONResponse(content=result)


@song_router.get("/{song_id}")
def get_by_id(
    song_id: int,
    service: Annotated[SongService, Depends(get_song_service)],
    artist_id: int | None = None,
) -> JSONResponse:
    """Einen Song anhand der Song-ID lesen."""
    song: Final = service.find_by_id(song_id=song_id, artist_id=artist_id)
    return JSONResponse(content=_song_to_dict(song))


def _song_slice_to_page(
    songs_slice: Slice[SongDTO],
    pageable: Pageable,
) -> dict[str, Any]:
    song_dicts: Final = tuple(_song_to_dict(song) for song in songs_slice.content)
    page: Final = Page.create(
        content=song_dicts,
        pageable=pageable,
        total_elements=songs_slice.total_elements,
    )
    return asdict(obj=page)


def _song_to_dict(song: SongDTO) -> dict[str, Any]:
    return asdict(obj=song)
