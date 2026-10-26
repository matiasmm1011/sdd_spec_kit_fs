---

description: "Lista de tareas para implementar el Organizador de Tareas Académicas"
---

# Tareas: Organizador de Tareas Académicas

**Entrada**: Documentos de diseño en `specs/001-organizador-tareas/`

**Prerrequisitos**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/api.md](contracts/api.md), [quickstart.md](quickstart.md)

**Pruebas**: OBLIGATORIAS. El Principio II de la constitución exige pruebas automatizadas antes de dar por terminada cualquier funcionalidad. Dentro de cada historia, las pruebas se escriben primero y DEBEN fallar antes de implementar.

**Organización**: Las tareas se agrupan por historia de usuario para poder implementar y probar cada historia de forma independiente.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: Se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes)
- **[Historia]**: Historia de usuario a la que pertenece la tarea (US1, US2, US3, US4)
- Cada descripción incluye la ruta exacta del archivo

## Convenciones de rutas

Proyecto único en la raíz del repositorio (ver "Estructura del Proyecto" en el plan): código en `app/`, frontend estático en `app/estatico/`, pruebas en `tests/`.

---

## Fase 1: Preparación (Infraestructura compartida)

**Propósito**: Inicialización del proyecto y estructura básica

- [X] T001 Crear la estructura de carpetas del plan: `app/`, `app/estatico/`, `tests/unit/`, `tests/integration/`, `tests/e2e/` y `datos/`, con `app/__init__.py` vacío
- [X] T002 [P] Crear `requirements.txt` con las dependencias de ejecución (`fastapi` y `uvicorn`) compatibles con Python 3.12
- [X] T003 [P] Crear `requirements-dev.txt` que incluya `-r requirements.txt` más `pytest`, `httpx` y `pytest-playwright`
- [X] T004 [P] Crear `.gitignore` que excluya `datos/`, `.venv/`, `__pycache__/` y `.pytest_cache/`
- [X] T005 [P] Crear `pytest.ini` con `testpaths = tests` y el marcador `e2e` para las pruebas de navegador

---

## Fase 2: Fundamentos (Prerrequisitos bloqueantes)

**Propósito**: Infraestructura central que DEBE estar completa antes de CUALQUIER historia de usuario

**⚠️ CRÍTICO**: Ninguna historia de usuario puede comenzar hasta terminar esta fase

- [X] T006 Implementar `app/db.py`: función que lee la ruta de la base desde la variable de entorno `RUTA_DB` (por defecto `datos/tareas.db`), función `conectar(ruta)` que ejecuta `PRAGMA foreign_keys = ON` en cada apertura y usa filas accesibles por nombre, y función `crear_esquema(conexion)` con las sentencias SQL de "Esquema SQLite" de `data-model.md` (tablas `materias` y `tareas`, restricciones `CHECK`, `UNIQUE` en `nombre_clave`, `ON DELETE CASCADE` e índices `idx_tareas_fecha` e `idx_tareas_materia`)
- [X] T007 Implementar `app/main.py` (depende de T006): fábrica `crear_app(ruta_db=None)` que crea el esquema al iniciar; dependencia `obtener_conexion`; dependencia `obtener_ahora` que devuelve la hora actual en UTC y puede sustituirse en pruebas; manejador de errores que devuelva siempre el formato `{"detalle": [{"campo": ..., "mensaje": ...}]}` con mensajes en español para `422`, `404` y `409` (contrato `contracts/api.md`, "Convenciones"); montaje de `/estatico` y ruta `GET /` que sirve `app/estatico/index.html`; variable de módulo `app = crear_app()`
- [X] T008 [P] Crear `app/estatico/index.html` base: `<html lang="es">`, `charset`, `meta viewport`, título, `header` y `main` semánticos, enlaces a `estilos.css` y a `app.js` (como módulo), sin contenido de historias todavía
- [X] T009 [P] Crear `app/estatico/estilos.css` base con enfoque móvil primero: variables de color de la paleta, `box-sizing: border-box`, ancho máximo para evitar desplazamiento horizontal, indicador de foco visible, clase de texto solo para lectores de pantalla y tamaños de fuente legibles
- [X] T010 Crear `tests/conftest.py` (depende de T007): fixtures `ruta_db` (archivo temporal por prueba), `reloj` (hora simulada modificable inyectada como `obtener_ahora`) y `cliente` (`TestClient` de FastAPI sobre una aplicación creada con `crear_app(ruta_db)`)
- [X] T011 [P] Crear `tests/e2e/conftest.py`: fixture que levanta la aplicación con Uvicorn en un hilo, en un puerto libre y con una base temporal, y fixtures de página de Playwright con la URL base
- [X] T012 Escribir `tests/integration/test_base.py` (depende de T007 y T010): `GET /` devuelve `200`, HTML con `lang="es"` y `meta viewport`; el esquema existe tras crear la aplicación; los datos persisten al crear de nuevo la aplicación con la misma `ruta_db` (FR-014); `PRAGMA foreign_keys` está activo

