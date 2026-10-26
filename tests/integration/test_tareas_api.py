"""API de tareas: crear, editar, eliminar y listar (FR-004, FR-005, FR-006, FR-008)."""

from app.db import conectar
from ayudas import cuerpo_tarea


def test_crear_una_tarea_devuelve_201_con_su_materia(cliente, materia):
    respuesta = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"]))

    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "id": 1,
        "titulo": "Taller de límites",
        "descripcion": "Ejercicios 1 al 10",
        "fecha_entrega": "2026-11-04T04:59:00Z",
        "completada": False,
        "materia": {"id": materia["id"], "nombre": "Cálculo II", "color": "#1D4ED8"},
    }


def test_crear_una_tarea_sin_descripcion_es_valido(cliente, materia):
    cuerpo = cuerpo_tarea(materia["id"])
    del cuerpo["descripcion"]

    respuesta = cliente.post("/api/tareas", json=cuerpo)

    assert respuesta.status_code == 201
    assert respuesta.json()["descripcion"] is None


def test_se_permite_crear_una_tarea_con_fecha_pasada(cliente, materia):
    respuesta = cliente.post(
        "/api/tareas", json=cuerpo_tarea(materia["id"], fecha_entrega="2020-01-01T08:00:00Z")
    )

    assert respuesta.status_code == 201


def test_cada_dato_invalido_aparece_una_vez_en_el_detalle(cliente):
    respuesta = cliente.post(
        "/api/tareas", json={"titulo": "   ", "fecha_entrega": "mañana", "descripcion": "a" * 501}
    )

    assert respuesta.status_code == 422
    campos = [e["campo"] for e in respuesta.json()["detalle"]]
    assert sorted(campos) == ["descripcion", "fecha_entrega", "materia_id", "titulo"]


def test_una_materia_inexistente_devuelve_422_en_el_campo_materia_id(cliente):
    respuesta = cliente.post("/api/tareas", json=cuerpo_tarea(99))

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"] == [
        {"campo": "materia_id", "mensaje": "La materia indicada no existe."}
    ]


def test_un_titulo_de_101_caracteres_devuelve_422_e_indica_el_limite(cliente, materia):
    respuesta = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"], titulo="a" * 101))

    assert respuesta.status_code == 422
    assert "100" in respuesta.json()["detalle"][0]["mensaje"]


def test_una_fecha_sin_zona_horaria_devuelve_422(cliente, materia):
    respuesta = cliente.post(
        "/api/tareas", json=cuerpo_tarea(materia["id"], fecha_entrega="2026-11-03T23:59:00")
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"][0]["campo"] == "fecha_entrega"


def test_un_dato_rechazado_no_se_guarda(cliente, materia):
    cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"], titulo=""))

    assert cliente.get("/api/tareas").json() == []


def test_listar_devuelve_cada_tarea_con_su_materia(cliente, materia):
    cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"]))

    respuesta = cliente.get("/api/tareas")

    assert respuesta.status_code == 200
    tarea = respuesta.json()[0]
    assert tarea["materia"] == {"id": materia["id"], "nombre": "Cálculo II", "color": "#1D4ED8"}


def test_listar_sin_tareas_devuelve_lista_vacia(cliente):
    assert cliente.get("/api/tareas").json() == []


def test_editar_una_tarea_no_cambia_su_estado_completada(cliente, materia, ruta_db):
    tarea = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"])).json()
    conexion = conectar(ruta_db)
    conexion.execute("UPDATE tareas SET completada = 1 WHERE id = ?", (tarea["id"],))
    conexion.commit()
    conexion.close()

    respuesta = cliente.put(
        f"/api/tareas/{tarea['id']}",
        json=cuerpo_tarea(materia["id"], titulo="Título nuevo", descripcion=None),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Título nuevo"
    assert respuesta.json()["descripcion"] is None
    assert respuesta.json()["completada"] is True


def test_editar_puede_cambiar_la_materia_de_la_tarea(cliente, materia):
    otra = cliente.post("/api/materias", json={"nombre": "Física", "color": "#15803D"}).json()
    tarea = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"])).json()

    respuesta = cliente.put(f"/api/tareas/{tarea['id']}", json=cuerpo_tarea(otra["id"]))

    assert respuesta.json()["materia"]["nombre"] == "Física"


def test_editar_una_tarea_inexistente_devuelve_404(cliente, materia):
    respuesta = cliente.put("/api/tareas/99", json=cuerpo_tarea(materia["id"]))

    assert respuesta.status_code == 404
    assert respuesta.json()["detalle"][0]["mensaje"] == "La tarea no existe."


def test_editar_con_datos_invalidos_devuelve_422(cliente, materia):
    tarea = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"])).json()

    respuesta = cliente.put(f"/api/tareas/{tarea['id']}", json=cuerpo_tarea(materia["id"], titulo=""))

    assert respuesta.status_code == 422


def test_eliminar_una_tarea_devuelve_204(cliente, materia):
    tarea = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"])).json()

    respuesta = cliente.delete(f"/api/tareas/{tarea['id']}")

    assert respuesta.status_code == 204
    assert cliente.get("/api/tareas").json() == []


def test_eliminar_una_tarea_inexistente_devuelve_404(cliente):
    assert cliente.delete("/api/tareas/99").status_code == 404
