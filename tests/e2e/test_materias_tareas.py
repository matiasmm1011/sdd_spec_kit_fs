"""Flujos de la Historia 1 en el navegador: materias, tareas y borrado en cascada."""

from playwright.sync_api import Page, expect

FECHA_FUTURA = "2030-12-31"


def crear_materia_por_api(page: Page, url_base: str, nombre: str, color: str = "#1D4ED8") -> dict:
    respuesta = page.request.post(f"{url_base}/api/materias", data={"nombre": nombre, "color": color})
    assert respuesta.status == 201
    return respuesta.json()


def crear_tarea_por_api(page: Page, url_base: str, materia_id: int, titulo: str) -> dict:
    respuesta = page.request.post(
        f"{url_base}/api/tareas",
        data={
            "titulo": titulo,
            "fecha_entrega": f"{FECHA_FUTURA}T23:59:00-05:00",
            "materia_id": materia_id,
        },
    )
    assert respuesta.status == 201
    return respuesta.json()


def registrar_materia(page: Page, nombre: str) -> None:
    page.locator("#materia-nombre").fill(nombre)
    page.get_by_role("button", name="Guardar materia").click()


def test_sin_materias_se_ve_el_estado_vacio_y_no_se_puede_crear_tareas(page: Page, url_base):
    page.goto(url_base)

    expect(page.locator("#vacio-materias")).to_be_visible()
    expect(page.locator("#vacio-materias")).to_contain_text("Registra la primera materia")
    expect(page.locator("#aviso-sin-materias")).to_be_visible()
    expect(page.locator("#guardar-tarea")).to_be_disabled()
    expect(page.locator("#vacio-tareas")).to_be_visible()


def test_crear_una_materia_la_muestra_con_su_nombre_y_color(page: Page, url_base):
    page.goto(url_base)

    registrar_materia(page, "Cálculo II")

    elemento = page.locator("#lista-materias li", has_text="Cálculo II")
    expect(elemento).to_be_visible()
    expect(page.locator("#vacio-materias")).to_be_hidden()
    expect(page.locator("#guardar-tarea")).to_be_enabled()
    expect(page.locator("#mensajes")).to_contain_text("Materia guardada")


def test_crear_una_tarea_la_muestra_asociada_a_su_materia(page: Page, url_base):
    crear_materia_por_api(page, url_base, "Cálculo II")
    page.goto(url_base)

    page.locator("#tarea-titulo").fill("Taller de límites")
    page.locator("#tarea-fecha").fill(FECHA_FUTURA)
    expect(page.locator("#tarea-hora")).to_have_value("23:59")
    page.locator("#tarea-materia").select_option(label="Cálculo II")
    page.get_by_role("button", name="Guardar tarea").click()

    tarea = page.locator("#lista-tareas li", has_text="Taller de límites")
    expect(tarea).to_be_visible()
    expect(tarea).to_contain_text("Cálculo II")
    expect(page.locator("#vacio-tareas")).to_be_hidden()


def test_una_tarea_invalida_muestra_cada_error_y_conserva_lo_escrito(page: Page, url_base):
    crear_materia_por_api(page, url_base, "Cálculo II")
    page.goto(url_base)

    # El navegador ya limita a 100 caracteres lo que se escribe (maxlength); el límite
    # en el servidor se prueba en los tests de la API. Aquí se prueba un título en blanco.
    page.locator("#tarea-titulo").fill("   ")
    page.locator("#tarea-descripcion").fill("Texto que no debe perderse")
    page.get_by_role("button", name="Guardar tarea").click()

    expect(page.locator("#error-tarea-titulo")).to_contain_text("no puede estar vacío")
    expect(page.locator("#error-tarea-fecha_entrega")).to_contain_text("obligatorio")
    expect(page.locator("#tarea-titulo")).to_have_value("   ")
    expect(page.locator("#tarea-descripcion")).to_have_value("Texto que no debe perderse")
    expect(page.locator("#lista-tareas li")).to_have_count(0)


