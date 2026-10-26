# Modelo de Datos (Fase 1): Organizador de Tareas Académicas

Origen: entidades y requisitos de [spec.md](spec.md); decisiones en [research.md](research.md).

## Entidades

### Materia

Asignatura que cursa el estudiante.

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | entero, autoincremental | Identificador interno, asignado por el sistema |
| `nombre` | texto | Obligatorio; se recorta (espacios al inicio y al final); entre 1 y 50 caracteres tras recortar; no puede ser solo espacios (FR-002) |
| `nombre_clave` | texto, único | Interno: `nombre` recortado y pasado por `casefold()`; garantiza unicidad sin distinguir mayúsculas ni acentos de mayúscula (FR-002) |
| `color` | texto | Obligatorio; debe ser uno de los valores de la paleta (ver abajo) |

Campo derivado en las respuestas (no se almacena): `total_tareas`, cantidad de tareas de la
materia, usada por la interfaz para la confirmación de borrado (FR-016).

**Relaciones**: una materia tiene cero o muchas tareas.

### Tarea

Obligación académica del estudiante.

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | entero, autoincremental | Identificador interno |
| `titulo` | texto | Obligatorio; se recorta; entre 1 y 100 caracteres; no puede ser solo espacios (FR-005) |
| `descripcion` | texto, opcional | Hasta 500 caracteres; se recorta; vacío se guarda como ausente (FR-005) |
| `fecha_entrega` | instante en UTC | Obligatoria; se recibe en ISO 8601 **con zona horaria**; se permiten fechas pasadas (FR-004, caso límite) |
| `completada` | booleano | `false` al crear; se puede alternar (FR-011) |
| `materia_id` | entero | Obligatorio; debe existir una materia con ese `id`; borrado en cascada (FR-016) |

Campo derivado en las respuestas (no se almacena, FR-020): `plazo`, ver "Regla de plazo".

## Paleta de colores permitida

Valores válidos para `Materia.color` (la interfaz muestra también el nombre en texto):

| Nombre | Valor |
|--------|-------|
| Azul | `#1D4ED8` |
| Verde | `#15803D` |
| Rojo | `#B91C1C` |
| Naranja | `#C2410C` |
| Morado | `#7E22CE` |
| Turquesa | `#0F766E` |
| Rosa | `#BE185D` |
| Gris | `#475569` |

Todos tienen contraste suficiente con texto blanco (relación mínima 4,5:1), de modo que el nombre
de la materia pueda mostrarse sobre su color.

## Regla de plazo (derivada)

Se evalúa en cada consulta con el instante actual `ahora` (reloj del servidor, inyectable en
pruebas):

| Condición | Valor de `plazo` |
|-----------|------------------|
| `completada` es verdadero | `ninguno` (FR-012) |
| `fecha_entrega` ≤ `ahora` | `vencida` (FR-009) |
| `ahora` < `fecha_entrega` ≤ `ahora` + 48 horas | `urgente` (FR-010) |
| `fecha_entrega` > `ahora` + 48 horas | `ninguno` |

Una tarea nunca es a la vez `vencida` y `urgente`. Los límites son: exactamente `ahora` → vencida;
exactamente `ahora + 48 h` → urgente.

## Transiciones de estado

```text
pendiente  --(marcar como completada)-->  completada
completada --(desmarcar)-------------->  pendiente
```

El `plazo` no es un estado almacenado: una tarea pendiente pasa de `ninguno` a `urgente` y luego a
`vencida` solo por el paso del tiempo.

## Esquema SQLite

```sql
CREATE TABLE IF NOT EXISTS materias (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL CHECK (length(nombre) BETWEEN 1 AND 50),
    nombre_clave TEXT NOT NULL UNIQUE,
    color        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tareas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo        TEXT NOT NULL CHECK (length(titulo) BETWEEN 1 AND 100),
    descripcion   TEXT CHECK (descripcion IS NULL OR length(descripcion) <= 500),
    fecha_entrega TEXT NOT NULL,          -- ISO 8601 en UTC, ordenable como texto
    completada    INTEGER NOT NULL DEFAULT 0 CHECK (completada IN (0, 1)),
    materia_id    INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tareas_fecha ON tareas (fecha_entrega);
CREATE INDEX IF NOT EXISTS idx_tareas_materia ON tareas (materia_id);
```

La conexión debe ejecutar `PRAGMA foreign_keys = ON` en cada apertura para que la cascada funcione.
La validación principal ocurre en la capa de esquemas (mensajes claros en español); las
restricciones `CHECK` son una segunda barrera de seguridad.

## Volumen esperado

Decenas de materias y cientos de tareas: no se requiere paginación ni particionado. El listado se
ordena con `ORDER BY fecha_entrega ASC, id ASC`.
