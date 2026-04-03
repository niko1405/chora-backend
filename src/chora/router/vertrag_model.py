"""Pydantic-Modell für die Vertrag-Entität."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from chora.entity.vertrag import Vertrag

__all__ = ["VertragModel"]


class VertragModel(BaseModel):
    """Pydantic Modell für die Darstellung eines Vertrags in der API."""

    startdatum: date
    """Startdatum des Vertrags im Format 'YYYY-MM-DD'."""

    enddatum: date
    """Enddatum des Vertrags im Format 'YYYY-MM-DD'."""

    dauer: Annotated[int, Field(gt=0)]
    """Die Dauer des Vertrags in Monaten."""

    firma: Annotated[
        str,
        StringConstraints(min_length=1, max_length=100),
    ]
    """Die Firma, mit der der Vertrag abgeschlossen wurde."""

    gehalt: Annotated[float, Field(gt=0)]
    """Das Gehalt, das im Vertrag vereinbart wurde."""

    def to_vertrag(self) -> Vertrag:
        """Konvertierung in ein Vertrag-Objekt für SQLAlchemy.

        :return: Vertrag-Objekt für SQLAlchemy
        :rtype: Vertrag
        """
        vertrag_dict = self.model_dump()
        vertrag_dict["id"] = None
        vertrag_dict["artist_id"] = None
        vertrag_dict["artist"] = None
        return Vertrag(**vertrag_dict)
