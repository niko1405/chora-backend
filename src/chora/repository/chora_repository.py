"""Repository fuer die Chora-Objekte."""

from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from chora.entity import Artist


__all__ = ["ChoraRepository"]


class ChoraRepository:
    """Repository-Klasse mit CRUD Methoden für Chora-Objekte."""

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
