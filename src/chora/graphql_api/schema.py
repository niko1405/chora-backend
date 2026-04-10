"""Schema für GraphQL durch Strawberry."""

from typing import Final

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.types import Info

from chora.repository.artist_repository import ArtistRepository
from chora.repository.song_repository import SongRepository
from chora.security import Role, TokenService, UserService
from chora.service import ArtistDTO
from chora.service.artist_service import ArtistService
from chora.service.artist_write_service import ArtistWriteService
from chora.service.exceptions import NotFoundError

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
