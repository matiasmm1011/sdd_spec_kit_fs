---
name: equipo-tareas
description: Reparto de tareas del equipo (3 integrantes) según asignaciones.md. Muestra la lista de tareas de cada integrante, implementa las tuyas una por una, hace commit y push al terminar cada una, y si una tarea tuya depende de otra de un compañero espera con git fetch hasta que se suba y continúa sola. Úsala cuando el usuario escriba /equipo-tareas o pida seguir con sus tareas del equipo.
disable-model-invocation: true
argument-hint: "[nombre del integrante, opcional]"
---

# Tareas del equipo

Coordina el trabajo de tres personas sobre `specs/001-organizador-tareas/tasks.md` usando
[asignaciones.md](../../../asignaciones.md) (quién hace qué) y un script que sabe qué tareas están
hechas, listas o bloqueadas. El usuario pidió explícitamente que cada tarea terminada se suba con
`git push`, así que no hace falta confirmar cada push.

Todo se hace con un solo script (PowerShell), desde la raíz del repositorio:

```powershell
.\.claude\skills\equipo-tareas\scripts\equipo.ps1 -Accion <listar|siguiente|esperar|subir> [opciones]
```

Si el usuario pasó un nombre como argumento (`$ARGUMENTS`), añade `-Persona "<nombre>"` en todas las
llamadas. Si no, el script deduce quién eres con `git config user.name` y `user.email`
(ver `equipo.json` > `alias`). Si no logra identificarte, pregunta al usuario su nombre.

## Flujo

### 1. Preparar y mostrar la lista

1. Comprueba que estás en `main` y sin cambios sin guardar (`git status -sb`). Si hay cambios
   ajenos a este flujo, pregunta al usuario antes de seguir.
2. Ejecuta `git fetch origin` y `git pull --rebase origin main` para tener lo último
   (incluido `asignaciones.md` y las marcas `[X]` de los compañeros).
3. Ejecuta `-Accion listar` y muestra al usuario un resumen: cuántas tareas hizo cada integrante
   y la lista de **sus** tareas con su estado (`[x]` hecha, `[>]` lista, `[ ]` bloqueada y por qué).

### 2. Bucle de trabajo

Repite hasta que no queden tareas tuyas:

1. Ejecuta `-Accion siguiente`. Según la primera palabra de la salida:
   - **`LISTA Txxx`**: implementa esa tarea (paso 3).
   - **`BLOQUEADA`**: ninguna tarea tuya se puede hacer todavía. Ve al paso 4 (esperar).
   - **`TERMINADO`**: ve al paso 5.
2. (Solo si hay varias tareas listas, el script devuelve la primera de tu lista. Eso permite
   adelantar trabajo que no depende de nadie, por ejemplo el CSS, mientras el backend se termina.)

### 3. Implementar la tarea

1. Lee la descripción de la tarea en `asignaciones.md` y en `specs/001-organizador-tareas/tasks.md`,
   y los documentos que necesites (`plan.md`, `data-model.md`, `contracts/api.md`,
   `.specify/memory/constitution.md`).
2. Implementa **solo lo que pide esa tarea**, siguiendo la constitución del proyecto (simplicidad,
   pruebas, código legible, validación de entradas, accesibilidad). Todo el texto en español.
3. Respeta la capa de cada integrante (tabla "Criterio de reparto" de `asignaciones.md`):
   Alejandro solo `tests/`, Sebastian solo `app/*.py` y `README.md`, Matias solo `app/estatico/`.
   Si la tarea obliga a tocar un archivo de otra capa, **detente y pregunta al usuario**: debe
   coordinarlo con su compañero. No uses `-PermitirOtrasCapas` sin que el usuario lo autorice.
