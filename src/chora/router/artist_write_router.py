"""ArtistWriteRouter: Router für die Bearbeitung von Künstlern."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from chora.router.artist_model import ArtistModel

__all__: list[str] = ["artist_write_router"]


artist_write_router: Final = APIRouter(tags=["Schreiben"])


@artist_write_router.post("")
def post(
    artist_model: ArtistModel,
    request: Request,
    service: Annotated[ArtistWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Künstler anzulegen.

    :param artist_model: Künstlerdaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    :raises UsernameExistsError: Falls der Benutzername bereits existiert
    """
    logger.debug("artist_model={}", artist_model)
    artist_dto: Final = service.create(artist=artist_model.to_artist())
    logger.debug("artist_dto={}", artist_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{artist_dto.id}"},
    )

# TODO Weitere Endpoints für die Bearbeitung von Künstlern implementieren, zB PUT, DELETE.
