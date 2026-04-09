"""Data Transfer Object (DTO) für Song-Daten."""

from dataclasses import dataclass

import strawberry

from chora.entity.song import Song

__all__: list[str] = ["SongDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class SongDTO:
    """Data Transfer Object (DTO) für Song-Daten."""

    id: int
    """Eindeutige ID des Songs."""

    titel: str
    """Titel des Songs."""

    erscheinungsdatum: str
    """Erscheinungsdatum des Songs im Format 'YYYY-MM-DD'."""

    dauer: int
    """Dauer des Songs in Sekunden."""

    genres: list[str]
    """Genres des Songs als Liste von Namen."""

    artist_id: int
    """ID des zugehörigen Artists."""

    def __init__(self, song: Song) -> None:
        """Initialisiert das SongDTO aus einem Song-Objekt.

        :param song: Song-Objekt, aus dem die Daten extrahiert werden
        """
        song_id: int | None = song.id
        self.id = song_id if song_id is not None else -1
        self.titel = song.titel
        self.erscheinungsdatum = song.erscheinungsdatum.isoformat()
        self.dauer = song.dauer
        self.genres = song.genres_json if song.genres_json is not None else []
        self.artist_id = song.artist_id
