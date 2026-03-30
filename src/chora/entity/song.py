"""Entity-Klasse für Songs."""

from datetime import date

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chora.entity.artist import Artist
from chora.entity.base import Base


class Song(Base):
    """Entity-Klasse für Songs."""

    __tablename___ = "song"

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID, startet ab 1000"""

    titel: Mapped[str]
    """Der Titel des Songs"""

    erscheinungsdatum: Mapped[date]
    """Das Erscheinungsjahr vom Song"""

    dauer: Mapped[int]
    """Die Dauer des Songs in Sekunden"""

    artist_id: Mapped[int] = mapped_column(ForeignKey(column="artist.id"))
    """Id des zugehörigen Artisten als Fremdschlüssel inder DB-Tabelle."""

    artist: Mapped[Artist] = relationship(
        back_populates="songs",
    )
    """Das zugehörige Artist-Objekt"""

    def __repr__(self) -> str:
        """Ausgabe der Songs als String ohne die Artistdaten."""
        return (
            f"Song(id={self.id}, Titel={self.titel}, "
            + f"Erscheinungsdatum={self.erscheinungsdatum}, Dauer={self.dauer})"
        )
