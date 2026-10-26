"""Regla de plazo: vencida, urgente o ninguno (FR-009, FR-010, FR-012)."""

from datetime import datetime, timedelta, timezone

import pytest

from app.plazos import calcular_plazo

AHORA = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
UN_SEGUNDO = timedelta(seconds=1)
CUARENTA_Y_OCHO_HORAS = timedelta(hours=48)


@pytest.mark.parametrize(
    "fecha_entrega",
    [AHORA - timedelta(days=3), AHORA, AHORA + UN_SEGUNDO, AHORA + timedelta(days=10)],
)
def test_una_tarea_completada_no_tiene_plazo(fecha_entrega):
    assert calcular_plazo(fecha_entrega, True, AHORA) == "ninguno"


def test_una_fecha_igual_a_ahora_esta_vencida():
    assert calcular_plazo(AHORA, False, AHORA) == "vencida"


def test_una_fecha_anterior_a_ahora_esta_vencida():
    assert calcular_plazo(AHORA - timedelta(days=1), False, AHORA) == "vencida"


def test_un_segundo_despues_de_ahora_es_urgente():
    assert calcular_plazo(AHORA + UN_SEGUNDO, False, AHORA) == "urgente"


def test_exactamente_48_horas_despues_es_urgente():
    assert calcular_plazo(AHORA + CUARENTA_Y_OCHO_HORAS, False, AHORA) == "urgente"


def test_48_horas_y_un_segundo_despues_no_tiene_plazo():
    fecha_entrega = AHORA + CUARENTA_Y_OCHO_HORAS + UN_SEGUNDO

    assert calcular_plazo(fecha_entrega, False, AHORA) == "ninguno"


def test_una_fecha_con_otra_zona_horaria_se_compara_por_su_instante():
    # 07:00 en UTC-05:00 son las 12:00 en UTC: el mismo instante que `AHORA`.
    fecha_entrega = datetime(2026, 11, 1, 7, 0, tzinfo=timezone(timedelta(hours=-5)))

    assert calcular_plazo(fecha_entrega, False, AHORA) == "vencida"


@pytest.mark.parametrize("horas", range(-72, 73, 6))
def test_una_tarea_pendiente_tiene_un_solo_plazo_valido(horas):
    plazo = calcular_plazo(AHORA + timedelta(hours=horas), False, AHORA)

    # Devuelve un único texto: nunca puede ser "vencida" y "urgente" a la vez.
    assert plazo in {"vencida", "urgente", "ninguno"}
    esperado = "vencida" if horas <= 0 else "urgente" if horas <= 48 else "ninguno"
    assert plazo == esperado
