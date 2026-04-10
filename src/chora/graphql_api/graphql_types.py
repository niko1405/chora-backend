"""Schema für GraphQL."""

import strawberry

__all__ = ["ArtistInput", "SongInput", "Suchparameter", "VertragInput"]


@strawberry.input
class Suchparameter:
    """Suchparameter für Artisten."""

    name: str | None = None
    """Name des Artisten."""

    genre: str | None = None
    """Genre des Artisten."""

    alter: int | None = None
    """Alter des Artisten."""

    email: str | None = None
    """E-Mail-Adresse des Artisten."""


@strawberry.input
class VertragInput:
    """Eingabe für Vertrag."""

    artist_id: int
    """ID des Artisten."""

    agent_id: int
    """ID des Agenten."""

    start_date: str
    """Startdatum des Vertrags."""

    end_date: str
    """Enddatum des Vertrags."""


@strawberry.input
class SongInput:
    """Eingabe für Song."""

    title: str
    """Titel des Songs."""

    duration: int
    """Dauer des Songs in Sekunden."""


@strawberry.input
class ArtistInput:
    """Eingabe für Künstler."""

    name: str
    """Name des Künstlers."""

    genre: str
    """Genre des Künstlers."""

    alter: int
    """Alter des Künstlers."""

    email: str
    """E-Mail-Adresse des Künstlers."""

    vertrag: VertragInput
    """Vertrag des Künstlers."""

    songs: list[SongInput]
    """Liste der Songs des Künstlers."""

    username: str
    """Benutzername des Künstlers."""
