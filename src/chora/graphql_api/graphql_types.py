"""Schema für GraphQL."""
import email_validator
from chora.graphql_api import VertragInput
from gevent.ares import __all__


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


