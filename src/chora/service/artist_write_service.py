"""Geschäftslogik für Artist Schreiboperationen."""

from typing import Final

from keycloak.exceptions import KeycloakError
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from chora.entity.artist import Artist
from chora.entity.vertrag import Vertrag
from chora.repository.artist_repository import ArtistRepository
from chora.repository.session_factory import Session
from chora.repository.song_repository import SongRepository
from chora.security.user import User
from chora.security.user_service import UserService
from chora.service.artist_dto import ArtistDTO
from chora.service.artist_update_options import ArtistPatchData, ArtistUpdateOptions
from chora.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from chora.service.mailer import send_mail

__all__ = ["ArtistWriteService"]


class ArtistWriteService:
    """Service-Klasse mit Geschäftslogik für Entity Artist."""

    def __init__(
        self,
        repo: ArtistRepository,
        song_repo: SongRepository,
        user_service: UserService,
    ) -> None:
        """Konstruktor mit abhängigem ArtistRepository und UserService."""
        self.repo: ArtistRepository = repo
        self.song_repo: SongRepository = song_repo
        self.user_service: UserService = user_service

    def create(self, artist: Artist, song_ids: list[int] | None = None) -> ArtistDTO:
        """Einen neuen Artist anlegen.

        :param artist: Der neue Artist ohne ID
        :return: Der neu angelegte Artist mit generierter ID
        :rtype: ArtistDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "artist={}, vertrag={}, song_ids={}",
            artist,
            artist.vertrag,
            song_ids,
        )

        username: Final = artist.username
        if username is None:
            raise ValueError

        if self.user_service.username_exists(username):
            raise UsernameExistsError(username)

        email: Final = artist.email
        if self.user_service.email_exists(email):
            raise EmailExistsError(email=email)

        if song_ids is not None:
            with Session() as session:
                self._validate_song_ids(song_ids=song_ids, session=session)

        user: Final = User(
            username=username,
            email=artist.email,
            nachname=artist.name,
            vorname=artist.name,
            password="p",  # noqa: S106 # NOSONAR
            roles=[],
        )
        user_id = self.user_service.create_user(user)
        logger.debug("user_id={}", user_id)

        try:
            with Session() as session:
                artist_db: Final = self.repo.create(artist=artist, session=session)
                if song_ids is not None:
                    self._replace_songs_by_ids(
                        artist_db=artist_db,
                        song_ids=song_ids,
                        session=session,
                    )
                artist_dto: Final = ArtistDTO(artist_db)
                session.commit()
        except SQLAlchemyError:
            logger.error(
                "DB-Transaktion fuer Artist fehlgeschlagen. "
                "Loesche Keycloak-User mit user_id={}",
                user_id,
            )
            try:
                self.user_service.delete_user(user_id)
            except KeycloakError:
                logger.error(
                    "Keycloak-User mit user_id={} konnte nach DB-Fehler "
                    "nicht geloescht werden",
                    user_id,
                )
            raise

        send_mail(artist_dto=artist_dto)
        logger.debug("artist_dto={}", artist_dto)
        return artist_dto

    def update(
        self,
        artist: Artist,
        artist_id: int,
        version: int,
        options: ArtistUpdateOptions | None = None,
    ) -> ArtistDTO:
        """Daten eines Artisten ändern.

        :param artist: Die neuen Daten
        :param artist_id: ID des zu aktualisierenden Artisten
        :param version: Version für optimistische Synchronisation
        :return: Der aktualisierte Artist
        :rtype: ArtistDTO
        :raises NotFoundError: Falls der zu aktualisierende Artist nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        update_options = options if options is not None else ArtistUpdateOptions()

        logger.debug(
            (
                "artist_id={}, version={}, replace_vertrag={}, "
                "replace_songs={}, song_ids={}, artist={}"
            ),
            artist_id,
            version,
            update_options.replace_vertrag,
            update_options.replace_songs,
            update_options.song_ids,
            artist,
        )

        with Session() as session:
            if (
                artist_db := self.repo.find_by_id(
                    artist_id=artist_id, session=session
                )
            ) is None:
                raise NotFoundError(artist_id)
            if artist_db.version > version:
                raise VersionOutdatedError(version)

            email: Final = artist.email
            if email != artist_db.email and self.repo.exists_email_other_id(
                artist_id=artist_id,
                email=email,
                session=session,
            ):
                raise EmailExistsError(email)

            old_email: Final = artist_db.email
            old_name: Final = artist_db.name

            artist_db.set(artist)
            # Änderungen an Name oder Email können Auswirkungen auf Keycloak haben,
            # daher hier schon synchronisieren
            self._sync_keycloak_if_needed(
                username=artist_db.username,
                old_user_data=(old_email, old_name),
                new_user_data=(artist.email, artist.name),
            )

            if update_options.replace_vertrag:
                if artist.vertrag is None:
                    raise ValueError("Vertrag muss fuer Vollersatz gesetzt sein")
                self._replace_vertrag(
                    artist_db=artist_db,
                    new_vertrag=artist.vertrag,
                    session=session,
                )

            if update_options.replace_songs:
                self._replace_songs(
                    artist_db=artist_db,
                    song_ids=update_options.song_ids,
                    session=session,
                )

            if (
                artist_updated := self.repo.update(artist=artist_db, session=session)
            ) is None:
                raise NotFoundError(artist_id)
            artist_dto: Final = ArtistDTO(artist_updated)
            logger.debug("{}", artist_dto)

            session.commit()
            # CAVEAT: Die erhoehte Versionsnummer ist erst COMMIT sichtbar
            artist_dto.version += 1
            return artist_dto

    def patch(
        self,
        patch_data: ArtistPatchData,
        artist_id: int,
        version: int,
        options: ArtistUpdateOptions | None = None,
    ) -> ArtistDTO:
        """Daten eines Artisten teilweise ändern.

        :param artist_id: ID des zu aktualisierenden Artisten
        :param version: Version für optimistische Synchronisation
        :param patch_data: Optionale Daten fuer das PATCH
        :param options: Optionen für Relationen
        :return: Der aktualisierte Artist
        :rtype: ArtistDTO
        """
        update_options = options if options is not None else ArtistUpdateOptions()

        logger.debug(
            (
                "PATCH artist_id={}, version={}, name={}, geburtsdatum={}, email={}, "
                "replace_vertrag={}, replace_songs={}, song_ids={}"
            ),
            artist_id,
            version,
            patch_data.name,
            patch_data.geburtsdatum,
            patch_data.email,
            update_options.replace_vertrag,
            update_options.replace_songs,
            update_options.song_ids,
        )

        with Session() as session:
            if (
                artist_db := self.repo.find_by_id(
                    artist_id=artist_id, session=session
                )
            ) is None:
                raise NotFoundError(artist_id)
            if artist_db.version > version:
                raise VersionOutdatedError(version)

            if (
                patch_data.email is not None
                and patch_data.email != artist_db.email
                and self.repo.exists_email_other_id(
                    artist_id=artist_id,
                    email=patch_data.email,
                    session=session,
                )
            ):
                raise EmailExistsError(patch_data.email)

            old_email: Final = artist_db.email
            old_name: Final = artist_db.name

            self._apply_patch_scalars(artist_db=artist_db, patch_data=patch_data)
            self._apply_patch_relations(
                artist_db=artist_db,
                patch_data=patch_data,
                update_options=update_options,
                session=session,
            )
            self._sync_keycloak_patch_if_needed(
                artist_db=artist_db,
                old_email=old_email,
                old_name=old_name,
            )

            if (
                artist_updated := self.repo.patch(artist=artist_db, session=session)
            ) is None:
                raise NotFoundError(artist_id)

            artist_dto: Final = ArtistDTO(artist_updated)
            logger.debug("{}", artist_dto)

            session.commit()
            artist_dto.version += 1
            return artist_dto

    @staticmethod
    def _apply_patch_scalars(artist_db: Artist, patch_data: ArtistPatchData) -> None:
        """Optionale Primitive aus PATCH auf den Artist anwenden."""
        if patch_data.name is not None:
            artist_db.name = patch_data.name
        if patch_data.geburtsdatum is not None:
            artist_db.geburtsdatum = patch_data.geburtsdatum
        if patch_data.email is not None:
            artist_db.email = patch_data.email

    def _apply_patch_relations(
        self,
        *,
        artist_db: Artist,
        patch_data: ArtistPatchData,
        update_options: ArtistUpdateOptions,
        session,
    ) -> None:
        """Optionale Relationen aus PATCH anwenden."""
        if update_options.replace_vertrag:
            self._replace_vertrag(
                artist_db=artist_db,
                new_vertrag=patch_data.vertrag,
                session=session,
            )

        if update_options.replace_songs:
            self._replace_songs(
                artist_db=artist_db,
                song_ids=update_options.song_ids,
                session=session,
            )

    def _replace_vertrag(
        self,
        *,
        artist_db: Artist,
        new_vertrag: Vertrag | None,
        session,
    ) -> None:
        """Vertrag eines Artists durch ein neues Objekt ersetzen."""
        if artist_db.vertrag is not None:
            session.delete(artist_db.vertrag)
            session.flush()

        if new_vertrag is None:
            artist_db.vertrag = None
            return

        new_vertrag.artist = artist_db
        artist_db.vertrag = new_vertrag
        session.add(new_vertrag)
        session.flush()

    def _sync_keycloak_patch_if_needed(
        self,
        *,
        artist_db: Artist,
        old_email: str,
        old_name: str,
    ) -> None:
        """Keycloak nach PATCH aktualisieren, wenn Name oder Email geändert wurden."""
        self._sync_keycloak_if_needed(
            username=artist_db.username,
            old_user_data=(old_email, old_name),
            new_user_data=(artist_db.email, artist_db.name),
        )

    def _sync_keycloak_if_needed(
        self,
        *,
        username: str | None,
        old_user_data: tuple[str, str],
        new_user_data: tuple[str, str],
    ) -> None:
        """Keycloak nur bei relevanten Aenderungen aktualisieren."""
        if username is None:
            return
        new_email, new_name = new_user_data

        if old_user_data == new_user_data:
            return

        try:
            self.user_service.update_user(
                username=username,
                email=new_email,
                vorname=new_name,
                nachname=new_name,
            )
        except KeycloakError:
            logger.error("Keycloak-Update fuer username={} fehlgeschlagen", username)
            raise

    def _replace_songs(
        self,
        artist_db: Artist,
        song_ids: list[int] | None,
        session,
    ) -> None:
        """Songs fuer einen Artist vollständig ersetzen."""
        self._replace_songs_by_ids(
            artist_db=artist_db,
            song_ids=song_ids if song_ids is not None else [],
            session=session,
        )

    def _replace_songs_by_ids(
        self,
        artist_db: Artist,
        song_ids: list[int],
        session,
    ) -> None:
        """Songs fuer einen Artist durch eine Liste vorhandener Song-IDs ersetzen."""
        if len(song_ids) != len(set(song_ids)):
            raise ValueError("Song-IDs duerfen nicht mehrfach vorkommen")

        songs_from_ids = self.song_repo.find_by_ids(song_ids=song_ids, session=session)
        if len(songs_from_ids) != len(song_ids):
            raise NotFoundError

        songs_by_id = {song.id: song for song in songs_from_ids}
        ordered_songs = [songs_by_id[song_id] for song_id in song_ids]

        keep_song_ids = set(song_ids)
        for song_db in list(artist_db.songs):
            if song_db.id not in keep_song_ids:
                if artist_db in song_db.artists:
                    song_db.artists.remove(artist_db)
                if len(song_db.artists) == 0:
                    self.song_repo.delete(song=song_db, session=session)

        for song in ordered_songs:
            if artist_db not in song.artists:
                song.artists.append(artist_db)

        artist_db.songs = ordered_songs

    def _validate_song_ids(self, song_ids: list[int], session) -> None:
        """Vorab prüfen, ob alle Song-IDs existieren."""
        if len(song_ids) != len(set(song_ids)):
            raise ValueError("Song-IDs duerfen nicht mehrfach vorkommen")
        songs_from_ids = self.song_repo.find_by_ids(song_ids=song_ids, session=session)
        if len(songs_from_ids) != len(song_ids):
            raise NotFoundError

    def delete_by_id(self, artist_id: int) -> None:
        """Einen Artist anhand seiner ID löschen.

        :param artist_id: ID des zu löschenden Artisten
        """
        logger.debug("artist_id={}", artist_id)
        with Session() as session:
            self.repo.delete_by_id(artist_id=artist_id, session=session)
            session.commit()
