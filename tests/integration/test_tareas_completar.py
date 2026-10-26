"""Marcar y desmarcar tareas como completadas (FR-011, FR-012)."""

import pytest

from ayudas import cuerpo_tarea

# El reloj simulado empieza el 2026-11-01 a las 12:00 UTC: esta fecha ya pasó.
AYER = "2026-10-31T12:00:00Z"


@pytest.fixture
def tarea_vencida(cliente, materia) -> dict:
    respuesta = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"], fecha_entrega=AYER))
    assert respuesta.status_code == 201
    return respuesta.json()


def marcar(cliente, tarea_id, cuerpo):
    return cliente.patch(f"/api/tareas/{tarea_id}/completada", json=cuerpo)


def test_marcar_una_tarea_vencida_la_completa_y_le_quita_el_plazo(cliente, tarea_vencida):
    respuesta = marcar(cliente, tarea_vencida["id"], {"completada": True})

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True
    assert respuesta.json()["plazo"] == "ninguno"


def test_desmarcar_una_tarea_vencida_le_devuelve_la_marca(cliente, tarea_vencida):
    marcar(cliente, tarea_vencida["id"], {"completada": True})

    respuesta = marcar(cliente, tarea_vencida["id"], {"completada": False})

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is False
    assert respuesta.json()["plazo"] == "vencida"


def test_el_cambio_se_guarda_y_se_ve_en_el_listado(cliente, tarea_vencida):
    marcar(cliente, tarea_vencida["id"], {"completada": True})

    tarea = cliente.get("/api/tareas").json()[0]

    assert tarea["completada"] is True
    assert tarea["plazo"] == "ninguno"


def test_marcar_no_cambia_los_demas_datos_de_la_tarea(cliente, tarea_vencida):
    respuesta = marcar(cliente, tarea_vencida["id"], {"completada": True}).json()

    for campo in ("id", "titulo", "descripcion", "fecha_entrega", "materia"):
        assert respuesta[campo] == tarea_vencida[campo]


def test_marcar_dos_veces_deja_la_tarea_completada(cliente, tarea_vencida):
    marcar(cliente, tarea_vencida["id"], {"completada": True})

    respuesta = marcar(cliente, tarea_vencida["id"], {"completada": True})

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True


def test_marcar_una_tarea_inexistente_devuelve_404(cliente):
    respuesta = marcar(cliente, 99, {"completada": True})

    assert respuesta.status_code == 404
    assert respuesta.json()["detalle"][0]["mensaje"] == "La tarea no existe."


@pytest.mark.parametrize("valor", ["true", "si", 1, 0, None, [], {}])
def test_un_valor_que_no_es_booleano_devuelve_422(cliente, tarea_vencida, valor):
    respuesta = marcar(cliente, tarea_vencida["id"], {"completada": valor})

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"][0]["campo"] == "completada"
    # La tarea no cambia.
    assert cliente.get("/api/tareas").json()[0]["completada"] is False


def test_sin_el_campo_completada_devuelve_422(cliente, tarea_vencida):
    respuesta = marcar(cliente, tarea_vencida["id"], {})

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"] == [
        {"campo": "completada", "mensaje": "Este dato es obligatorio."}
    ]
