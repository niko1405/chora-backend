"""Schema für GraphQL durch Strawberry."""
from gevent.ares import __all__

from typing import Final

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.types import Info

from chora.repository.artist_repository import ArtistRepository
from chora.repository.song_repository import SongRepository
from chora.security.dependencies import _token_service
from chora.security.token_service import TokenService
from chora.service import ArtistDTO
from chora.service.artist_service import ArtistService
from chora.service.artist_write_service import ArtistWriteService
from chora.service.user_service import UserService

__all__ = ["graphql_router"]

_repo: Final = ArtistRepository()
_song_repo: Final = SongRepository()
_service: ArtistService = ArtistService(repo=_repo)
_user_service: UserService = UserService()
_write_service: ArtistWriteService = ArtistWriteService(
    repo=_repo, song_repo=_song_repo, user_service=_user_service
)
_token_service: Final = TokenService()