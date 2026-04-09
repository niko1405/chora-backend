"""Repository fuer Song-Objekte."""

from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from chora.entity.song import Song
from chora.repository.pageable import Pageable
from chora.repository.slice import Slice

__all__ = ["SongRepository"]


class SongRepository:
    """Repository-Klasse mit CRUD-Methoden fuer Song-Objekte."""

    def find_by_id(
        self,
        song_id: int | None,
        artist_id: int,
        session: Session,
    ) -> Song | None:
        """Song anhand der ID und Artist-ID suchen."""
        if song_id is None:
            return None

        statement: Final = select(Song).where(
            Song.id == song_id,
            Song.artist_id == artist_id,
        )
        return session.scalar(statement)

    def find(
        self,
        artist_id: int,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Song]:
        """Songs eines Artists mit Pagination suchen."""
        offset = pageable.number * pageable.size
        statement: Final = (
            select(Song)
            .where(Song.artist_id == artist_id)
            .limit(pageable.size)
            .offset(offset)
            if pageable.size != 0
            else select(Song).where(Song.artist_id == artist_id)
        )
        songs = tuple(session.scalars(statement).all())
        total_elements = self._count_rows(artist_id=artist_id, session=session)
        return Slice(content=songs, total_elements=total_elements)

    def find_by_ids(self, song_ids: list[int], session: Session) -> list[Song]:
        """Songs anhand einer ID-Liste suchen."""
        if len(song_ids) == 0:
            return []
        statement: Final = select(Song).where(Song.id.in_(song_ids))
        return list(session.scalars(statement).all())

    def create(self, song: Song, session: Session) -> Song:
        """Einen Song anlegen."""
        session.add(song)
        session.flush()
        return song

    def update(self, song: Song, session: Session) -> Song:
        """Einen Song aktualisieren."""
        session.flush()
        return song

    def delete(self, song: Song, session: Session) -> None:
        """Einen Song loeschen."""
        session.delete(song)
        session.flush()

    def _count_rows(self, artist_id: int, session: Session) -> int:
        statement: Final = select(Song.id).where(Song.artist_id == artist_id)
        return len(session.scalars(statement).all())
