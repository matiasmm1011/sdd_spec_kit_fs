// Interfaz del Organizador de Tareas Académicas.
// Sin frameworks. Todo el texto que escribe el estudiante se inserta con
// textContent (nunca innerHTML) para que se muestre tal cual y no como HTML.

// Debe coincidir con PALETA_COLORES de app/esquemas.py (lo comprueba una prueba).
const PALETA = [
  { nombre: "Azul", valor: "#1D4ED8" },
  { nombre: "Verde", valor: "#15803D" },
  { nombre: "Rojo", valor: "#B91C1C" },
  { nombre: "Naranja", valor: "#C2410C" },
  { nombre: "Morado", valor: "#7E22CE" },
  { nombre: "Turquesa", valor: "#0F766E" },
  { nombre: "Rosa", valor: "#BE185D" },
  { nombre: "Gris", valor: "#475569" },
];

// Si el estudiante borra la hora se usa el final del día (supuesto de la especificación).
const HORA_POR_DEFECTO = "23:59";

// Campo que devuelve la API -> id del control del formulario que se enfoca al fallar.
const CONTROLES = {
  materia: { nombre: "materia-nombre", color: "materia-color" },
  tarea: {
    titulo: "tarea-titulo",
    descripcion: "tarea-descripcion",
    fecha_entrega: "tarea-fecha",
    materia_id: "tarea-materia",
  },
};

const estado = { materias: [], tareas: [] };

const $ = (id) => document.getElementById(id);

// --- Comunicación con la API ----------------------------------------------

class ErrorApi extends Error {
  constructor(detalle) {
    super("La API rechazó la petición.");
    this.detalle = detalle;
  }
}

class ErrorDeRed extends Error {}

async function pedir(metodo, ruta, cuerpo) {
  const opciones = { method: metodo };
  if (cuerpo !== undefined) {
    opciones.headers = { "Content-Type": "application/json" };
    opciones.body = JSON.stringify(cuerpo);
  }

  let respuesta;
  try {
    respuesta = await fetch(ruta, opciones);
  } catch {
    throw new ErrorDeRed("No hay conexión con el servidor.");
  }

  if (respuesta.status === 204) return null;
  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) throw new ErrorApi(datos?.detalle ?? []);
  return datos;
}

// --- Mensajes y errores ---------------------------------------------------

function mostrarMensaje(texto, esError = false) {
  const zona = $("mensajes");
  zona.textContent = texto;
  zona.classList.toggle("mensajes-error", esError);
}

function limpiarErrores(formulario) {
  for (const parrafo of formulario.querySelectorAll(".error")) parrafo.textContent = "";
  for (const control of formulario.querySelectorAll("[aria-invalid]")) {
    control.removeAttribute("aria-invalid");
  }
}

function mostrarErrores(prefijo, detalle) {
  let primerControl = null;
  for (const { campo, mensaje } of detalle) {
    const parrafo = $(`error-${prefijo}-${campo}`);
    if (!parrafo) {
      mostrarMensaje(mensaje, true);
      continue;
    }
    parrafo.textContent = mensaje;
    const control = $(CONTROLES[prefijo][campo]);
    if (control && control.tagName !== "FIELDSET") control.setAttribute("aria-invalid", "true");
    primerControl ??= control;
  }
  // Enfoca el primer control con error; en el grupo de colores, su primera opción.
  const enfocable = primerControl?.tagName === "FIELDSET"
    ? primerControl.querySelector("input")
    : primerControl;
  enfocable?.focus();
}

function manejarError(error, prefijo) {
  if (error instanceof ErrorApi) {
    mostrarErrores(prefijo, error.detalle);
  } else {
    mostrarMensaje("No se pudo conectar con el servidor. Revisa que esté en marcha e inténtalo de nuevo.", true);
  }
}

// --- Utilidades de interfaz -----------------------------------------------

