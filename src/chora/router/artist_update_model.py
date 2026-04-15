"""Pydantic Update Modell für die Darstellung der Artist-Entität in der API."""


from typing import Any, Self

from pydantic import ConfigDict, model_validator

from chora.entity.song import Song
from chora.entity.vertrag import Vertrag
from chora.router.artist_base_model import ArtistBaseModel
from chora.router.song_model import SongModel
from chora.router.vertrag_model import VertragModel

__all__ = ["ArtistUpdateModel"]


class ArtistUpdateModel(ArtistBaseModel):
    """Pydantic Modell für die Aktualisierung eines Artists."""

    vertrag: VertragModel | None = None
    """Optionaler Vollersatz für den Vertrag."""

    songs: list[Any] | None = None
    """Optionaler Vollersatz für Songs als Modelle oder reine IDs."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "OneDirection",
                "geburtsdatum": "1990-01-01",
                "email": "onedirection@example.com",
                "username": "harry",
                "vertrag": {
                    "startdatum": "2026-01-01",
                    "enddatum": "2028-12-31",
                    "dauer": 36,
                    "firma": "Universal",
                    "gehalt": 250000.0
                },
                "songs": [
                    {
                        "titel": "My Song",
                        "genres": ["ROCK", "POP"],
                        "erscheinungsdatum": "2026-01-01",
                        "dauer": 215
                    }
                ]
            }
        }
    )

    @model_validator(mode="after")
    def validate_song_representation(self) -> Self:
        """Songs duerfen entweder als IDs oder als Modelle angegeben werden."""
        songs_raw = self.model_dump().get("songs")
        if songs_raw is None:
            return self
        if not isinstance(songs_raw, list) or len(songs_raw) == 0:
            return self

        if not all(isinstance(song, (int, dict)) for song in songs_raw):
            raise ValueError("Songs muessen Song-Objekte oder IDs sein")

        contains_ids = any(isinstance(song, int) for song in songs_raw)
        contains_models = any(isinstance(song, dict) for song in songs_raw)
        if contains_ids and contains_models:
            raise ValueError(
                "Songs muessen entweder als IDs oder als Song-Objekte angegeben werden"
            )
        return self

    def songs_are_ids(self) -> bool:
        """Pruefen, ob Songs als ID-Liste angegeben wurden."""
        songs_raw = self.model_dump().get("songs")
        if songs_raw is None:
            return False
        if not isinstance(songs_raw, list) or len(songs_raw) == 0:
            return False
        return all(isinstance(song, int) for song in songs_raw)

    def song_ids(self) -> list[int] | None:
        """Song-IDs liefern, falls Songs als ID-Liste angegeben wurden."""
        if not self.songs_are_ids():
            return None
        songs_raw = self.model_dump().get("songs")
        if not isinstance(songs_raw, list):
            return None
        return [song_id for song_id in songs_raw if isinstance(song_id, int)]

    def songs_to_entities(self) -> list[Song] | None:
        """Songs als Entities liefern, falls Songs als Objekte angegeben wurden."""
        songs_raw = self.model_dump().get("songs")
        if songs_raw is None:
            return None
        if self.songs_are_ids():
            return None
        if not isinstance(songs_raw, list):
            return None

        songs_list = songs_raw
        return [
            SongModel.model_validate(song_raw).to_song()
            for song_raw in songs_list
            if isinstance(song_raw, dict)
        ]

    def vertrag_to_entity(self) -> Vertrag | None:
        """Vertrag als Entity liefern."""
        if self.vertrag is None:
            return None
        return self.vertrag.to_vertrag()
