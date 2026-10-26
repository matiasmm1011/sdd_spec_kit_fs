# Especificación de Funcionalidad: Organizador de Tareas Académicas

**Rama de la funcionalidad**: `001-organizador-tareas`

**Creado**: 2026-10-26

**Estado**: Borrador

**Entrada**: Descripción del usuario: "Quiero una aplicación para estudiantes de la UPB que les ayude a organizar sus tareas académicas. El estudiante puede registrar sus materias (nombre y color). Puede crear tareas asociadas a una materia, con título, descripción opcional y fecha de entrega. Ve un listado de tareas ordenado por fecha de entrega, donde las tareas vencidas se destacan y las próximas 48 horas aparecen como "urgentes". Puede marcar tareas como completadas y filtrarlas por materia o por estado. En esta primera versión no hay inicio de sesión: es un solo usuario por dispositivo."

## Aclaraciones

### Sesión 2026-10-26

- Q: Cuando el estudiante elimina una materia que ya tiene tareas, ¿qué debe pasar con esas tareas? → A: Se eliminan también sus tareas, tras una confirmación que indica cuántas son.
- Q: ¿Cuál es la longitud máxima permitida para el nombre de la materia, el título de la tarea y la descripción de la tarea? → A: Nombre de materia: 50 caracteres; título de tarea: 100; descripción: 500.
- Q: ¿Cómo se calcula que una tarea es "urgente": con una ventana móvil de 48 horas exactas contadas desde el momento actual, o por días de calendario? → A: Ventana móvil: urgente si faltan 48 horas o menos desde el momento actual y la tarea aún no ha vencido.

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Registrar materias y crear tareas (Prioridad: P1)

El estudiante registra las materias que cursa, indicando un nombre y un color para cada una. Luego crea tareas asociadas a una de esas materias, con un título, una descripción opcional y una fecha de entrega.

**Por qué esta prioridad**: Sin materias y tareas no existe nada que organizar. Es la base de la aplicación y, por sí sola, ya permite al estudiante dejar registradas sus obligaciones académicas.

**Prueba independiente**: Se puede probar registrando una materia ("Cálculo II", azul) y creando una tarea en ella; la tarea debe aparecer guardada y asociada a esa materia, incluso después de cerrar y volver a abrir la aplicación.

**Escenarios de aceptación**:

1. **Dado** que el estudiante no tiene materias, **cuando** registra una materia con nombre y color, **entonces** la materia aparece en su lista de materias con ese color.
2. **Dado** que existe al menos una materia, **cuando** el estudiante crea una tarea con título, fecha de entrega y materia, **entonces** la tarea queda guardada y asociada a esa materia.
3. **Dado** que el estudiante crea una tarea sin descripción, **cuando** la guarda, **entonces** la tarea se crea correctamente porque la descripción es opcional.
4. **Dado** que el estudiante intenta crear una tarea sin título, sin fecha de entrega o sin materia, **cuando** intenta guardarla, **entonces** el sistema la rechaza y muestra un mensaje claro indicando qué falta.
5. **Dado** que el estudiante intenta registrar una materia sin nombre, **cuando** intenta guardarla, **entonces** el sistema la rechaza y muestra un mensaje claro.

---

### Historia de Usuario 2 - Ver el listado de tareas con vencidas y urgentes destacadas (Prioridad: P2)

El estudiante ve todas sus tareas en un único listado ordenado por fecha de entrega, de la más próxima a la más lejana. Las tareas cuya fecha de entrega ya pasó se destacan como vencidas, y las que vencen dentro de las próximas 48 horas se marcan como "urgentes".

**Por qué esta prioridad**: Es el valor central de la aplicación: saber de un vistazo qué hay que entregar y qué es prioritario. Depende de que ya existan tareas (Historia 1).

**Prueba independiente**: Se puede probar creando tres tareas (una con fecha pasada, una dentro de 24 horas y una dentro de 10 días) y verificando el orden del listado y las marcas visuales de cada una.

**Escenarios de aceptación**:

1. **Dado** que existen varias tareas pendientes, **cuando** el estudiante abre el listado, **entonces** las tareas aparecen ordenadas por fecha de entrega ascendente.
2. **Dado** que una tarea pendiente tiene fecha de entrega anterior al momento actual, **cuando** el estudiante ve el listado, **entonces** la tarea se muestra destacada como "vencida".
3. **Dado** que una tarea pendiente vence dentro de las próximas 48 horas, **cuando** el estudiante ve el listado, **entonces** la tarea se muestra con la etiqueta "urgente".
4. **Dado** que una tarea pendiente vence en más de 48 horas, **cuando** el estudiante ve el listado, **entonces** la tarea se muestra sin marca de vencida ni de urgente.
5. **Dado** que cada tarea pertenece a una materia, **cuando** el estudiante ve el listado, **entonces** cada tarea muestra el nombre y el color de su materia.

---

### Historia de Usuario 3 - Marcar tareas como completadas (Prioridad: P3)

El estudiante marca una tarea como completada cuando la termina, y puede revertirla a pendiente si se equivocó.

