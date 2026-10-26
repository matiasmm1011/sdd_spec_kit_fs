"""Acceso a SQLite: ruta de la base, conexión y creación del esquema."""

import os
import sqlite3
from pathlib import Path

from fastapi import Request

RUTA_DB_POR_DEFECTO = "datos/tareas.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS materias (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL CHECK (length(nombre) BETWEEN 1 AND 50),
    nombre_clave TEXT NOT NULL UNIQUE,
    color        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tareas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo        TEXT NOT NULL CHECK (length(titulo) BETWEEN 1 AND 100),
    descripcion   TEXT CHECK (descripcion IS NULL OR length(descripcion) <= 500),
    fecha_entrega TEXT NOT NULL,          -- ISO 8601 en UTC, ordenable como texto
    completada    INTEGER NOT NULL DEFAULT 0 CHECK (completada IN (0, 1)),
    materia_id    INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tareas_fecha ON tareas (fecha_entrega);
CREATE INDEX IF NOT EXISTS idx_tareas_materia ON tareas (materia_id);
"""


def obtener_ruta_db() -> str:
    """Ruta de la base de datos: la variable RUTA_DB o el valor por defecto."""
    return os.environ.get("RUTA_DB", RUTA_DB_POR_DEFECTO)


def conectar(ruta: str) -> sqlite3.Connection:
    """Abre una conexión con claves foráneas activas y filas accesibles por nombre."""
    if ruta != ":memory:":
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False: FastAPI puede resolver la dependencia y ejecutar
    # el endpoint en hilos distintos; la conexión no se comparte entre peticiones.
    conexion = sqlite3.connect(ruta, check_same_thread=False)
    conexion.row_factory = sqlite3.Row
    # SQLite ignora las claves foráneas (y el ON DELETE CASCADE) si no se activan
    # en cada conexión.
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_esquema(conexion: sqlite3.Connection) -> None:
    conexion.executescript(ESQUEMA)
    conexion.commit()


def obtener_conexion(request: Request):
    """Dependencia de FastAPI: una conexión por petición, cerrada al terminar."""
    conexion = conectar(request.app.state.ruta_db)
    try:
        yield conexion
    finally:
        conexion.close()
