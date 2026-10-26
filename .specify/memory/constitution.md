<!--
Informe de Impacto de Sincronización
- Cambio de versión: (plantilla sin completar) → 1.0.0
- Principios modificados: ninguno (constitución inicial)
- Principios añadidos: I. Simplicidad primero; II. Pruebas obligatorias;
  III. Código legible; IV. Validación de entradas; V. Accesible y responsivo
- Secciones añadidas: Restricciones Adicionales; Flujo de Desarrollo y Puertas de Calidad; Gobernanza
- Secciones eliminadas: ninguna
- Pendientes (TODO diferidos): ninguno. El nombre del proyecto se definió como
  "Proyecto Académico UPB" por no haberse indicado uno específico.
-->
# Constitución del Proyecto Académico UPB

Todo documento del proyecto (especificaciones, planes, tareas, README y comentarios
relevantes) MUST estar redactado en español.

## Principios Fundamentales

### I. Simplicidad primero (YAGNI)
Se MUST implementar la solución mínima que cumpla el requisito. No se añaden capas de
abstracción, configuraciones, dependencias ni funcionalidades "por si acaso". Toda
complejidad adicional MUST justificarse por escrito en el plan o en la revisión.

*Justificación*: un proyecto académico tiene alcance y tiempo acotados; el código simple
es más fácil de entender, probar, defender y mantener.

### II. Pruebas obligatorias (NO NEGOCIABLE)
Toda funcionalidad MUST contar con pruebas automatizadas antes de darse por terminada.
Una tarea no se marca como completada si sus pruebas no existen o no pasan. Las pruebas
MUST cubrir el camino feliz y los casos de error relevantes, y MUST poder ejecutarse con
un único comando documentado.

*Justificación*: las pruebas automatizadas son la evidencia verificable de que la
funcionalidad cumple lo especificado y evitan regresiones.

### III. Código legible
Los nombres de variables, funciones y archivos MUST ser claros y descriptivos. Las
funciones MUST ser pequeñas y con una sola responsabilidad. Lo que no sea evidente
(decisiones de diseño, reglas de negocio, soluciones poco intuitivas) MUST documentarse
con comentarios o documentación breve que explique el porqué, no lo obvio del cómo.

*Justificación*: el código se lee más veces de las que se escribe; la legibilidad facilita
la revisión por docentes y compañeros.

### IV. Validación de entradas
Todo dato proveniente del usuario (formularios, parámetros, cuerpos de petición,
archivos) MUST validarse antes de procesarse o almacenarse: tipo, formato, rango y
longitud. Las entradas inválidas MUST rechazarse con un mensaje de error claro y sin
exponer detalles internos. Cada regla de validación MUST tener su prueba automatizada.

*Justificación*: la validación previene errores, datos corruptos y vulnerabilidades
comunes como la inyección.

### V. Accesible y responsivo
La interfaz MUST funcionar correctamente tanto en celular como en computadora, sin
desplazamiento horizontal ni elementos inutilizables en pantallas pequeñas. La interfaz
MUST ser accesible: HTML semántico, etiquetas asociadas a los campos de formulario,
contraste de color suficiente y uso completo mediante teclado.

*Justificación*: los usuarios acceden desde distintos dispositivos y capacidades; una
interfaz inclusiva amplía su utilidad.

## Restricciones Adicionales

- Las dependencias externas SHOULD limitarse a las estrictamente necesarias (ver
  Principio I); cada una MUST tener un motivo documentado.
- Los secretos y credenciales MUST NOT incluirse en el repositorio; se usan variables de
  entorno.
- Los mensajes de error mostrados al usuario MUST estar en español.

## Flujo de Desarrollo y Puertas de Calidad

- Todo cambio MUST seguir el flujo de Spec Kit: especificación, plan, tareas e
  implementación.
- Antes de integrar un cambio: las pruebas automatizadas MUST pasar y el cambio MUST
  revisarse contra los cinco principios de esta constitución.
- Los commits MUST describir el cambio de forma clara y concisa.
- Una funcionalidad con interfaz MUST verificarse en vista de celular y de computadora.

## Gobernanza

Esta constitución prevalece sobre cualquier otra práctica del proyecto. Las enmiendas
MUST documentarse, indicar su motivo y actualizar la versión y la fecha de última
enmienda. Cuando una enmienda cambie o elimine un principio, MUST revisarse la
coherencia de las especificaciones, planes y tareas existentes.

Política de versionado semántico:
- MAYOR: eliminación o redefinición incompatible de principios o de la gobernanza.
- MENOR: adición de un principio o sección, o ampliación sustancial de la guía.
- PARCHE: aclaraciones, correcciones de redacción y refinamientos no semánticos.

Revisión de cumplimiento: toda revisión de código y todo plan MUST verificar el
cumplimiento de los principios; las excepciones MUST justificarse por escrito.

**Versión**: 1.0.0 | **Ratificada**: 2026-10-26 | **Última enmienda**: 2026-10-26
