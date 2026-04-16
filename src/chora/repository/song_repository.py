"""Repository fuer Song-Objekte."""

from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from chora.entity.artist import Artist
from chora.entity.song import Song
from chora.repository.pageable import Pageable
from chora.repository.slice import Slice

__all__ = ["SongRepository"]


class SongRepository:
    """Repository-Klasse mit CRUD-Methoden fuer Song-Objekte."""

    def find_by_id(
        self,
        song_id: int | None,
        artist_id: int | None,
        session: Session,
    ) -> Song | None:
        """Song anhand der ID und optionaler Artist-ID suchen."""
        if song_id is None:
            return None

        statement = (
            select(Song)
            .options(joinedload(Song.artists))
            .where(
                Song.id == song_id,
            )
        )
        if artist_id is not None:
            statement = statement.where(Song.artists.any(Artist.id == artist_id))
        return session.scalars(statement).unique().one_or_none()

    def find(
        self,
        artist_id: int | None,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Song]:
        """Songs mit Pagination suchen, optional nach Artist gefiltert."""
        offset = pageable.number * pageable.size
        statement = select(Song).options(joinedload(Song.artists))
        if artist_id is not None:
            statement = statement.where(Song.artists.any(Artist.id == artist_id))
        if pageable.size != 0:
            statement = statement.limit(pageable.size).offset(offset)
        songs = tuple(session.scalars(statement).unique().all())
        total_elements = self._count_rows(artist_id=artist_id, session=session)
        return Slice(content=songs, total_elements=total_elements)

    def find_by_ids(self, song_ids: list[int], session: Session) -> list[Song]:
        """Songs anhand einer ID-Liste suchen."""
        if len(song_ids) == 0:
            return []
        statement: Final = (
            select(Song).options(joinedload(Song.artists)).where(Song.id.in_(song_ids))
        )
        return list(session.scalars(statement).unique().all())

    def find_by_titel(self, titel: str, session: Session) -> Song | None:
        """Song anhand des Titels suchen."""
        statement: Final = select(Song).where(Song.titel == titel)
        return session.scalar(statement)

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

    def _count_rows(self, artist_id: int | None, session: Session) -> int:
        statement = select(Song.id)
        if artist_id is not None:
            statement = statement.where(Song.artists.any(Artist.id == artist_id))
        return len(session.scalars(statement).all())