**Punto de control**: Base lista; ya se pueden implementar las historias de usuario

---

## Fase 3: Historia de Usuario 1 - Registrar materias y crear tareas (Prioridad: P1) 🎯 MVP

**Objetivo**: El estudiante registra materias (nombre y color), crea, edita y elimina tareas asociadas, y los datos se validan y persisten.

**Prueba independiente**: Registrar la materia "Cálculo II" en azul, crear una tarea en ella y comprobar que queda guardada y asociada, incluso tras reiniciar la aplicación; comprobar los rechazos de validación y el borrado en cascada con confirmación.

### Pruebas de la Historia 1 (escribir primero; deben FALLAR antes de implementar) ⚠️

- [X] T013 [P] [US1] Escribir `tests/unit/test_esquemas.py`: materia con nombre vacío, solo espacios y de 51 caracteres rechazada, de 50 aceptada, recortada al guardar; color fuera de la paleta rechazado; tarea con título vacío/solo espacios/101 caracteres rechazada y de 100 aceptada; descripción de 501 caracteres rechazada y de 500 aceptada; descripción de solo espacios queda como ausente; `fecha_entrega` sin zona horaria o inválida rechazada; `materia_id` ausente rechazado; los mensajes están en español e indican el límite numérico (FR-002, FR-005)
- [X] T014 [P] [US1] Escribir `tests/integration/test_materias_api.py`: `POST` `201`; "Cálculo II" y "CÁLCULO ii" → `409`; `422` por nombre inválido o color fuera de la paleta; `GET` ordenado por nombre con `total_tareas`; `PUT` `200` (sin conflicto consigo misma), `404`, `409`, `422`; `DELETE` `204` borra la materia y todas sus tareas (pendientes y completadas), `404` si no existe; todos los errores usan el formato `detalle` (FR-001, FR-002, FR-003, FR-016)
- [X] T015 [P] [US1] Escribir `tests/integration/test_tareas_api.py`: `POST` `201` con y sin descripción; fecha pasada permitida; `422` con un elemento de `detalle` por cada dato inválido (FR-005); `materia_id` inexistente → `422`; `PUT` `200`/`404`/`422` sin cambiar `completada`; `DELETE` `204`/`404`; `GET` devuelve cada tarea con su `materia` (`id`, `nombre`, `color`) (FR-004, FR-005, FR-006, FR-008)
- [X] T016 [P] [US1] Escribir `tests/e2e/test_materias_tareas.py`: sin materias se ve el mensaje de estado vacío y no se puede crear tarea (FR-017); crear materia y tarea; rechazo visible de nombre duplicado; el texto escrito no se pierde al ser rechazado; eliminar materia con tareas muestra la confirmación con el número de tareas, cancelar no borra y confirmar borra la materia y sus tareas (FR-016)

### Implementación de la Historia 1

