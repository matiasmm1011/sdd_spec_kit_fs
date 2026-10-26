"""Listado de tareas: orden por fecha y plazo calculado (FR-007, FR-009, FR-010, FR-020)."""

from app.db import conectar
from ayudas import cuerpo_tarea

# El reloj simulado empieza el 2026-11-01 a las 12:00 UTC (ver tests/conftest.py).
AYER = "2026-10-31T12:00:00Z"
EN_24_HORAS = "2026-11-02T12:00:00Z"
EN_10_DIAS = "2026-11-11T12:00:00Z"


def crear(cliente, materia, titulo, fecha_entrega) -> dict:
    respuesta = cliente.post(
        "/api/tareas",
        json=cuerpo_tarea(materia["id"], titulo=titulo, fecha_entrega=fecha_entrega),
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_el_listado_se_ordena_por_fecha_de_entrega_ascendente(cliente, materia):
    crear(cliente, materia, "Lejana", EN_10_DIAS)
    crear(cliente, materia, "Pasada", AYER)
    crear(cliente, materia, "Próxima", EN_24_HORAS)

    titulos = [t["titulo"] for t in cliente.get("/api/tareas").json()]

    assert titulos == ["Pasada", "Próxima", "Lejana"]


def test_el_orden_compara_instantes_aunque_cambie_la_zona_horaria(cliente, materia):
    # 20:00 en UTC-05:00 es la 01:00 UTC del día siguiente: va después de las 00:30 UTC.
    crear(cliente, materia, "Tarde en Bogotá", "2026-11-05T20:00:00-05:00")
    crear(cliente, materia, "Madrugada UTC", "2026-11-06T00:30:00Z")

    titulos = [t["titulo"] for t in cliente.get("/api/tareas").json()]

    assert titulos == ["Madrugada UTC", "Tarde en Bogotá"]


def test_las_tareas_con_la_misma_fecha_se_ordenan_por_id(cliente, materia):
    primera = crear(cliente, materia, "Primera", EN_10_DIAS)
    segunda = crear(cliente, materia, "Segunda", EN_10_DIAS)
    crear(cliente, materia, "Anterior", EN_24_HORAS)

    ids = [t["id"] for t in cliente.get("/api/tareas").json()]

    assert ids[1:] == [primera["id"], segunda["id"]]


def test_cada_tarea_del_listado_trae_su_plazo(cliente, materia):
    crear(cliente, materia, "Pasada", AYER)
    crear(cliente, materia, "Próxima", EN_24_HORAS)
    crear(cliente, materia, "Lejana", EN_10_DIAS)

    plazos = [t["plazo"] for t in cliente.get("/api/tareas").json()]

    assert plazos == ["vencida", "urgente", "ninguno"]


def test_una_tarea_completada_no_se_marca_aunque_este_vencida(cliente, materia, ruta_db):
    tarea = crear(cliente, materia, "Pasada", AYER)
    conexion = conectar(ruta_db)
    conexion.execute("UPDATE tareas SET completada = 1 WHERE id = ?", (tarea["id"],))
    conexion.commit()
    conexion.close()

    assert cliente.get("/api/tareas").json()[0]["plazo"] == "ninguno"


def test_el_plazo_pasa_de_ninguno_a_urgente_y_a_vencida_con_el_tiempo(cliente, materia, reloj):
    crear(cliente, materia, "Lejana", EN_10_DIAS)

    def estado_actual() -> dict:
        return cliente.get("/api/tareas").json()[0]

    inicial = estado_actual()
    assert inicial["plazo"] == "ninguno"

    reloj.avanzar(days=8)
    assert estado_actual()["plazo"] == "urgente"

    reloj.avanzar(days=2)
    final = estado_actual()
    assert final["plazo"] == "vencida"

    # Solo cambia el campo derivado: los datos guardados son los mismos.
    del inicial["plazo"], final["plazo"]
    assert final == inicial


def test_crear_una_tarea_devuelve_su_plazo(cliente, materia):
    assert crear(cliente, materia, "Próxima", EN_24_HORAS)["plazo"] == "urgente"


def test_editar_una_tarea_devuelve_el_plazo_recalculado(cliente, materia):
    tarea = crear(cliente, materia, "Lejana", EN_10_DIAS)

    respuesta = cliente.put(
        f"/api/tareas/{tarea['id']}", json=cuerpo_tarea(materia["id"], fecha_entrega=AYER)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["plazo"] == "vencida"
