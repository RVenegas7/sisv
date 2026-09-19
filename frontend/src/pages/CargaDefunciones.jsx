import { useEffect, useState } from "react"
import { actualizarDefuncion, crearDefuncion, eliminarDefuncion, listarDefunciones, obtenerConfiguracion } from "../api/sisv"
import SeccionCIE from "../components/SeccionCIE"
import SelectTerritorial from "../components/SelectTerritorial"
import CentroSelector from "../components/CentroSelector"
import { Boton, Campo, Input, Seccion, Select } from "../components/ui"
import { SELECCION_CIE_VACIA, seleccionDesdeRegistro, useVersionCIE, validarCIE } from "../utils/cie"

const VACIO = {
  registro_numero: "",
  lote_id: "",
  fecha_evento: "",
  hora_defuncion: "",
  fallecido_nombres: "",
  fallecido_apellidos: "",
  fallecido_cedula: "",
  sexo: "",
  fecha_nacimiento: "",
  lugar_defuncion: "ESTABLECIMIENTO",
  establecimiento: "",
  estado: "",
  municipio: "",
  parroquia: "",
  comunidad: "",
  organizacion: null,
  causa_directa: "",
  embarazo_o_puerperio: false,
  autopsia: false,
  embalsamado: false,
  certificador_nombres: "",
  certificador_cedula: "",
}

const REQUERIDOS = ["registro_numero", "fecha_evento", "fallecido_nombres", "fallecido_apellidos", "sexo"]

