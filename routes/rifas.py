"""Endpoints REST para administrar rifas."""

from __future__ import annotations

from flask import Blueprint, request
from werkzeug.exceptions import BadRequest, NotFound

from services.rifa_service import (
    create_rifa,
    delete_rifa,
    get_rifa,
    list_rifas,
    replace_rifa,
    update_rifa_partial,
)
from utils.responses import success_response
from utils.validators import (
    parse_json_payload,
    validate_create_payload,
    validate_patch_payload,
    validate_put_payload,
)

rifas_bp = Blueprint("rifas", __name__)


@rifas_bp.get("/health")
def healthcheck() -> tuple[object, int]:
    """Devuelve el estado basico de salud de la API.

    Returns:
        Respuesta JSON simple para healthcheck.
    """

    return success_response({"status": "ok"})


@rifas_bp.get("/rifas")
def list_rifas_handler() -> tuple[object, int]:
    """Lista todas las rifas registradas.

    Returns:
        Respuesta JSON con la lista ordenada de rifas.
    """

    rifas = [rifa.to_dict() for rifa in list_rifas()]
    return success_response(rifas)


@rifas_bp.get("/rifas/<int:numero>")
def get_rifa_handler(numero: int) -> tuple[object, int]:
    """Obtiene una rifa existente por su numero.

    Args:
        numero: Identificador de la rifa en la URL.

    Returns:
        Respuesta JSON con la rifa encontrada.

    Raises:
        NotFound: Si la rifa no existe.
    """

    rifa = get_rifa(numero)
    if rifa is None:
        raise NotFound("Rifa no encontrada.")

    return success_response(rifa.to_dict())


@rifas_bp.post("/rifas")
def create_rifa_handler() -> tuple[object, int]:
    """Crea una nueva rifa.

    Returns:
        Respuesta JSON con la rifa creada.

    Raises:
        BadRequest: Si el payload es invalido o el numero ya existe.
    """

    payload = parse_json_payload(request)
    validated_payload = validate_create_payload(payload)

    try:
        rifa = create_rifa(validated_payload)
    except ValueError as error:
        raise BadRequest(str(error)) from error

    return success_response(rifa.to_dict(), 201)


@rifas_bp.put("/rifas/<int:numero>")
def replace_rifa_handler(numero: int) -> tuple[object, int]:
    """Reemplaza completamente una rifa existente.

    Args:
        numero: Identificador de la rifa en la URL.

    Returns:
        Respuesta JSON con la rifa actualizada.

    Raises:
        BadRequest: Si el payload es invalido.
        NotFound: Si la rifa no existe.
    """

    payload = parse_json_payload(request)
    validated_payload = validate_put_payload(payload, numero)
    rifa = replace_rifa(numero, validated_payload)
    if rifa is None:
        raise NotFound("Rifa no encontrada.")

    return success_response(rifa.to_dict())


@rifas_bp.patch("/rifas/<int:numero>")
def patch_rifa_handler(numero: int) -> tuple[object, int]:
    """Actualiza parcialmente una rifa existente.

    Args:
        numero: Identificador de la rifa en la URL.

    Returns:
        Respuesta JSON con la rifa actualizada.

    Raises:
        BadRequest: Si el payload es invalido.
        NotFound: Si la rifa no existe.
    """

    payload = parse_json_payload(request)
    validated_payload = validate_patch_payload(payload, numero)
    rifa = update_rifa_partial(numero, validated_payload)
    if rifa is None:
        raise NotFound("Rifa no encontrada.")

    return success_response(rifa.to_dict())


@rifas_bp.delete("/rifas/<int:numero>")
def delete_rifa_handler(numero: int) -> tuple[object, int]:
    """Elimina una rifa existente.

    Args:
        numero: Identificador de la rifa en la URL.

    Returns:
        Respuesta JSON con confirmacion de borrado.

    Raises:
        NotFound: Si la rifa no existe.
    """

    was_deleted = delete_rifa(numero)
    if not was_deleted:
        raise NotFound("Rifa no encontrada.")

    return success_response(
        {
            "message": "Rifa eliminada correctamente.",
            "numero": numero,
        }
    )
