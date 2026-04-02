"""Pydantic Update Modell für die Darstellung der Artist-Entität in der API."""


from datetime import date
from typing import Annotated, Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

from chora.entity.artist import Artist

__all__ = ["ArtistUpdateModel"]


class ArtistUpdateModel(BaseModel):
    """Pydantic Modell für die Aktualisierung eines Artists."""

    name: Annotated[
        str,
        StringConstraints(
            pattern=r"^[a-zA-Z\s]+$", min_length=1, max_length=100
        ),
    ]
    """Der Name des Artisten"""

    geburtsdatum: date
    """Das Geburtsdatum."""

    email: EmailStr
    """Die eindeutige Emailadresse."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "OneDirection",
                "geburtsdatum": "1990-01-01",
                "email": "onedirection@example.com"
            }
        }
    )

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
        """Konvertierung in ein Artist-Objekt für SQLAlchemy.

        :return: Artist-Objekt für SQLAlchemy
        :rtype: Artist
        """
        logger.debug("self={}", self)
        artist_dict = self.to_dict()

        artist = Artist(**artist_dict)
        logger.debug("artist={}", artist)
        return artist
