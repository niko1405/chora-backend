"""Pydantic-Modell für die Song-Entität."""

from datetime import date
from typing import Annotated, Self

from pydantic import BaseModel, Field, StringConstraints, model_validator

from chora.entity.genre import Genre
from chora.entity.song import Song

__all__ = ["SongModel"]


class SongModel(BaseModel):
    """Pydantic Modell für die Darstellung eines Songs in der API."""

    titel: Annotated[
        str,
        StringConstraints(pattern=r"^[a-zA-Z\s]+$", min_length=1, max_length=100),
    ]
    """Der Titel des Songs."""

    genres: list[Genre]
    """Die Genres des Songs."""

    erscheinungsdatum: date
    """Das Erscheinungsdatum des Songs."""

    dauer: Annotated[int, Field(gt=0)]
    """Die Dauer des Songs in Sekunden."""

    artist_ids: list[int] | None = None
    """Die IDs der zugehörigen Artists."""

    @model_validator(mode="after")
    def validate_artist_ids(self) -> Self:
        """Artist-IDs müssen als reine Integer-Liste angegeben werden."""
        artist_ids_raw = self.model_dump().get("artist_ids")
        if artist_ids_raw is None:
            return self
        if not isinstance(artist_ids_raw, list):
            raise ValueError("artist_ids muss eine Liste sein")
        for artist_id in artist_ids_raw:
            if not isinstance(artist_id, int):
                raise ValueError("artist_ids muss nur IDs enthalten")
        return self

    @model_validator(mode="after")
    def validate_erscheinungsdatum(self) -> Self:
        """Das Erscheinungsdatum darf nicht in der Zukunft liegen."""
        if self.erscheinungsdatum > date.today():
            raise ValueError("erscheinungsdatum darf nicht in der Zukunft liegen")
        return self

    def to_song(self) -> Song:
        """Konvertierung in ein Song-Objekt für SQLAlchemy.

        :return: Song-Objekt für SQLAlchemy
        :rtype: Song
        """
        song_dict = self.model_dump()
        song_dict["id"] = None
        song_dict.pop("artist_ids", None)
        song_dict["artists"] = []
        return Song(**song_dict)
