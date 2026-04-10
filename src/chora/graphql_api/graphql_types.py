"""Schema für GraphQL."""

import strawberry

__all__ = ["Suchparameter", "VertragInput"]


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