**Por qué esta prioridad**: Permite llevar el progreso y evita que tareas ya entregadas sigan apareciendo como urgentes o vencidas. Es útil, pero la aplicación ya aporta valor sin ella.

**Prueba independiente**: Se puede probar marcando como completada una tarea vencida y comprobando que deja de destacarse como vencida o urgente.

**Escenarios de aceptación**:

1. **Dado** que existe una tarea pendiente, **cuando** el estudiante la marca como completada, **entonces** la tarea pasa a estado "completada" y se distingue visualmente de las pendientes.
2. **Dado** que una tarea vencida o urgente se marca como completada, **cuando** el estudiante ve el listado, **entonces** ya no se muestra como vencida ni como urgente.
3. **Dado** que una tarea está completada, **cuando** el estudiante la desmarca, **entonces** vuelve a estado "pendiente" y recupera sus marcas de vencida o urgente si corresponden.

---

### Historia de Usuario 4 - Filtrar tareas por materia o por estado (Prioridad: P4)

El estudiante filtra el listado para ver solo las tareas de una materia, o solo las pendientes o solo las completadas. Los filtros pueden combinarse.

**Por qué esta prioridad**: Mejora la comodidad cuando hay muchas tareas, pero el listado completo ya cubre la necesidad principal.

**Prueba independiente**: Se puede probar con tareas de dos materias y distintos estados, aplicando cada filtro por separado y combinados, y verificando que el listado muestra solo lo esperado.

**Escenarios de aceptación**:

1. **Dado** que existen tareas de varias materias, **cuando** el estudiante filtra por una materia, **entonces** solo se muestran las tareas de esa materia, en orden por fecha de entrega.
2. **Dado** que existen tareas pendientes y completadas, **cuando** el estudiante filtra por estado "pendientes" o "completadas", **entonces** solo se muestran las tareas de ese estado.
3. **Dado** que el estudiante aplica filtro de materia y de estado a la vez, **cuando** ve el listado, **entonces** solo se muestran las tareas que cumplen ambos criterios.
4. **Dado** que ninguna tarea cumple los filtros aplicados, **cuando** el estudiante ve el listado, **entonces** se muestra un mensaje indicando que no hay tareas con esos criterios.
5. **Dado** que hay filtros aplicados, **cuando** el estudiante los quita, **entonces** se vuelve a mostrar el listado completo.

---

### Casos Límite

- ¿Qué ocurre cuando el estudiante aún no tiene materias y quiere crear una tarea? El sistema debe indicarle que primero registre una materia.
- ¿Qué ocurre cuando no hay ninguna tarea? El listado muestra un mensaje de estado vacío que invita a crear la primera tarea.
- ¿Qué ocurre si el estudiante crea una tarea con una fecha de entrega ya pasada? Se permite (por ejemplo, para registrar un atraso) y la tarea se muestra de inmediato como vencida.
- ¿Qué ocurre cuando una tarea vence exactamente a las 48 horas del momento actual? Se considera urgente (el límite de 48 horas es inclusivo). Una tarea cuya hora de entrega es exactamente el momento actual se considera vencida.
- ¿Qué ocurre con una tarea que pasa de "urgente" a "vencida" mientras la aplicación está abierta? Su marca se actualiza sin que el estudiante tenga que recargar manualmente.
- ¿Qué ocurre si el estudiante registra dos materias con el mismo nombre? El sistema lo rechaza con un mensaje claro, ignorando diferencias de mayúsculas y minúsculas.
- ¿Qué ocurre si el estudiante intenta eliminar una materia que tiene tareas? El sistema le advierte y solicita confirmación indicando cuántas tareas se eliminarán junto con la materia; si cancela, no se elimina nada.
- ¿Qué ocurre con entradas que superan los límites (nombre de materia: 50 caracteres; título: 100; descripción: 500) o con solo espacios en blanco en el título o el nombre? Se rechazan con un mensaje claro de validación que indica el límite; el texto ya escrito no se pierde.
- ¿Qué ocurre si el estudiante usa la aplicación en un celular? Todas las funciones deben ser utilizables en pantallas pequeñas.

## Requisitos *(obligatorio)*

### Requisitos Funcionales

