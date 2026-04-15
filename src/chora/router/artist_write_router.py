"""ArtistWriteRouter: Router für die Bearbeitung von Künstlern."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from chora.problem_details import create_problem_details
from chora.router.artist_model import ArtistModel
from chora.router.artist_patch_model import ArtistPatchModel
from chora.router.artist_update_model import ArtistUpdateModel
from chora.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from chora.router.dependencies import get_write_service
from chora.security.role import Role
from chora.security.roles_required import RolesRequired
from chora.service.artist_update_options import ArtistPatchData
from chora.service.artist_write_service import ArtistUpdateOptions, ArtistWriteService

__all__: list[str] = ["artist_write_router"]


artist_write_router: Final = APIRouter(tags=["Schreiben"])


def _parse_if_match_version(request: Request) -> int | Response:
    """Version aus If-Match Header lesen und validieren."""
    if_match_value: Final = request.headers.get(IF_MATCH)
    if if_match_value is None:
        return create_problem_details(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        )

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return create_problem_details(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    version: Final = if_match_value[1:-1]
    try:
        return int(version)
    except ValueError:
        return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)


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
    artist_dto: Final = service.create(
        artist=artist_model.to_artist(),
        song_ids=artist_model.songs,
    )
    logger.debug("artist_dto={}", artist_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{artist_dto.id}"},
    )


@artist_write_router.put(
    "/{artist_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def put(
    artist_id: int,
    artist_update_model: ArtistUpdateModel,
    request: Request,
    service: Annotated[ArtistWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen bestehenden Künstler zu aktualisieren.

    :param artist_id: ID des zu aktualisierenden Künstlers
    :param artist_update_model: Aktualisierte Künstlerdaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises NotFoundError: Falls kein Künstler mit der angegebenen ID existiert
    :raises VersionOutdatedError: Falls die Version des Künstlers veraltet ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "artist_id={}, if_match={}, artist_model={}",
        artist_id,
        if_match_value,
        artist_update_model,
    )

    version_or_response: Final = _parse_if_match_version(request)
    if isinstance(version_or_response, Response):
        return version_or_response
    version_int: Final = version_or_response

    artist: Final = artist_update_model.to_artist()
    # Prüfen, ob Vertrag oder Songs ersetzt werden sollen, damit die Service-Methode
    # entsprechend aufgerufen werden kann
    replace_vertrag: Final = "vertrag" in artist_update_model.model_fields_set
    replace_songs: Final = "songs" in artist_update_model.model_fields_set

    vertrag = artist_update_model.vertrag_to_entity()
    if vertrag is not None:
        artist.vertrag = vertrag

    artist_modified: Final = service.update(
        artist=artist,
        artist_id=artist_id,
        version=version_int,
        options=ArtistUpdateOptions(
            replace_vertrag=replace_vertrag,
            replace_songs=replace_songs,
            song_ids=artist_update_model.song_ids(),
        ),
    )
    logger.debug("artist_modified={}", artist_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{artist_modified.version}"'},
    )


@artist_write_router.patch(
    "/{artist_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.USER]))],
)
def patch(
    artist_id: int,
    artist_patch_model: ArtistPatchModel,
    request: Request,
    service: Annotated[ArtistWriteService, Depends(get_write_service)],
) -> Response:
    """PATCH-Request, um einen bestehenden Künstler teilweise zu aktualisieren."""
    logger.debug("artist_id={}, artist_patch_model={}", artist_id, artist_patch_model)

    version_or_response: Final = _parse_if_match_version(request)
    if isinstance(version_or_response, Response):
        return version_or_response
    version_int: Final = version_or_response

    vertrag = artist_patch_model.vertrag_to_entity()

    artist_modified: Final = service.patch(
        patch_data=ArtistPatchData(
            name=artist_patch_model.name,
            geburtsdatum=artist_patch_model.geburtsdatum,
            email=(
                None
                if artist_patch_model.email is None
                else str(artist_patch_model.email)
            ),
            vertrag=vertrag,
        ),
        artist_id=artist_id,
        version=version_int,
        options=ArtistUpdateOptions(
            replace_vertrag="vertrag" in artist_patch_model.model_fields_set,
            replace_songs="songs" in artist_patch_model.model_fields_set,
            song_ids=artist_patch_model.song_ids(),
        ),
    )
    logger.debug("artist_modified={}", artist_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{artist_modified.version}"'},
    )


@artist_write_router.delete(
    "/{artist_id}",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def delete(
    artist_id: int,
    service: Annotated[ArtistWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen Künstler zu löschen.

    :param artist_id: ID des zu löschenden Künstlers
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises NotFoundError: Falls kein Künstler mit der angegebenen ID existiert
    """
    logger.debug("artist_id={}", artist_id)
    service.delete_by_id(artist_id=artist_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
