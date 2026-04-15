"""Entity-Klasse für Artist."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Self

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chora.entity.base import Base

if TYPE_CHECKING:
    from chora.entity.song import Song
    from chora.entity.vertrag import Vertrag


class Artist(Base):
    """Entity-Klasse für Artistdaten."""

    __tablename__ = "artist"

    name: Mapped[str]
    """Der Name des Artisten"""

    geburtsdatum: Mapped[date]
    """Das Geburtsdatum."""

    username: Mapped[str | None]
    """Der Benutzername für Login"""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    email: Mapped[str] = mapped_column(unique=True)
    """Die eindeutige Emailadresse."""

    songs: Mapped[list["Song"]] = relationship(
        back_populates="artist",
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Songs"""

    vertrag: Mapped["Vertrag"] = relationship(
        back_populates="artist",
        cascade="save-update, delete",
    )
    """Das in einer 1:1-Beziehung referenzierte Vertrag."""

    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Synchronisation."""

    erzeugt: Mapped[datetime | None] = mapped_column(
        insert_default=datetime.now,
        default=None,
    )
    """Der Zeitstempel für das initiale INSERT in die DB-Tabelle."""

    aktualisiert: Mapped[datetime | None] = mapped_column(
        "aktualisert",
        insert_default=datetime.now,
        onupdate=datetime.now,
        default=None,
    )
    """Der Zeitstempel vom letzen UPDATE in der DB-Tabelle."""

    __mapper_args__ = {"version_id_col": version}

    def set(self, artist: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param artist: Artist-Objekt mit den aktuellen Daten
        """
        self.name = artist.name
        self.email = artist.email
        self.geburtsdatum = artist.geburtsdatum

    def __eq__(self, other: Any) -> bool:
        """Vergleich auf Gleicheit, ohne Joins zu verursachen."""
        # Vergleich der Referenzen: id(self) == id(other)
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    def __repr__(self) -> str:
        """Ausgabe der Artistdaten als String ohne die Song- und Vertragsdaten."""
        return (
            f"Artist(id={self.id}, Name={self.name}, "
            + f"Geburtsdatum={self.geburtsdatum}, Email={self.email})"
        )
