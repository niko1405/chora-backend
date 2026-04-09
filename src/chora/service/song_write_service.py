"""Geschaeftslogik fuer Song-Schreiboperationen."""

from typing import Final

from loguru import logger

from chora.entity.song import Song
from chora.repository.artist_repository import ArtistRepository
from chora.repository.session_factory import Session
from chora.repository.song_repository import SongRepository
from chora.service.exceptions import NotFoundError

__all__ = ["SongWriteService"]


class SongWriteService:
    """Service-Klasse fuer die Schreiblogik von Songs."""

    def __init__(
        self,
        artist_repo: ArtistRepository,
        song_repo: SongRepository,
    ) -> None:
        """Konstruktor mit Artist- und Song-Repository."""
        self.artist_repo = artist_repo
        self.song_repo = song_repo

    def create(self, artist_id: int, song: Song) -> Song:
        """Einen neuen Song fuer einen Artist anlegen."""
        logger.debug("artist_id={}, song={}", artist_id, song)
        with Session() as session:
            artist = self.artist_repo.find_by_id(artist_id=artist_id, session=session)
            if artist is None:
                raise NotFoundError(artist_id=artist_id)

            song.artist = artist
            song_db: Final = self.song_repo.create(song=song, session=session)
            session.commit()
            return song_db

    def update(self, artist_id: int, song_id: int, song: Song) -> Song:
        """Einen Song eines Artists aktualisieren."""
        logger.debug("artist_id={}, song_id={}, song={}", artist_id, song_id, song)
        with Session() as session:
            artist = self.artist_repo.find_by_id(artist_id=artist_id, session=session)
            if artist is None:
                raise NotFoundError(artist_id=artist_id)

            song_db = self.song_repo.find_by_id(
                song_id=song_id,
                artist_id=artist_id,
                session=session,
            )
            if song_db is None:
                raise NotFoundError(artist_id=artist_id)

            song_db.titel = song.titel
            song_db.erscheinungsdatum = song.erscheinungsdatum
            song_db.dauer = song.dauer
            song_db.genres_json = song.genres_json

            song_updated: Final = self.song_repo.update(song=song_db, session=session)
            session.commit()
            return song_updated

    def delete(self, artist_id: int, song_id: int) -> None:
        """Einen Song eines Artists loeschen."""
        logger.debug("artist_id={}, song_id={}", artist_id, song_id)
        with Session() as session:
            artist = self.artist_repo.find_by_id(artist_id=artist_id, session=session)
            if artist is None:
                raise NotFoundError(artist_id=artist_id)

            song_db = self.song_repo.find_by_id(
                song_id=song_id,
                artist_id=artist_id,
                session=session,
            )
            if song_db is None:
                raise NotFoundError(artist_id=artist_id)

            self.song_repo.delete(song=song_db, session=session)
            session.commit()
