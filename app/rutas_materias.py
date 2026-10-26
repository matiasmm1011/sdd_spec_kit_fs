"""Endpoints de /api/materias."""

import sqlite3
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Response

from app.db import obtener_conexion
from app.esquemas import MateriaEntrada, MateriaSalida

router = APIRouter(prefix="/api/materias", tags=["materias"])

CONSULTA_MATERIAS = """
    SELECT m.id, m.nombre, m.color, COUNT(t.id) AS total_tareas
    FROM materias m
    LEFT JOIN tareas t ON t.materia_id = m.id
"""


def _clave_del_nombre(nombre: str) -> str:
    """Clave de unicidad: ignora mayúsculas y la forma en que se escribió el acento."""
    return unicodedata.normalize("NFC", nombre).casefold()


def _materia_o_404(conexion: sqlite3.Connection, materia_id: int) -> dict:
    fila = conexion.execute(
        CONSULTA_MATERIAS + " WHERE m.id = ? GROUP BY m.id", (materia_id,)
    ).fetchone()
    if fila is None:
        raise HTTPException(404, detail={"campo": None, "mensaje": "La materia no existe."})
    return dict(fila)


def _nombre_repetido() -> HTTPException:
    return HTTPException(
        409, detail={"campo": "nombre", "mensaje": "Ya existe una materia con ese nombre."}
    )


def _clave_de_orden(nombre: str) -> str:
    """Orden alfabético en español: sin distinguir mayúsculas ni acentos."""
    sin_acentos = "".join(
        letra
        for letra in unicodedata.normalize("NFD", nombre)
        if not unicodedata.combining(letra)
    )
    return sin_acentos.casefold()


@router.get("", response_model=list[MateriaSalida])
def listar_materias(conexion: sqlite3.Connection = Depends(obtener_conexion)):
    filas = conexion.execute(CONSULTA_MATERIAS + " GROUP BY m.id")
    materias = [dict(fila) for fila in filas]
    # SQLite no sabe ordenar con acentos (colocaría "Álgebra" después de "Física").
    return sorted(materias, key=lambda m: (_clave_de_orden(m["nombre"]), m["id"]))


@router.post("", status_code=201, response_model=MateriaSalida)
def crear_materia(
    datos: MateriaEntrada, conexion: sqlite3.Connection = Depends(obtener_conexion)
):
    try:
        cursor = conexion.execute(
            "INSERT INTO materias (nombre, nombre_clave, color) VALUES (?, ?, ?)",
            (datos.nombre, _clave_del_nombre(datos.nombre), datos.color),
        )
    except sqlite3.IntegrityError:
        raise _nombre_repetido() from None
    conexion.commit()
    return _materia_o_404(conexion, cursor.lastrowid)


@router.put("/{materia_id}", response_model=MateriaSalida)
def editar_materia(
    materia_id: int,
    datos: MateriaEntrada,
    conexion: sqlite3.Connection = Depends(obtener_conexion),
):
    _materia_o_404(conexion, materia_id)
    try:
        conexion.execute(
            "UPDATE materias SET nombre = ?, nombre_clave = ?, color = ? WHERE id = ?",
            (datos.nombre, _clave_del_nombre(datos.nombre), datos.color, materia_id),
        )
    except sqlite3.IntegrityError:
        raise _nombre_repetido() from None
    conexion.commit()
    return _materia_o_404(conexion, materia_id)


@router.delete("/{materia_id}", status_code=204)
def eliminar_materia(
    materia_id: int, conexion: sqlite3.Connection = Depends(obtener_conexion)
):
    """Elimina la materia y, por la cascada de la base, todas sus tareas."""
    _materia_o_404(conexion, materia_id)
    conexion.execute("DELETE FROM materias WHERE id = ?", (materia_id,))
    conexion.commit()
    return Response(status_code=204)
