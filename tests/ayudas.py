"""Funciones de apoyo compartidas por las pruebas."""


def cuerpo_tarea(materia_id: int, **cambios) -> dict:
    """Cuerpo válido para crear una tarea; `cambios` sobrescribe campos."""
    cuerpo = {
        "titulo": "Taller de límites",
        "descripcion": "Ejercicios 1 al 10",
        "fecha_entrega": "2026-11-03T23:59:00-05:00",
        "materia_id": materia_id,
    }
    cuerpo.update(cambios)
    return cuerpo