function crear(etiqueta, { texto, clase, atributos } = {}, hijos = []) {
  const elemento = document.createElement(etiqueta);
  if (texto !== undefined) elemento.textContent = texto;
  if (clase) elemento.className = clase;
  for (const [nombre, valor] of Object.entries(atributos ?? {})) {
    elemento.setAttribute(nombre, valor);
  }
  elemento.append(...hijos);
  return elemento;
}

function boton(texto, etiquetaAccesible, alHacerClic, clase = "secundario") {
  const elemento = crear("button", {
    texto,
    clase,
    atributos: { type: "button", "aria-label": etiquetaAccesible },
  });
  elemento.addEventListener("click", alHacerClic);
  return elemento;
}

function plural(cantidad, singular, pluralTexto) {
  return `${cantidad} ${cantidad === 1 ? singular : pluralTexto}`;
}

function confirmar(texto) {
  return new Promise((resolver) => {
    const dialogo = $("dialogo");
    const origen = document.activeElement;
    let resuelto = false;
    const terminar = (valor) => {
      if (resuelto) return;
      resuelto = true;
      if (dialogo.open) dialogo.close();
      origen?.focus();
      resolver(valor);
    };
    $("dialogo-texto").textContent = texto;
    $("dialogo-confirmar").onclick = () => terminar(true);
    $("dialogo-cancelar").onclick = () => terminar(false);
    dialogo.oncancel = () => terminar(false); // tecla Escape
    dialogo.showModal();
    $("dialogo-cancelar").focus();
  });
}

// --- Fechas ---------------------------------------------------------------

function aIsoConZona(fecha, hora) {
  if (!fecha) return undefined;
  const instante = new Date(`${fecha}T${hora || HORA_POR_DEFECTO}`);
  return Number.isNaN(instante.getTime()) ? undefined : instante.toISOString();
}

function aFechaYHoraLocal(iso) {
  const instante = new Date(iso);
  const dos = (numero) => String(numero).padStart(2, "0");
  return {
    fecha: `${instante.getFullYear()}-${dos(instante.getMonth() + 1)}-${dos(instante.getDate())}`,
    hora: `${dos(instante.getHours())}:${dos(instante.getMinutes())}`,
  };
}

function formatearFecha(iso) {
  return new Date(iso).toLocaleString("es", { dateStyle: "medium", timeStyle: "short" });
}

// --- Materias -------------------------------------------------------------

function dibujarOpcionesDeColor() {
  const contenedor = $("opciones-color");
  PALETA.forEach(({ nombre, valor }, indice) => {
    const entrada = crear("input", {
      atributos: { type: "radio", name: "color", value: valor, id: `color-${indice}` },
    });
    const muestra = crear("span", { clase: "muestra", atributos: { "aria-hidden": "true" } });
    muestra.style.background = valor;
    const etiqueta = crear("label", { clase: "opcion-color", atributos: { for: `color-${indice}` } }, [
      muestra,
      crear("span", { texto: nombre }),
    ]);
    contenedor.append(entrada, etiqueta);
  });
}

function colorSeleccionado() {
  return document.querySelector("#materia-color input:checked")?.value;
}

function seleccionarColor(valor) {
  for (const entrada of document.querySelectorAll("#materia-color input")) {
    entrada.checked = entrada.value === valor;
  }
}

function reiniciarFormularioMateria() {
  const formulario = $("form-materia");
  limpiarErrores(formulario);
  $("materia-id").value = "";
  $("materia-nombre").value = "";
  seleccionarColor(PALETA[0].valor);
  $("guardar-materia").textContent = "Guardar materia";
  $("cancelar-materia").hidden = true;
}

function editarMateria(materia) {
  limpiarErrores($("form-materia"));
  $("materia-id").value = materia.id;
  $("materia-nombre").value = materia.nombre;
  seleccionarColor(materia.color);
  $("guardar-materia").textContent = "Guardar cambios";
  $("cancelar-materia").hidden = false;
  $("materia-nombre").focus();
}

