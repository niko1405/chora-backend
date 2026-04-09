"""Pydantic-Modell für die Song-Entität."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from chora.entity.genre import Genre
from chora.entity.song import Song

__all__ = ["SongModel"]


class SongModel(BaseModel):
    """Pydantic Modell für die Darstellung eines Songs in der API."""

    titel: Annotated[
        str,
        StringConstraints(
            pattern=r"^[a-zA-Z\s]+$", min_length=1, max_length=100
        ),
    ]
    """Der Titel des Songs."""

    genres: list[Genre]
    """Die Genres des Songs."""

    erscheinungsdatum: date
    """Das Erscheinungsdatum des Songs."""

    dauer: Annotated[int, Field(gt=0)]
    """Die Dauer des Songs in Sekunden."""

    def to_song(self) -> Song:
        """Konvertierung in ein Song-Objekt für SQLAlchemy.

        :return: Song-Objekt für SQLAlchemy
        :rtype: Song
        """
        song_dict = self.model_dump()
        song_dict["id"] = None
        song_dict["artist_id"] = None
        song_dict["artist"] = None
        return Song(**song_dict)
