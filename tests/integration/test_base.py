"""Pruebas de la base técnica: página principal, esquema, persistencia y errores."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.db import conectar, crear_esquema
from app.main import crear_app


def test_la_raiz_sirve_html_en_espanol_con_viewport(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]
    assert '<html lang="es">' in respuesta.text
    assert 'name="viewport"' in respuesta.text


def test_los_recursos_estaticos_se_sirven(cliente):
    assert cliente.get("/estatico/estilos.css").status_code == 200
    assert cliente.get("/estatico/app.js").status_code == 200


def test_el_esquema_existe_al_crear_la_aplicacion(cliente, ruta_db):
    conexion = conectar(ruta_db)
    tablas = {fila["name"] for fila in conexion.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    )}
    conexion.close()

    assert {"materias", "tareas"} <= tablas


def test_las_claves_foraneas_estan_activas(ruta_db):
    conexion = conectar(ruta_db)
    activas = conexion.execute("PRAGMA foreign_keys").fetchone()[0]
    conexion.close()

    assert activas == 1


def _insertar_materia_y_tarea(conexion):
    conexion.execute(
        "INSERT INTO materias (nombre, nombre_clave, color) VALUES ('Cálculo II', 'cálculo ii', '#1D4ED8')"
    )
    conexion.execute(
        "INSERT INTO tareas (titulo, fecha_entrega, materia_id) "
        "VALUES ('Taller', '2026-11-03T04:59:00Z', 1)"
    )
    conexion.commit()


def test_borrar_una_materia_borra_sus_tareas_en_cascada(cliente, ruta_db):
    conexion = conectar(ruta_db)
    _insertar_materia_y_tarea(conexion)

    conexion.execute("DELETE FROM materias WHERE id = 1")
    conexion.commit()
    restantes = conexion.execute("SELECT COUNT(*) FROM tareas").fetchone()[0]
    conexion.close()

    assert restantes == 0


def test_los_datos_persisten_al_reiniciar_la_aplicacion(ruta_db):
    with TestClient(crear_app(ruta_db=ruta_db)):
        conexion = conectar(ruta_db)
        _insertar_materia_y_tarea(conexion)
        conexion.close()

    with TestClient(crear_app(ruta_db=ruta_db)):
        conexion = conectar(ruta_db)
        titulos = [fila["titulo"] for fila in conexion.execute("SELECT titulo FROM tareas")]
        conexion.close()

    assert titulos == ["Taller"]


def test_crear_el_esquema_dos_veces_no_falla(ruta_db):
    conexion = conectar(ruta_db)
    crear_esquema(conexion)
    crear_esquema(conexion)
    conexion.close()


@pytest.mark.parametrize(
    "sentencia",
    [
        "INSERT INTO materias (nombre, nombre_clave, color) VALUES ('', 'x', '#1D4ED8')",
        f"INSERT INTO materias (nombre, nombre_clave, color) VALUES ('{'a' * 51}', 'x', '#1D4ED8')",
    ],
)
def test_la_base_rechaza_nombres_de_materia_fuera_de_rango(cliente, ruta_db, sentencia):
    conexion = conectar(ruta_db)
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute(sentencia)
    conexion.close()


def test_la_base_rechaza_titulos_y_descripciones_demasiado_largos(cliente, ruta_db):
    conexion = conectar(ruta_db)
    _insertar_materia_y_tarea(conexion)

    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute(
            "INSERT INTO tareas (titulo, fecha_entrega, materia_id) "
            f"VALUES ('{'a' * 101}', '2026-11-03T04:59:00Z', 1)"
        )
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute(
            "INSERT INTO tareas (titulo, descripcion, fecha_entrega, materia_id) "
            f"VALUES ('Ok', '{'a' * 501}', '2026-11-03T04:59:00Z', 1)"
        )
    conexion.close()


def test_una_ruta_inexistente_devuelve_el_formato_de_error_en_espanol(cliente):
    respuesta = cliente.get("/api/inexistente")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detalle": [{"campo": None, "mensaje": "No se encontró lo que buscas."}]
    }


def test_un_error_de_tipo_usa_el_formato_detalle_en_espanol(ruta_db):
    aplicacion = crear_app(ruta_db=ruta_db)

    @aplicacion.get("/api/prueba")
    def prueba(numero: int):
        return {"numero": numero}

    with TestClient(aplicacion) as cliente_http:
        con_texto = cliente_http.get("/api/prueba?numero=abc")
        sin_dato = cliente_http.get("/api/prueba")

    assert con_texto.status_code == 422
    assert con_texto.json() == {
        "detalle": [{"campo": "numero", "mensaje": "Debe ser un número entero."}]
    }
    assert sin_dato.status_code == 422
    assert sin_dato.json() == {
        "detalle": [{"campo": "numero", "mensaje": "Este dato es obligatorio."}]
    }
