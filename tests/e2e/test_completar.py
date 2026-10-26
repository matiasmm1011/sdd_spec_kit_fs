"""Marcar y desmarcar una tarea en el navegador (FR-011, FR-012)."""

import re
from datetime import datetime, timedelta, timezone

from playwright.sync_api import Page, expect


def preparar_tarea_vencida(page: Page, url_base: str) -> None:
    materia = page.request.post(
        f"{url_base}/api/materias", data={"nombre": "Cálculo II", "color": "#1D4ED8"}
    ).json()
    # El servidor de estas pruebas usa el reloj real: ayer ya está vencida.
    ayer = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    respuesta = page.request.post(
        f"{url_base}/api/tareas",
        data={"titulo": "Taller atrasado", "fecha_entrega": ayer, "materia_id": materia["id"]},
    )
    assert respuesta.status == 201
    page.goto(url_base)


def test_marcar_una_tarea_vencida_la_distingue_y_quita_vencida(page: Page, url_base):
    preparar_tarea_vencida(page, url_base)
    tarea = page.locator("#lista-tareas li", has_text="Taller atrasado")
    boton = tarea.locator("button[aria-pressed]")
    expect(tarea.locator(".etiqueta-plazo")).to_have_text("Vencida")
    expect(boton).to_have_attribute("aria-pressed", "false")

    boton.click()

    # Se distingue con una clase visual y con un texto, no solo con color.
    expect(tarea).to_have_class(re.compile(r"\btarea-completada\b"))
    expect(tarea.locator(".etiqueta-completada")).to_have_text("Completada")
    expect(tarea.locator(".etiqueta-plazo")).to_have_count(0)
    expect(tarea.locator("button[aria-pressed]")).to_have_attribute("aria-pressed", "true")


def test_desmarcar_la_devuelve_a_pendiente_con_su_marca(page: Page, url_base):
    preparar_tarea_vencida(page, url_base)
    tarea = page.locator("#lista-tareas li", has_text="Taller atrasado")
    tarea.locator("button[aria-pressed]").click()
    expect(tarea.locator("button[aria-pressed]")).to_have_attribute("aria-pressed", "true")

    tarea.locator("button[aria-pressed]").click()

    expect(tarea.locator("button[aria-pressed]")).to_have_attribute("aria-pressed", "false")
    expect(tarea.locator(".etiqueta-plazo")).to_have_text("Vencida")
    expect(tarea.locator(".etiqueta-completada")).to_have_count(0)


def test_el_estado_completada_se_conserva_al_recargar(page: Page, url_base):
    preparar_tarea_vencida(page, url_base)
    tarea = page.locator("#lista-tareas li", has_text="Taller atrasado")
    tarea.locator("button[aria-pressed]").click()
    expect(tarea.locator("button[aria-pressed]")).to_have_attribute("aria-pressed", "true")

    page.reload()

    tarea = page.locator("#lista-tareas li", has_text="Taller atrasado")
    expect(tarea.locator("button[aria-pressed]")).to_have_attribute("aria-pressed", "true")
    expect(tarea.locator(".etiqueta-plazo")).to_have_count(0)
