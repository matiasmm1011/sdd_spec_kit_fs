"""Modelos de entrada y salida de la API, con las reglas de validación de los datos."""

from datetime import datetime, timezone

from pydantic import BaseModel, StrictInt, field_validator

PALETA_COLORES = (
    "#1D4ED8",  # Azul
    "#15803D",  # Verde
    "#B91C1C",  # Rojo
    "#C2410C",  # Naranja
    "#7E22CE",  # Morado
    "#0F766E",  # Turquesa
    "#BE185D",  # Rosa
    "#475569",  # Gris
)

LIMITE_NOMBRE_MATERIA = 50
LIMITE_TITULO = 100
LIMITE_DESCRIPCION = 500


# --- Entrada ---------------------------------------------------------------


class MateriaEntrada(BaseModel):
    nombre: str
    color: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, nombre: str) -> str:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre de la materia no puede estar vacío.")
        if len(nombre) > LIMITE_NOMBRE_MATERIA:
            raise ValueError(
                f"El nombre de la materia no puede superar los {LIMITE_NOMBRE_MATERIA} caracteres."
            )
        return nombre

    @field_validator("color")
    @classmethod
    def validar_color(cls, color: str) -> str:
        color = color.strip().upper()
        if color not in PALETA_COLORES:
            raise ValueError("El color no es válido. Elige uno de la paleta.")
        return color


class TareaEntrada(BaseModel):
    titulo: str
    descripcion: str | None = None
    fecha_entrega: datetime
    materia_id: StrictInt

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, titulo: str) -> str:
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("El título no puede estar vacío.")
        if len(titulo) > LIMITE_TITULO:
            raise ValueError(f"El título no puede superar los {LIMITE_TITULO} caracteres.")
        return titulo

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, descripcion: str | None) -> str | None:
        if descripcion is None:
            return None
        descripcion = descripcion.strip()
        if len(descripcion) > LIMITE_DESCRIPCION:
            raise ValueError(
                f"La descripción no puede superar los {LIMITE_DESCRIPCION} caracteres."
            )
        return descripcion or None

    @field_validator("fecha_entrega", mode="before")
    @classmethod
    def validar_fecha_entrega(cls, valor) -> datetime:
        # Se interpreta el texto a mano (en lugar de dejar que Pydantic convierta)
        # para exigir zona horaria y rechazar números u otros tipos.
        if not isinstance(valor, str):
            raise ValueError("La fecha de entrega debe ser texto en formato ISO 8601.")
        try:
            fecha = datetime.fromisoformat(valor)
        except ValueError:
            raise ValueError("La fecha de entrega no es válida.") from None
        if fecha.tzinfo is None:
            raise ValueError(
                "La fecha de entrega debe incluir la zona horaria (por ejemplo Z o -05:00)."
            )
        return fecha.astimezone(timezone.utc)


# --- Salida ----------------------------------------------------------------


class MateriaSalida(BaseModel):
    id: int
    nombre: str
    color: str
    total_tareas: int


class MateriaEnTarea(BaseModel):
    id: int
    nombre: str
    color: str


class TareaSalida(BaseModel):
    id: int
    titulo: str
    descripcion: str | None
    fecha_entrega: str
    completada: bool
    materia: MateriaEnTarea
