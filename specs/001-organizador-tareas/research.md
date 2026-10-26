# Investigación (Fase 0): Organizador de Tareas Académicas

Las tecnologías vienen dadas por el usuario (Python 3.12, FastAPI, SQLite, frontend sin
frameworks, pytest, un solo proyecto, sin Docker). No quedan marcadores `NEEDS CLARIFICATION`.
Este documento registra las decisiones de diseño que sí había que tomar.

## D1. Dónde se calcula "vencida" y "urgente"

- **Decisión**: el servidor calcula el campo `plazo` (`vencida`, `urgente` o `ninguno`) en cada
  respuesta del listado, usando un reloj inyectable (`ahora()` como dependencia de FastAPI).
  La regla vive en una función pura en `app/plazos.py`.
- **Justificación**: cumple FR-020 (no se guarda el estado, se deriva de la hora actual) y permite
  probar los límites exactos (48 h inclusive, hora igual a "ahora" = vencida) con una hora
  simulada, sin esperar tiempo real. Como el servidor corre en el mismo dispositivo que el
  navegador, ambos relojes coinciden.
- **Alternativas consideradas**:
  - Calcularlo en JavaScript con el reloj del navegador: la regla quedaría fuera del alcance de
    pytest y duplicaría lógica si luego se necesita en otro lugar.
  - Guardar una columna `estado_plazo` y actualizarla con un proceso periódico: añade complejidad
    y puede quedar desfasada.

## D2. Actualización de las marcas sin recargar la página

- **Decisión**: el frontend vuelve a pedir el listado cada 60 segundos y al recuperar el foco de
  la pestaña.
- **Justificación**: cubre el caso límite "una tarea pasa de urgente a vencida con la aplicación
  abierta" con una sola línea de `setInterval`, sin WebSockets ni eventos del servidor.
- **Alternativas consideradas**: WebSockets o Server-Sent Events (excesivo para un usuario);
  recalcular en el navegador (ver D1).

## D3. Almacenamiento y acceso a datos

- **Decisión**: SQLite en un archivo (`datos/tareas.db`) con el módulo estándar `sqlite3`, SQL
  escrito a mano en funciones pequeñas, claves foráneas activadas (`PRAGMA foreign_keys = ON`) y
  `ON DELETE CASCADE` de tareas respecto a materias.
- **Justificación**: cumple FR-014 (persistencia entre sesiones) y FR-016 (borrado en cascada) con
  cero dependencias adicionales. Son solo dos tablas; un ORM no aporta valor (Principio I).
- **Alternativas consideradas**: SQLAlchemy o SQLModel (dependencia y curva de aprendizaje sin
  beneficio a esta escala); archivos JSON (sin integridad referencial ni consultas).

## D4. Unicidad del nombre de materia sin distinguir mayúsculas

- **Decisión**: se guarda una columna `nombre_clave` con el nombre recortado y pasado por
  `str.casefold()`, con restricción `UNIQUE`. La columna `nombre` conserva lo que escribió el
  estudiante.
- **Justificación**: `COLLATE NOCASE` de SQLite solo ignora mayúsculas ASCII, por lo que "Cálculo"
  y "CÁLCULO" se considerarían distintos. `casefold()` resuelve acentos y la "ñ" (FR-002).
- **Alternativas consideradas**: `COLLATE NOCASE` (incorrecto con caracteres no ASCII); comprobar
  duplicados solo en código sin restricción en la base (permitiría condiciones de carrera).

## D5. Fechas y zonas horarias

- **Decisión**: la API recibe y devuelve `fecha_entrega` en ISO 8601 **con desplazamiento
  horario** (por ejemplo `2026-11-03T23:59:00-05:00`). El servidor la guarda normalizada a UTC. El
  navegador convierte la fecha y hora que el estudiante eligió (zona del dispositivo) a ese
  formato y muestra las fechas en hora local. Las fechas sin zona horaria se rechazan con error 422.
- **Justificación**: evita ambigüedad en el cálculo de la ventana de 48 horas (la spec toma como
  referencia la zona del dispositivo) y permite comparar instantes directamente.
- **Alternativas consideradas**: guardar hora local sin zona (se rompe si el dispositivo cambia de
  zona o hay cambio de hora); enviar solo la fecha (impide calcular las 48 h con precisión).

## D6. Hora por defecto de la fecha de entrega

- **Decisión**: el formulario tiene un campo de fecha y otro de hora; la hora se precarga con
  `23:59`. Por tanto, la API siempre recibe fecha y hora completas.
- **Justificación**: aplica el supuesto de la spec (final del día si no se indica hora) en la
  interfaz, manteniendo la API simple y estricta.

## D7. Paleta de colores de las materias

- **Decisión**: ocho colores predefinidos, validados en el servidor como valores hexadecimales de
  una lista cerrada (definida en [data-model.md](data-model.md)). La interfaz los muestra como
  opciones con nombre en texto, no solo con color, para accesibilidad.
- **Justificación**: la spec establece una paleta predefinida. Una lista cerrada evita colores
  ilegibles o entradas maliciosas y permite garantizar el contraste del texto.
- **Alternativas consideradas**: selector de color libre (riesgo de contraste insuficiente y más
  validación).

## D8. Frontend sin frameworks

- **Decisión**: una sola página `index.html` con `estilos.css` y `app.js` (módulo ES). Se construye
  el DOM con `textContent` y `createElement` (nunca `innerHTML` con datos del usuario) para evitar
  inyección de HTML. Diseño móvil primero con CSS Grid/Flexbox y una consulta de medios para
  pantallas anchas.
- **Justificación**: requisito del usuario; cumple Principios I y V. El uso de `textContent`
  refuerza el Principio IV en la capa de presentación.
- **Alternativas consideradas**: frameworks o bibliotecas de componentes (descartados por el
  usuario y por simplicidad).

## D9. Estrategia de pruebas

- **Decisión**: tres niveles con pytest.
  1. **Unitarias**: regla de plazos (`plazos.py`) y validaciones (`esquemas.py`), sin base de datos.
  2. **Integración**: `TestClient` de FastAPI contra una base SQLite temporal por prueba y un reloj
     simulado; cubren cada endpoint y cada escenario de aceptación que no dependa del navegador.
  3. **Interfaz (e2e)**: `pytest-playwright` contra un servidor de pruebas, solo para los flujos
     clave: crear materia y tarea, ver marcas vencida/urgente, completar, filtrar, confirmar
     borrado en cascada y comprobar que a 360 px no hay desplazamiento horizontal.
- **Justificación**: cumple el Principio II con el menor número de piezas. Las pruebas en
  navegador son las únicas capaces de verificar FR-018 y SC-007.
- **Alternativas consideradas**: solo pruebas de API (deja la interfaz sin automatizar); Selenium
  (más pesado que Playwright); pruebas unitarias de JavaScript con Node (añade otro ecosistema).

## D10. Ejecución local y seguridad

- **Decisión**: Uvicorn enlazado a `127.0.0.1:8000` por defecto; la ruta de la base de datos se
  configura con la variable de entorno `RUTA_DB` (valor por defecto `datos/tareas.db`). Sin
  autenticación (spec FR-015). El frontend y la API comparten origen, por lo que no se habilita CORS.
- **Justificación**: sin inicio de sesión, no exponer el servicio a la red evita que terceros lean
  o modifiquen los datos. La variable de entorno permite aislar las pruebas.
- **Alternativas consideradas**: enlazar a `0.0.0.0` para usar desde el celular en la misma red
  (queda como opción documentada en el README, advirtiendo que cualquiera en la red tendría acceso).
