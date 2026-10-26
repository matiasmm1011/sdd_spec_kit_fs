# Lista de Verificación de Experiencia de Usuario y Validación de Datos: Organizador de Tareas Académicas

**Propósito**: Validar la calidad (completitud, claridad, consistencia y medibilidad) de los requisitos de experiencia de usuario y de validación de datos antes de generar las tareas de implementación
**Creado**: 2026-10-26
**Funcionalidad**: [spec.md](../spec.md) (con apoyo de [plan.md](../plan.md), [data-model.md](../data-model.md) y [contracts/api.md](../contracts/api.md))

**Nota**: Esta lista personalizada la genera el comando `/speckit-checklist` a partir del contexto y los requisitos de la funcionalidad.
**Propiedad de la revisión**: Esta lista es un artefacto de revisión de calidad de requisitos a cargo de quien revisa. Marque un elemento con `[x]` solo cuando determine que el criterio de calidad del requisito se cumple.
**Significado de las marcas**: `[x]` indica que el criterio fue revisado y cumple con la calidad de requisitos. No significa que el trabajo de implementación esté terminado.

**Profundidad**: estándar (revisión previa a `/speckit-tasks`). **Audiencia**: autor y revisor de la especificación.

## Claridad de las Reglas de Validación

- [ ] CHK001 ¿Está definido qué significa "mensaje claro" (contenido mínimo: qué campo falló, por qué y cómo corregirlo) en las validaciones de materias y tareas? [Clarity, Spec §FR-002, §FR-005]
- [ ] CHK002 ¿Se especifica si el límite de "caracteres" (50/100/500) cuenta caracteres visibles, puntos de código o bytes, incluidos acentos, "ñ" y emojis? [Ambiguity, Spec §Aclaraciones]
- [ ] CHK003 ¿Se define si los espacios al inicio y al final se descartan antes de contar la longitud y antes de guardar? [Gap, Spec §FR-002, §FR-005]
- [ ] CHK004 ¿Se define el tratamiento de los espacios y saltos de línea internos (por ejemplo, varios espacios seguidos o saltos de línea en el título y en la descripción)? [Gap, Spec §FR-005]
- [ ] CHK005 ¿Se indica si una descripción compuesta solo por espacios se considera "ausente" o inválida? [Gap, Spec §FR-004]
- [ ] CHK006 ¿Se exige que los mensajes de longitud indiquen el límite numérico en todos los campos, y no solo en el caso límite de entradas largas? [Consistency, Spec §FR-002, §FR-005, §Casos Límite]
- [ ] CHK007 ¿Está definida en la especificación (y no solo en el plan) la paleta de colores permitida y el comportamiento si se recibe un color fuera de ella? [Gap, Spec §Supuestos, §FR-001]
- [ ] CHK008 ¿Está definido el criterio de "nombre ya existente" (qué diferencias se ignoran: mayúsculas, acentos, espacios) con suficiente precisión para escribir pruebas? [Clarity, Spec §FR-002]
- [ ] CHK009 ¿Se especifica si se permiten tareas con el mismo título (en la misma materia o en distintas)? [Gap, Spec §FR-004]
- [ ] CHK010 ¿Se definen requisitos para texto con caracteres especiales o marcado (por ejemplo `<`, `>`, comillas) en nombres, títulos y descripciones? [Gap, Principio IV de la constitución]

## Validación de Fechas y Horas

- [ ] CHK011 ¿Se define qué es una "fecha válida" (formato aceptado, fechas inexistentes como 31 de febrero, límites mínimo y máximo razonables)? [Ambiguity, Spec §FR-005]
- [ ] CHK012 ¿Son consistentes el requisito de "fecha y hora obligatorias" y el supuesto de que, sin hora, se usa 23:59? [Conflict, Spec §FR-004, §Supuestos]
- [ ] CHK013 ¿Se especifica con qué zona horaria se interpretan y se muestran las fechas cuando el dispositivo cambia de zona o de horario de verano? [Gap, Spec §Supuestos]
- [ ] CHK014 ¿Se aclara si las fechas pasadas se aceptan también al editar una tarea y no solo al crearla? [Coverage, Spec §Casos Límite, §FR-006]
- [ ] CHK015 ¿Se define el formato de presentación de la fecha de entrega (orden día/mes/año, 12 o 24 horas, nombre de mes) y si se muestra tiempo restante en las tareas urgentes? [Gap, Spec §FR-008]
- [ ] CHK016 ¿Están cuantificados los límites del cálculo de "vencida" y "urgente" (igualdad exacta con el momento actual y con las 48 horas) de forma que no se contradigan? [Consistency, Spec §FR-009, §FR-010]

## Completitud de los Requisitos de Edición y Borrado

- [ ] CHK017 ¿Se aplican explícitamente las mismas reglas de validación al editar materias y tareas que al crearlas? [Coverage, Spec §FR-003, §FR-006]
- [ ] CHK018 ¿Se aclara que la unicidad del nombre de materia al editar ignora a la propia materia que se edita? [Gap, Spec §FR-002, §FR-003]
- [ ] CHK019 ¿Están definidos los requisitos de cambiar la materia de una tarea existente y de editar el color de una materia (y su efecto en las tareas ya listadas)? [Gap, Spec §FR-003, §FR-006]
- [ ] CHK020 ¿Se especifica si eliminar una tarea individual exige confirmación o permite deshacer, de forma consistente con la confirmación al eliminar una materia? [Consistency, Spec §FR-006, §FR-016]
- [ ] CHK021 ¿Se define si se puede editar una tarea ya completada? [Gap, Spec §FR-006, §FR-011]

