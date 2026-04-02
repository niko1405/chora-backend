"""Entity-Klasse für Vertrag."""

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chora.entity.artist import Artist
from chora.entity.base import Base


class Vertrag(Base):
    """Die Entity-Klasse für Vertrag."""

    __tablename__ = "vertrag"

    dauer: Mapped[int]
    """Die Dauer des Vertrags in Monaten."""

    firma: Mapped[str]
    """Die Firma, mit der der Vertrag abgeschlossen wurde."""

    gehalt: Mapped[float]
    """Das Gehalt, das im Vertrag vereinbart wurde."""

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
         primary_key=True
    )
    """Die eindeutige ID des Vertrags."""

    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    """Die ID des Künstlers, der den Vertrag abgeschlossen hat, als Fremdschlüssel."""

    artist: Mapped[Artist] = relationship(back_populates="vertrag")
    """Die Beziehung zum Künstler, der den Vertrag abgeschlossen hat."""

    def __repr__(self) -> str:
        """String-Repräsentation des Vertrags."""
        return (
            f"Vertrag(id={self.id}, dauer={self.dauer}, "
            f"firma='{self.firma}', gehalt={self.gehalt})"
        )
