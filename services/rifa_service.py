"""Servicios CRUD para la entidad `Rifa`."""

from __future__ import annotations

from datetime import UTC, datetime

from database import get_db
from models import Rifa


def list_rifas() -> list[Rifa]:
    """Lista todas las rifas ordenadas por numero.

    Returns:
        Lista de instancias `Rifa`.
    """

    connection = get_db()
    rows = connection.execute(
        """
        SELECT numero, nombre, telefono, mail, pagado, timestamp
        FROM rifas
        ORDER BY numero ASC
        """
    ).fetchall()
    return [Rifa.from_row(row) for row in rows]


def get_rifa(numero: int) -> Rifa | None:
    """Busca una rifa por su numero.

    Args:
        numero: Identificador de la rifa.

    Returns:
        Instancia `Rifa` si existe, o `None` si no se encontro.
    """

    connection = get_db()
    row = connection.execute(
        """
        SELECT numero, nombre, telefono, mail, pagado, timestamp
        FROM rifas
        WHERE numero = ?
        """,
        (numero,),
    ).fetchone()

    if row is None:
        return None

    return Rifa.from_row(row)


def create_rifa(payload: dict[str, object]) -> Rifa:
    """Crea una nueva rifa en la base de datos.

    Args:
        payload: Datos validados del request.

    Returns:
        Rifa creada y persistida.

    Raises:
        ValueError: Si ya existe una rifa con el mismo numero.
    """

    numero = int(payload["numero"])
    if get_rifa(numero) is not None:
        raise ValueError("Ya existe una rifa con ese numero.")

    timestamp = build_timestamp()
    connection = get_db()
    connection.execute(
        """
        INSERT INTO rifas (numero, nombre, telefono, mail, pagado, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            numero,
            payload["nombre"],
            payload["telefono"],
            payload["mail"],
            _serialize_pagado(payload["pagado"]),
            timestamp,
        ),
    )
    connection.commit()

    created_rifa = get_rifa(numero)
    if created_rifa is None:
        raise RuntimeError("No se pudo recuperar la rifa creada.")

    return created_rifa


def replace_rifa(numero: int, payload: dict[str, object]) -> Rifa | None:
    """Reemplaza completamente los campos mutables de una rifa.

    Args:
        numero: Identificador de la rifa.
        payload: Datos validados del request.

    Returns:
        Rifa actualizada, o `None` si no existe.
    """

    if get_rifa(numero) is None:
        return None

    connection = get_db()
    connection.execute(
        """
        UPDATE rifas
        SET nombre = ?, telefono = ?, mail = ?, pagado = ?
        WHERE numero = ?
        """,
        (
            payload["nombre"],
            payload["telefono"],
            payload["mail"],
            _serialize_pagado(payload["pagado"]),
            numero,
        ),
    )
    connection.commit()

    return get_rifa(numero)


def update_rifa_partial(numero: int, payload: dict[str, object]) -> Rifa | None:
    """Actualiza parcialmente una rifa existente.

    Args:
        numero: Identificador de la rifa.
        payload: Campos parciales ya validados.

    Returns:
        Rifa actualizada, o `None` si no existe.
    """

    current_rifa = get_rifa(numero)
    if current_rifa is None:
        return None

    updated_nombre = payload.get("nombre", current_rifa.nombre)
    updated_telefono = payload.get("telefono", current_rifa.telefono)
    updated_mail = payload.get("mail", current_rifa.mail)
    updated_pagado = payload.get("pagado", current_rifa.pagado)

    connection = get_db()
    connection.execute(
        """
        UPDATE rifas
        SET nombre = ?, telefono = ?, mail = ?, pagado = ?
        WHERE numero = ?
        """,
        (
            updated_nombre,
            updated_telefono,
            updated_mail,
            _serialize_pagado(updated_pagado),
            numero,
        ),
    )
    connection.commit()

    return get_rifa(numero)


def delete_rifa(numero: int) -> bool:
    """Elimina una rifa por su numero.

    Args:
        numero: Identificador de la rifa.

    Returns:
        `True` si se elimino una fila, `False` si no existia.
    """

    connection = get_db()
    cursor = connection.execute(
        "DELETE FROM rifas WHERE numero = ?",
        (numero,),
    )
    connection.commit()
    return cursor.rowcount > 0


def build_timestamp() -> str:
    """Genera un timestamp UTC serializado en ISO 8601.

    Returns:
        Timestamp UTC con sufijo `Z`.
    """

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _serialize_pagado(value: bool | None) -> int | None:
    """Convierte el valor de `pagado` al formato persistible en SQLite.

    Args:
        value: Valor validado del payload o del modelo.

    Returns:
        `1`, `0` o `None`.
    """

    if value is None:
        return None
    return int(value)