- [X] T017 [US1] Implementar `app/esquemas.py`: constante `PALETA_COLORES` con los valores `#1D4ED8`, `#15803D`, `#B91C1C`, `#C2410C`, `#7E22CE`, `#0F766E`, `#BE185D` y `#475569`; modelos Pydantic de entrada y salida de materia y tarea con las reglas verbatim de `data-model.md`: nombre "obligatorio; se recorta; entre 1 y 50 caracteres tras recortar; no puede ser solo espacios", título "obligatorio; se recorta; entre 1 y 100 caracteres; no puede ser solo espacios", descripción "hasta 500 caracteres; se recorta; vacío se guarda como ausente", `fecha_entrega` "obligatoria; ISO 8601 con zona horaria; se permiten fechas pasadas", `materia_id` obligatorio; mensajes de error en español
- [X] T018 [P] [US1] Implementar `app/rutas_materias.py` (depende de T017): `GET`, `POST`, `PUT` y `DELETE` de `/api/materias` según el contrato; `nombre_clave` = nombre recortado pasado por `casefold()`; `409` con mensaje en español si ya existe; `total_tareas` calculado con `COUNT`; listado ordenado por nombre
- [X] T019 [P] [US1] Implementar `app/rutas_tareas.py` (depende de T017): `POST`, `PUT`, `DELETE` y `GET` (sin filtros ni plazo todavía) de `/api/tareas`; normalizar `fecha_entrega` a UTC con formato fijo `AAAA-MM-DDTHH:MM:SSZ` para que se ordene como texto; `completada` es falso al crear y `PUT` no lo modifica; `422` si la materia no existe, con el campo `materia_id`
- [X] T020 [US1] Registrar los routers de materias y tareas en `app/main.py` (depende de T018 y T019)
- [X] T021 [P] [US1] Extender `app/estatico/index.html`: sección de materias con formulario (etiqueta asociada, `maxlength="50"` y selector de color con el nombre del color en texto), lista de materias, formulario de tarea (título con `maxlength="100"`, descripción con `maxlength="500"`, campos de fecha y de hora precargada con `23:59`, selector de materia), región de mensajes con `aria-live` y un `<dialog>` de confirmación de borrado; el servidor sigue siendo la validación definitiva
- [X] T022 [US1] Implementar en `app/estatico/app.js` (depende de T021): funciones `fetch` hacia `/api`; cargar y mostrar materias y tareas; crear/editar/eliminar materias y tareas; convertir fecha y hora locales a ISO 8601 con desplazamiento horario; mostrar los errores de `detalle` junto a cada campo conservando lo escrito; confirmación de borrado de materia con `total_tareas` (omitida si es cero); estados vacíos y aviso de registrar primero una materia; construir el DOM solo con `textContent`/`createElement`, nunca `innerHTML` con datos del usuario
- [X] T023 [P] [US1] Añadir a `app/estatico/estilos.css` los estilos de formularios, muestras de color con su nombre, lista de materias y diálogo de confirmación, con áreas táctiles de al menos 44 px y diseño móvil primero

**Punto de control**: La Historia 1 debe funcionar por completo y probarse sola (MVP)

---

## Fase 4: Historia de Usuario 2 - Listado con vencidas y urgentes destacadas (Prioridad: P2)

**Objetivo**: El listado se ordena por fecha de entrega y marca cada tarea pendiente como vencida o urgente según la hora actual.

**Prueba independiente**: Crear tareas con fecha de ayer, dentro de 24 horas y dentro de 10 días, y comprobar el orden y la marca de cada una.

### Pruebas de la Historia 2 (escribir primero; deben FALLAR antes de implementar) ⚠️

