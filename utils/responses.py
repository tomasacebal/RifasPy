"""Helpers para construir respuestas JSON consistentes."""

from __future__ import annotations

from typing import Any

from flask import Response, jsonify


def success_response(data: Any, status_code: int = 200) -> tuple[Response, int]:
    """Construye una respuesta JSON de exito.

    Args:
        data: Carga util que sera enviada al cliente.
        status_code: Codigo HTTP de la respuesta.

    Returns:
        Tupla con la respuesta Flask y el codigo HTTP.
    """

    return jsonify({"success": True, "data": data}), status_code


def error_response(
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
) -> tuple[Response, int]:
    """Construye una respuesta JSON de error.

    Args:
        message: Mensaje principal de error.
        status_code: Codigo HTTP de la respuesta.
        details: Detalles opcionales para debugging o validacion.

    Returns:
        Tupla con la respuesta Flask y el codigo HTTP.
    """

    error_payload: dict[str, Any] = {"message": message}
    if details is not None:
        error_payload["details"] = details

    return jsonify({"success": False, "error": error_payload}), status_code
