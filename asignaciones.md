# Asignaciones: Organizador de Tareas Académicas

**Fuente**: [specs/001-organizador-tareas/tasks.md](specs/001-organizador-tareas/tasks.md)

**Estado actual**: Fases 1, 2 y 3 terminadas (T001–T023). Faltan 26 tareas (T024–T049): Historias 2, 3 y 4 y el pulido final.

## Criterio de reparto

Cada integrante se encarga de una capa distinta del proyecto, así nadie hace la misma tarea ni edita los mismos archivos:

| Integrante | Rol | Archivos que le pertenecen |
|---|---|---|
| Alejandro Rozich | Pruebas | `tests/` |
| Sebastian Catunta | Backend (API) | `app/*.py`, `README.md` |
| Matias Meneses | Frontend (interfaz) | `app/estatico/` |

Si alguien necesita cambiar un archivo de otra capa, lo coordina con su responsable antes de hacerlo.

---

## Alejandro Rozich — Pruebas (9 tareas)

Escribe las pruebas **antes** de que se implemente cada historia; deben fallar al principio (Principio II de la constitución).

| ID | Historia | Tarea |
|---|---|---|
| T024 | US2 | `tests/unit/test_plazos.py`: reglas de `vencida`, `urgente` y `ninguno`, incluidos los límites de 48 horas |
| T025 | US2 | `tests/integration/test_tareas_listado.py`: orden por `fecha_entrega` e `id`, campo `plazo`, cambio de plazo al avanzar el reloj |
| T026 | US2 | `tests/e2e/test_listado.py`: orden y etiquetas "Vencida"/"Urgente" en el navegador |
| T032 | US3 | `tests/integration/test_tareas_completar.py`: `PATCH /api/tareas/{id}/completada` (`200`, `404`, `422`) |
| T033 | US3 | `tests/e2e/test_completar.py`: marcar y desmarcar una tarea vencida |
| T038 | US4 | `tests/integration/test_tareas_filtros.py`: filtros `materia_id` y `estado`, combinaciones y errores |
| T039 | US4 | `tests/e2e/test_filtros.py`: filtros en la interfaz, mensaje de resultados vacíos y "Quitar filtros" |
| T045 | Pulido | `tests/e2e/test_accesibilidad.py`: 360 px sin desplazamiento, etiquetas, uso con teclado y texto literal en títulos |
| T048 | Pulido | Ejecutar `pytest` completo e informar los fallos a quien corresponda |

## Sebastian Catunta — Backend (9 tareas)

| ID | Historia | Tarea |
|---|---|---|
| T027 | US2 | `app/plazos.py`: función pura `calcular_plazo(fecha_entrega, completada, ahora)` |
| T028 | US2 | Añadir `plazo` al modelo de salida de tarea en `app/esquemas.py` (después de T027) |
| T029 | US2 | `app/rutas_tareas.py`: orden `fecha_entrega ASC, id ASC` y `plazo` en todas las respuestas (después de T028) |
| T034 | US3 | Modelo de entrada estricto `{"completada": bool}` en `app/esquemas.py` |
| T035 | US3 | `PATCH /api/tareas/{id}/completada` en `app/rutas_tareas.py` (después de T034) |
| T040 | US4 | Parámetros `materia_id` y `estado` en `GET /api/tareas` |
| T044 | Pulido | `README.md` en español: instalación, ejecución, `RUTA_DB`, `pytest` y advertencia sobre `0.0.0.0` |
| T047 | Pulido | Revisión de seguridad: sin `innerHTML` con datos del usuario, ruta de la base solo desde `RUTA_DB`, servidor en `127.0.0.1` |
| T049 | Pulido | Ejecutar los escenarios de `quickstart.md` y registrar diferencias con la especificación |

## Matias Meneses — Frontend (8 tareas)

| ID | Historia | Tarea |
|---|---|---|
| T030 | US2 | `app.js`: mostrar cada tarea con fecha local, materia y etiqueta "Vencida"/"Urgente"; refresco cada 60 s y con `visibilitychange` |
| T031 | US2 | `estilos.css`: estilos de tarea vencida y urgente con contraste suficiente |
| T036 | US3 | `app.js`: botón para marcar/desmarcar con `aria-pressed` y refresco del listado |
| T037 | US3 | `estilos.css`: estilo de tarea completada (tachado más un indicador que no sea solo color) |
| T041 | US4 | `index.html`: selector de materia ("Todas"), selector de estado y botón "Quitar filtros" |
| T042 | US4 | `app.js`: aplicar y quitar filtros, enviar parámetros a la API y mensaje de resultados vacíos (después de T041) |
| T043 | US4 | `estilos.css`: barra de filtros adaptable a 360 px |
| T046 | Pulido | Revisión de accesibilidad: foco en el diálogo, errores con `aria-live`, reintento ante fallos y contraste |

---

## Orden de trabajo

Las tres personas avanzan juntas, historia por historia:

1. **Historia 2**: Alejandro escribe T024–T026 → Sebastian hace T027–T029 → Matias hace T030–T031.
2. **Historia 3**: Alejandro escribe T032–T033 → Sebastian hace T034–T035 → Matias hace T036–T037.
3. **Historia 4**: Alejandro escribe T038–T039 → Sebastian hace T040 → Matias hace T041–T043.
4. **Pulido**: T044, T045 y T046 en paralelo; después T047; al final T048 y T049.

Matias puede adelantar el HTML y CSS de cada historia mientras Sebastian termina la API, porque usa el contrato de [contracts/api.md](specs/001-organizador-tareas/contracts/api.md). Una historia está terminada cuando todas sus pruebas pasan.

## Reglas del equipo

- Cada integrante trabaja en su propia rama (por ejemplo `us2-backend`) y se integra a `main` con una revisión de otro integrante.
- Al terminar una tarea, marcarla con `[X]` en `tasks.md`.
- Hacer un commit por tarea o por grupo lógico de tareas.
