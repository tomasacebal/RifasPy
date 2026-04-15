"""Factory principal para crear la aplicacion Flask."""

from __future__ import annotations

from typing import Any

from flask import Flask, Request, Response, request
from werkzeug.exceptions import BadRequest, MethodNotAllowed, NotFound

from config import Config
from database import init_database
from routes import rifas_bp
from utils.responses import error_response

GENERIC_BAD_REQUEST = "The browser (or proxy) sent a request that this server could not understand."
GENERIC_NOT_FOUND = (
    "The requested URL was not found on the server. If you entered the URL manually "
    "please check your spelling and try again."
)
GENERIC_METHOD_NOT_ALLOWED = "The method is not allowed for the requested URL."


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Crea y configura la aplicacion Flask de rifas.

    Args:
        test_config: Configuracion opcional para pruebas o entornos externos.

    Returns:
        Instancia configurada de Flask.
    """

    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    init_database(app)
    register_cors(app)
    app.register_blueprint(rifas_bp, url_prefix=app.config["API_PREFIX"])
    register_error_handlers(app)

    return app


def register_cors(app: Flask) -> None:
    """Configura headers CORS permisivos para toda la API.

    Args:
        app: Aplicacion Flask a configurar.

    Returns:
        No retorna ningun valor.
    """

    @app.after_request
    def add_cors_headers(response: Response) -> Response:
        """Agrega headers CORS a cada respuesta.

        Args:
            response: Respuesta generada por Flask.

        Returns:
            Respuesta con headers CORS aplicados.
        """

        origin = request.headers.get("Origin")
        requested_headers = _get_requested_headers(request)

        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Headers"] = requested_headers
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Vary"] = "Origin"

        return response


def register_error_handlers(app: Flask) -> None:
    """Registra handlers JSON para errores HTTP y errores internos.

    Args:
        app: Aplicacion Flask a configurar.

    Returns:
        No retorna ningun valor.
    """

    @app.errorhandler(BadRequest)
    def handle_bad_request(error: BadRequest) -> tuple[object, int]:
        """Devuelve un body JSON consistente para errores 400.

        Args:
            error: Excepcion HTTP capturada por Flask.

        Returns:
            Respuesta JSON de error.
        """

        message = _resolve_message(error.description, "Solicitud invalida.", {GENERIC_BAD_REQUEST})
        return error_response(message, 400)

    @app.errorhandler(NotFound)
    def handle_not_found(error: NotFound) -> tuple[object, int]:
        """Devuelve un body JSON consistente para errores 404.

        Args:
            error: Excepcion HTTP capturada por Flask.

        Returns:
            Respuesta JSON de error.
        """

        message = _resolve_message(error.description, "Recurso no encontrado.", {GENERIC_NOT_FOUND})
        return error_response(message, 404)

    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(error: MethodNotAllowed) -> tuple[object, int]:
        """Devuelve un body JSON consistente para errores 405.

        Args:
            error: Excepcion HTTP capturada por Flask.

        Returns:
            Respuesta JSON de error.
        """

        message = _resolve_message(
            error.description,
            "Metodo no permitido.",
            {GENERIC_METHOD_NOT_ALLOWED},
        )
        return error_response(message, 405)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> tuple[object, int]:
        """Devuelve un body JSON consistente para errores no controlados.

        Args:
            error: Excepcion inesperada capturada por Flask.

        Returns:
            Respuesta JSON de error interno.
        """

        app.logger.exception("Unhandled error: %s", error)
        return error_response("Ocurrio un error interno.", 500)


def _get_requested_headers(current_request: Request) -> str:
    """Resuelve los headers permitidos para CORS.

    Args:
        current_request: Request actual recibido por Flask.

    Returns:
        Lista de headers permitidos en formato texto.
    """

    requested_headers = current_request.headers.get("Access-Control-Request-Headers")
    if requested_headers:
        return requested_headers

    return "Content-Type, Authorization"


def _resolve_message(description: str | None, fallback: str, generic_values: set[str]) -> str:
    """Elige un mensaje final para la respuesta de error.

    Args:
        description: Descripcion original de la excepcion.
        fallback: Mensaje local por defecto.
        generic_values: Descripciones genericas que deben ocultarse.

    Returns:
        Mensaje final amigable para el cliente.
    """

    if description is None or description in generic_values:
        return fallback
    return description
