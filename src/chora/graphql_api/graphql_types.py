"""Schema für GraphQL."""

import strawberry

__all__ = ["ArtistInput", "Suchparameter", "VertragInput"]


@strawberry.input
class Suchparameter:
    """Suchparameter für Artisten."""

    name: str | None = None
    """Name des Artisten."""

    email: str | None = None
    """E-Mail-Adresse des Artisten."""


@strawberry.input
class VertragInput:
    """Eingabe für Vertrag."""

    dauer: int
    """Dauer des Vertrags in Monaten."""

    startdatum: str
    """Startdatum des Vertrags."""

    enddatum: str
    """Enddatum des Vertrags."""

    firma: str
    """Firma, mit der der Vertrag abgeschlossen wurde."""

    gehalt: float
    """Gehalt, das im Vertrag vereinbart wurde."""


@strawberry.input
class ArtistInput:
    """Eingabe für Künstler."""

    name: str
    """Name des Künstlers."""

    geburtsdatum: str
    """Geburtsdatum des Künstlers im Format 'YYYY-MM-DD'."""

    email: str
    """E-Mail-Adresse des Künstlers."""

    vertrag: VertragInput
    """Vertrag des Künstlers."""

    songs: list[int]
    """Liste der Song-IDs des Künstlers."""

    username: str
    """Benutzername des Künstlers."""


@strawberry.type
class CreatePayload:
    """Payload für die Erstellung eines Künstlers."""

    id: int
    """ID des erstellten Künstlers."""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # noqa: N815  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""
