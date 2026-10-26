# Guía Rápida de Validación: Organizador de Tareas Académicas

Guía para instalar, ejecutar y comprobar de punta a punta que la funcionalidad cumple la
[especificación](spec.md). No contiene código de implementación: los detalles están en el
[contrato de la API](contracts/api.md) y en el [modelo de datos](data-model.md).

## Requisitos previos

- Python 3.12 instalado (`py -3.12 --version` en Windows, `python3.12 --version` en macOS/Linux).
- Un navegador moderno (para la interfaz y para las pruebas de navegador).

## Preparación

Desde la raíz del repositorio:

```bash
py -3.12 -m venv .venv
```

Activar el entorno virtual (Windows PowerShell: `.venv\Scripts\Activate.ps1`; macOS/Linux:
`source .venv/bin/activate`) e instalar dependencias:

```bash
pip install -r requirements-dev.txt
```

Instalar el navegador que usan las pruebas de interfaz (una sola vez):

```bash
playwright install chromium
```

## Ejecutar la aplicación

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000`. Los datos se guardan en `datos/tareas.db` (o en la ruta de la
variable de entorno `RUTA_DB`). Se conservan al detener y volver a iniciar el servidor.

## Ejecutar las pruebas automatizadas

Un único comando ejecuta todo (Principio II de la constitución):

```bash
pytest
```

Para una ejecución rápida sin navegador:

```bash
pytest tests/unit tests/integration
```

**Resultado esperado**: todas las pruebas pasan. Las pruebas de interfaz (`tests/e2e`) fallan si
no se instaló antes el navegador con `playwright install chromium`.

## Escenarios de validación manual

Cada escenario indica el resultado esperado y el requisito que comprueba.

### 1. Materias y tareas (Historia 1: FR-001 a FR-006)

1. Con la base vacía, abrir la aplicación: se ve un mensaje que invita a registrar una materia (FR-017).
2. Intentar crear una tarea sin materias: la interfaz indica que primero hay que registrar una materia.
3. Registrar la materia "Cálculo II" con color Azul: aparece en la lista con ese color.
4. Registrar de nuevo "CÁLCULO ii": se rechaza con un mensaje claro de nombre repetido (FR-002).
5. Intentar guardar una materia con nombre vacío, solo espacios o de 51 caracteres: se rechaza indicando el límite.
6. Crear una tarea con título, fecha y hora (la hora viene precargada en 23:59), sin descripción: se crea correctamente.
7. Intentar crear una tarea con título de 101 caracteres o descripción de 501: se rechaza y el texto escrito no se pierde.

### 2. Listado, vencidas y urgentes (Historia 2: FR-007 a FR-010, FR-020)

1. Crear tres tareas: una con fecha de ayer, una dentro de 24 horas y una dentro de 10 días.
2. El listado las muestra en ese orden (ascendente por fecha), cada una con el nombre y color de su materia.
3. La primera aparece destacada como "vencida"; la segunda con la etiqueta "urgente"; la tercera sin marca.
4. Crear una tarea que venza dentro de exactamente 48 horas: aparece como "urgente".
5. Crear una tarea que venza dentro de 48 horas y 1 minuto: no aparece como urgente. Tras esperar ese minuto (el listado se refresca solo cada 60 s), pasa a "urgente" sin recargar la página.

### 3. Completar tareas (Historia 3: FR-011, FR-012)

1. Marcar como completada la tarea vencida: se distingue visualmente y ya no se muestra como vencida.
2. Desmarcarla: vuelve a pendiente y recupera la marca de vencida.

### 4. Filtros (Historia 4: FR-013, FR-017)

1. Con tareas de dos materias y estados mixtos, filtrar por una materia: solo se ven las de esa materia.
2. Filtrar por estado "pendientes" y luego "completadas": se ven solo las de cada estado.
3. Combinar materia y estado: se ven solo las que cumplen ambos.
4. Aplicar una combinación sin resultados: aparece un mensaje de que no hay tareas con esos criterios.
5. Quitar los filtros: vuelve el listado completo.

### 5. Borrado de una materia (FR-016)

1. Eliminar una materia con 3 tareas: aparece una confirmación que dice que se eliminarán 3 tareas.
2. Cancelar: no se elimina nada.
3. Repetir y confirmar: desaparecen la materia y sus 3 tareas (pendientes y completadas).
4. Eliminar una materia sin tareas: se elimina sin el aviso de tareas.

### 6. Responsivo y accesible (FR-018, SC-007)

1. Abrir la aplicación con el navegador a 360 px de ancho (modo dispositivo móvil): no hay desplazamiento horizontal y todas las acciones son alcanzables.
2. Repetir en una ventana de escritorio.
3. Recorrer formularios y botones usando solo el teclado (Tab, Enter, Espacio): todo es operable y el foco siempre es visible.
4. Verificar que cada campo de formulario tiene una etiqueta visible asociada.

### 7. Persistencia (FR-014, SC-006)

1. Detener el servidor (Ctrl+C) y volver a iniciarlo: materias, tareas y estados siguen ahí.
