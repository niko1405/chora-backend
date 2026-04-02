"""Entity-Klasse für Songs."""

from dataclasses import InitVar
from datetime import date

from loguru import logger
from sqlalchemy import JSON, ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, reconstructor, relationship

from chora.entity.artist import Artist
from chora.entity.base import Base
from chora.entity.genre import Genre


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

    genres: InitVar[list[Genre] | None]
    """Die Genres des Songs als Liste von Genre-Enum-Werten"""

    artist_id: Mapped[int] = mapped_column(ForeignKey(column="artist.id"))
    """Id des zugehörigen Artisten als Fremdschlüssel inder DB-Tabelle."""

    artist: Mapped[Artist] = relationship(
        back_populates="songs",
    )
    """Das zugehörige Artist-Objekt"""

    genres_json: Mapped[list[str] | None] = mapped_column(
        JSON,
        name="genres",
        init=False,
    )
    """Die Genres als JSON-Array von Strings für die DB-Spalte"""

    def __post_init__(
        self,
        genres: list[Genre] | None,
    ) -> None:
        """Für SQLAlchemy: genres_json setzen für INSERT oder UPDATE.

        :param genres: Liste mit Genres als Enum
        """
        logger.debug("genres={}", genres)
        logger.debug("self={}", self)
        self.genres_json = (
            [genre_enum.name for genre_enum in genres]
            if genres is not None
            else None
        )
        logger.debug("self.genres_json={}", self.genres_json)

    @reconstructor
    def on_load(self) -> None:
        """Auslesen aus der DB: die Enum-Liste durch die DB-Strings initialisieren."""
        self.genres = (  # pyright: ignore[reportAttributeAccessIssue]
            [Genre[genre_name] for genre_name in self.genres_json]
            if self.genres_json is not None
            else []
        )
        logger.debug(
            "genres={}",
            self.genres,  # pyright: ignore[reportAttributeAccessIssue]
        )

    def __repr__(self) -> str:
        """Ausgabe der Songs als String ohne die Artistdaten."""
        return (
            f"Song(id={self.id}, Titel={self.titel}, "
            + f"Erscheinungsdatum={self.erscheinungsdatum}, Dauer={self.dauer})"
        )