async function guardarMateria(evento) {
  evento.preventDefault();
  limpiarErrores($("form-materia"));
  const id = $("materia-id").value;
  const cuerpo = { nombre: $("materia-nombre").value, color: colorSeleccionado() };
  try {
    await pedir(id ? "PUT" : "POST", id ? `/api/materias/${id}` : "/api/materias", cuerpo);
  } catch (error) {
    manejarError(error, "materia");
    return;
  }
  reiniciarFormularioMateria();
  mostrarMensaje("Materia guardada.");
  await recargar();
}

async function eliminarMateria(materia) {
  if (materia.total_tareas > 0) {
    const n = materia.total_tareas;
    const aceptado = await confirmar(
      `La materia "${materia.nombre}" tiene ${plural(n, "tarea", "tareas")}. ` +
        `Si la eliminas, también se eliminarán ${n === 1 ? "esa tarea" : `esas ${n} tareas`}. ` +
        "¿Quieres continuar?",
    );
    if (!aceptado) return;
  }
  try {
    await pedir("DELETE", `/api/materias/${materia.id}`);
  } catch (error) {
    manejarError(error, "materia");
    return;
  }
  if ($("materia-id").value === String(materia.id)) reiniciarFormularioMateria();
  if ($("tarea-materia").value === String(materia.id)) reiniciarFormularioTarea();
  mostrarMensaje("Materia eliminada.");
  await recargar();
}

function dibujarMaterias() {
  const lista = $("lista-materias");
  lista.replaceChildren(
    ...estado.materias.map((materia) => {
      const muestra = crear("span", { clase: "muestra", atributos: { "aria-hidden": "true" } });
      muestra.style.background = materia.color;
      const cantidad = materia.total_tareas === 0 ? "Sin tareas" : plural(materia.total_tareas, "tarea", "tareas");
      return crear("li", {}, [
        crear("div", { clase: "elemento-texto" }, [
          muestra,
          crear("strong", { texto: materia.nombre }),
          crear("span", { clase: "suave", texto: cantidad }),
        ]),
        crear("div", { clase: "acciones" }, [
          boton("Editar", `Editar materia ${materia.nombre}`, () => editarMateria(materia)),
          boton("Eliminar", `Eliminar materia ${materia.nombre}`, () => eliminarMateria(materia)),
        ]),
      ]);
    }),
  );
  $("vacio-materias").hidden = estado.materias.length > 0;
}

// --- Tareas ---------------------------------------------------------------

function reiniciarFormularioTarea() {
  const formulario = $("form-tarea");
  limpiarErrores(formulario);
  $("tarea-id").value = "";
  $("tarea-titulo").value = "";
  $("tarea-descripcion").value = "";
  $("tarea-fecha").value = "";
  $("tarea-hora").value = HORA_POR_DEFECTO;
  $("guardar-tarea").textContent = "Guardar tarea";
  $("cancelar-tarea").hidden = true;
}

function editarTarea(tarea) {
  limpiarErrores($("form-tarea"));
  const { fecha, hora } = aFechaYHoraLocal(tarea.fecha_entrega);
  $("tarea-id").value = tarea.id;
  $("tarea-titulo").value = tarea.titulo;
  $("tarea-descripcion").value = tarea.descripcion ?? "";
  $("tarea-fecha").value = fecha;
  $("tarea-hora").value = hora;
  $("tarea-materia").value = String(tarea.materia.id);
  $("guardar-tarea").textContent = "Guardar cambios";
  $("cancelar-tarea").hidden = false;
  $("tarea-titulo").focus();
}