def test_un_nombre_de_materia_repetido_se_rechaza_y_conserva_el_texto(page: Page, url_base):
    page.goto(url_base)
    registrar_materia(page, "Cálculo II")
    expect(page.locator("#lista-materias li")).to_have_count(1)

    registrar_materia(page, "CÁLCULO ii")

    expect(page.locator("#error-materia-nombre")).to_contain_text("Ya existe una materia")
    expect(page.locator("#materia-nombre")).to_have_value("CÁLCULO ii")
    expect(page.locator("#lista-materias li")).to_have_count(1)


def test_borrar_una_materia_con_tareas_pide_confirmacion_con_el_numero_de_tareas(
    page: Page, url_base
):
    materia = crear_materia_por_api(page, url_base, "Cálculo II")
    crear_tarea_por_api(page, url_base, materia["id"], "Taller 1")
    crear_tarea_por_api(page, url_base, materia["id"], "Taller 2")
    page.goto(url_base)

    page.get_by_role("button", name="Eliminar materia Cálculo II").click()
    expect(page.locator("#dialogo")).to_be_visible()
    expect(page.locator("#dialogo-texto")).to_contain_text("2 tareas")

    page.get_by_role("button", name="Cancelar").click()
    expect(page.locator("#dialogo")).to_be_hidden()
    expect(page.locator("#lista-materias li")).to_have_count(1)
    expect(page.locator("#lista-tareas li")).to_have_count(2)

    page.get_by_role("button", name="Eliminar materia Cálculo II").click()
    page.locator("#dialogo-confirmar").click()

    expect(page.locator("#lista-materias li")).to_have_count(0)
    expect(page.locator("#lista-tareas li")).to_have_count(0)
    expect(page.locator("#vacio-materias")).to_be_visible()


def test_borrar_una_materia_sin_tareas_no_pide_confirmacion(page: Page, url_base):
    crear_materia_por_api(page, url_base, "Física")
    page.goto(url_base)

    page.get_by_role("button", name="Eliminar materia Física").click()

    expect(page.locator("#dialogo")).to_be_hidden()
    expect(page.locator("#lista-materias li")).to_have_count(0)


def test_editar_una_materia_actualiza_su_nombre(page: Page, url_base):
    crear_materia_por_api(page, url_base, "Física")
    page.goto(url_base)

    page.get_by_role("button", name="Editar materia Física").click()
    page.locator("#materia-nombre").fill("Física II")
    page.get_by_role("button", name="Guardar cambios").click()

    expect(page.locator("#lista-materias li", has_text="Física II")).to_be_visible()
    expect(page.locator("#lista-materias li")).to_have_count(1)


def test_editar_y_eliminar_una_tarea(page: Page, url_base):
    materia = crear_materia_por_api(page, url_base, "Física")
    crear_tarea_por_api(page, url_base, materia["id"], "Informe")
    page.goto(url_base)

    page.get_by_role("button", name="Editar tarea Informe").click()
    expect(page.locator("#tarea-titulo")).to_have_value("Informe")
    page.locator("#tarea-titulo").fill("Informe final")
    page.get_by_role("button", name="Guardar cambios").click()
    expect(page.locator("#lista-tareas li", has_text="Informe final")).to_be_visible()

    page.get_by_role("button", name="Eliminar tarea Informe final").click()
    expect(page.locator("#lista-tareas li")).to_have_count(0)
    expect(page.locator("#vacio-tareas")).to_be_visible()


def test_si_el_servidor_no_responde_se_muestra_un_mensaje_en_espanol(page: Page, url_base):
    page.goto(url_base)
    page.route("**/api/**", lambda ruta: ruta.abort())

    registrar_materia(page, "Cálculo II")

    expect(page.locator("#mensajes")).to_contain_text("No se pudo conectar con el servidor")
