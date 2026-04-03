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

    name: str
    """Name des Artists."""

    email: str
    """E-Mail-Adresse des Artists."""

    geburtsdatum: str
    """Geburtsdatum des Artists im Format 'YYYY-MM-DD'."""

    vertrag: VertragDTO
    """Vertrag des Artists."""

    def __init__(self, artist: Artist) -> None:
        """Initialisiert das ArtistDTO aus einem Artist-Objekt.

        :param artist: Artist-Objekt, aus dem die Daten extrahiert werden
        """
        self.id = artist.id
        self.name = artist.name
        self.email = artist.email
        self.geburtsdatum = artist.geburtsdatum.isoformat()
        self.vertrag = VertragDTO(artist.vertrag)