- **FR-001**: El sistema DEBE permitir al estudiante registrar una materia indicando un nombre y un color.
- **FR-002**: El sistema DEBE rechazar materias sin nombre, con nombre compuesto solo por espacios, con nombre de más de 50 caracteres, o con un nombre ya existente (sin distinguir mayúsculas de minúsculas), mostrando un mensaje claro.
- **FR-003**: El sistema DEBE permitir al estudiante ver, editar y eliminar sus materias.
- **FR-004**: El sistema DEBE permitir crear una tarea asociada a una materia existente, con título obligatorio, descripción opcional y fecha y hora de entrega obligatorias.
- **FR-005**: El sistema DEBE validar los datos de cada tarea antes de guardarla (título no vacío y de máximo 100 caracteres, descripción de máximo 500 caracteres, fecha válida, materia existente) y mostrar un mensaje claro por cada dato inválido.
- **FR-006**: El sistema DEBE permitir al estudiante editar y eliminar sus tareas.
- **FR-007**: El sistema DEBE mostrar un listado de tareas ordenado por fecha de entrega ascendente.
- **FR-008**: El sistema DEBE mostrar, en cada tarea del listado, su título, fecha de entrega, estado y el nombre y color de su materia.
- **FR-009**: El sistema DEBE destacar visualmente como "vencida" toda tarea pendiente cuya fecha y hora de entrega sea igual o anterior al momento actual.
- **FR-010**: El sistema DEBE marcar como "urgente" toda tarea pendiente que cumpla ambas condiciones: (a) la fecha y hora de entrega es posterior al momento actual y (b) faltan 48 horas o menos para ella, contadas como ventana móvil desde el momento actual (no por días de calendario). Una tarea nunca es a la vez "vencida" y "urgente".
- **FR-011**: El sistema DEBE permitir marcar una tarea como completada y revertirla a pendiente.
- **FR-012**: El sistema NO DEBE mostrar como vencida ni como urgente a una tarea completada.
- **FR-013**: El sistema DEBE permitir filtrar el listado por materia y por estado (pendiente o completada), de forma individual o combinada, y permitir quitar los filtros.
- **FR-014**: El sistema DEBE conservar las materias, tareas y su estado entre sesiones de uso en el mismo dispositivo.
- **FR-015**: El sistema DEBE funcionar sin inicio de sesión, tratando los datos como pertenecientes a un único usuario por dispositivo.
- **FR-016**: Al eliminar una materia con tareas, el sistema DEBE pedir confirmación indicando cuántas tareas se eliminarán junto con la materia y, si se confirma, eliminar la materia y todas sus tareas (pendientes y completadas). Si el estudiante cancela, no se elimina nada. Una materia sin tareas se elimina sin necesidad de ese aviso.
- **FR-017**: El sistema DEBE mostrar un estado vacío orientativo cuando no haya materias, tareas o resultados de filtrado.
- **FR-018**: La interfaz DEBE ser utilizable tanto en celular como en computadora, con elementos accesibles (etiquetas asociadas a los campos, contraste suficiente y uso por teclado).
- **FR-019**: Todos los textos de la interfaz y los mensajes de error DEBEN estar en español.
- **FR-020**: El estado "vencida" o "urgente" de las tareas DEBE reflejar la hora actual cada vez que se muestra el listado, sin depender de un valor guardado.

### Entidades Clave *(incluir si la funcionalidad involucra datos)*

- **Materia**: Asignatura que cursa el estudiante. Atributos: nombre (único) y color. Una materia tiene cero o muchas tareas.
- **Tarea**: Obligación académica del estudiante. Atributos: título, descripción (opcional), fecha y hora de entrega, estado (pendiente o completada) y la materia a la que pertenece. Cada tarea pertenece a exactamente una materia.

## Criterios de Éxito *(obligatorio)*

### Resultados Medibles

- **SC-001**: Un estudiante nuevo puede registrar una materia y crear su primera tarea en menos de 2 minutos, sin instrucciones previas.
- **SC-002**: Un estudiante identifica en menos de 5 segundos cuáles tareas están vencidas y cuáles son urgentes al abrir el listado.
- **SC-003**: Al menos el 90 % de los estudiantes de una prueba de usabilidad completa las acciones principales (crear tarea, completarla y filtrar por materia) en el primer intento.
- **SC-004**: El 100 % de las tareas del listado aparece en el orden correcto de fecha de entrega y con la marca correcta (vencida, urgente o ninguna) en las pruebas de aceptación.
- **SC-005**: Marcar una tarea como completada, o aplicar un filtro, se refleja en el listado en menos de 1 segundo desde la perspectiva del estudiante.
- **SC-006**: Los datos registrados se conservan en el 100 % de los casos al cerrar y volver a abrir la aplicación en el mismo dispositivo.
- **SC-007**: Todas las funciones principales se pueden completar sin desplazamiento horizontal ni elementos ilegibles tanto en una pantalla de celular (ancho de 360 px) como en una de computadora.

## Supuestos

- Los usuarios son estudiantes de la UPB que usan la aplicación de forma personal; no hay colaboración ni datos compartidos entre estudiantes.
- La primera versión no incluye inicio de sesión ni sincronización entre dispositivos: los datos viven únicamente en el dispositivo donde se usan, y cambiar de dispositivo implica empezar con datos vacíos.
- La fecha de entrega incluye día y hora, necesarios para calcular la ventana de 48 horas; si el estudiante no indica hora, se asume el final del día seleccionado (23:59).
- La zona horaria de referencia es la del dispositivo del estudiante.
- El color de una materia se elige de una paleta predefinida de colores; no se requiere un selector de color libre.
- No se incluyen en esta versión: recordatorios o notificaciones, tareas recurrentes, adjuntos, subtareas, prioridades manuales ni calendario.
- Se asume un volumen personal de uso (decenas de materias y cientos de tareas como máximo), sin requisitos especiales de rendimiento.
- La aplicación se rige por la constitución del proyecto: simplicidad, pruebas automatizadas, validación de entradas y diseño accesible y responsivo.
