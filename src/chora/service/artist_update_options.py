"""Optionsklasse für Artist-Updates mit Vollersatz von Relationen."""

from dataclasses import dataclass
from datetime import date

from chora.entity.song import Song
from chora.entity.vertrag import Vertrag

__all__ = ["ArtistPatchData", "ArtistUpdateOptions"]


@dataclass(slots=True, kw_only=True)
class ArtistUpdateOptions:
    """Optionen fuer Artist-Updates mit Vollersatz von Relationen."""

    replace_vertrag: bool = False
    replace_songs: bool = False
    song_ids: list[int] | None = None


@dataclass(slots=True, kw_only=True)
class ArtistPatchData:
    """Optionale Daten für PATCH auf Artist."""

    name: str | None = None
    geburtsdatum: date | None = None
    email: str | None = None
    vertrag: Vertrag | None = None
    songs: list[Song] | None = None