- [ ] T024 [P] [US2] Escribir `tests/unit/test_plazos.py`: tarea completada → `ninguno`; fecha igual a `ahora` → `vencida`; fecha anterior → `vencida`; `ahora` + 1 segundo → `urgente`; exactamente `ahora` + 48 horas → `urgente`; `ahora` + 48 horas + 1 segundo → `ninguno`; una tarea nunca es vencida y urgente a la vez (FR-009, FR-010, FR-012)
- [ ] T025 [P] [US2] Escribir `tests/integration/test_tareas_listado.py` con el reloj simulado: el `GET /api/tareas` devuelve las tareas ordenadas por `fecha_entrega` ascendente con desempate por `id`; cada objeto trae `plazo`; avanzar el reloj cambia el `plazo` sin modificar los datos guardados (FR-020); `POST` y `PUT` también devuelven `plazo` (FR-007, FR-009, FR-010, FR-020)
- [ ] T026 [P] [US2] Escribir `tests/e2e/test_listado.py`: tres tareas (pasada, dentro de 24 horas y dentro de 10 días) aparecen en ese orden; la primera muestra la etiqueta de texto "Vencida", la segunda "Urgente" y la tercera ninguna; cada tarea muestra nombre y color de su materia (FR-008)

### Implementación de la Historia 2

- [ ] T027 [P] [US2] Implementar `app/plazos.py` con la función pura `calcular_plazo(fecha_entrega, completada, ahora)` según la tabla "Regla de plazo" de `data-model.md`: `completada` → `ninguno`; `fecha_entrega` ≤ `ahora` → `vencida`; `ahora` < `fecha_entrega` ≤ `ahora` + 48 horas → `urgente`; en otro caso `ninguno`
- [ ] T028 [US2] Añadir `plazo` (`vencida`, `urgente` o `ninguno`) al modelo de salida de tarea en `app/esquemas.py` (depende de T027)
- [ ] T029 [US2] Actualizar `app/rutas_tareas.py` (depende de T028): `GET` con `ORDER BY fecha_entrega ASC, id ASC` y cálculo de `plazo` con la dependencia `obtener_ahora` en todas las respuestas que devuelven una tarea
- [ ] T030 [US2] Actualizar `app/estatico/app.js`: mostrar cada tarea con título, fecha local formateada, estado, nombre y color de su materia y una etiqueta de texto "Vencida" o "Urgente" (no solo color); volver a pedir el listado cada 60 segundos y al recuperar el foco de la pestaña (`visibilitychange`)
- [X] T031 [P] [US2] Añadir a `app/estatico/estilos.css` los estilos de tarea vencida y urgente (etiqueta de texto más color y borde) con contraste suficiente

**Punto de control**: Las Historias 1 y 2 funcionan; el listado marca vencidas y urgentes

---

## Fase 5: Historia de Usuario 3 - Marcar tareas como completadas (Prioridad: P3)

**Objetivo**: El estudiante marca y desmarca tareas como completadas, y las completadas dejan de aparecer como vencidas o urgentes.

**Prueba independiente**: Marcar como completada una tarea vencida y comprobar que pierde la marca; desmarcarla y comprobar que la recupera.

### Pruebas de la Historia 3 (escribir primero; deben FALLAR antes de implementar) ⚠️

- [ ] T032 [P] [US3] Escribir `tests/integration/test_tareas_completar.py`: `PATCH /api/tareas/{id}/completada` con `true` devuelve `200` con `plazo` igual a `ninguno` para una tarea vencida; con `false` recupera `vencida`; `404` si no existe; `422` si `completada` no es booleano (FR-011, FR-012)
- [ ] T033 [P] [US3] Escribir `tests/e2e/test_completar.py`: marcar una tarea vencida como completada la distingue visualmente y quita "Vencida"; desmarcarla la devuelve a pendiente con su marca

### Implementación de la Historia 3

- [ ] T034 [US3] Añadir el modelo de entrada `{"completada": bool}` (estricto, sin convertir otros tipos) en `app/esquemas.py`
- [ ] T035 [US3] Implementar `PATCH /api/tareas/{id}/completada` en `app/rutas_tareas.py` (depende de T034), devolviendo la tarea con `plazo` recalculado
- [ ] T036 [US3] Actualizar `app/estatico/app.js`: control para marcar/desmarcar cada tarea con etiqueta accesible y estado expresado con `aria-pressed`, y refresco del listado
- [X] T037 [P] [US3] Añadir a `app/estatico/estilos.css` el estilo distintivo de tareas completadas (texto tachado más indicador no basado solo en color)

