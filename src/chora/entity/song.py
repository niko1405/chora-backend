"""Entity-Klasse für Songs."""

from __future__ import annotations

from dataclasses import InitVar
from datetime import date
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import JSON, Column, ForeignKey, Identity, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, reconstructor, relationship

from chora.entity.base import Base
from chora.entity.genre import Genre

if TYPE_CHECKING:
    from chora.entity.artist import Artist


song_artist = Table(
    "song_artist",
    Base.metadata,
    Column(
        "song_id",
        Integer,
        ForeignKey("song.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "artist_id",
        Integer,
        ForeignKey("artist.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)


class Song(Base):
    """Entity-Klasse für Songs."""

    __tablename__ = "song"

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

    genres: InitVar[list[Genre] | None]  # ty:ignore[invalid-type-form]
    """Die Genres des Songs als Liste von Genre-Enum-Werten"""

    artists: Mapped[list[Artist]] = relationship(
        back_populates="songs",
        secondary=song_artist,
    )
    """Die zugehörigen Artist-Objekte."""

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
            [genre_enum.name for genre_enum in genres] if genres is not None else None
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

    @property
    def artist_ids(self) -> list[int]:
        """Die IDs aller zugehörigen Artists."""
        return [artist.id for artist in self.artists if artist.id is not None]

    @property
    def artist_id(self) -> int | None:
        """Kompatibilitätszugriff auf die erste zugehörige Artist-ID."""
        artist_ids = self.artist_ids
        return artist_ids[0] if len(artist_ids) > 0 else None

    def __repr__(self) -> str:
        """Ausgabe der Songs als String ohne die Artistdaten."""
        return (
            f"Song(id={self.id}, Titel={self.titel}, "
            + f"Erscheinungsdatum={self.erscheinungsdatum}, Dauer={self.dauer})"
        )
