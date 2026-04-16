"""Geschaeftslogik fuer Song-Schreiboperationen."""

from typing import Final

from loguru import logger

from chora.entity.artist import Artist
from chora.entity.song import Song
from chora.repository.artist_repository import ArtistRepository
from chora.repository.session_factory import Session
from chora.repository.song_repository import SongRepository
from chora.service.exceptions import NotFoundError, SongTitleExistsError

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

    def create(self, song: Song, artist_ids: list[int] | None = None) -> int:
        """Einen neuen Song anlegen und optional Artists verknüpfen."""
        logger.debug("artist_ids={}, song={}", artist_ids, song)
        with Session() as session:
            self._ensure_unique_titel(titel=song.titel, session=session)
            artists = self._find_artists_by_ids(
                artist_ids=artist_ids if artist_ids is not None else [],
                session=session,
            )
            song_db: Final = self.song_repo.create(song=song, session=session)
            song_db.artists = artists
            song_id = song_db.id
            if song_id is None:
                raise ValueError("Song-ID nach dem Anlegen nicht ermittelt werden")
            session.commit()
            return song_id

    def update(
        self,
        song_id: int,
        song: Song,
        artist_id: int | None = None,
        artist_ids: list[int] | None = None,
    ) -> Song:
        """Einen Song aktualisieren und optional die Artists ersetzen."""
        logger.debug(
            "song_id={}, artist_id={}, artist_ids={}, song={}",
            song_id,
            artist_id,
            artist_ids,
            song,
        )
        with Session() as session:
            if artist_id is not None and (
                self.artist_repo.find_by_id(artist_id=artist_id, session=session)
                is None
            ):
                raise NotFoundError(artist_id=artist_id)

            song_db = self.song_repo.find_by_id(
                song_id=song_id,
                artist_id=artist_id,
                session=session,
            )
            if song_db is None:
                raise NotFoundError(artist_id=artist_id)

            self._ensure_unique_titel(
                titel=song.titel,
                session=session,
                exclude_song_id=song_db.id,
            )

            song_db.titel = song.titel
            song_db.erscheinungsdatum = song.erscheinungsdatum
            song_db.dauer = song.dauer
            song_db.genres_json = song.genres_json

            if artist_ids is not None:
                song_db.artists = self._find_artists_by_ids(
                    artist_ids=artist_ids,
                    session=session,
                )

            song_updated: Final = self.song_repo.update(song=song_db, session=session)
            session.commit()
            return song_updated

    def delete(self, song_id: int) -> None:
        """Einen Song loeschen."""
        logger.debug("song_id={}", song_id)
        with Session() as session:
            song_db = self.song_repo.find_by_id(
                song_id=song_id,
                artist_id=None,
                session=session,
            )
            if song_db is None:
                raise NotFoundError()  # noqa: RSE102

            self.song_repo.delete(song=song_db, session=session)

            session.commit()

    def _find_artists_by_ids(
        self,
        artist_ids: list[int],
        session,
    ) -> list[Artist]:
        if len(artist_ids) != len(set(artist_ids)):
            raise ValueError("Artist-IDs duerfen nicht mehrfach vorkommen")

        artists = [
            artist
            for artist in (
                self.artist_repo.find_by_id(artist_id=artist_id, session=session)
                for artist_id in artist_ids
            )
            if artist is not None
        ]
        if len(artists) != len(artist_ids):
            raise NotFoundError()  # noqa: RSE102
        return artists

    def _ensure_unique_titel(
        self,
        *,
        titel: str,
        session,
        exclude_song_id: int | None = None,
    ) -> None:
        existing_song = self.song_repo.find_by_titel(titel=titel, session=session)
        if existing_song is None:
            return
        if exclude_song_id is not None and existing_song.id == exclude_song_id:
            return
        raise SongTitleExistsError(titel=titel)
