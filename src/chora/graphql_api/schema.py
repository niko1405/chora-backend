"""Schema für GraphQL durch Strawberry."""
from collections.abc import Sequence
from typing import Final

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.types import Info

from chora.graphql_api import Suchparameter
from chora.repository.artist_repository import ArtistRepository, Pageable
from chora.repository.song_repository import SongRepository
from chora.security import Role, TokenService, UserService
from chora.service import (
    ArtistDTO,
    ArtistService,
    ArtistWriteService,
    NotFoundError,
)

__all__ = ["graphql_router"]

_repo: Final = ArtistRepository()
_song_repo: Final = SongRepository()
_service: ArtistService = ArtistService(repo=_repo)
_user_service: UserService = UserService()
_write_service: ArtistWriteService = ArtistWriteService(
    repo=_repo, song_repo=_song_repo, user_service=_user_service
)
_token_service: Final = TokenService()


@strawberry.type
class Query:
    """GraphQL Query, um Artistdaten zu lesen."""

    @strawberry.field
    def artist(self, artist_id: strawberry.ID, info: Info) -> ArtistDTO | None:
        """Gibt einen Artist zurück.

        :param artist_id: ID des Artists
        :param info: GraphQL Info Objekt
        :return: Artist Objekt
        :rtype ArtistDTO | None
        :raises NotFoundError: Wenn kein Artist mit der angegebenen ID gefunden wird
        """
        logger.debug("artist_id={}", artist_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            artist_dto: Final = _service.find_by_id(artist_id=int(artist_id), user=user)
        except NotFoundError:
            return None
        logger.debug("artist_dto={}", artist_dto)
        return artist_dto

    @strawberry.field
    def artists(self, suchparameter: Suchparameter, info: Info
    ) -> Sequence[ArtistDTO]:
        """Artist durch Suchparameter finden.

        :param suchparameter: Suchparameter für die Suche
        :param info: GraphQL Info Objekt
        :return: Liste von Artist Objekten
        :rtype list[ArtistDTO]
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        suchparameter_dict: Final[dict[str, str]] = dict(vars(suchparameter))
        suchparameter_filtered = {
            key: value
            for key, value in suchparameter_dict.items()
            if value is not None and value
        }
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            artists_dto: Final = _service.find(
                queryparams=suchparameter_filtered, pageable=pageable
            )
        except NotFoundError:
            return []
        logger.debug("{}", artists_dto)
        return artists_dto.content

# TODO : Mutation implementieren, um Artistdaten zu erstellen, zu aktualisieren und zu löschen.