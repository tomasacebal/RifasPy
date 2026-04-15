"""Utilidades para conexion e inicializacion de SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, current_app, g

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS rifas (
    numero INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT,
    mail TEXT,
    pagado INTEGER,
    timestamp TEXT NOT NULL
);
"""


def resolve_database_path(database_path: str, root_path: str) -> Path:
    """Resuelve la ruta final del archivo SQLite.

    Args:
        database_path: Ruta configurada para la base de datos.
        root_path: Ruta raiz de la aplicacion Flask.

    Returns:
        Ruta absoluta al archivo SQLite.
    """

    path = Path(database_path)
    if not path.is_absolute():
        path = Path(root_path) / path
    return path


def get_db() -> sqlite3.Connection:
    """Obtiene la conexion SQLite activa del contexto actual.

    Returns:
        Conexion SQLite configurada con `sqlite3.Row`.
    """

    if "db" not in g:
        database_path = current_app.config["RESOLVED_DATABASE_PATH"]
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


def close_db(_: object | None = None) -> None:
    """Cierra la conexion SQLite si existe en el contexto.

    Args:
        _: Error opcional recibido por Flask en el teardown.

    Returns:
        No retorna ningun valor.
    """

    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db() -> None:
    """Crea la tabla principal de rifas si aun no existe.

    Returns:
        No retorna ningun valor.
    """

    connection = get_db()
    connection.executescript(SCHEMA_SQL)
    ensure_rifas_schema(connection)
    connection.commit()


def ensure_rifas_schema(connection: sqlite3.Connection) -> None:
    """Aplica cambios incrementales al schema de rifas.

    Args:
        connection: Conexion SQLite activa.

    Returns:
        No retorna ningun valor.
    """

    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(rifas)").fetchall()
    }
    if "pagado" not in columns:
        connection.execute("ALTER TABLE rifas ADD COLUMN pagado INTEGER")


def init_database(app: Flask) -> None:
    """Inicializa SQLite y registra el manejo de conexion en Flask.

    Args:
        app: Aplicacion Flask a configurar.

    Returns:
        No retorna ningun valor.
    """

    database_path = resolve_database_path(app.config["DATABASE_PATH"], app.root_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    app.config["RESOLVED_DATABASE_PATH"] = str(database_path)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
