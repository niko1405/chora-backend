"""ArtistGetRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from chora.repository.pageable import Pageable
from chora.repository.slice import Slice
from chora.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from chora.router.dependencies import get_service
from chora.router.page import Page
from chora.service.artist_dto import ArtistDTO
from chora.service.artist_service import ArtistService

__all__: list[str] = ["artist_router"]

artist_router: Final = APIRouter(tags=["Lesen"])


# Get Artist by ID
@artist_router.get(
    "/{artist_id}",
    dependencies=[],
)
def get_by_id(
    artist_id: int,
    request: Request,
    service: Annotated[ArtistService, Depends(get_service)],
) -> Response:
    """Hole einen Künstler anhand seiner ID.

    :param artist_id: Die ID des Künstlers, der abgerufen werden soll.
    :type artist_id: int
    :param request: Das FastAPI Request-Objekt, das Informationen über die HTTP-Anfrage enthält.
    :type request: Request
    :param service: Der ArtistService, der die Geschäftslogik für Künstler bereitstellt.
                    Dieser wird automatisch von FastAPI bereitgestellt.
    :type service: ArtistService
    :return: Eine HTTP-Antwort mit den Daten des angeforderten Künstlers oder einem Fehlerstatus.
    :rtype: Response
    """  # noqa: E501
    logger.debug("artist_id={}", artist_id)

    artist: Final = service.find_by_id(artist_id=artist_id)
    logger.debug("{}", artist)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == artist.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    return JSONResponse(
        content=jsonable_encoder(_artist_to_dict(artist)),
        headers={ETAG: f'"{artist.version}"'},
    )


# Get by query parameters (e.g. name, email)
@artist_router.get(
    "",
    dependencies=[],
)
def get(
    request: Request,
    service: Annotated[ArtistService, Depends(get_service)],
) -> JSONResponse:
    """Hole Künstler anhand von Query-Parametern.

    :param request: Das FastAPI Request-Objekt, das Informationen über die HTTP-Anfrage enthält.
    :type request: Request
    :param service: Der ArtistService, der die Geschäftslogik für Künstler bereitstellt.
                    Dieser wird automatisch von FastAPI bereitgestellt.
    :type service: ArtistService
    :return: Eine HTTP-Antwort mit den Daten der angeforderten Künstler oder einem Fehlerstatus.
    :rtype: JSONResponse
    """  # noqa: E501
    query_params: Final = request.query_params
    log_str: Final = "{}"
    logger.debug(log_str, query_params)

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    suchparameter = dict(query_params)
    if "page" in query_params:
        del suchparameter["page"]
    if "size" in query_params:
        del suchparameter["size"]

    artist_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _artist_slice_to_page(artist_slice, pageable)
    logger.debug(log_str, result)
    return JSONResponse(content=jsonable_encoder(result))


def _artist_slice_to_page(
    artist_slice: Slice[ArtistDTO], pageable: Pageable
) -> dict[str, Any]:
    """Konvertiert ein ArtistSlice in eine Page für die JSON-Antwort.

    :param artist_slice: Das ArtistSlice-Objekt, das konvertiert werden soll.
    :type artist_slice: ArtistSlice
    :param pageable: Das Pageable-Objekt mit den Informationen zur Pagination.
    :type pageable: Pageable
    :return: Ein Dictionary mit den Daten der Seite, einschließlich der Künstler
        und der Metadaten.
    :rtype: dict[str, Any]
    """
    artist_dict: Final = tuple(
        _artist_to_dict(artist) for artist in artist_slice.content
    )
    page: Final = Page.create(
        content=artist_dict,
        pageable=pageable,
        total_elements=artist_slice.total_elements,
    )
    return asdict(obj=page)


def _artist_to_dict(artist: ArtistDTO) -> dict[str, Any]:
    """Konvertiert ein ArtistDTO in ein Dictionary für die JSON-Antwort.

    :param artist: Das ArtistDTO-Objekt, das konvertiert werden soll.
    :type artist: ArtistDTO
    :return: Ein Dictionary mit den Daten des Künstlers.
    :rtype: dict[str, Any]
    """
    artist_dict: Final = asdict(obj=artist)
    artist_dict.pop("version")
    return artist_dict
