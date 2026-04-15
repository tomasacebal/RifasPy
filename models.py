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
        pagado: Estado de pago opcional.
        timestamp: Fecha de creacion en formato ISO 8601 UTC.
    """

    numero: int
    nombre: str
    telefono: str | None
    mail: str | None
    pagado: bool | None
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
            pagado=_parse_pagado(row["pagado"]),
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
            "pagado": self.pagado,
            "timestamp": self.timestamp,
        }

def _parse_pagado(value: int | None) -> bool | None:
    """Convierte el valor SQLite de `pagado` a boolean o `None`.

    Args:
        value: Valor almacenado en SQLite.

    Returns:
        `True`, `False` o `None`.
    """

    if value is None:
        return None
    return bool(value)
