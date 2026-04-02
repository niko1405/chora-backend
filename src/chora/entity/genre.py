"""Enum für die Musikgenres, die in der Datenbank verwendet werden."""

from enum import StrEnum

import strawberry


@strawberry.enum
class Genre(StrEnum):
    """Enum für die Musikgenres, die in der Datenbank verwendet werden."""

    ROCK = "Rock"
    POP = "Pop"
    HIPHOP = "HipHop"
    JAZZ = "Jazz"
    CLASSICAL = "Classical"
    ELECTRONIC = "Electronic"
    COUNTRY = "Country"
    REGGAE = "Reggae"
    BLUES = "Blues"
    FOLK = "Folk"
    METAL = "Metal"
    PUNK = "Punk"
    OTHER = "Other"
