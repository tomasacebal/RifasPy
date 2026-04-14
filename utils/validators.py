"""Validaciones y parsing para requests JSON de rifas."""

from __future__ import annotations

import re
from typing import Any

from flask import Request
from werkzeug.exceptions import BadRequest

ALLOWED_FIELDS = {"numero", "nombre", "telefono", "mail"}
UPDATABLE_FIELDS = {"nombre", "telefono", "mail"}
MAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_json_payload(request: Request) -> dict[str, Any]:
    """Parsea el body JSON y exige un objeto valido.

    Args:
        request: Request Flask actual.

    Returns:
        Diccionario con el payload JSON.

    Raises:
        BadRequest: Si el body no es JSON o no es un objeto.
    """

    if not request.is_json:
        raise BadRequest("El body debe enviarse como JSON.")

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise BadRequest("El body JSON debe ser un objeto.")

    return payload


def validate_create_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Valida y normaliza el payload de creacion.

    Args:
        payload: JSON recibido por el endpoint de alta.

    Returns:
        Payload validado y normalizado.

    Raises:
        BadRequest: Si algun dato no cumple las reglas minimas.
    """

    _validate_allowed_fields(payload)
    _validate_required_fields(payload, {"numero", "nombre"})

    return {
        "numero": _normalize_numero(payload["numero"]),
        "nombre": _normalize_nombre(payload["nombre"]),
        "telefono": _normalize_optional_text(payload.get("telefono"), "telefono"),
        "mail": _normalize_mail(payload.get("mail")),
    }


def validate_put_payload(payload: dict[str, Any], path_numero: int) -> dict[str, Any]:
    """Valida y normaliza el payload de actualizacion completa.

    Args:
        payload: JSON recibido por el endpoint de reemplazo.
        path_numero: Numero presente en la URL.

    Returns:
        Payload validado y normalizado.

    Raises:
        BadRequest: Si hay datos invalidos o inconsistentes.
    """

    _validate_allowed_fields(payload)
    _validate_required_fields(payload, {"nombre"})
    _validate_path_numero(payload, path_numero)

    return {
        "nombre": _normalize_nombre(payload["nombre"]),
        "telefono": _normalize_optional_text(payload.get("telefono"), "telefono"),
        "mail": _normalize_mail(payload.get("mail")),
    }


def validate_patch_payload(payload: dict[str, Any], path_numero: int) -> dict[str, Any]:
    """Valida y normaliza el payload de actualizacion parcial.

    Args:
        payload: JSON recibido por el endpoint parcial.
        path_numero: Numero presente en la URL.

    Returns:
        Payload validado y normalizado solo con campos presentes.

    Raises:
        BadRequest: Si no hay campos editables o hay datos invalidos.
    """

    _validate_allowed_fields(payload)
    _validate_path_numero(payload, path_numero)

    mutable_fields = [field for field in UPDATABLE_FIELDS if field in payload]
    if not mutable_fields:
        raise BadRequest("PATCH debe incluir al menos un campo editable.")

    normalized_payload: dict[str, Any] = {}
    if "nombre" in payload:
        normalized_payload["nombre"] = _normalize_nombre(payload["nombre"])
    if "telefono" in payload:
        normalized_payload["telefono"] = _normalize_optional_text(payload["telefono"], "telefono")
    if "mail" in payload:
        normalized_payload["mail"] = _normalize_mail(payload["mail"])

    return normalized_payload


def _validate_allowed_fields(payload: dict[str, Any]) -> None:
    """Verifica que el payload no contenga campos no soportados.

    Args:
        payload: JSON recibido por el cliente.

    Returns:
        No retorna ningun valor.

    Raises:
        BadRequest: Si aparecen campos no soportados.
    """

    unknown_fields = sorted(set(payload.keys()) - ALLOWED_FIELDS)
    if unknown_fields:
        raise BadRequest(
            f"Campos no soportados: {', '.join(unknown_fields)}."
        )


def _validate_required_fields(payload: dict[str, Any], required_fields: set[str]) -> None:
    """Verifica que existan los campos obligatorios.

    Args:
        payload: JSON recibido por el cliente.
        required_fields: Campos obligatorios para la operacion.

    Returns:
        No retorna ningun valor.

    Raises:
        BadRequest: Si falta algun campo obligatorio.
    """

    missing_fields = sorted(field for field in required_fields if field not in payload)
    if missing_fields:
        raise BadRequest(
            f"Faltan campos obligatorios: {', '.join(missing_fields)}."
        )


def _validate_path_numero(payload: dict[str, Any], path_numero: int) -> None:
    """Impide cambiar el numero de la rifa desde el body.

    Args:
        payload: JSON recibido por el cliente.
        path_numero: Numero presente en la URL.

    Returns:
        No retorna ningun valor.

    Raises:
        BadRequest: Si `numero` en el body difiere del path.
    """

    if "numero" not in payload:
        return

    body_numero = _normalize_numero(payload["numero"])
    if body_numero != path_numero:
        raise BadRequest("El campo 'numero' es inmutable y debe coincidir con la URL.")


def _normalize_numero(value: Any) -> int:
    """Valida que `numero` sea un entero valido.

    Args:
        value: Valor a validar.

    Returns:
        Numero validado como entero.

    Raises:
        BadRequest: Si el valor no es un entero valido.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise BadRequest("El campo 'numero' debe ser un integer.")
    return value


def _normalize_nombre(value: Any) -> str:
    """Valida y normaliza el nombre obligatorio.

    Args:
        value: Valor a validar.

    Returns:
        Nombre limpio y sin espacios laterales.

    Raises:
        BadRequest: Si el nombre es nulo, no es string o queda vacio.
    """

    if not isinstance(value, str):
        raise BadRequest("El campo 'nombre' debe ser un string no vacio.")

    normalized_value = value.strip()
    if not normalized_value:
        raise BadRequest("El campo 'nombre' no puede estar vacio.")

    return normalized_value


def _normalize_optional_text(value: Any, field_name: str) -> str | None:
    """Normaliza un string opcional.

    Args:
        value: Valor a validar.
        field_name: Nombre del campo para mensajes de error.

    Returns:
        String sin espacios laterales o `None` si queda vacio.

    Raises:
        BadRequest: Si el valor no es `None` ni `str`.
    """

    if value is None:
        return None

    if not isinstance(value, str):
        raise BadRequest(f"El campo '{field_name}' debe ser un string o null.")

    normalized_value = value.strip()
    return normalized_value or None


def _normalize_mail(value: Any) -> str | None:
    """Valida y normaliza el mail opcional.

    Args:
        value: Valor a validar.

    Returns:
        Mail valido o `None` si no fue informado.

    Raises:
        BadRequest: Si el mail no cumple el formato basico.
    """

    normalized_value = _normalize_optional_text(value, "mail")
    if normalized_value is None:
        return None

    if not MAIL_PATTERN.fullmatch(normalized_value):
        raise BadRequest("El campo 'mail' debe tener un formato valido.")

    return normalized_value
