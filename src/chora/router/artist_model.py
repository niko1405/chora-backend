"""Pydantic-Model für Artist-Entitäten."""


from typing import Final

from chora.entity.artist import Artist
from chora.router.artist_base_model import ArtistBaseModel
from chora.router.song_model import SongModel
from chora.router.vertrag_model import VertragModel

__all__: list[str] = ["ArtistModel"]


class ArtistModel(ArtistBaseModel):
    """Pydantic Modell für die Darstellung eines Artists in der API."""

    vertrag: VertragModel
    """Zugehöriger Vertrag des Artists."""
    songs: list[SongModel]
    """Liste der Songs des Artists."""

    def to_artist(self) -> Artist:
        """Konvertierung in ein Artist-Objekt für SQLAlchemy."""
        artist: Final = super().to_artist()
        artist.vertrag = self.vertrag.to_vertrag()
        artist.songs = [song_model.to_song() for song_model in self.songs]
        return artist
