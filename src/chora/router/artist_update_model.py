"""Pydantic Update Modell für die Darstellung der Artist-Entität in der API."""


from typing import Self

from pydantic import ConfigDict, model_validator

from chora.entity.vertrag import Vertrag
from chora.router.artist_base_model import ArtistBaseModel
from chora.router.vertrag_model import VertragModel

__all__ = ["ArtistUpdateModel"]


class ArtistUpdateModel(ArtistBaseModel):
    """Pydantic Modell für die Aktualisierung eines Artists."""

    vertrag: VertragModel | None = None
    """Optionaler Vollersatz für den Vertrag."""

    songs: list[int] | None = None
    """Optionaler Vollersatz für Songs als IDs."""

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
                "songs": [1001, 1002]
            }
        }
    )

    @model_validator(mode="after")
    def validate_song_ids(self) -> Self:
        """Songs duerfen nur als IDs angegeben werden."""
        songs_raw = self.model_dump().get("songs")
        if songs_raw is None:
            return self
        if not isinstance(songs_raw, list):
            raise ValueError("Songs muessen als ID-Liste angegeben werden")
        for song_id in songs_raw:
            if not isinstance(song_id, int):
                raise ValueError("Songs muessen als ID-Liste angegeben werden")
        return self

    def songs_are_ids(self) -> bool:
        """Pruefen, ob Songs als ID-Liste angegeben wurden."""
        return self.songs is not None

    def song_ids(self) -> list[int] | None:
        """Song-IDs liefern, falls Songs als ID-Liste angegeben wurden."""
        return self.songs

    def vertrag_to_entity(self) -> Vertrag | None:
        """Vertrag als Entity liefern."""
        if self.vertrag is None:
            return None
        return self.vertrag.to_vertrag()
