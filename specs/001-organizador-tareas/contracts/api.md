# Contrato de la API REST: Organizador de Tareas Académicas

Interfaz que expone la aplicación al frontend (y a las pruebas). Todas las rutas cuelgan de
`/api`, usan JSON (`Content-Type: application/json`) y no requieren autenticación (FR-015).
Los mensajes de error están en español (FR-019). Las reglas de campos están en
[data-model.md](../data-model.md).

La interfaz web se sirve en `GET /` (archivo `index.html`) y los recursos estáticos en `/estatico/*`.

## Convenciones

- **Fechas**: `fecha_entrega` en ISO 8601 con zona horaria (ej. `2026-11-03T23:59:00-05:00`).
  Las respuestas la devuelven en UTC (ej. `2026-11-04T04:59:00Z`).
- **Códigos de estado**: `200` éxito; `201` creado; `204` sin contenido; `404` no existe;
  `409` conflicto (nombre de materia repetido); `422` datos inválidos.
- **Formato de error**:

  ```json
  { "detalle": [ { "campo": "titulo", "mensaje": "El título no puede estar vacío." } ] }
  ```

  `detalle` es una lista: cada dato inválido genera un elemento (FR-005). Para `404` y `409`
  la lista tiene un solo elemento con `campo` en `null` o el campo implicado.

## Materias

### `GET /api/materias`

Lista las materias ordenadas por nombre.

Respuesta `200`:

```json
[ { "id": 1, "nombre": "Cálculo II", "color": "#1D4ED8", "total_tareas": 3 } ]
```

### `POST /api/materias`

Crea una materia.

Cuerpo:

```json
{ "nombre": "Cálculo II", "color": "#1D4ED8" }
```

| Resultado | Condición |
|-----------|-----------|
| `201` con la materia creada | Datos válidos |
| `422` | `nombre` vacío, solo espacios o de más de 50 caracteres; `color` fuera de la paleta |
| `409` | Ya existe una materia con ese nombre (sin distinguir mayúsculas) |

### `PUT /api/materias/{id}`

Reemplaza nombre y color de una materia. Mismo cuerpo y mismas validaciones que `POST`. La
unicidad ignora a la propia materia que se edita.

Respuestas: `200` con la materia actualizada, `404`, `409`, `422`.

### `DELETE /api/materias/{id}`

Elimina la materia **y todas sus tareas** (pendientes y completadas). La confirmación al
estudiante la hace la interfaz usando `total_tareas` (FR-016).

Respuestas: `204`, `404`.

## Tareas

Objeto tarea en las respuestas:

```json
{
  "id": 7,
  "titulo": "Taller de límites",
  "descripcion": "Ejercicios 1 al 10",
  "fecha_entrega": "2026-11-04T04:59:00Z",
  "completada": false,
  "plazo": "urgente",
  "materia": { "id": 1, "nombre": "Cálculo II", "color": "#1D4ED8" }
}
```

`plazo` toma uno de los valores `vencida`, `urgente` o `ninguno`, calculado en cada consulta
(FR-009, FR-010, FR-012, FR-020). `descripcion` es `null` si no se indicó.

### `GET /api/tareas`

Lista las tareas ordenadas por `fecha_entrega` ascendente (empate por `id`) (FR-007).

Parámetros de consulta opcionales, combinables (FR-013):

| Parámetro | Valores | Efecto |
|-----------|---------|--------|
| `materia_id` | entero | Solo tareas de esa materia |
| `estado` | `pendiente` \| `completada` | Solo tareas en ese estado |

Respuestas: `200` con la lista (vacía si nada coincide), `422` si `estado` no es válido o
`materia_id` no es un entero. Un `materia_id` inexistente devuelve lista vacía con `200`.

### `POST /api/tareas`

Crea una tarea.

Cuerpo:

```json
{
  "titulo": "Taller de límites",
  "descripcion": "Ejercicios 1 al 10",
  "fecha_entrega": "2026-11-03T23:59:00-05:00",
  "materia_id": 1
}
```

`descripcion` es opcional. Se permiten fechas pasadas.

| Resultado | Condición |
|-----------|-----------|
| `201` con la tarea creada | Datos válidos |
| `422` | `titulo` vacío/solo espacios/más de 100 caracteres; `descripcion` de más de 500; `fecha_entrega` ausente, inválida o sin zona horaria; `materia_id` ausente o que no existe |

### `PUT /api/tareas/{id}`

Edita título, descripción, fecha y materia. Mismo cuerpo y validaciones que `POST`. No cambia
el estado `completada`.

Respuestas: `200` con la tarea actualizada, `404`, `422`.

### `PATCH /api/tareas/{id}/completada`

Marca o desmarca la tarea (FR-011).

Cuerpo:

```json
{ "completada": true }
```

Respuestas: `200` con la tarea actualizada (con `plazo` recalculado), `404`, `422` si
`completada` no es booleano.

### `DELETE /api/tareas/{id}`

Elimina una tarea.

Respuestas: `204`, `404`.

## Trazabilidad con la especificación

| Requisito | Dónde se cubre |
|-----------|----------------|
| FR-001, FR-002, FR-003 | `/api/materias` (POST, PUT, GET, DELETE) |
| FR-004, FR-005, FR-006 | `/api/tareas` (POST, PUT, DELETE) |
| FR-007, FR-013 | `GET /api/tareas` y sus parámetros |
| FR-008, FR-009, FR-010, FR-012, FR-020 | Objeto tarea: `materia`, `plazo` calculado |
| FR-011 | `PATCH /api/tareas/{id}/completada` |
| FR-016 | `DELETE /api/materias/{id}` y `total_tareas` |
| FR-014, FR-015 | Persistencia SQLite; sin autenticación |
| FR-017, FR-018, FR-019 | Interfaz (`app/estatico/`) y mensajes de error en español |
