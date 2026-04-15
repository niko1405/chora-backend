"""Gemeinsame Basis fuer Artist-Request-Modelle."""

from datetime import date
from typing import Annotated, Any, Final

from loguru import logger
from pydantic import BaseModel, EmailStr, StringConstraints

from chora.entity.artist import Artist

__all__ = ["ArtistBaseModel"]


class ArtistBaseModel(BaseModel):
    """Gemeinsame Felder und Konvertierung fuer Artist-Modelle."""

    name: Annotated[
        str,
        StringConstraints(
            pattern=r"^[a-zA-Z\-\s]+$",
            min_length=1,
            max_length=100,
        ),
    ]
    """Der Name des Artisten."""

    username: Annotated[
        str,
        StringConstraints(
            pattern=r"^[a-zA-Z\-\s]+$",
            min_length=1,
            max_length=100,
        ),
    ]
    """Der Nutzername des Artisten."""

    geburtsdatum: date
    """Das Geburtsdatum."""

    email: EmailStr
    """Die eindeutige Emailadresse."""

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert das Pydantic-Modell in ein Dictionary."""
        artist_dict = self.model_dump()
        artist_dict["id"] = None
        artist_dict["vertrag"] = None
        artist_dict["songs"] = []
        artist_dict["erzeugt"] = None
        artist_dict["aktualisiert"] = None
        return artist_dict

    def to_artist(self) -> Artist:
        """Konvertierung in ein Artist-Objekt für SQLAlchemy."""
        logger.debug("self={}", self)
        artist_dict = self.to_dict()
        artist: Final = Artist(**artist_dict)
        logger.debug("artist={}", artist)
        return artist