**Punto de control**: Las Historias 1, 2 y 3 funcionan

---

## Fase 6: Historia de Usuario 4 - Filtrar por materia o por estado (Prioridad: P4)

**Objetivo**: El estudiante filtra el listado por materia y/o estado, y puede quitar los filtros.

**Prueba independiente**: Con tareas de dos materias y estados mixtos, aplicar cada filtro por separado y combinados y comprobar el resultado.

### Pruebas de la Historia 4 (escribir primero; deben FALLAR antes de implementar) ⚠️

- [ ] T038 [P] [US4] Escribir `tests/integration/test_tareas_filtros.py`: `materia_id`, `estado=pendiente`, `estado=completada` y las combinaciones; el orden por fecha se conserva; `estado` inválido → `422`; `materia_id` no entero → `422`; `materia_id` inexistente → lista vacía con `200` (FR-013)
- [ ] T039 [P] [US4] Escribir `tests/e2e/test_filtros.py`: filtrar por materia, por estado y combinados; mensaje de que no hay tareas con esos criterios (FR-017); "Quitar filtros" restablece el listado completo

### Implementación de la Historia 4

- [ ] T040 [US4] Añadir los parámetros de consulta `materia_id` y `estado` (`pendiente` o `completada`) al `GET /api/tareas` en `app/rutas_tareas.py`
- [ ] T041 [P] [US4] Añadir a `app/estatico/index.html` los controles de filtro: selector de materia con la opción "Todas", selector de estado con etiquetas asociadas y botón "Quitar filtros"
- [ ] T042 [US4] Implementar en `app/estatico/app.js` (depende de T041) la aplicación y el quitado de filtros, el envío de los parámetros a la API y el mensaje de resultados vacíos
- [ ] T043 [P] [US4] Añadir a `app/estatico/estilos.css` los estilos de la barra de filtros, adaptables a pantallas de 360 px

**Punto de control**: Todas las historias son funcionales de forma independiente

---

## Fase 7: Pulido y Aspectos Transversales

**Propósito**: Mejoras que afectan a varias historias y cierre de calidad

- [ ] T044 [P] Crear `README.md` en español: requisitos (Python 3.12), instalación, ejecución con Uvicorn en `127.0.0.1`, variable `RUTA_DB`, cómo ejecutar `pytest` y la advertencia de seguridad si se enlaza a `0.0.0.0` para usar el celular
- [ ] T045 [P] Escribir `tests/e2e/test_accesibilidad.py`: a 360 px de ancho no hay desplazamiento horizontal (SC-007); cada campo de formulario tiene una etiqueta asociada; todas las acciones se pueden realizar solo con teclado; un título como `<script>alert(1)</script>` se muestra como texto literal (FR-018)
- [ ] T046 Revisión de accesibilidad y mensajes: foco al abrir y cerrar el diálogo de confirmación, mensajes de error anunciados con `aria-live`, errores de guardado o lectura con un mensaje en español y posibilidad de reintentar, contraste de los textos sobre los colores de materia (en `app/estatico/app.js`, `index.html` y `estilos.css`)
- [ ] T047 Revisión de seguridad: confirmar que no hay uso de `innerHTML` con datos del usuario en `app/estatico/app.js`, que la ruta de la base solo se toma de `RUTA_DB` y que el servidor documentado escucha en `127.0.0.1`
- [ ] T048 Ejecutar `pytest` completo y corregir fallos; instalar antes `playwright install chromium` si falta el navegador
- [ ] T049 Ejecutar los escenarios de `quickstart.md` y registrar cualquier diferencia con la especificación

---

## Dependencias y Orden de Ejecución

### Dependencias entre fases