const OPCIONES = {
  SEXO: [
    ["F", "Femenino"],
    ["M", "Masculino"],
    ["I", "Indeterminado"],
  ],
  LUGAR: [
    ["ESTABLECIMIENTO", "Establecimiento de salud"],
    ["DOMICILIO", "Domicilio"],
    ["VIA_PUBLICA", "Vía pública"],
    ["OTRO", "Otro"],
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

export default function CargaDefunciones({ usuario }) {
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
    listarDefunciones().then(setLista).catch(() => setLista([]))
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
    setEstado({ tipo: "info", texto: `Editando certificado #${reg.id}.` })
    setCieVersion(reg.version_cie || "CIE11")
    setVersionManual(true)
    setCieSeleccion(await seleccionDesdeRegistro(reg))
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  async function borrar(reg) {
    if (!window.confirm(`¿Eliminar el certificado #${reg.id} (${reg.registro_numero})?`)) return
    try {
      await eliminarDefuncion(reg.id)
      setLista(await listarDefunciones())
      setEstado({ tipo: "ok", texto: `Certificado #${reg.id} eliminado.` })
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
    setEstado({ tipo: "info", texto: "Enviando registro…" })
    try {
      const payload = {
        ...form,
        version_cie: cieVersion,
        organizacion:
          usuario?.organizacion?.nivel === "CENTRO" ? usuario.organizacion.id : form.organizacion ?? null,
        cie10: cieVersion === "CIE10" ? cieSeleccion.cie10.id : null,
        cie11: cieVersion === "CIE11" ? cieSeleccion.cie11.id : null,
        cie10_detalle: cieVersion === "CIE10" ? cieSeleccion.cie10 : null,
        cie11_detalle: cieVersion === "CIE11" ? cieSeleccion.cie11 : null,
      }
      if (editandoId) {
        await actualizarDefuncion(editandoId, payload)
        setEstado({ tipo: "ok", texto: `Certificado #${editandoId} actualizado.` })
      } else {
        const creado = await crearDefuncion(payload)
        setEstado({ tipo: "ok", texto: `Certificado creado: ${creado.registro_numero} #${creado.id}` })
      }
      setLista(await listarDefunciones())
      cancelarEdicion()
    } catch (err) {
      setEstado({ tipo: "error", texto: err.message })
    }
  }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Registro de Defunciones</h1>
        <p>Certificados de defunción - SISV. La causa se clasifica contra CIE-10 (histórico) o CIE-11 (actual) según la fecha.</p>
      </header>

      {estado.tipo && (
        <div className={`aviso aviso-${estado.tipo}`} role="status">
          {estado.texto}
        </div>
      )}

      {editandoId && (
        <div className="aviso aviso-editando">
          Editando el certificado de defunción <strong>#{editandoId}</strong>.
          <button type="button" className="btn-mini" onClick={cancelarEdicion}>
            Cancelar edición
          </button>
        </div>
      )}

      <form className="formulario" onSubmit={enviar} noValidate>
        {!permisos.puede_escribir && (
          <div className="aviso aviso-info">
            Su rol (<strong>{usuario?.rol_label}</strong>) es de solo lectura: no está habilitada la carga de certificados.
          </div>
        )}
        <fieldset disabled={!permisos.puede_escribir}>
        <Seccion titulo="1. Certificado de defunción">
          <Campo label="Nº de certificado" htmlFor="registro_numero" error={errores.registro_numero}>
            <Input
              id="registro_numero"
              value={form.registro_numero}
              error={errores.registro_numero}
              onChange={(e) => cambiar("registro_numero", e.target.value)}
              placeholder="DEF-YYYY-XXXXXX"
            />
          </Campo>
          <Campo label="Lote de carga (opcional)" htmlFor="lote_id">
            <Input id="lote_id" value={form.lote_id} onChange={(e) => cambiar("lote_id", e.target.value)} />
          </Campo>
          <Campo label="Fecha de defunción" htmlFor="fecha_evento" error={errores.fecha_evento}>
            <Input
              id="fecha_evento"
              type="date"
              value={form.fecha_evento}
              error={errores.fecha_evento}
              onChange={(e) => cambiar("fecha_evento", e.target.value)}
            />
          </Campo>
          <Campo label="Hora" htmlFor="hora_defuncion">
            <Input id="hora_defuncion" type="time" value={form.hora_defuncion} onChange={(e) => cambiar("hora_defuncion", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="2. Datos del fallecido">
          <Campo label="Nombres" htmlFor="fallecido_nombres" error={errores.fallecido_nombres}>
            <Input id="fallecido_nombres" value={form.fallecido_nombres} error={errores.fallecido_nombres} onChange={(e) => cambiar("fallecido_nombres", e.target.value)} />
          </Campo>
          <Campo label="Apellidos" htmlFor="fallecido_apellidos" error={errores.fallecido_apellidos}>
            <Input id="fallecido_apellidos" value={form.fallecido_apellidos} error={errores.fallecido_apellidos} onChange={(e) => cambiar("fallecido_apellidos", e.target.value)} />
          </Campo>
          <Campo label="Cédula (opcional)" htmlFor="fallecido_cedula">
            <Input id="fallecido_cedula" value={form.fallecido_cedula} onChange={(e) => cambiar("fallecido_cedula", e.target.value)} placeholder="V-12345678" />
          </Campo>
          <Campo label="Sexo" htmlFor="sexo" error={errores.sexo}>
            <Select id="sexo" opciones={OPCIONES.SEXO} value={form.sexo} onChange={(e) => cambiar("sexo", e.target.value)} />
          </Campo>
          <Campo label="Fecha de nacimiento" htmlFor="fecha_nacimiento">
            <Input id="fecha_nacimiento" type="date" value={form.fecha_nacimiento} onChange={(e) => cambiar("fecha_nacimiento", e.target.value)} />
          </Campo>
          <Campo label="Lugar de defunción" htmlFor="lugar_defuncion">
            <Select id="lugar_defuncion" opciones={OPCIONES.LUGAR} value={form.lugar_defuncion} onChange={(e) => cambiar("lugar_defuncion", e.target.value)} />
          </Campo>
          <Campo label="Establecimiento" htmlFor="establecimiento">
            <Input id="establecimiento" value={form.establecimiento} onChange={(e) => cambiar("establecimiento", e.target.value)} />
          </Campo>
          <SelectTerritorial
            valor={{ estado: form.estado, municipio: form.municipio, parroquia: form.parroquia, comunidad: form.comunidad }}
            onChange={(t) => setForm((f) => ({ ...f, ...t }))}
          />
          <CentroSelector usuario={usuario} value={form.organizacion} onChange={(v) => cambiar("organizacion", v)} />
        </Seccion>

        <Seccion titulo="3. Causas y procedimientos">
          <Campo label="Causa inmediata (texto)" htmlFor="causa_directa">
            <Input id="causa_directa" value={form.causa_directa} onChange={(e) => cambiar("causa_directa", e.target.value)} />
          </Campo>
          <label className="checkbox">
            <input type="checkbox" checked={form.embarazo_o_puerperio} onChange={(e) => cambiar("embarazo_o_puerperio", e.target.checked)} />
            Defunción materna (embarazo/puerperio)
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.autopsia} onChange={(e) => cambiar("autopsia", e.target.checked)} />
            Se realizó autopsia
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.embalsamado} onChange={(e) => cambiar("embalsamado", e.target.checked)} />
            Embalsamado
          </label>
        </Seccion>

        <Seccion titulo="4. Médico certificador">
          <Campo label="Nombres" htmlFor="certificador_nombres">
            <Input id="certificador_nombres" value={form.certificador_nombres} onChange={(e) => cambiar("certificador_nombres", e.target.value)} />
          </Campo>
          <Campo label="Cédula" htmlFor="certificador_cedula">
            <Input id="certificador_cedula" value={form.certificador_cedula} onChange={(e) => cambiar("certificador_cedula", e.target.value)} />
          </Campo>
        </Seccion>

        <SeccionCIE
          titulo="5. Clasificación CIE (causa básica de defunción)"
          etiqueta="Causa de defunción"
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
          <Boton disabled={!permisos.puede_escribir}>{editandoId ? "Guardar cambios del certificado" : "Guardar certificado de defunción"}</Boton>
        </div>
      </form>

      <section className="lista">
        <h2>Certificados registrados ({lista.length})</h2>
        <table>
          <thead>
            <tr>
              <th>Nº</th>
              <th>Fecha</th>
              <th>Fallecido</th>
              <th>Sexo</th>
              <th>Lugar</th>
              <th>Municipio</th>
              <th>CIE</th>
              <th>Centro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {lista.map((r) => (
              <tr key={r.id}>
                <td>{r.registro_numero}</td>
                <td>{r.fecha_evento}</td>
                <td>{r.fallecido_nombres} {r.fallecido_apellidos}</td>
                <td>{r.sexo}</td>
                <td>{r.lugar_defuncion}</td>
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