"""Data Transfer Object (DTO) für Vertrags-Daten."""

from dataclasses import dataclass
from datetime import date

import strawberry

from chora.entity.vertrag import Vertrag

__all__: list[str] = ["VertragDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class VertragDTO:
    """Data Transfer Object (DTO) für Vertrags-Daten."""

    id: int
    """Eindeutige ID des Vertrags."""

    startdatum: date
    """Startdatum des Vertrags im Format 'YYYY-MM-DD'."""

    enddatum: date
    """Enddatum des Vertrags im Format 'YYYY-MM-DD'."""

    dauer: int
    """Die Dauer des Vertrags in Monaten."""

    firma: str
    """Die Firma, mit der der Vertrag abgeschlossen wurde."""

    gehalt: float
    """Das Gehalt, das im Vertrag vereinbart wurde."""

    def __init__(self, vertrag: Vertrag) -> None:
        """Initialisiert das VertragDTO aus einem Vertrag-Objekt.

        :param vertrag: Vertrag-Objekt, aus dem die Daten extrahiert werden
        """
        self.id = vertrag.id
        self.startdatum = vertrag.startdatum
        self.enddatum = vertrag.enddatum
        self.dauer = vertrag.dauer
        self.firma = vertrag.firma
        self.gehalt = vertrag.gehalt
