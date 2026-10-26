"""Fixtures compartidas: base de datos temporal, reloj simulado y cliente de la API."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import crear_app


class RelojSimulado:
    """Reloj que se puede mover a voluntad para probar vencidas y urgentes."""

    def __init__(self, ahora: datetime):
        self.ahora = ahora

    def __call__(self) -> datetime:
        return self.ahora

    def avanzar(self, **duracion) -> None:
        self.ahora += timedelta(**duracion)


@pytest.fixture
def ruta_db(tmp_path) -> str:
    return str(tmp_path / "pruebas.db")


@pytest.fixture
def reloj() -> RelojSimulado:
    return RelojSimulado(datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc))


@pytest.fixture
def cliente(ruta_db, reloj):
    aplicacion = crear_app(ruta_db=ruta_db, reloj=reloj)
    # El uso como gestor de contexto ejecuta el ciclo de vida (crea el esquema).
    with TestClient(aplicacion) as cliente_http:
        yield cliente_http


@pytest.fixture
def materia(cliente) -> dict:
    """Una materia ya creada a través de la API."""
    respuesta = cliente.post("/api/materias", json={"nombre": "Cálculo II", "color": "#1D4ED8"})
    assert respuesta.status_code == 201
    return respuesta.json()