4. Verifica antes de subir:
   - Ejecuta las pruebas con el entorno virtual: `.\.venv\Scripts\python.exe -m pytest -q`
     (o `pytest` si el entorno está activo).
   - No debes romper pruebas que ya pasaban. Las pruebas nuevas de historias cuyo código aún no
     existe pueden fallar: es lo esperado cuando se escriben primero (Principio II). En ese caso
     las tareas de pruebas (Alejandro) se suben con sus pruebas fallando, y las demás tareas deben
     dejar en verde las pruebas de su historia.
   - Para cambios de interfaz, comprueba además que se ven bien a 360 px y en escritorio.
5. Sube la tarea:

   ```powershell
   .\.claude\skills\equipo-tareas\scripts\equipo.ps1 -Accion subir -Tarea Txxx -Coautor "<línea de coautoría>"
   ```

   El script marca `[X]` en `tasks.md`, hace un commit con el ID de la tarea, ejecuta
   `git pull --rebase origin main` y `git push origin main` (reintenta si el push es rechazado).
   En `-Coautor` pasa la línea de coautoría que te corresponda como agente. Las tareas que no
   cambian código (por ejemplo "ejecutar pytest" o "revisar la seguridad") también se cierran con
   `subir`: describe antes al usuario el resultado o los hallazgos.
   - Código de salida **20**: conflicto en el rebase. Abre los archivos en conflicto, resuélvelos
     conservando el trabajo de ambos (en `tasks.md`, ambas marcas `[X]`), `git add`,
     `git rebase --continue` y `git push origin main`.
   - Código de salida **21**: hay cambios fuera de tu capa. Revisa `git status`; no los incluyas
     si no son de esta tarea.
6. Vuelve al paso 1 del bucle.

### 4. Esperar a que se desbloquee una tarea

Cuando el estado sea `BLOQUEADA`, lanza la espera **en segundo plano** y no hagas sondeos
manuales ni dormidas:

```powershell
.\.claude\skills\equipo-tareas\scripts\equipo.ps1 -Accion esperar
```

(Con la herramienta de PowerShell usa `run_in_background: true`; avisará al terminar.)
Dile al usuario qué tareas de qué compañero faltan y que quedas a la espera. El script hace
`git fetch` cada 60 segundos (`equipo.json` > `intervalo_segundos`) hasta que alguna tarea tuya
pase a estar lista y, si no tienes cambios locales, descarga lo nuevo con `git pull --rebase`.
Al terminar:

- **`DESBLOQUEADA Txxx`**: vuelve al paso 1 del bucle (si el script avisó de cambios locales
  sin subir, haz primero `git pull --rebase origin main`).
- **`TERMINADO`**: ve al paso 5.
- **`TIEMPO AGOTADO`** (código 12, tras `max_minutos_espera`): informa al usuario y pregúntale si
  quiere seguir esperando.

### 5. Cierre

Cuando `siguiente` diga `TERMINADO`, muestra con `-Accion listar` el estado final del equipo y
resume al usuario lo que hiciste (tareas, commits y archivos). No modifiques `asignaciones.md`
ni marques tareas de otros integrantes.

## Reglas y límites

- **Una tarea a la vez**: implementa, verifica, sube, y recién entonces pasa a la siguiente.
- **Solo tus tareas**: si el usuario pide algo distinto, atiéndelo y retoma el flujo después.
- **Nunca** uses `git push --force`, `git reset --hard` ni borres ramas o archivos de compañeros.
- Si algo es ambiguo (una tarea poco clara, una dependencia que parece incorrecta), pregunta al
  usuario antes de suponer.
- Las dependencias salen de los textos "(después de Txxx)" de `asignaciones.md` y de
  `dependencias` en `equipo.json`. Si el orden de trabajo del equipo cambia, edita ese archivo.

## Archivos de esta skill

- `scripts/equipo.ps1`: acciones `listar`, `siguiente`, `esperar` y `subir`.
- `equipo.json`: alias de git de cada integrante, capas que le pertenecen, dependencias entre
  tareas, intervalo y tiempo máximo de espera, y rama de trabajo (`main`).
