"""API de materias: creación, listado, edición, borrado en cascada (FR-001 a FR-003, FR-016)."""

import re
from pathlib import Path

from app.db import conectar
from app.esquemas import PALETA_COLORES
from ayudas import cuerpo_tarea

MATERIA = {"nombre": "Cálculo II", "color": "#1D4ED8"}
APP_JS = Path(__file__).parents[2] / "app" / "estatico" / "app.js"


def test_crear_una_materia_devuelve_201(cliente):
    respuesta = cliente.post("/api/materias", json=MATERIA)

    assert respuesta.status_code == 201
    assert respuesta.json() == {"id": 1, **MATERIA, "total_tareas": 0}


def test_el_nombre_se_guarda_recortado(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "  Física  ", "color": "#15803D"})

    assert respuesta.json()["nombre"] == "Física"


def test_un_nombre_repetido_ignorando_mayusculas_y_acentos_devuelve_409(cliente, materia):
    respuesta = cliente.post("/api/materias", json={"nombre": "CÁLCULO ii", "color": "#B91C1C"})

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detalle": [{"campo": "nombre", "mensaje": "Ya existe una materia con ese nombre."}]
    }


def test_un_nombre_invalido_devuelve_422_con_el_formato_detalle(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "   ", "color": "#1D4ED8"})

    assert respuesta.status_code == 422
    detalle = respuesta.json()["detalle"]
    assert [e["campo"] for e in detalle] == ["nombre"]
    assert "vacío" in detalle[0]["mensaje"]


def test_un_nombre_de_51_caracteres_devuelve_422_e_indica_el_limite(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "a" * 51, "color": "#1D4ED8"})

    assert respuesta.status_code == 422
    assert "50" in respuesta.json()["detalle"][0]["mensaje"]


def test_un_color_fuera_de_la_paleta_devuelve_422(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "Física", "color": "#123456"})

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"][0]["campo"] == "color"


def test_un_cuerpo_vacio_reporta_cada_campo_obligatorio(cliente):
    respuesta = cliente.post("/api/materias", json={})

    assert respuesta.status_code == 422
    assert {e["campo"] for e in respuesta.json()["detalle"]} == {"nombre", "color"}
    assert all(e["mensaje"] == "Este dato es obligatorio." for e in respuesta.json()["detalle"])


def test_listar_ordena_por_nombre_e_incluye_total_de_tareas(cliente, materia):
    cliente.post("/api/materias", json={"nombre": "Álgebra", "color": "#15803D"})
    cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"]))
    cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"], titulo="Otra"))

    respuesta = cliente.get("/api/materias")

    assert respuesta.status_code == 200
    assert [(m["nombre"], m["total_tareas"]) for m in respuesta.json()] == [
        ("Álgebra", 0),
        ("Cálculo II", 2),
    ]


def test_listar_sin_materias_devuelve_lista_vacia(cliente):
    assert cliente.get("/api/materias").json() == []


def test_editar_una_materia_devuelve_200_con_los_nuevos_datos(cliente, materia):
    respuesta = cliente.put(
        f"/api/materias/{materia['id']}", json={"nombre": "Cálculo III", "color": "#7E22CE"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Cálculo III"
    assert respuesta.json()["color"] == "#7E22CE"


def test_editar_una_materia_conservando_su_nombre_no_es_conflicto(cliente, materia):
    respuesta = cliente.put(
        f"/api/materias/{materia['id']}", json={"nombre": "cálculo ii", "color": "#7E22CE"}
    )

    assert respuesta.status_code == 200


def test_editar_con_el_nombre_de_otra_materia_devuelve_409(cliente, materia):
    otra = cliente.post("/api/materias", json={"nombre": "Física", "color": "#15803D"}).json()

    respuesta = cliente.put(f"/api/materias/{otra['id']}", json=MATERIA)

    assert respuesta.status_code == 409


def test_editar_una_materia_inexistente_devuelve_404(cliente):
    respuesta = cliente.put("/api/materias/99", json=MATERIA)

    assert respuesta.status_code == 404
    assert respuesta.json()["detalle"][0]["mensaje"] == "La materia no existe."


def test_editar_con_datos_invalidos_devuelve_422(cliente, materia):
    respuesta = cliente.put(f"/api/materias/{materia['id']}", json={"nombre": "", "color": "x"})

    assert respuesta.status_code == 422
    assert {e["campo"] for e in respuesta.json()["detalle"]} == {"nombre", "color"}


def test_un_id_que_no_es_numero_devuelve_422_en_espanol(cliente):
    respuesta = cliente.put("/api/materias/abc", json=MATERIA)

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"] == [
        {"campo": "materia_id", "mensaje": "Debe ser un número entero."}
    ]


def test_eliminar_una_materia_sin_tareas_devuelve_204(cliente, materia):
    respuesta = cliente.delete(f"/api/materias/{materia['id']}")

    assert respuesta.status_code == 204
    assert cliente.get("/api/materias").json() == []


def test_eliminar_una_materia_borra_todas_sus_tareas(cliente, materia, ruta_db):
    otra = cliente.post("/api/materias", json={"nombre": "Física", "color": "#15803D"}).json()
    cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"], titulo="Pendiente"))
    completada = cliente.post("/api/tareas", json=cuerpo_tarea(materia["id"], titulo="Hecha")).json()
    cliente.post("/api/tareas", json=cuerpo_tarea(otra["id"], titulo="De otra materia"))
    conexion = conectar(ruta_db)
    conexion.execute("UPDATE tareas SET completada = 1 WHERE id = ?", (completada["id"],))
    conexion.commit()
    conexion.close()

    respuesta = cliente.delete(f"/api/materias/{materia['id']}")

    assert respuesta.status_code == 204
    titulos = [t["titulo"] for t in cliente.get("/api/tareas").json()]
    assert titulos == ["De otra materia"]


def test_eliminar_una_materia_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/api/materias/99")

    assert respuesta.status_code == 404


def test_la_paleta_del_frontend_coincide_con_la_del_servidor():
    colores_js = set(re.findall(r"#[0-9A-Fa-f]{6}", APP_JS.read_text(encoding="utf-8")))

    assert {c.upper() for c in colores_js} == set(PALETA_COLORES)
