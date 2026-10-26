"""Aplicación FastAPI: API REST en /api y frontend estático en /."""

from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import rutas_materias, rutas_tareas
from app.db import conectar, crear_esquema, obtener_ruta_db

DIRECTORIO_ESTATICO = Path(__file__).parent / "estatico"

MENSAJES_HTTP = {
    404: "No se encontró lo que buscas.",
    405: "Método no permitido.",
    409: "La operación entra en conflicto con datos existentes.",
}

# Traducción de los errores que genera Pydantic por tipo (los validadores propios
# del proyecto ya devuelven su mensaje en español).
MENSAJES_VALIDACION = {
    "missing": "Este dato es obligatorio.",
    "int_parsing": "Debe ser un número entero.",
    "int_type": "Debe ser un número entero.",
    "bool_parsing": "Debe ser verdadero o falso.",
    "bool_type": "Debe ser verdadero o falso.",
    "string_type": "Debe ser texto.",
    "literal_error": "El valor no es válido.",
    "enum": "El valor no es válido.",
    "json_invalid": "El cuerpo de la petición no es un JSON válido.",
    "datetime_parsing": "La fecha y hora no son válidas.",
    "datetime_type": "La fecha y hora no son válidas.",
}
MENSAJE_VALIDACION_GENERICO = "El valor no es válido."
PREFIJO_VALIDADOR_PROPIO = "Value error, "


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _error_json(status_code: int, errores: list[dict]) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detalle": errores})


def _campo_del_error(ubicacion: tuple) -> str | None:
    """Nombre del campo a partir de la ubicación de Pydantic, sin 'body'/'query'."""
    nombres = [str(parte) for parte in ubicacion if parte not in ("body", "query", "path")]
    return nombres[-1] if nombres else None


def _mensaje_del_error(error: dict) -> str:
    mensaje = error.get("msg", "")
    if error.get("type") == "value_error" and mensaje.startswith(PREFIJO_VALIDADOR_PROPIO):
        return mensaje[len(PREFIJO_VALIDADOR_PROPIO):]
    return MENSAJES_VALIDACION.get(error.get("type"), MENSAJE_VALIDACION_GENERICO)


async def _manejar_validacion(_: Request, excepcion: RequestValidationError) -> JSONResponse:
    errores = [
        {"campo": _campo_del_error(error["loc"]), "mensaje": _mensaje_del_error(error)}
        for error in excepcion.errors()
    ]
    return _error_json(422, errores)


async def _manejar_http(_: Request, excepcion: StarletteHTTPException) -> JSONResponse:
    """Las rutas lanzan HTTPException(detail={'campo': ..., 'mensaje': ...})."""
    if isinstance(excepcion.detail, dict):
        error = {
            "campo": excepcion.detail.get("campo"),
            "mensaje": excepcion.detail["mensaje"],
        }
    else:
        mensaje = MENSAJES_HTTP.get(excepcion.status_code, "No se pudo completar la operación.")
        error = {"campo": None, "mensaje": mensaje}
    return _error_json(excepcion.status_code, [error])


def crear_app(ruta_db: str | None = None, reloj: Callable[[], datetime] | None = None) -> FastAPI:
    """Crea la aplicación. `ruta_db` y `reloj` se pueden sustituir en las pruebas."""

    @asynccontextmanager
    async def ciclo_de_vida(aplicacion: FastAPI):
        conexion = conectar(aplicacion.state.ruta_db)
        try:
            crear_esquema(conexion)
        finally:
            conexion.close()
        yield

    aplicacion = FastAPI(title="Organizador de Tareas Académicas", lifespan=ciclo_de_vida)
    aplicacion.state.ruta_db = ruta_db or obtener_ruta_db()
    aplicacion.state.reloj = reloj or ahora_utc

    aplicacion.add_exception_handler(RequestValidationError, _manejar_validacion)
    aplicacion.add_exception_handler(StarletteHTTPException, _manejar_http)

    aplicacion.include_router(rutas_materias.router)
    aplicacion.include_router(rutas_tareas.router)

    aplicacion.mount("/estatico", StaticFiles(directory=DIRECTORIO_ESTATICO), name="estatico")

    @aplicacion.get("/", include_in_schema=False)
    def pagina_principal() -> FileResponse:
        return FileResponse(DIRECTORIO_ESTATICO / "index.html")

    return aplicacion


app = crear_app()