- **Preparación (Fase 1)**: sin dependencias; puede empezar de inmediato
- **Fundamentos (Fase 2)**: depende de la Preparación; BLOQUEA todas las historias
- **Historias de usuario (Fase 3 en adelante)**: dependen de los Fundamentos
- **Pulido (Fase 7)**: depende de las historias que se vayan a entregar

### Dependencias entre historias

- **US1 (P1)**: empieza tras los Fundamentos; sin dependencias de otras historias
- **US2 (P2)**: empieza tras los Fundamentos; usa la creación de tareas de US1 (rutas y formulario), por lo que se implementa después de US1
- **US3 (P3)**: se implementa después de US1; el efecto sobre el plazo se ve con US2, pero la API se puede probar sin la interfaz de US2
- **US4 (P4)**: se implementa después de US1; el orden del resultado filtrado coincide con el de US2

Todas modifican `app/rutas_tareas.py`, `app/esquemas.py`, `app/estatico/app.js` y `app/estatico/estilos.css`; por eso las historias se implementan en orden de prioridad y no en paralelo sobre esos archivos.

### Dentro de cada historia

- Las pruebas se escriben primero y deben fallar antes de implementar
- Esquemas antes de rutas; rutas antes de interfaz
- Historia completa antes de pasar a la siguiente prioridad

### Oportunidades de paralelismo

- Fase 1: T002, T003, T004 y T005 en paralelo
- Fase 2: T008, T009 y T011 en paralelo; T010 y T012 tras T007
- Historia 1: las pruebas T013–T016 en paralelo; luego T018 y T019 en paralelo; T021 y T023 en paralelo
- Historias 2, 3 y 4: sus pruebas unitarias, de integración y de navegador (archivos distintos) en paralelo dentro de cada historia
- Pulido: T044 y T045 en paralelo

---

## Ejemplo de Paralelismo: Historia de Usuario 1

```text
# Lanzar juntas las pruebas de la Historia 1:
Tarea: "Escribir tests/unit/test_esquemas.py"
Tarea: "Escribir tests/integration/test_materias_api.py"
Tarea: "Escribir tests/integration/test_tareas_api.py"
Tarea: "Escribir tests/e2e/test_materias_tareas.py"

# Después, lanzar juntas las rutas (ambas dependen de app/esquemas.py):
Tarea: "Implementar app/rutas_materias.py"
Tarea: "Implementar app/rutas_tareas.py"
```

---

## Estrategia de Implementación

### Primero el MVP (solo Historia 1)

1. Completar la Fase 1: Preparación
2. Completar la Fase 2: Fundamentos (CRÍTICO: bloquea todo)
3. Completar la Fase 3: Historia 1
4. **DETENERSE y VALIDAR**: ejecutar `pytest` y los escenarios 1 y 5 de `quickstart.md`
5. Mostrar el resultado si está listo

### Entrega incremental

1. Preparación + Fundamentos → base lista
2. Historia 1 → probar → MVP
3. Historia 2 → probar → el listado ya destaca lo urgente
4. Historia 3 → probar → se puede llevar el progreso
5. Historia 4 → probar → comodidad con muchas tareas
6. Pulido → accesibilidad, seguridad y documentación

---

## Notas

- [P] = archivos distintos y sin dependencias pendientes
- La etiqueta [Historia] vincula cada tarea con su historia para dar trazabilidad
- Cada historia debe poder completarse y probarse de forma independiente
- Verificar que las pruebas fallen antes de implementar
- Confirmar los cambios (commit) después de cada tarea o grupo lógico
- Los archivos de pruebas por historia (`test_tareas_listado.py`, `test_tareas_completar.py`, `test_tareas_filtros.py`) refinan la estructura del plan, que listaba un solo `test_tareas_api.py`, para permitir el trabajo en paralelo
- Evitar: tareas vagas, conflictos en un mismo archivo y dependencias entre historias que rompan la independencia
- El checklist [ux-validacion.md](checklists/ux-validacion.md) tiene elementos de calidad de requisitos aún sin revisar (por ejemplo CHK007, CHK012, CHK028); sus resultados pueden obligar a ajustar estas tareas
