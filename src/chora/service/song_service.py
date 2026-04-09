"""Geschaeftslogik fuer Song-Leseoperationen."""

from typing import Final

from chora.repository.artist_repository import ArtistRepository
from chora.repository.pageable import Pageable
from chora.repository.session_factory import Session
from chora.repository.slice import Slice
from chora.repository.song_repository import SongRepository
from chora.service.exceptions import NotFoundError
from chora.service.song_dto import SongDTO

__all__ = ["SongService"]


class SongService:
    """Service-Klasse fuer die Leselogik von Songs je Artist."""

    def __init__(
        self,
        artist_repo: ArtistRepository,
        song_repo: SongRepository,
    ) -> None:
        """Konstruktor mit Artist- und Song-Repository."""
        self.artist_repo = artist_repo
        self.song_repo = song_repo

    def find_by_id(self, artist_id: int, song_id: int) -> SongDTO:
        """Song eines Artists anhand der Song-ID lesen."""
        with Session() as session:
            if (
                self.artist_repo.find_by_id(
                    artist_id=artist_id,
                    session=session,
                )
                is None
            ):
                raise NotFoundError(artist_id=artist_id)

            song: Final = self.song_repo.find_by_id(
                song_id=song_id,
                artist_id=artist_id,
                session=session,
            )
            if song is None:
                raise NotFoundError(artist_id=artist_id)

            song_dto: Final = SongDTO(song=song)
            session.commit()
            return song_dto

    def find(self, artist_id: int, pageable: Pageable) -> Slice[SongDTO]:
        """Songs eines Artists mit Pagination lesen."""
        with Session() as session:
            if (
                self.artist_repo.find_by_id(
                    artist_id=artist_id,
                    session=session,
                )
                is None
            ):
                raise NotFoundError(artist_id=artist_id)

            songs_slice: Final = self.song_repo.find(
                artist_id=artist_id,
                pageable=pageable,
                session=session,
            )
            if len(songs_slice.content) == 0:
                raise NotFoundError(artist_id=artist_id)

            song_dtos: Final = tuple(SongDTO(song=song) for song in songs_slice.content)
            songs_dto_slice: Final = Slice(
                content=song_dtos,
                total_elements=songs_slice.total_elements,
            )
            session.commit()
            return songs_dto_slice
