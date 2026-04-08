"""Data Transfer Object (DTO) für Artist-Daten."""

from dataclasses import dataclass

import strawberry

from chora.entity.artist import Artist
from chora.service.vertrag_dto import VertragDTO

__all__: list[str] = ["ArtistDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class ArtistDTO:
    """Data Transfer Object (DTO) für Artist-Daten."""

    id: int
    """Eindeutige ID des Artists."""

    version: int
    """Versionsnummer für optimistische Synchronisation."""

    name: str
    """Name des Artists."""

    email: str
    """E-Mail-Adresse des Artists."""

    geburtsdatum: str
    """Geburtsdatum des Artists im Format 'YYYY-MM-DD'."""

    vertrag: VertragDTO
    """Vertrag des Artists."""

    username: str | None
    """Benutzername des Artists, falls vorhanden."""

    def __init__(self, artist: Artist) -> None:
        """Initialisiert das ArtistDTO aus einem Artist-Objekt.

        :param artist: Artist-Objekt, aus dem die Daten extrahiert werden
        """
        artist_id: int | None = artist.id
        self.id = artist_id if artist_id is not None else -1
        self.version = artist.version
        self.name = artist.name
        self.email = artist.email
        self.geburtsdatum = artist.geburtsdatum.isoformat()
        self.vertrag = VertragDTO(artist.vertrag)
        self.username: str = artist.username if artist.username is not None else "N/A"
