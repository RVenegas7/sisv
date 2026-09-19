import { useEffect, useState } from "react"
import { actualizarNacimiento, crearNacimiento, eliminarNacimiento, listarNacimientos, obtenerConfiguracion, obtenerDashboard } from "../api/sisv"
import SeccionCIE from "../components/SeccionCIE"
import SelectTerritorial from "../components/SelectTerritorial"
import CentroSelector from "../components/CentroSelector"
import { Boton, Campo, Input, Seccion, Select } from "../components/ui"
import { SELECCION_CIE_VACIA, seleccionDesdeRegistro, useVersionCIE, validarCIE } from "../utils/cie"

const VACIO = {
  registro_numero: "",
  lote_id: "",
  fecha_evento: "",
  hora_nacimiento: "",
  sexo: "",
  peso_gramos: "",
  talla_cm: "",
  edad_gestacional_semanas: "",
  tipo_parto: "VAGINAL",
  tipo_embarazo: "UNICO",
  numero_gemelar: "",
  sitio_nacimiento: "ESTABLECIMIENTO",
  establecimiento: "",
  estado: "",
  municipio: "",
  parroquia: "",
  comunidad: "",
  organizacion: null,
  nacido_vivo: true,
  apgar_1m: "",
  apgar_5m: "",
  madre_nombres: "",
  madre_apellidos: "",
  madre_cedula: "",
  madre_edad: "",
  madre_estado_civil: "SOLTERA",
  padre_nombres: "",
  padre_apellidos: "",
  padre_cedula: "",
  libro: "",
  folio: "",
  acta: "",
}

const OPCIONES = {
  SEXO: [
    ["F", "Femenino"],
    ["M", "Masculino"],
    ["I", "Indeterminado"],
  ],
  TIPO_PARTO: [
    ["VAGINAL", "Vaginal"],
    ["CESAREA", "Cesárea"],
    ["INSTRUMENTAL", "Instrumental"],
    ["OTRO", "Otro"],
  ],
  TIPO_EMBARAZO: [
    ["UNICO", "Único"],
    ["GEMELAR", "Gemelar"],
    ["TRIPLE", "Triple"],
    ["MULTIPLE", "Múltiple"],
  ],
  SITIO: [
    ["ESTABLECIMIENTO", "Establecimiento de salud"],
    ["DOMICILIO", "Domicilio"],
    ["VIA_PUBLICA", "Vía pública"],
    ["OTRO", "Otro"],
  ],
  ESTADO_CIVIL: [
    ["SOLTERA", "Soltera"],
    ["CASADA", "Casada"],
    ["DIVORCIADA", "Divorciada"],
    ["VIUDA", "Viuda"],
    ["UNION_LIBRE", "Unión libre"],
  ],
}

const REQUERIDOS = [
  "registro_numero",
  "fecha_evento",
  "sexo",
  "madre_nombres",
  "madre_apellidos",
  "madre_cedula",
  "madre_edad",
]

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

