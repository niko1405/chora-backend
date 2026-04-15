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
    """Service-Klasse fuer die Leselogik von Songs."""

    def __init__(
        self,
        artist_repo: ArtistRepository,
        song_repo: SongRepository,
    ) -> None:
        """Konstruktor mit Artist- und Song-Repository."""
        self.artist_repo = artist_repo
        self.song_repo = song_repo

    def find_by_id(self, song_id: int, artist_id: int | None = None) -> SongDTO:
        """Song anhand der Song-ID lesen, optional gefiltert nach Artist."""
        with Session() as session:
            if artist_id is not None and (
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

    def find(self, artist_id: int | None, pageable: Pageable) -> Slice[SongDTO]:
        """Songs mit Pagination lesen, optional nach Artist gefiltert."""
        with Session() as session:
            if artist_id is not None and (
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
            if artist_id is not None and len(songs_slice.content) == 0:
                raise NotFoundError(artist_id=artist_id)

            song_dtos: Final = tuple(SongDTO(song=song) for song in songs_slice.content)
            songs_dto_slice: Final = Slice(
                content=song_dtos,
                total_elements=songs_slice.total_elements,
            )
            session.commit()
            return songs_dto_slice
