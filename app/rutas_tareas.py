"""Endpoints de /api/tareas."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response

from app.db import obtener_conexion
from app.esquemas import TareaEntrada, TareaSalida

router = APIRouter(prefix="/api/tareas", tags=["tareas"])

CONSULTA_TAREAS = """
    SELECT t.id, t.titulo, t.descripcion, t.fecha_entrega, t.completada,
           m.id AS materia_id, m.nombre AS materia_nombre, m.color AS materia_color
    FROM tareas t
    JOIN materias m ON m.id = t.materia_id
"""


def _fecha_a_texto(fecha: datetime) -> str:
    """UTC con formato fijo, para que el orden alfabético sea el cronológico."""
    return fecha.strftime("%Y-%m-%dT%H:%M:%SZ")


def _fila_a_tarea(fila: sqlite3.Row) -> dict:
    return {
        "id": fila["id"],
        "titulo": fila["titulo"],
        "descripcion": fila["descripcion"],
        "fecha_entrega": fila["fecha_entrega"],
        "completada": bool(fila["completada"]),
        "materia": {
            "id": fila["materia_id"],
            "nombre": fila["materia_nombre"],
            "color": fila["materia_color"],
        },
    }


def _tarea_o_404(conexion: sqlite3.Connection, tarea_id: int) -> dict:
    fila = conexion.execute(CONSULTA_TAREAS + " WHERE t.id = ?", (tarea_id,)).fetchone()
    if fila is None:
        raise HTTPException(404, detail={"campo": None, "mensaje": "La tarea no existe."})
    return _fila_a_tarea(fila)


def _exigir_materia(conexion: sqlite3.Connection, materia_id: int) -> None:
    existe = conexion.execute("SELECT 1 FROM materias WHERE id = ?", (materia_id,)).fetchone()
    if existe is None:
        raise HTTPException(
            422, detail={"campo": "materia_id", "mensaje": "La materia indicada no existe."}
        )


@router.get("", response_model=list[TareaSalida])
def listar_tareas(conexion: sqlite3.Connection = Depends(obtener_conexion)):
    filas = conexion.execute(CONSULTA_TAREAS + " ORDER BY t.id")
    return [_fila_a_tarea(fila) for fila in filas]


@router.post("", status_code=201, response_model=TareaSalida)
def crear_tarea(datos: TareaEntrada, conexion: sqlite3.Connection = Depends(obtener_conexion)):
    _exigir_materia(conexion, datos.materia_id)
    cursor = conexion.execute(
        "INSERT INTO tareas (titulo, descripcion, fecha_entrega, materia_id) VALUES (?, ?, ?, ?)",
        (datos.titulo, datos.descripcion, _fecha_a_texto(datos.fecha_entrega), datos.materia_id),
    )
    conexion.commit()
    return _tarea_o_404(conexion, cursor.lastrowid)


@router.put("/{tarea_id}", response_model=TareaSalida)
def editar_tarea(
    tarea_id: int,
    datos: TareaEntrada,
    conexion: sqlite3.Connection = Depends(obtener_conexion),
):
    """Edita los datos de la tarea; no modifica su estado `completada`."""
    _tarea_o_404(conexion, tarea_id)
    _exigir_materia(conexion, datos.materia_id)
    conexion.execute(
        "UPDATE tareas SET titulo = ?, descripcion = ?, fecha_entrega = ?, materia_id = ? "
        "WHERE id = ?",
        (
            datos.titulo,
            datos.descripcion,
            _fecha_a_texto(datos.fecha_entrega),
            datos.materia_id,
            tarea_id,
        ),
    )
    conexion.commit()
    return _tarea_o_404(conexion, tarea_id)


@router.delete("/{tarea_id}", status_code=204)
def eliminar_tarea(tarea_id: int, conexion: sqlite3.Connection = Depends(obtener_conexion)):
    _tarea_o_404(conexion, tarea_id)
    conexion.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    conexion.commit()
    return Response(status_code=204)