## Calidad de los Requisitos de Experiencia de Usuario

- [ ] CHK022 ¿Está cuantificado "destacar" en una tarea vencida y la etiqueta "urgente" (propiedades visuales mínimas) de modo que se puedan verificar de forma objetiva? [Measurability, Spec §FR-009, §FR-010]
- [ ] CHK023 ¿Se exige que vencida, urgente y completada se distingan por algo más que el color (texto, icono o forma)? [Gap, Spec §FR-018]
- [ ] CHK024 ¿Se define dónde se ubican las tareas completadas en el listado (mezcladas por fecha, al final o con filtro por defecto) y cuál es el estado inicial de los filtros? [Ambiguity, Spec §FR-007, §FR-013]
- [ ] CHK025 ¿Se especifica el orden de desempate cuando dos tareas tienen la misma fecha y hora de entrega? [Gap, Spec §FR-007]
- [ ] CHK026 ¿Se define si los filtros aplicados se conservan al recargar o al reabrir la aplicación? [Gap, Spec §FR-013]
- [ ] CHK027 ¿Se define cuándo se muestran los mensajes de validación (al enviar o mientras se escribe), cómo se indican los campos obligatorios y que el texto ya escrito se conserva en todos los casos de rechazo, no solo en el de longitud? [Consistency, Spec §FR-005, §Casos Límite]
- [ ] CHK028 ¿Hay requisitos para los estados de carga y de error cuando no se puede leer o guardar la información (por ejemplo, falla al guardar), incluido cómo se recupera el estudiante? [Gap, Exception Flow]
- [ ] CHK029 ¿Están alineados los tres estados vacíos (sin materias, sin tareas, sin resultados de filtro) con una acción sugerida concreta para cada uno? [Completeness, Spec §FR-017]
- [ ] CHK030 ¿Se cuantifica el plazo máximo para que una marca de "urgente" pase a "vencida" sin recargar manualmente? [Measurability, Spec §Casos Límite, §FR-020]
- [ ] CHK031 ¿Se mantiene un vocabulario consistente para los estados y las marcas ("pendiente", "completada", "vencida", "urgente") en historias, requisitos y mensajes? [Consistency, Spec §FR-009 a §FR-013]

## Accesibilidad y Diseño Responsivo

- [ ] CHK032 ¿Están definidos los anchos de pantalla soportados (mínimo y puntos de cambio de diseño), más allá del ancho de 360 px mencionado, y qué significa "elementos ilegibles"? [Ambiguity, Spec §SC-007, §FR-018]
- [ ] CHK033 ¿Se especifican requisitos de tamaño mínimo de las áreas táctiles para el uso en celular? [Gap, Spec §FR-018]
- [ ] CHK034 ¿Se define el comportamiento del foco y la navegación con teclado en la confirmación de borrado y en los mensajes de error? [Gap, Spec §FR-016, §FR-018]
- [ ] CHK035 ¿Se exige que los mensajes de error y los cambios dinámicos del listado sean comunicados a tecnologías de apoyo (por ejemplo, lectores de pantalla)? [Gap, Spec §FR-018]
- [ ] CHK036 ¿Es verificable "contraste suficiente" porque se indica la relación mínima exigida? [Measurability, Spec §FR-018]
- [ ] CHK037 ¿Se exige que la información de color de una materia tenga también una representación en texto y no dependa solo del color? [Gap, Spec §FR-001, §FR-008]

## Calidad de los Criterios de Aceptación y Supuestos

- [ ] CHK038 ¿Es medible SC-003 (90 % en el primer intento) porque define tamaño de muestra, perfil de participantes y qué cuenta como "primer intento"? [Measurability, Spec §SC-003]
- [ ] CHK039 ¿Existe un criterio de éxito o de aceptación para la validación de datos (por ejemplo, ninguna entrada inválida se guarda), y no solo para tiempos y usabilidad? [Gap, Spec §Criterios de Éxito]
- [ ] CHK040 ¿Está definido qué ocurre cuando se superan los volúmenes supuestos (decenas de materias, cientos de tareas), o se aclara que no hay límite impuesto? [Assumption, Spec §Supuestos]

## Notas

- Marque los elementos con `[x]` solo después de que la revisión confirme que se cumple el criterio de calidad del requisito
- Deje sin marcar los elementos que aún requieren aclaración, corrección o evaluación de quien revisa
- `/speckit-implement` lee el estado de las casillas como una puerta y no debe modificar las marcas
- `checklists/requirements.md` tiene un ciclo de vida independiente, mantenido por `/speckit-specify` y `/speckit-clarify`
- Añada comentarios o hallazgos en línea
- Los elementos están numerados de forma secuencial (CHK001 a CHK040) para facilitar su referencia
