"""Repository fuer die Chora-Objekte."""

from collections.abc import Mapping
from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from chora.entity import Artist
from chora.repository.pageable import Pageable
from chora.repository.slice import Slice


__all__ = ["ArtistRepository"]


class ArtistRepository:
    """Repository-Klasse mit CRUD Methoden für Artist-Objekte."""

    def find_by_id(self,artist_id: int | None, session: Session) -> Artist | None:
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
        artist: Final =session.scalar(statement)

        logger.debug("artist={}", artist)
        return artist

    def find(
        self,
        suchparameter: Mapping[str, str], 
        pageable: Pageable, 
        session: Session,
        ) -> Slice[Artist]:
        """Artist-Objekte anhand von Suchparametern suchen."""

        """
        :param suchparameter: Mapping mit Suchparametern
        :param pageable: Pageable-Objekt für die Paginierung
        :param session: Session-Objekt für die DB-Verbindung
        :return: Slice mit gefundenen Artist-Objekten
        :rtype: Slice[Artist]
        """
        # To Do: Implementieren der Suchlogik basierend auf den Suchparametern