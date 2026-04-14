"""Configuracion base para la API de rifas."""

from __future__ import annotations


class Config:
    """Define la configuracion base de la aplicacion.

    Returns:
        No retorna ningun valor.
    """

    HOST = "localhost"
    PORT = 6969
    API_PREFIX = "/api/v1"
    DATABASE_PATH = "instance/rifas.db"
    JSON_SORT_KEYS = False
    TESTING = False
