"""Reglas de validación de materias y tareas (FR-002, FR-005)."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.esquemas import PALETA_COLORES, MateriaEntrada, TareaEntrada


def mensajes(error: ValidationError) -> dict[str, str]:
    """Mensaje de cada campo inválido, sin el prefijo que añade Pydantic."""
    return {
        str(e["loc"][-1]): e["msg"].removeprefix("Value error, ") for e in error.errors()
    }


def tarea_valida(**cambios) -> dict:
    datos = {
        "titulo": "Taller de límites",
        "descripcion": "Ejercicios 1 al 10",
        "fecha_entrega": "2026-11-03T23:59:00-05:00",
        "materia_id": 1,
    }
    datos.update(cambios)
    return datos


# --- Materia ---------------------------------------------------------------


def test_materia_valida_se_acepta():
    materia = MateriaEntrada(nombre="Cálculo II", color="#1D4ED8")

    assert materia.nombre == "Cálculo II"
    assert materia.color == "#1D4ED8"


def test_el_nombre_de_materia_se_recorta():
    assert MateriaEntrada(nombre="  Física  ", color="#1D4ED8").nombre == "Física"


@pytest.mark.parametrize("nombre", ["", "   ", "\t\n"])
def test_nombre_de_materia_vacio_o_solo_espacios_se_rechaza(nombre):
    with pytest.raises(ValidationError) as error:
        MateriaEntrada(nombre=nombre, color="#1D4ED8")

    assert "vacío" in mensajes(error.value)["nombre"]


def test_nombre_de_materia_de_50_caracteres_se_acepta():
    assert len(MateriaEntrada(nombre="a" * 50, color="#1D4ED8").nombre) == 50


def test_nombre_de_materia_de_51_caracteres_se_rechaza_e_indica_el_limite():
    with pytest.raises(ValidationError) as error:
        MateriaEntrada(nombre="a" * 51, color="#1D4ED8")

    assert "50" in mensajes(error.value)["nombre"]


def test_el_limite_del_nombre_de_materia_se_mide_tras_recortar():
    # 50 letras rodeadas de espacios son válidas: el límite se mide tras recortar.
    assert MateriaEntrada(nombre="  " + "a" * 50 + "  ", color="#1D4ED8").nombre == "a" * 50


@pytest.mark.parametrize("color", ["#000000", "azul", "", "#1D4ED"])
def test_color_fuera_de_la_paleta_se_rechaza(color):
    with pytest.raises(ValidationError) as error:
        MateriaEntrada(nombre="Física", color=color)

    assert "paleta" in mensajes(error.value)["color"]


def test_color_de_la_paleta_en_minusculas_se_normaliza():
    assert MateriaEntrada(nombre="Física", color="#1d4ed8").color == "#1D4ED8"


def test_la_paleta_tiene_los_ocho_colores_definidos():
    assert PALETA_COLORES == (
        "#1D4ED8", "#15803D", "#B91C1C", "#C2410C",
        "#7E22CE", "#0F766E", "#BE185D", "#475569",
    )


def test_materia_sin_nombre_ni_color_reporta_ambos_campos():
    with pytest.raises(ValidationError) as error:
        MateriaEntrada()

    assert {"nombre", "color"} <= set(mensajes(error.value))


# --- Tarea -----------------------------------------------------------------


def test_tarea_valida_se_acepta():
    tarea = TareaEntrada(**tarea_valida())

    assert tarea.titulo == "Taller de límites"
    assert tarea.descripcion == "Ejercicios 1 al 10"
    assert tarea.materia_id == 1


def test_el_titulo_se_recorta():
    assert TareaEntrada(**tarea_valida(titulo="  Taller  ")).titulo == "Taller"


@pytest.mark.parametrize("titulo", ["", "   "])
def test_titulo_vacio_o_solo_espacios_se_rechaza(titulo):
    with pytest.raises(ValidationError) as error:
        TareaEntrada(**tarea_valida(titulo=titulo))

    assert "vacío" in mensajes(error.value)["titulo"]


def test_titulo_de_100_caracteres_se_acepta():
    assert len(TareaEntrada(**tarea_valida(titulo="a" * 100)).titulo) == 100


def test_titulo_de_101_caracteres_se_rechaza_e_indica_el_limite():
    with pytest.raises(ValidationError) as error:
        TareaEntrada(**tarea_valida(titulo="a" * 101))

    assert "100" in mensajes(error.value)["titulo"]


def test_descripcion_de_500_caracteres_se_acepta():
    assert len(TareaEntrada(**tarea_valida(descripcion="a" * 500)).descripcion) == 500


def test_descripcion_de_501_caracteres_se_rechaza_e_indica_el_limite():
    with pytest.raises(ValidationError) as error:
        TareaEntrada(**tarea_valida(descripcion="a" * 501))

    assert "500" in mensajes(error.value)["descripcion"]


@pytest.mark.parametrize("descripcion", [None, "", "   "])
def test_descripcion_ausente_o_en_blanco_queda_como_ausente(descripcion):
    assert TareaEntrada(**tarea_valida(descripcion=descripcion)).descripcion is None


def test_la_descripcion_es_opcional():
    datos = tarea_valida()
    del datos["descripcion"]

    assert TareaEntrada(**datos).descripcion is None


def test_la_fecha_con_zona_horaria_se_convierte_a_utc():
    tarea = TareaEntrada(**tarea_valida(fecha_entrega="2026-11-03T23:59:00-05:00"))

    assert tarea.fecha_entrega == datetime(2026, 11, 4, 4, 59, tzinfo=timezone.utc)
    assert tarea.fecha_entrega.utcoffset() == timedelta(0)


def test_la_fecha_con_z_final_se_acepta():
    tarea = TareaEntrada(**tarea_valida(fecha_entrega="2026-11-04T04:59:00Z"))

    assert tarea.fecha_entrega == datetime(2026, 11, 4, 4, 59, tzinfo=timezone.utc)


@pytest.mark.parametrize("fecha", ["2026-11-03T23:59:00", "2026-11-03"])
def test_fecha_sin_zona_horaria_se_rechaza(fecha):
    with pytest.raises(ValidationError) as error:
        TareaEntrada(**tarea_valida(fecha_entrega=fecha))

    assert "zona horaria" in mensajes(error.value)["fecha_entrega"]


@pytest.mark.parametrize("fecha", ["no es fecha", "2026-02-31T10:00:00Z", ""])
def test_fecha_invalida_se_rechaza(fecha):
    with pytest.raises(ValidationError) as error:
        TareaEntrada(**tarea_valida(fecha_entrega=fecha))

    assert "no es válida" in mensajes(error.value)["fecha_entrega"]


def test_fecha_que_no_es_texto_se_rechaza():
    with pytest.raises(ValidationError) as error:
        TareaEntrada(**tarea_valida(fecha_entrega=1700000000))

    assert "texto" in mensajes(error.value)["fecha_entrega"]


def test_materia_id_ausente_se_rechaza():
    datos = tarea_valida()
    del datos["materia_id"]

    with pytest.raises(ValidationError) as error:
        TareaEntrada(**datos)

    assert "materia_id" in mensajes(error.value)


@pytest.mark.parametrize("materia_id", ["1", 1.5, True])
def test_materia_id_que_no_es_entero_se_rechaza(materia_id):
    with pytest.raises(ValidationError) as error:
        TareaEntrada(**tarea_valida(materia_id=materia_id))

    assert "materia_id" in mensajes(error.value)


def test_cada_dato_invalido_genera_un_mensaje_propio():
    with pytest.raises(ValidationError) as error:
        TareaEntrada(titulo="", fecha_entrega="mañana")

    assert set(mensajes(error.value)) == {"titulo", "fecha_entrega", "materia_id"}
