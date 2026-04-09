# Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Factory-Funktionen für Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from chora.repository.artist_repository import ArtistRepository
from chora.repository.song_repository import SongRepository
from chora.security.dependencies import get_user_service
from chora.security.user_service import UserService
from chora.service.artist_service import ArtistService
from chora.service.artist_write_service import ArtistWriteService
from chora.service.song_service import SongService
from chora.service.song_write_service import SongWriteService


def get_repository() -> ArtistRepository:
    """Factory-Funktion für ArtistRepository.

    :return: Das Repository
    :rtype: ArtistRepository
    """
    return ArtistRepository()


def get_song_repository() -> SongRepository:
    """Factory-Funktion für SongRepository."""
    return SongRepository()


def get_service(
    repo: Annotated[ArtistRepository, Depends(get_repository)],
) -> ArtistService:
    """Factory-Funktion für ArtistService."""
    return ArtistService(repo=repo)


def get_write_service(
    repo: Annotated[ArtistRepository, Depends(get_repository)],
    song_repo: Annotated[SongRepository, Depends(get_song_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ArtistWriteService:
    """Factory-Funktion für ArtistWriteService."""
    return ArtistWriteService(
        repo=repo,
        song_repo=song_repo,
        user_service=user_service,
    )


def get_song_service(
    artist_repo: Annotated[ArtistRepository, Depends(get_repository)],
    song_repo: Annotated[SongRepository, Depends(get_song_repository)],
) -> SongService:
    """Factory-Funktion für SongService."""
    return SongService(artist_repo=artist_repo, song_repo=song_repo)


def get_song_write_service(
    artist_repo: Annotated[ArtistRepository, Depends(get_repository)],
    song_repo: Annotated[SongRepository, Depends(get_song_repository)],
) -> SongWriteService:
    """Factory-Funktion für SongWriteService."""
    return SongWriteService(artist_repo=artist_repo, song_repo=song_repo)
