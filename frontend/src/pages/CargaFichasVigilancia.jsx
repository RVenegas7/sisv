import { useEffect, useState } from "react"
import { actualizarFicha, crearFicha, eliminarFicha, listarFichas, obtenerConfiguracion } from "../api/sisv"
import SeccionCIE from "../components/SeccionCIE"
import SelectTerritorial from "../components/SelectTerritorial"
import CentroSelector from "../components/CentroSelector"
import { Boton, Campo, Input, Seccion, Select } from "../components/ui"
import { SELECCION_CIE_VACIA, seleccionDesdeRegistro, useVersionCIE, validarCIE } from "../utils/cie"

const VACIO = {
  codigo_notificacion: "",
  nombre_evento: "",
  fecha_notificacion: "",
  fecha_evento: "",
  fecha_inicio_sintomas: "",
  clasificacion: "SOSPECHOSO",
  establecimiento: "",
  estado: "",
  municipio: "",
  parroquia: "",
  comunidad: "",
  organizacion: null,
  paciente_nombres: "",
  paciente_apellidos: "",
  paciente_cedula: "",
  sexo: "",
  edad: "",
  sintomas: "",
  nota: "",
}

const REQUERIDOS = [
  "codigo_notificacion",
  "nombre_evento",
  "fecha_notificacion",
  "fecha_evento",
  "clasificacion",
  "paciente_nombres",
  "paciente_apellidos",
]

const OPCIONES = {
  SEXO: [
    ["F", "Femenino"],
    ["M", "Masculino"],
    ["I", "Indeterminado"],
  ],
  CLASIFICACION: [
    ["SOSPECHOSO", "Sospechoso"],
    ["PROBABLE", "Probable"],
    ["CONFIRMADO", "Confirmado"],
    ["DESCARTADO", "Descartado"],
  ],
}

function validar(form, cieVersion, cieSeleccion) {
  const errores = {}
  for (const campo of REQUERIDOS) {
    if (!String(form[campo] ?? "").trim()) {
      errores[campo] = "Campo obligatorio"
    }
  }
  const errorCie = validarCIE(cieVersion, cieSeleccion)
  if (errorCie) errores.cie = errorCie
  return errores
}

function mostrarCIE(r) {
  if (r.cie10_detalle) return `${r.cie10_detalle.codigo} (CIE-10)`
  if (r.cie11_detalle) return `${r.cie11_detalle.codigo} (CIE-11)`
  return "—"
}

