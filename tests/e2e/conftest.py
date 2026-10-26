"""Fixtures de las pruebas de interfaz: servidor real en un puerto libre."""

import socket
import threading
import time

import pytest
import uvicorn

from app.main import crear_app

ESPERA_MAXIMA_ARRANQUE = 10  # segundos


def pytest_collection_modifyitems(items):
    """Marca como `e2e` todas las pruebas de esta carpeta."""
    for prueba in items:
        if "tests/e2e" in prueba.nodeid.replace("\\", "/"):
            prueba.add_marker(pytest.mark.e2e)


def _puerto_libre() -> int:
    with socket.socket() as conector:
        conector.bind(("127.0.0.1", 0))
        return conector.getsockname()[1]


@pytest.fixture
def url_base(tmp_path):
    """URL de un servidor con base de datos propia y vacía para cada prueba."""
    puerto = _puerto_libre()
    configuracion = uvicorn.Config(
        crear_app(ruta_db=str(tmp_path / "e2e.db")),
        host="127.0.0.1",
        port=puerto,
        log_level="warning",
    )
    servidor = uvicorn.Server(configuracion)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()

    limite = time.monotonic() + ESPERA_MAXIMA_ARRANQUE
    while not servidor.started:
        if time.monotonic() > limite:
            raise RuntimeError("El servidor de pruebas no arrancó a tiempo.")
        time.sleep(0.05)

    yield f"http://127.0.0.1:{puerto}"

    servidor.should_exit = True
    hilo.join(timeout=5)
