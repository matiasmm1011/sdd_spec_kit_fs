"""Regla de plazo de una tarea (data-model.md, "Regla de plazo")."""

from datetime import datetime, timedelta

MARGEN_URGENTE = timedelta(hours=48)


def calcular_plazo(fecha_entrega: datetime, completada: bool, ahora: datetime) -> str:
    """Devuelve "vencida", "urgente" o "ninguno"; no se guarda, depende de `ahora`."""
    if completada:
        return "ninguno"
    if fecha_entrega <= ahora:
        return "vencida"
    if fecha_entrega <= ahora + MARGEN_URGENTE:
        return "urgente"
    return "ninguno"
