"""Repository fuer die Chora-Objekte."""
from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from chora.entity import Artist
from chora.repository.pageable import Pageable
from chora.repository.slice import Slice

__all__ = ["ArtistRepository"]


class ArtistRepository:
    """Repository-Klasse mit CRUD Methoden für Artist-Objekte."""

    def find_by_id(self, artist_id: int | None, session: Session) -> Artist | None:
        """Artist anhand der ID suchen.

        :param artist_id: ID des gesuchten Artist-Objekts
        :param session: Session-Objekt für die DB-Verbindung
        :return: Gefundenes Artist-Objekt oder None, falls nicht gefunden
        :rtype: Artist | None
        """
        logger.debug("artist_id={}", artist_id)

        if artist_id is None:
            return None

        statement: Final = (
            select(Artist)
            .options(joinedload(Artist.vertrag))
            .where(Artist.id == artist_id)
        )
        artist: Final = session.scalar(statement)

        logger.debug("artist={}", artist)
        return artist

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
        session: Session,
    ) -> Slice[Artist]:
        """Artist-Objekte anhand von Suchparametern suchen.

        :param suchparameter: Mapping mit Suchparametern
        :param pageable: Pageable-Objekt für die Paginierung
        :param session: Session-Objekt für die DB-Verbindung
        :return: Slice mit gefundenen Artist-Objekten
        :rtype: Slice[Artist]
        """
        logger.debug("suchparameter={}", suchparameter)
        if not suchparameter:
            return self._find_all(pageable=pageable, session=session)

        for key, value in suchparameter.items():
            if key == "email":
                artist: Artist | None = self._find_by_email(
                    email=value,
                    session=session,
                )
                logger.debug("artist={}", artist)
                return (
                    Slice(content=(artist,), total_elements=1)
                    if artist is not None
                    else Slice(content=(), total_elements=0)
                )
            if key == "name":
                artists: Slice[Artist] = self._find_by_name(
                    teil=value,
                    pageable=pageable,
                    session=session,
                )
                logger.debug("artists={}", artists)
                return artists
        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Artist]:
        """Alle Artist-Objekte mit Pagination suchen."""
        logger.debug("aufgerufen")
        offset: int = pageable.number * pageable.size
        statement: Final = (
            (
                select(Artist)
                .options(joinedload(Artist.vertrag))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Artist).options(joinedload(Artist.vertrag))
            )
        )
        artists: Final = session.scalars(statement).all()
        anzahl: Final = self._count_all_rows(session)
        artist_slice: Final = Slice(content=tuple(artists), total_elements=anzahl)
        logger.debug("artist_slice={}", artist_slice)
        return artist_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(Artist.id)
        return len(session.scalars(statement).all())

    def _find_by_email(self, email: str, session: Session) -> Artist | None:
        """Artist-Objekt anhand der E-Mail suchen.

        :param email: E-Mail des gesuchten Artist-Objekts
        :param session: Session-Objekt für die DB-Verbindung
        :return: Gefundenes Artist-Objekt oder None, falls nicht gefunden
        :rtype: Artist | None
        """
        logger.debug("email={}", email)
        statement: Final = (
            select(Artist)
            .options(joinedload(Artist.vertrag))
            .where(func.lower(Artist.email) == email.lower())
        )
        artist: Final = session.scalar(statement)
        logger.debug("artist={}", artist)
        return artist

    def _find_by_name(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Artist]:
        logger.debug("teil={}", teil)
        offset = pageable.number * pageable.size
        statement: Final = (
            (
                select(Artist)
                .options(joinedload(Artist.vertrag))
                .filter(Artist.name.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Artist)
                .options(joinedload(Artist.vertrag))
                .filter(Artist.name.ilike(f"%{teil}%"))
            )
        )
        artists: Final = session.scalars(statement).all()
        anzahl: Final = self._count_rows_name(teil, session)
        artist_slice: Final = Slice(content=tuple(artists), total_elements=anzahl)
        logger.debug("{}", artist_slice)
        return artist_slice

    def _count_rows_name(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count(Artist.id))
            .select_from(Artist)
            .where(Artist.name.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def exists_email(self, email: str, session: Session) -> bool:
        """Pruefen, ob eine E-Mail bereits existiert.

        :param email: Emailadresse
        :param patient_id: eigene Patient-ID
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = (
            select(Artist.id)
            .where(func.lower(Artist.email) == email.lower())
            .limit(1)
        )
        result: Final = session.scalar(statement)
        return result is not None

    def create(self, artist: Artist, session: Session) -> Artist:
        """Einen Artist anlegen."""
        logger.debug("artist={}", artist)
        session.add(artist)
        session.flush()
        return artist

    def update(self, artist: Artist, session: Session) -> Artist | None:
        """Einen Artist aktualisieren."""
        return self.patch(artist=artist, session=session)

    def patch(self, artist: Artist, session: Session) -> Artist | None:
        """Einen Artist teilweise aktualisieren."""
        logger.debug("artist={}", artist)
        session.flush()
        return artist

    def delete_by_id(self, artist_id: int, session: Session) -> bool:
        """Einen Artist anhand seiner ID löschen."""
        logger.debug("artist_id={}", artist_id)
        artist = self.find_by_id(artist_id=artist_id, session=session)
        if artist is None:
            return False
        session.delete(artist)
        session.flush()
        return True

    def exists_email_other_id(
        self,
        artist_id: int,
        email: str,
        session: Session,
    ) -> bool:
        """Pruefen, ob eine E-Mail bei einem anderen Artist bereits existiert."""
        statement: Final = (
            select(Artist.id)
            .where(func.lower(Artist.email) == email.lower(), Artist.id != artist_id)
            .limit(1)
        )
        result: Final = session.scalar(statement)
        return result is not None

    def find_name(self, teil: str, session: Session) -> Sequence[str]:
        """Artist-Objekte anhand eines Namens suchen."""
        logger.debug("teil={}", teil)
        statement: Final = (
            select(Artist.name)
            .filter(Artist.name.ilike(f"%{teil}%"))
            .distinct()
        )
        artists: Final = (session.scalars(statement)).all()
        logger.debug("artists={}", artists)
        return artists