async function guardarTarea(evento) {
  evento.preventDefault();
  limpiarErrores($("form-tarea"));
  const id = $("tarea-id").value;
  const materia = $("tarea-materia").value;
  const cuerpo = {
    titulo: $("tarea-titulo").value,
    descripcion: $("tarea-descripcion").value,
    fecha_entrega: aIsoConZona($("tarea-fecha").value, $("tarea-hora").value),
    materia_id: materia ? Number(materia) : undefined,
  };
  try {
    await pedir(id ? "PUT" : "POST", id ? `/api/tareas/${id}` : "/api/tareas", cuerpo);
  } catch (error) {
    manejarError(error, "tarea");
    return;
  }
  reiniciarFormularioTarea();
  mostrarMensaje("Tarea guardada.");
  await recargar();
}

async function eliminarTarea(tarea) {
  try {
    await pedir("DELETE", `/api/tareas/${tarea.id}`);
  } catch (error) {
    manejarError(error, "tarea");
    return;
  }
  if ($("tarea-id").value === String(tarea.id)) reiniciarFormularioTarea();
  mostrarMensaje("Tarea eliminada.");
  await recargar();
}

function dibujarOpcionesDeMateria() {
  const selector = $("tarea-materia");
  const previa = selector.value;
  selector.replaceChildren(
    ...estado.materias.map((materia) =>
      crear("option", { texto: materia.nombre, atributos: { value: String(materia.id) } }),
    ),
  );
  if (estado.materias.some((materia) => String(materia.id) === previa)) selector.value = previa;
}

function dibujarTareas() {
  const lista = $("lista-tareas");
  lista.replaceChildren(
    ...estado.tareas.map((tarea) => {
      const materia = crear("span", { clase: "etiqueta-materia", texto: tarea.materia.nombre });
      materia.style.background = tarea.materia.color;
      const contenido = [
        crear("div", { clase: "elemento-texto" }, [
          crear("strong", { texto: tarea.titulo }),
          materia,
        ]),
        crear("p", { clase: "suave", texto: `Entrega: ${formatearFecha(tarea.fecha_entrega)}` }),
      ];
      if (tarea.descripcion) contenido.push(crear("p", { texto: tarea.descripcion }));
      contenido.push(
        crear("div", { clase: "acciones" }, [
          boton("Editar", `Editar tarea ${tarea.titulo}`, () => editarTarea(tarea)),
          boton("Eliminar", `Eliminar tarea ${tarea.titulo}`, () => eliminarTarea(tarea)),
        ]),
      );
      return crear("li", {}, contenido);
    }),
  );
  $("vacio-tareas").hidden = estado.tareas.length > 0;
}

function actualizarFormularioDeTarea() {
  const sinMaterias = estado.materias.length === 0;
  $("aviso-sin-materias").hidden = !sinMaterias;
  for (const control of $("form-tarea").querySelectorAll("input:not([type=hidden]), textarea, select, button")) {
    if (control.id !== "cancelar-tarea") control.disabled = sinMaterias;
  }
}

// --- Carga y arranque -----------------------------------------------------

function dibujar() {
  dibujarMaterias();
  dibujarOpcionesDeMateria();
  actualizarFormularioDeTarea();
  dibujarTareas();
}

async function recargar() {
  try {
    const [materias, tareas] = await Promise.all([
      pedir("GET", "/api/materias"),
      pedir("GET", "/api/tareas"),
    ]);
    estado.materias = materias;
    estado.tareas = tareas;
  } catch {
    mostrarMensaje("No se pudo conectar con el servidor. Revisa que esté en marcha e inténtalo de nuevo.", true);
    return;
  }
  dibujar();
}

function iniciar() {
  dibujarOpcionesDeColor();
  reiniciarFormularioMateria();
  $("form-materia").addEventListener("submit", guardarMateria);
  $("cancelar-materia").addEventListener("click", reiniciarFormularioMateria);
  $("form-tarea").addEventListener("submit", guardarTarea);
  $("cancelar-tarea").addEventListener("click", reiniciarFormularioTarea);
  recargar();
}

iniciar();