export default function CargaNacimientos({ usuario }) {
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
  const [stats, setStats] = useState(null)
  const [editandoId, setEditandoId] = useState(null)

  useEffect(() => {
    listarNacimientos().then(setLista).catch(() => setLista([]))
    obtenerDashboard()
      .then((d) => setStats({ total: d.totales.nacimientos, nacidos_vivos: d.nacimientos_salud.nacidos_vivos, por_sexo: d.nacimientos_salud.por_sexo, por_tipo_parto: d.nacimientos_salud.por_tipo_parto }))
      .catch(() => setStats(null))
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
    setEstado({ tipo: "info", texto: `Editando registro #${reg.id}.` })
    setCieVersion(reg.version_cie || "CIE11")
    setVersionManual(true)
    setCieSeleccion(await seleccionDesdeRegistro(reg))
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  async function borrar(reg) {
    if (!window.confirm(`¿Eliminar el registro de nacimiento #${reg.id} (${reg.registro_numero})?`)) return
    try {
      await eliminarNacimiento(reg.id)
      setLista(await listarNacimientos())
      obtenerDashboard()
        .then((d) => setStats({ total: d.totales.nacimientos, nacidos_vivos: d.nacimientos_salud.nacidos_vivos, por_sexo: d.nacimientos_salud.por_sexo, por_tipo_parto: d.nacimientos_salud.por_tipo_parto }))
        .catch(() => null)
      setEstado({ tipo: "ok", texto: `Registro #${reg.id} eliminado.` })
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
        peso_gramos: Number(form.peso_gramos) || null,
        talla_cm: Number(form.talla_cm) || null,
        edad_gestacional_semanas: Number(form.edad_gestacional_semanas) || null,
        madre_edad: Number(form.madre_edad),
        folio: Number(form.folio) || null,
        acta: Number(form.acta) || null,
        version_cie: cieVersion,
        organizacion:
          usuario?.organizacion?.nivel === "CENTRO" ? usuario.organizacion.id : form.organizacion ?? null,
        cie10: cieVersion === "CIE10" ? cieSeleccion.cie10.id : null,
        cie11: cieVersion === "CIE11" ? (cieSeleccion.subgrupo ?? cieSeleccion.cie11).id : null,
        cie10_detalle: cieVersion === "CIE10" ? cieSeleccion.cie10 : null,
        cie11_detalle: cieVersion === "CIE11" ? cieSeleccion.cie11 : null,
      }
      if (editandoId) {
        await actualizarNacimiento(editandoId, payload)
        setEstado({ tipo: "ok", texto: `Registro #${editandoId} actualizado.` })
      } else {
        const creado = await crearNacimiento(payload)
        setEstado({ tipo: "ok", texto: `Registro creado: ${creado.registro_numero} #${creado.id}` })
      }
      const nuevaLista = await listarNacimientos()
      setLista(nuevaLista)
      obtenerDashboard()
        .then((d) => setStats({ total: d.totales.nacimientos, nacidos_vivos: d.nacimientos_salud.nacidos_vivos, por_sexo: d.nacimientos_salud.por_sexo, por_tipo_parto: d.nacimientos_salud.por_tipo_parto }))
        .catch(() => null)
      cancelarEdicion()
    } catch (err) {
      setEstado({ tipo: "error", texto: err.message })
    }
  }

  const observaciones = (col, rotulo) =>
    `${rotulo}: ${col ? `${col} ` : ""} ${stats ? Object.entries(stats[col]).map(([k, v]) => `${k}: ${v}`).join(", ") : ""}`

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Registro de Nacimientos</h1>
        <p>Formulario de carga - SISV. Los códigos CIE se validan contra el catálogo según la fecha del evento.</p>
      </header>

      {stats && (
        <div className="stats">
          <span><b>{stats.total}</b> registros</span>
          <span title={observaciones("por_sexo", "Por sexo")}><b>{stats.nacidos_vivos}</b> nacidos vivos</span>
        </div>
      )}

      {estado.tipo && (
        <div className={`aviso aviso-${estado.tipo}`} role="status">
          {estado.texto}
        </div>
      )}

      {editandoId && (
        <div className="aviso aviso-editando">
          Editando el registro de nacimiento <strong>#{editandoId}</strong>.
          <button type="button" className="btn-mini" onClick={cancelarEdicion}>
            Cancelar edición
          </button>
        </div>
      )}

      <form className="formulario" onSubmit={enviar} noValidate>
        {!permisos.puede_escribir && (
          <div className="aviso aviso-info">
            Su rol (<strong>{usuario?.rol_label}</strong>) es de solo lectura: no está habilitada la carga de registros.
          </div>
        )}
        <fieldset disabled={!permisos.puede_escribir}>
        <Seccion titulo="1. Registro civil">
          <Campo label="Nº de registro" htmlFor="registro_numero" error={errores.registro_numero}>
            <Input
              id="registro_numero"
              value={form.registro_numero}
              error={errores.registro_numero}
              onChange={(e) => cambiar("registro_numero", e.target.value)}
              placeholder="NC-YYYY-XXXXXX"
            />
          </Campo>
          <Campo label="Lote de carga (opcional)" htmlFor="lote_id">
            <Input id="lote_id" value={form.lote_id} onChange={(e) => cambiar("lote_id", e.target.value)} />
          </Campo>
          <Campo label="Libro" htmlFor="libro">
            <Input id="libro" value={form.libro} onChange={(e) => cambiar("libro", e.target.value)} />
          </Campo>
          <Campo label="Folio" htmlFor="folio">
            <Input id="folio" type="number" value={form.folio} onChange={(e) => cambiar("folio", e.target.value)} />
          </Campo>
          <Campo label="Acta" htmlFor="acta">
            <Input id="acta" type="number" value={form.acta} onChange={(e) => cambiar("acta", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="2. Datos del nacimiento">
          <Campo label="Fecha de nacimiento" htmlFor="fecha_evento" error={errores.fecha_evento}>
            <Input
              id="fecha_evento"
              type="date"
              value={form.fecha_evento}
              error={errores.fecha_evento}
              onChange={(e) => cambiar("fecha_evento", e.target.value)}
            />
          </Campo>
          <Campo label="Hora" htmlFor="hora_nacimiento">
            <Input id="hora_nacimiento" type="time" value={form.hora_nacimiento} onChange={(e) => cambiar("hora_nacimiento", e.target.value)} />
          </Campo>
          <Campo label="Sexo" htmlFor="sexo" error={errores.sexo}>
            <Select id="sexo" opciones={OPCIONES.SEXO} value={form.sexo} onChange={(e) => cambiar("sexo", e.target.value)} />
          </Campo>
          <Campo label="Peso al nacer (gramos)" htmlFor="peso_gramos">
            <Input id="peso_gramos" type="number" min="200" max="8000" value={form.peso_gramos} onChange={(e) => cambiar("peso_gramos", e.target.value)} />
          </Campo>
          <Campo label="Talla (cm)" htmlFor="talla_cm">
            <Input id="talla_cm" type="number" step="0.1" value={form.talla_cm} onChange={(e) => cambiar("talla_cm", e.target.value)} />
          </Campo>
          <Campo label="Edad gestacional (semanas)" htmlFor="edad_gestacional_semanas">
            <Input id="edad_gestacional_semanas" type="number" min="20" max="44" value={form.edad_gestacional_semanas} onChange={(e) => cambiar("edad_gestacional_semanas", e.target.value)} />
          </Campo>
          <Campo label="Tipo de parto" htmlFor="tipo_parto">
            <Select id="tipo_parto" opciones={OPCIONES.TIPO_PARTO} value={form.tipo_parto} onChange={(e) => cambiar("tipo_parto", e.target.value)} />
          </Campo>
          <Campo label="Tipo de embarazo" htmlFor="tipo_embarazo">
            <Select id="tipo_embarazo" opciones={OPCIONES.TIPO_EMBARAZO} value={form.tipo_embarazo} onChange={(e) => cambiar("tipo_embarazo", e.target.value)} />
          </Campo>
          <Campo label="Nº gemelar" htmlFor="numero_gemelar">
            <Input id="numero_gemelar" type="number" min="1" value={form.numero_gemelar} onChange={(e) => cambiar("numero_gemelar", e.target.value)} />
          </Campo>
          <Campo label="Sitio del nacimiento" htmlFor="sitio_nacimiento">
            <Select id="sitio_nacimiento" opciones={OPCIONES.SITIO} value={form.sitio_nacimiento} onChange={(e) => cambiar("sitio_nacimiento", e.target.value)} />
          </Campo>
          <Campo label="Establecimiento" htmlFor="establecimiento">
            <Input id="establecimiento" value={form.establecimiento} onChange={(e) => cambiar("establecimiento", e.target.value)} />
          </Campo>
          <SelectTerritorial
            valor={{ estado: form.estado, municipio: form.municipio, parroquia: form.parroquia, comunidad: form.comunidad }}
            onChange={(t) => setForm((f) => ({ ...f, ...t }))}
          />
          <CentroSelector usuario={usuario} value={form.organizacion} onChange={(v) => cambiar("organizacion", v)} />
          <Campo label="Apgar 1 min" htmlFor="apgar_1m">
            <Input id="apgar_1m" type="number" min="0" max="10" value={form.apgar_1m} onChange={(e) => cambiar("apgar_1m", e.target.value)} />
          </Campo>
          <Campo label="Apgar 5 min" htmlFor="apgar_5m">
            <Input id="apgar_5m" type="number" min="0" max="10" value={form.apgar_5m} onChange={(e) => cambiar("apgar_5m", e.target.value)} />
          </Campo>
          <label className="checkbox">
            <input type="checkbox" checked={form.nacido_vivo} onChange={(e) => cambiar("nacido_vivo", e.target.checked)} />
            Nacido vivo
          </label>
        </Seccion>

        <Seccion titulo="3. Datos de la madre">
          <Campo label="Nombres" htmlFor="madre_nombres" error={errores.madre_nombres}>
            <Input id="madre_nombres" value={form.madre_nombres} error={errores.madre_nombres} onChange={(e) => cambiar("madre_nombres", e.target.value)} />
          </Campo>
          <Campo label="Apellidos" htmlFor="madre_apellidos" error={errores.madre_apellidos}>
            <Input id="madre_apellidos" value={form.madre_apellidos} error={errores.madre_apellidos} onChange={(e) => cambiar("madre_apellidos", e.target.value)} />
          </Campo>
          <Campo label="Cédula" htmlFor="madre_cedula" error={errores.madre_cedula}>
            <Input id="madre_cedula" value={form.madre_cedula} error={errores.madre_cedula} onChange={(e) => cambiar("madre_cedula", e.target.value)} placeholder="V-12345678" />
          </Campo>
          <Campo label="Edad" htmlFor="madre_edad" error={errores.madre_edad}>
            <Input id="madre_edad" type="number" min="10" max="60" value={form.madre_edad} error={errores.madre_edad} onChange={(e) => cambiar("madre_edad", e.target.value)} />
          </Campo>
          <Campo label="Estado civil" htmlFor="madre_estado_civil">
            <Select id="madre_estado_civil" opciones={OPCIONES.ESTADO_CIVIL} value={form.madre_estado_civil} onChange={(e) => cambiar("madre_estado_civil", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="4. Datos del padre (opcional)">
          {[
            ["padre_nombres", "Nombres"],
            ["padre_apellidos", "Apellidos"],
            ["padre_cedula", "Cédula"],
          ].map(([campo, rotulo]) => (
            <Campo key={campo} label={rotulo} htmlFor={campo}>
              <Input id={campo} value={form[campo]} onChange={(e) => cambiar(campo, e.target.value)} />
            </Campo>
          ))}
        </Seccion>

        <SeccionCIE
          titulo="5. Clasificación CIE (morbilidad o condición del recién nacido)"
          etiqueta="Diagnóstico / Condición"
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
          <Boton disabled={!permisos.puede_escribir}>{editandoId ? "Guardar cambios del registro" : "Guardar registro de nacimiento"}</Boton>
        </div>
      </form>

      <section className="lista">
        <h2>Últimos registros ({lista.length})</h2>
        <table>
          <thead>
            <tr>
              <th>Nº</th>
              <th>Fecha</th>
              <th>Sexo</th>
              <th>Peso</th>
              <th>Parto</th>
              <th>Madre (cédula)</th>
              <th>Establecimiento</th>
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
                <td>{r.sexo_label || r.sexo}</td>
                <td>{r.peso_gramos ? `${r.peso_gramos} g` : "—"}</td>
                <td>{r.tipo_parto_label || r.tipo_parto}</td>
                <td>{r.madre_cedula}</td>
                <td>{r.establecimiento || "—"}</td>
                <td>
                  {r.cie10_detalle
                    ? `${r.cie10_detalle.codigo} (CIE-10)`
                    : r.cie11_detalle
                      ? `${r.cie11_detalle.codigo} (CIE-11)`
                      : "—"}
                </td>
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