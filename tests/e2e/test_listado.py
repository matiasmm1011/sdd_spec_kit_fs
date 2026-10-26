"""Listado de la Historia 2 en el navegador: orden y etiquetas de plazo (FR-007 a FR-010)."""

from datetime import datetime, timedelta, timezone

from playwright.sync_api import Page, expect

AZUL = "#1D4ED8"


def en_iso(diferencia: timedelta) -> str:
    """Fecha relativa a la hora real, porque el servidor de estas pruebas usa el reloj real."""
    return (datetime.now(timezone.utc) + diferencia).strftime("%Y-%m-%dT%H:%M:%SZ")


def crear_materia_por_api(page: Page, url_base: str, nombre: str, color: str = AZUL) -> dict:
    respuesta = page.request.post(f"{url_base}/api/materias", data={"nombre": nombre, "color": color})
    assert respuesta.status == 201
    return respuesta.json()


def crear_tarea_por_api(page: Page, url_base: str, materia_id: int, titulo: str, fecha: str):
    respuesta = page.request.post(
        f"{url_base}/api/tareas",
        data={"titulo": titulo, "fecha_entrega": fecha, "materia_id": materia_id},
    )
    assert respuesta.status == 201


def preparar_tres_tareas(page: Page, url_base: str) -> None:
    """Se crean desordenadas para comprobar que el listado las ordena."""
    materia = crear_materia_por_api(page, url_base, "Cálculo II")
    crear_tarea_por_api(page, url_base, materia["id"], "Proyecto final", en_iso(timedelta(days=10)))
    crear_tarea_por_api(page, url_base, materia["id"], "Taller atrasado", en_iso(timedelta(days=-1)))
    crear_tarea_por_api(page, url_base, materia["id"], "Quiz de mañana", en_iso(timedelta(hours=24)))
    page.goto(url_base)


def test_las_tareas_aparecen_ordenadas_por_fecha_de_entrega(page: Page, url_base):
    preparar_tres_tareas(page, url_base)

    tareas = page.locator("#lista-tareas li")
    expect(tareas).to_have_count(3)
    expect(tareas.nth(0)).to_contain_text("Taller atrasado")
    expect(tareas.nth(1)).to_contain_text("Quiz de mañana")
    expect(tareas.nth(2)).to_contain_text("Proyecto final")


def test_cada_tarea_muestra_su_etiqueta_de_plazo_en_texto(page: Page, url_base):
    preparar_tres_tareas(page, url_base)

    tareas = page.locator("#lista-tareas li")
    expect(tareas.nth(0).locator(".etiqueta-plazo")).to_have_text("Vencida")
    expect(tareas.nth(1).locator(".etiqueta-plazo")).to_have_text("Urgente")
    expect(tareas.nth(2).locator(".etiqueta-plazo")).to_have_count(0)
    expect(tareas.nth(2)).not_to_contain_text("Vencida")
    expect(tareas.nth(2)).not_to_contain_text("Urgente")


def test_ninguna_tarea_muestra_vencida_y_urgente_a_la_vez(page: Page, url_base):
    preparar_tres_tareas(page, url_base)

    tareas = page.locator("#lista-tareas li")
    expect(tareas).to_have_count(3)
    for indice in range(3):
        expect(tareas.nth(indice).locator(".etiqueta-plazo")).to_have_count(1 if indice < 2 else 0)


def test_cada_tarea_muestra_el_nombre_y_el_color_de_su_materia(page: Page, url_base):
    fisica = crear_materia_por_api(page, url_base, "Física", "#15803D")
    calculo = crear_materia_por_api(page, url_base, "Cálculo II", AZUL)
    crear_tarea_por_api(page, url_base, fisica["id"], "Informe", en_iso(timedelta(days=5)))
    crear_tarea_por_api(page, url_base, calculo["id"], "Taller", en_iso(timedelta(days=6)))
    page.goto(url_base)

    informe = page.locator("#lista-tareas li", has_text="Informe").locator(".etiqueta-materia")
    taller = page.locator("#lista-tareas li", has_text="Taller").locator(".etiqueta-materia")
    expect(informe).to_have_text("Física")
    expect(informe).to_have_css("background-color", "rgb(21, 128, 61)")
    expect(taller).to_have_text("Cálculo II")
    expect(taller).to_have_css("background-color", "rgb(29, 78, 216)")
