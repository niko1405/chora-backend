"""Pydantic-Model für Artist-Entitäten."""

from typing import Final

from chora.entity.artist import Artist
from chora.router.artist_base_model import ArtistBaseModel
from chora.router.vertrag_model import VertragModel

__all__: list[str] = ["ArtistModel"]


class ArtistModel(ArtistBaseModel):
    """Pydantic Modell für die Darstellung eines Artists in der API."""

    vertrag: VertragModel
    """Zugehöriger Vertrag des Artists."""
    songs: list[int] | None = None
    """Liste der Song-IDs des Artists."""

    def to_artist(self) -> Artist:
        """Konvertierung in ein Artist-Objekt für SQLAlchemy."""
        artist: Final = super().to_artist()
        artist.vertrag = self.vertrag.to_vertrag()
        return artist
