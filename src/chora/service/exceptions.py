"""Exceptions in der Geschäftslogik."""

from collections.abc import Mapping

__all__ = [
    "EmailExistsError",
    "ForbiddenError",
    "NotFoundError",
    "SongTitleExistsError",
    "UsernameExistsError",
    "VersionOutdatedError",
]


class EmailExistsError(Exception):
    """Exception, wenn die Email bereits existiert."""

    def __init__(self, email: str) -> None:
        """Initialisiert die Exception mit der Email.

        :param email: Die Email, die bereits existiert
        """
        super().__init__(f"Die Email '{email}' existiert bereits.")
        self.email = email


class ForbiddenError(Exception):
    """Exception, wenn der Benutzer nicht berechtigt ist, eine Aktion durchzuführen."""

    def __init__(self) -> None:
        """Initialisiert die Exception."""
        super().__init__(
            "Der Benutzer ist nicht berechtigt, diese Aktion durchzuführen."
        )


class NotFoundError(Exception):
    """Exception, wenn eine Ressource nicht gefunden wurde."""

    def __init__(
        self, artist_id: int | None = None,
        suchparameter: Mapping[str, str] | None = None) -> None:
        """Initialisiert die Exception.

        :param artist_id: Die ID des nicht gefundenen Künstlers
        :param suchparameter: Die Suchparameter für die Suche
        """
        super().__init__("Not Found")
        self.artist_id = artist_id
        self.suchparameter = suchparameter


class UsernameExistsError(Exception):
    """Exception, wenn der Benutzername bereits existiert."""

    def __init__(self, username: str) -> None:
        """Initialisiert die Exception mit dem Benutzernamen.

        :param username: Der Benutzername, der bereits existiert
        """
        super().__init__(f"Der Benutzername '{username}' existiert bereits.")
        self.username = username


class SongTitleExistsError(Exception):
    """Exception, wenn der Songtitel bereits existiert."""

    def __init__(self, titel: str) -> None:
        """Initialisiert die Exception mit dem Songtitel.

        :param titel: Der Songtitel, der bereits existiert
        """
        super().__init__(f"Der Songtitel '{titel}' existiert bereits.")
        self.titel = titel


class VersionOutdatedError(Exception):
    """Exception, wenn die Version eines Objekts veraltet ist."""

    def __init__(self, version: int) -> None:
        """Initialisiert die Exception mit der veralteten Version.

        :param version: Die veraltete Version
        """
        super().__init__(f"Die Version {version} ist veraltet.")
        self.version = version
