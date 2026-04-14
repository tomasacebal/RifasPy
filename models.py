"""Modelos simples para representar entidades de la API."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Rifa:
    """Representa una rifa persistida en la base de datos.

    Args:
        numero: Identificador unico de la rifa.
        nombre: Nombre asociado a la rifa.
        telefono: Telefono opcional del participante.
        mail: Mail opcional del participante.
        timestamp: Fecha de creacion en formato ISO 8601 UTC.
    """

    numero: int
    nombre: str
    telefono: str | None
    mail: str | None
    timestamp: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Rifa":
        """Construye una instancia a partir de una fila SQLite.

        Args:
            row: Fila obtenida desde SQLite.

        Returns:
            Instancia de `Rifa`.
        """

        return cls(
            numero=row["numero"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            mail=row["mail"],
            timestamp=row["timestamp"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Serializa la rifa a un diccionario JSON friendly.

        Returns:
            Diccionario con los campos de la rifa.
        """

        return {
            "numero": self.numero,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "mail": self.mail,
            "timestamp": self.timestamp,
        }
