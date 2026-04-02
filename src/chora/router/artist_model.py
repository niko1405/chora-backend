"""Pydantic-Model für Artist-Entitäten."""


from typing import Any, Final

from loguru import logger

from chora.entity.artist import Artist
from chora.router.artist_update_model import ArtistUpdateModel
from chora.router.song_model import SongModel
from chora.router.vertrag_model import VertragModel

__all__: list[str] = ["ArtistModel"]


class ArtistModel(ArtistUpdateModel):
    """Pydantic Modell für die Darstellung eines Artists in der API."""

    vertrag: VertragModel
    """Zugehöriger Vertrag des Artists."""
    songs: list[SongModel]
    """Liste der Songs des Artists."""

    def to_artist(self) -> Artist:
        """Konvertierung in ein Artist-Objekt für SQLAlchemy.

        :return: Artist-Objekt für SQLAlchemy
        :rtype: Artist
        """
        logger.debug("self={}", self)
        artist_dict: dict[str, Any] = self.to_dict()
        artist_dict["vertrag"] = self.vertrag
        artist_dict["songs"] = self.songs

        artist: Final = Artist(**artist_dict)
        logger.debug("artist={}", artist)
        return artist
