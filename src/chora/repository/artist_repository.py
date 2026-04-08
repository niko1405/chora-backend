"""Repository fuer die Chora-Objekte."""

from collections.abc import Mapping
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
                artist: Artist | None = self._find_by_email(email=value, session=session)
                logger.debug("artist={}", artist)
                return (
                    Slice(content=(artist,), total_elements=1)
                    if artist is not None
                    else Slice(content=(), total_elements=0)
                )
            if key == "name":
                artists: Slice[Artist] = self._find_by_name(name=value, pageable=pageable, session=session)
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
            else (select(Artist).options(joinedload(Artist.vertrag)))
        )
        artists: Final = session.scalars(statement).all()
        anzahl: Final = self._count_all_rows(session)
        artist_slice: Final = Slice(content=tuple(artists), total_elements=anzahl)
        logger.debug("artist_slice={}", artist_slice)
        return artist_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Artist)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0