export default function CargaFichasVigilancia({ usuario }) {
  const permisos = usuario?.permisos || {}
  const [form, setForm] = useState(VACIO)
  const {
    version: cieVersion,
    setVersion: setCieVersion,
    versionManual,
    setVersionManual,
    seleccion: cieSeleccion,
    setSeleccion: setCieSeleccion,
  } = useVersionCIE(form.fecha_evento)
  const [errores, setErrores] = useState({})
  const [estado, setEstado] = useState({ tipo: "", texto: "" })
  const [lista, setLista] = useState([])
  const [editandoId, setEditandoId] = useState(null)

  useEffect(() => {
    listarFichas().then(setLista).catch(() => setLista([]))
    obtenerConfiguracion()
      .then((cfg) => {
        if (cfg.estado || cfg.municipio || cfg.parroquia || cfg.establecimiento) {
          setForm((f) => ({
            ...f,
            estado: cfg.estado || "",
            municipio: cfg.municipio || "",
            parroquia: cfg.parroquia || "",
            establecimiento: cfg.establecimiento || "",
          }))
        }
        if (cfg.organizacion_activa) {
          setForm((f) => ({ ...f, organizacion: cfg.organizacion_activa }))
        }
      })
      .catch(() => {})
  }, [])

  function cambiar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }))
  }

  function cancelarEdicion() {
    setEditandoId(null)
    setForm(VACIO)
    setErrores({})
    setEstado({ tipo: "", texto: "" })
    setCieSeleccion(SELECCION_CIE_VACIA)
    setCieVersion("CIE11")
    setVersionManual(false)
  }

  async function cargarEdicion(reg) {
    setForm({ ...VACIO, ...reg })
    setEditandoId(reg.id)
    setErrores({})
    setEstado({ tipo: "info", texto: `Editando ficha #${reg.id}.` })
    setCieVersion(reg.version_cie || "CIE11")
    setVersionManual(true)
    setCieSeleccion(await seleccionDesdeRegistro(reg))
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  async function borrar(reg) {
    if (!window.confirm(`¿Eliminar la ficha #${reg.id} (${reg.codigo_notificacion})?`)) return
    try {
      await eliminarFicha(reg.id)
      setLista(await listarFichas())
      setEstado({ tipo: "ok", texto: `Ficha #${reg.id} eliminada.` })
    } catch (err) {
      setEstado({ tipo: "error", texto: err.message })
    }
  }

  async function enviar(e) {
    e.preventDefault()
    const erroresForm = validar(form, cieVersion, cieSeleccion)
    setErrores(erroresForm)
    if (Object.keys(erroresForm).length) {
      setEstado({ tipo: "error", texto: "Corrija los campos marcados en rojo." })
      return
    }
    setEstado({ tipo: "info", texto: "Enviando ficha…" })
    try {
      const payload = {
        ...form,
        edad: Number(form.edad) || null,
        version_cie: cieVersion,
        organizacion:
          usuario?.organizacion?.nivel === "CENTRO" ? usuario.organizacion.id : form.organizacion ?? null,
        cie10: cieVersion === "CIE10" ? cieSeleccion.cie10.id : null,
        cie11: cieVersion === "CIE11" ? cieSeleccion.cie11.id : null,
        cie10_detalle: cieVersion === "CIE10" ? cieSeleccion.cie10 : null,
        cie11_detalle: cieVersion === "CIE11" ? cieSeleccion.cie11 : null,
      }
      if (editandoId) {
        await actualizarFicha(editandoId, payload)
        setEstado({ tipo: "ok", texto: `Ficha #${editandoId} actualizada.` })
      } else {
        const creado = await crearFicha(payload)
        setEstado({ tipo: "ok", texto: `Ficha de vigilancia creada: ${creado.codigo_notificacion} #${creado.id}` })
      }
      setLista(await listarFichas())
      cancelarEdicion()
    } catch (err) {
      setEstado({ tipo: "error", texto: err.message })
    }
  }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Fichas de Vigilancia Epidemiológica</h1>
        <p>Notificación de eventos de salud - SISV. La clasificación del evento usa CIE-10 (histórico) o CIE-11 (actual) según la fecha.</p>
      </header>

      {estado.tipo && (
        <div className={`aviso aviso-${estado.tipo}`} role="status">
          {estado.texto}
        </div>
      )}

      {editandoId && (
        <div className="aviso aviso-editando">
          Editando la ficha de vigilancia <strong>#{editandoId}</strong>.
          <button type="button" className="btn-mini" onClick={cancelarEdicion}>
            Cancelar edición
          </button>
        </div>
      )}

      <form className="formulario" onSubmit={enviar} noValidate>
        {!permisos.puede_escribir && (
          <div className="aviso aviso-info">
            Su rol (<strong>{usuario?.rol_label}</strong>) es de solo lectura: no está habilitada la carga de fichas.
          </div>
        )}
        <fieldset disabled={!permisos.puede_escribir}>
        <Seccion titulo="1. Notificación del evento">
          <Campo label="Código de notificación" htmlFor="codigo_notificacion" error={errores.codigo_notificacion}>
            <Input
              id="codigo_notificacion"
              value={form.codigo_notificacion}
              error={errores.codigo_notificacion}
              onChange={(e) => cambiar("codigo_notificacion", e.target.value)}
              placeholder="FV-YYYY-XXXXXX"
            />
          </Campo>
          <Campo label="Evento de salud" htmlFor="nombre_evento" error={errores.nombre_evento}>
            <Input
              id="nombre_evento"
              value={form.nombre_evento}
              error={errores.nombre_evento}
              onChange={(e) => cambiar("nombre_evento", e.target.value)}
              placeholder="Ej. Malaria, Dengue, Tuberculosis…"
            />
          </Campo>
          <Campo label="Fecha de notificación" htmlFor="fecha_notificacion" error={errores.fecha_notificacion}>
            <Input
              id="fecha_notificacion"
              type="date"
              value={form.fecha_notificacion}
              error={errores.fecha_notificacion}
              onChange={(e) => cambiar("fecha_notificacion", e.target.value)}
            />
          </Campo>
          <Campo label="Fecha del evento" htmlFor="fecha_evento" error={errores.fecha_evento}>
            <Input
              id="fecha_evento"
              type="date"
              value={form.fecha_evento}
              error={errores.fecha_evento}
              onChange={(e) => cambiar("fecha_evento", e.target.value)}
            />
          </Campo>
          <Campo label="Inicio de síntomas" htmlFor="fecha_inicio_sintomas">
            <Input id="fecha_inicio_sintomas" type="date" value={form.fecha_inicio_sintomas} onChange={(e) => cambiar("fecha_inicio_sintomas", e.target.value)} />
          </Campo>
          <Campo label="Clasificación" htmlFor="clasificacion" error={errores.clasificacion}>
            <Select id="clasificacion" opciones={OPCIONES.CLASIFICACION} value={form.clasificacion} onChange={(e) => cambiar("clasificacion", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="2. Datos del paciente">
          <Campo label="Nombres" htmlFor="paciente_nombres" error={errores.paciente_nombres}>
            <Input id="paciente_nombres" value={form.paciente_nombres} error={errores.paciente_nombres} onChange={(e) => cambiar("paciente_nombres", e.target.value)} />
          </Campo>
          <Campo label="Apellidos" htmlFor="paciente_apellidos" error={errores.paciente_apellidos}>
            <Input id="paciente_apellidos" value={form.paciente_apellidos} error={errores.paciente_apellidos} onChange={(e) => cambiar("paciente_apellidos", e.target.value)} />
          </Campo>
          <Campo label="Cédula (opcional)" htmlFor="paciente_cedula">
            <Input id="paciente_cedula" value={form.paciente_cedula} onChange={(e) => cambiar("paciente_cedula", e.target.value)} placeholder="V-12345678" />
          </Campo>
          <Campo label="Sexo" htmlFor="sexo">
            <Select id="sexo" opciones={OPCIONES.SEXO} value={form.sexo} onChange={(e) => cambiar("sexo", e.target.value)} />
          </Campo>
          <Campo label="Edad" htmlFor="edad">
            <Input id="edad" type="number" min="0" max="120" value={form.edad} onChange={(e) => cambiar("edad", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="3. Ubicación de la captación">
          <Campo label="Establecimiento" htmlFor="establecimiento">
            <Input id="establecimiento" value={form.establecimiento} onChange={(e) => cambiar("establecimiento", e.target.value)} />
          </Campo>
          <SelectTerritorial
            valor={{ estado: form.estado, municipio: form.municipio, parroquia: form.parroquia, comunidad: form.comunidad }}
            onChange={(t) => setForm((f) => ({ ...f, ...t }))}
          />
          <CentroSelector usuario={usuario} value={form.organizacion} onChange={(v) => cambiar("organizacion", v)} />
        </Seccion>

        <Seccion titulo="4. Clínica del evento">
          <Campo label="Síntomas" htmlFor="sintomas">
            <textarea id="sintomas" rows="3" value={form.sintomas} onChange={(e) => cambiar("sintomas", e.target.value)} />
          </Campo>
          <Campo label="Observaciones / nota" htmlFor="nota">
            <textarea id="nota" rows="2" value={form.nota} onChange={(e) => cambiar("nota", e.target.value)} />
          </Campo>
        </Seccion>

        <SeccionCIE
          titulo="5. Clasificación CIE del evento"
          etiqueta="Agente o evento CIE"
          fechaEvento={form.fecha_evento}
          version={cieVersion}
          setVersion={setCieVersion}
          versionManual={versionManual}
          setVersionManual={setVersionManual}
          seleccion={cieSeleccion}
          setSeleccion={setCieSeleccion}
          error={errores.cie}
        />

        </fieldset>

        <div className="pie-form">
          <Boton disabled={!permisos.puede_escribir}>{editandoId ? "Guardar cambios de la ficha" : "Guardar ficha de vigilancia"}</Boton>
        </div>
      </form>

      <section className="lista">
        <h2>Fichas registradas ({lista.length})</h2>
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>Evento</th>
              <th>Fecha</th>
              <th>Clasificación</th>
              <th>Paciente</th>
              <th>Municipio</th>
              <th>CIE</th>
              <th>Centro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {lista.map((r) => (
              <tr key={r.id}>
                <td>{r.codigo_notificacion}</td>
                <td>{r.nombre_evento}</td>
                <td>{r.fecha_evento}</td>
                <td>{r.clasificacion}</td>
                <td>{r.paciente_nombres} {r.paciente_apellidos}</td>
                <td>{r.municipio || "—"}</td>
                <td>{mostrarCIE(r)}</td>
                <td>{r.organizacion_nombre || "—"}</td>
                <td className="acciones">
                  {permisos.puede_editar && (
                    <button type="button" className="btn-mini" onClick={() => cargarEdicion(r)}>
                      Editar
                    </button>
                  )}
                  {permisos.puede_eliminar && (
                    <button type="button" className="btn-mini peligro" onClick={() => borrar(r)}>
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}