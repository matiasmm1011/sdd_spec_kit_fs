# Plan de Implementación: Organizador de Tareas Académicas

**Rama**: `001-organizador-tareas` | **Fecha**: 2026-10-26 | **Especificación**: [spec.md](spec.md)

**Entrada**: Especificación de la funcionalidad en `specs/001-organizador-tareas/spec.md`

## Resumen

Aplicación web local para que un estudiante de la UPB registre materias (nombre y color), cree
tareas asociadas a una materia, vea un listado ordenado por fecha de entrega con las tareas
vencidas y urgentes destacadas, las marque como completadas y las filtre por materia o estado.

Enfoque técnico (ver [research.md](research.md)): un único proyecto Python 3.12 con FastAPI que
expone una API REST JSON y sirve también el frontend estático (HTML, CSS y JavaScript sin
frameworks). Los datos se guardan en un archivo SQLite accedido con el módulo estándar
`sqlite3`. El estado "vencida"/"urgente" lo calcula el servidor en cada consulta a partir de un
reloj inyectable (FR-020), lo que permite probarlo con horas simuladas. Las pruebas usan pytest.

## Contexto Técnico

**Lenguaje/Versión**: Python 3.12 (backend) y JavaScript estándar del navegador (frontend, sin transpilación)

**Dependencias principales**: FastAPI (incluye Pydantic para validación) y Uvicorn como servidor. Nada más en ejecución.

**Almacenamiento**: SQLite en un solo archivo local (`datos/tareas.db`), acceso con `sqlite3` de la biblioteca estándar, sin ORM

**Pruebas**: pytest, con `httpx` para el cliente de pruebas de FastAPI y `pytest-playwright` (solo desarrollo) para unas pocas pruebas de interfaz en navegador

**Plataforma objetivo**: Aplicación local que corre en el dispositivo del estudiante (Windows, macOS o Linux) y se usa desde el navegador, tanto en computadora como en celular (pantalla de 360 px o más)

**Tipo de proyecto**: Aplicación web de un solo proyecto (API + frontend estático servido por la misma aplicación)

**Metas de rendimiento**: Listado, filtrado y marcado como completada visibles en menos de 1 segundo (SC-005) con hasta cientos de tareas

**Restricciones**: Sin Docker ni microservicios; sin inicio de sesión; un solo usuario por dispositivo; textos de interfaz y mensajes de error en español; servidor enlazado a `127.0.0.1` por defecto

**Escala/Alcance**: Un usuario; decenas de materias y cientos de tareas como máximo; 4 pantallas/secciones (materias, tareas, formulario de tarea, filtros)

## Verificación de la Constitución

*PUERTA: debe pasar antes de la investigación de la Fase 0. Se vuelve a verificar tras el diseño de la Fase 1.*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Simplicidad primero (YAGNI) | Un solo proyecto, sin ORM, sin capas de repositorio, sin framework de frontend, sin Docker ni cola de tareas. SQLite local y `sqlite3` estándar. | Cumple |
| II. Pruebas obligatorias | Cada endpoint y la regla de plazos tienen pruebas con pytest; los flujos de interfaz clave tienen pruebas en navegador. Un único comando: `pytest`. | Cumple |
| III. Código legible | Módulos pequeños por responsabilidad (`plazos`, `rutas_materias`, `rutas_tareas`, `db`, `esquemas`); nombres del dominio en español; docstrings solo para lo no obvio. | Cumple |
| IV. Validación de entradas | Validación en el servidor con Pydantic (longitudes 50/100/500, espacios en blanco, paleta de colores, fecha con zona horaria, materia existente, unicidad sin distinguir mayúsculas). Cada regla con su prueba. | Cumple |
| V. Accesible y responsivo | HTML semántico, `label` asociados, foco visible, diseño móvil primero, prueba automatizada de ausencia de desplazamiento horizontal a 360 px. | Cumple |
| Restricciones adicionales | Dependencias mínimas y justificadas (ver Seguimiento de Complejidad); sin secretos; mensajes de error en español. | Cumple |

**Resultado de la puerta inicial**: APROBADA, sin violaciones.

**Reevaluación tras el diseño (Fase 1)**: APROBADA. El diseño no añadió capas ni dependencias de ejecución; la única adición (pruebas en navegador) está justificada abajo.

## Estructura del Proyecto

### Documentación (esta funcionalidad)

```text
specs/001-organizador-tareas/
├── plan.md              # Este archivo (salida de /speckit-plan)
├── research.md          # Fase 0: decisiones técnicas y alternativas
├── data-model.md        # Fase 1: entidades, reglas y esquema
├── quickstart.md        # Fase 1: guía de ejecución y validación
├── contracts/
│   └── api.md           # Fase 1: contrato de la API REST
├── checklists/
│   └── requirements.md  # Calidad de la especificación
└── tasks.md             # Fase 2 (la crea /speckit-tasks, NO este comando)
```

### Código fuente (raíz del repositorio)

```text
app/
├── __init__.py
├── main.py              # Crea la aplicación FastAPI, registra rutas y sirve el frontend
├── db.py                # Conexión SQLite, creación del esquema y claves foráneas activas
├── esquemas.py          # Modelos Pydantic de entrada/salida y reglas de validación
├── plazos.py            # Regla pura: vencida / urgente / ninguno según el reloj
├── rutas_materias.py    # Endpoints de /api/materias
├── rutas_tareas.py      # Endpoints de /api/tareas
└── estatico/
    ├── index.html       # Página única (HTML semántico, lang="es")
    ├── estilos.css      # Estilos móvil primero
    └── app.js           # Lógica de interfaz con fetch (sin frameworks)

tests/
├── conftest.py          # Aplicación con base de datos temporal y reloj simulado
├── unit/
│   ├── test_plazos.py       # Reglas de vencida/urgente, incluidos los límites exactos
│   └── test_esquemas.py     # Reglas de validación de entradas
├── integration/
│   ├── test_materias_api.py # CRUD, unicidad, borrado en cascada
│   └── test_tareas_api.py   # CRUD, orden, filtros, completar, plazos
└── e2e/
    └── test_interfaz.py     # Flujos clave en navegador, incluida la vista de 360 px

datos/                   # Archivo SQLite (ignorado por control de versiones)
requirements.txt         # Dependencias de ejecución
requirements-dev.txt     # pytest, httpx, pytest-playwright
README.md                # Cómo instalar, ejecutar y probar (en español)
```

**Decisión de estructura**: un único proyecto en la raíz (sin carpetas `backend/` y `frontend/`
separadas). El frontend vive dentro de `app/estatico/` y lo sirve la misma aplicación, como pidió
el usuario. Las pruebas se separan por nivel (unitarias, de integración y de interfaz) para poder
ejecutar rápido las dos primeras.

## Seguimiento de Complejidad

> Solo se llena porque hay una adición que requiere justificación frente al Principio I.

| Adición | Por qué es necesaria | Alternativa más simple rechazada porque |
|---------|----------------------|-----------------------------------------|
| `pytest-playwright` (solo desarrollo) para pruebas en navegador | El Principio II exige pruebas automatizadas de *toda* la funcionalidad y el Principio V exige verificar la vista de celular; ambas cosas solo se pueden comprobar con un navegador real. | Probar solo la API dejaría sin cobertura automatizada la interfaz (marcas visuales, filtros, confirmación de borrado, 360 px) y obligaría a verificarlas a mano. |
