import { useEffect, useState } from "react"
import {
  actualizarDesignacion,
  actualizarRegistrador,
  actualizarRegistroCivil,
  crearDesignacion,
  crearRegistrador,
  crearRegistroCivil,
  eliminarDesignacion,
  eliminarRegistrador,
  eliminarRegistroCivil,
  listarDesignaciones,
  listarOrganizaciones,
  listarRegistradores,
  listarRegistrosCiviles,
  quienFirmaba,
} from "../api/sisv"
import { Boton, Campo, Input, Select } from "../components/ui"

const RC_VACIO = {
  nombre: "",
  organizacion: "",
  estado: "",
  municipio: "",
  parroquia: "",
  activo: true,
  observaciones: "",
}

const REG_VACIO = {
  nacionalidad: "V",
  cedula: "",
  nombres: "",
  apellidos: "",
  telefono: "",
  email: "",
  activo: true,
  observaciones: "",
}

const DIS_VACIO = {
  registro_civil: "",
  registrador: "",
  cargo: "TITULAR",
  desde: "",
  hasta: "",
  fecha_toma_posesion: "",
  acta_nombramiento: "",
  observaciones: "",
}

const CARGOS = [
  ["TITULAR", "Titular"],
  ["SUPLENTE", "Suplente"],
  ["ENCARGADO", "Encargado"],
]

const NACIONALIDADES = [
  ["V", "Venezolano"],
  ["E", "Extranjero"],
  ["P", "Pasaporte"],
  ["I", "Indocumentado"],
  ["O", "Otro"],
]

const SIN_VALOR = (v) => (v === "" || v === undefined ? null : v)

export default function Registradores({ usuario }) {
  const puedeEscribir = Boolean(usuario?.permisos?.puede_despachar)

  const [registros, setRegistros] = useState([])
  const [registradores, setRegistradores] = useState([])
  const [designaciones, setDesignaciones] = useState([])
  const [organizaciones, setOrganizaciones] = useState([])
  const [cargando, setCargando] = useState(true)
  const [estado, setEstado] = useState({ tipo: "", texto: "" })

  const [formRC, setFormRC] = useState(RC_VACIO)
  const [rcEditando, setRcEditando] = useState(null)
  const [formReg, setFormReg] = useState(REG_VACIO)
  const [regEditando, setRegEditando] = useState(null)
  const [formDis, setFormDis] = useState(DIS_VACIO)
  const [disEditando, setDisEditando] = useState(null)

  const [consulta, setConsulta] = useState({ registro_civil: "", fecha: "" })
  const [resultado, setResultado] = useState(null)

  function avisar(tipo, texto) {
    setEstado({ tipo, texto })
  }

  async function cargarTodo() {
    try {
      const [rc, rg, ds] = await Promise.all([
        listarRegistrosCiviles(),
        listarRegistradores(),
        listarDesignaciones(),
      ])
      setRegistros(rc.items)
      setRegistradores(rg.items)
      setDesignaciones(ds.items)
    } catch (e) {
      avisar("error", e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargarTodo()
    listarOrganizaciones()
      .then(setOrganizaciones)
      .catch(() => setOrganizaciones([]))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // -- Registros civiles ----------------------------------------------------
  async function guardarRC(e) {
    e.preventDefault()
    const payload = { ...formRC, organizacion: SIN_VALOR(formRC.organizacion) }
    try {
      if (rcEditando) {
        await actualizarRegistroCivil(rcEditando, payload)
        avisar("ok", `Registro civil «${payload.nombre}» actualizado.`)
      } else {
        await crearRegistroCivil(payload)
        avisar("ok", `Registro civil «${payload.nombre}» creado.`)
      }
      setFormRC(RC_VACIO)
      setRcEditando(null)
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  function editarRC(rc) {
    setFormRC({
      nombre: rc.nombre,
      organizacion: rc.organizacion ? String(rc.organizacion) : "",
      estado: rc.estado || "",
      municipio: rc.municipio || "",
      parroquia: rc.parroquia || "",
      activo: rc.activo,
      observaciones: rc.observaciones || "",
    })
    setRcEditando(rc.id)
  }

  async function borrarRC(rc) {
    if (!window.confirm(`¿Eliminar el registro civil «${rc.nombre}»?`)) return
    try {
      await eliminarRegistroCivil(rc.id)
      avisar("ok", `Registro civil «${rc.nombre}» eliminado.`)
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  // -- Registradores --------------------------------------------------------
  async function guardarReg(e) {
    e.preventDefault()
    try {
      if (regEditando) {
        await actualizarRegistrador(regEditando, formReg)
        avisar("ok", `Registrador «${formReg.nombres} ${formReg.apellidos}» actualizado.`)
      } else {
        await crearRegistrador(formReg)
        avisar("ok", `Registrador «${formReg.nombres} ${formReg.apellidos}» creado.`)
      }
      setFormReg(REG_VACIO)
      setRegEditando(null)
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  function editarReg(r) {
    setFormReg({
      nacionalidad: r.nacionalidad,
      cedula: r.cedula,
      nombres: r.nombres,
      apellidos: r.apellidos,
      telefono: r.telefono || "",
      email: r.email || "",
      activo: r.activo,
      observaciones: r.observaciones || "",
    })
    setRegEditando(r.id)
  }

  async function borrarReg(r) {
    if (!window.confirm(`¿Eliminar al registrador «${r.nombre_completo}»?`)) return
    try {
      await eliminarRegistrador(r.id)
      avisar("ok", `Registrador «${r.nombre_completo}» eliminado.`)
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  // -- Designaciones --------------------------------------------------------
  async function guardarDis(e) {
    e.preventDefault()
    const payload = {
      ...formDis,
      hasta: SIN_VALOR(formDis.hasta),
      fecha_toma_posesion: SIN_VALOR(formDis.fecha_toma_posesion),
    }
    try {
      if (disEditando) {
        await actualizarDesignacion(disEditando, payload)
        avisar("ok", "Designación actualizada.")
      } else {
        await crearDesignacion(payload)
        avisar("ok", "Designación registrada.")
      }
      setFormDis(DIS_VACIO)
      setDisEditando(null)
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  function editarDis(d) {
    setFormDis({
      registro_civil: String(d.registro_civil),
      registrador: String(d.registrador),
      cargo: d.cargo,
      desde: d.desde,
      hasta: d.hasta || "",
      fecha_toma_posesion: d.fecha_toma_posesion || "",
      acta_nombramiento: d.acta_nombramiento || "",
      observaciones: d.observaciones || "",
    })
    setDisEditando(d.id)
  }

  async function borrarDis(d) {
    if (!window.confirm("¿Eliminar esta designación del historial?")) return
    try {
      await eliminarDesignacion(d.id)
      avisar("ok", "Designación eliminada.")
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  // -- Consulta retroactiva -------------------------------------------------
  async function consultar(e) {
    e.preventDefault()
    if (!consulta.registro_civil || !consulta.fecha) {
      avisar("error", "Indique el registro civil y la fecha.")
      return
    }
    try {
      setResultado(await quienFirmaba(consulta.registro_civil, consulta.fecha))
    } catch (err) {
      avisar("error", err.message)
    }
  }

  const opcionesRC = registros.map((r) => [String(r.id), r.nombre])
  const opcionesReg = registradores.map((r) => [
    String(r.id),
    `${r.cedula_completa} ${r.nombre_completo}`,
  ])
  const nombreRC = (id) => registros.find((r) => r.id === id)?.nombre || `#${id}`

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Registradores civiles</h1>
        <p>
          Quién está a cargo de cada registro civil y desde qué fecha. El historial
          permite saber de forma retroactiva quién firmaba un certificado en una fecha.
        </p>
      </header>

      {estado.tipo && (
        <p className={`aviso ${estado.tipo}`} role="status">
          {estado.texto}
        </p>
      )}

      {/* -- Registros civiles -- */}
      <form onSubmit={guardarRC} className="seccion">
        <h2>{rcEditando ? "Editar registro civil" : "Nuevo registro civil"}</h2>
        <fieldset disabled={!puedeEscribir}>
          <div className="grid">
            <Campo label="Nombre">
              <Input
                value={formRC.nombre}
                required
                onChange={(e) => setFormRC((f) => ({ ...f, nombre: e.target.value }))}
              />
            </Campo>
            <Campo label="Centro / organización (opcional)">
              <Select
                opciones={organizaciones.map((o) => [String(o.id), o.nombre])}
                value={formRC.organizacion}
                onChange={(e) => setFormRC((f) => ({ ...f, organizacion: e.target.value }))}
              />
            </Campo>
            <Campo label="Estado">
              <Input
                value={formRC.estado}
                onChange={(e) => setFormRC((f) => ({ ...f, estado: e.target.value }))}
              />
            </Campo>
            <Campo label="Municipio">
              <Input
                value={formRC.municipio}
                onChange={(e) => setFormRC((f) => ({ ...f, municipio: e.target.value }))}
              />
            </Campo>
            <Campo label="Parroquia">
              <Input
                value={formRC.parroquia}
                onChange={(e) => setFormRC((f) => ({ ...f, parroquia: e.target.value }))}
              />
            </Campo>
            <Campo label="Activo">
              <Select
                opciones={[["true", "Sí"], ["false", "No"]]}
                value={String(formRC.activo)}
                onChange={(e) => setFormRC((f) => ({ ...f, activo: e.target.value === "true" }))}
              />
            </Campo>
          </div>
          {puedeEscribir && (
            <div className="pie-form">
              <Boton>{rcEditando ? "Guardar cambios" : "Crear registro civil"}</Boton>
              {rcEditando && (
                <button
                  type="button"
                  className="boton secundario"
                  onClick={() => {
                    setFormRC(RC_VACIO)
                    setRcEditando(null)
                  }}
                >
                  Cancelar
                </button>
              )}
            </div>
          )}
        </fieldset>
      </form>

      <section className="lista">
        <div className="cabecera-lista">
          <h2>Registros civiles ({registros.length})</h2>
        </div>
        {cargando ? (
          <p className="ayuda">Cargando…</p>
        ) : registros.length === 0 ? (
          <p className="ayuda">No hay registros civiles.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Centro</th>
                <th>Ubicación</th>
                <th>Designaciones</th>
                <th>Activo</th>
                {puedeEscribir && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {registros.map((rc) => (
                <tr key={rc.id}>
                  <td>{rc.nombre}</td>
                  <td>{rc.organizacion_nombre || "—"}</td>
                  <td>
                    {rc.estado || "—"} · {rc.municipio || "—"}
                  </td>
                  <td>{rc.designaciones_count}</td>
                  <td>{rc.activo ? "Sí" : "No"}</td>
                  {puedeEscribir && (
                    <td className="acciones">
                      <button type="button" className="btn-mini" onClick={() => editarRC(rc)}>
                        Editar
                      </button>
                      <button type="button" className="btn-mini peligro" onClick={() => borrarRC(rc)}>
                        Eliminar
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* -- Registradores -- */}
      <form onSubmit={guardarReg} className="seccion">
        <h2>{regEditando ? "Editar registrador" : "Nuevo registrador"}</h2>
        <fieldset disabled={!puedeEscribir}>
          <div className="grid">
            <Campo label="Nacionalidad">
              <Select
                opciones={NACIONALIDADES}
                value={formReg.nacionalidad}
                onChange={(e) => setFormReg((f) => ({ ...f, nacionalidad: e.target.value }))}
              />
            </Campo>
            <Campo label="Cédula">
              <Input
                value={formReg.cedula}
                required
                onChange={(e) => setFormReg((f) => ({ ...f, cedula: e.target.value }))}
              />
            </Campo>
            <Campo label="Nombres">
              <Input
                value={formReg.nombres}
                required
                onChange={(e) => setFormReg((f) => ({ ...f, nombres: e.target.value }))}
              />
            </Campo>
            <Campo label="Apellidos">
              <Input
                value={formReg.apellidos}
                required
                onChange={(e) => setFormReg((f) => ({ ...f, apellidos: e.target.value }))}
              />
            </Campo>
            <Campo label="Teléfono">
              <Input
                value={formReg.telefono}
                onChange={(e) => setFormReg((f) => ({ ...f, telefono: e.target.value }))}
              />
            </Campo>
            <Campo label="Correo">
              <Input
                type="email"
                value={formReg.email}
                onChange={(e) => setFormReg((f) => ({ ...f, email: e.target.value }))}
              />
            </Campo>
            <Campo label="Activo">
              <Select
                opciones={[["true", "Sí"], ["false", "No"]]}
                value={String(formReg.activo)}
                onChange={(e) => setFormReg((f) => ({ ...f, activo: e.target.value === "true" }))}
              />
            </Campo>
          </div>
          {puedeEscribir && (
            <div className="pie-form">
              <Boton>{regEditando ? "Guardar cambios" : "Crear registrador"}</Boton>
              {regEditando && (
                <button
                  type="button"
                  className="boton secundario"
                  onClick={() => {
                    setFormReg(REG_VACIO)
                    setRegEditando(null)
                  }}
                >
                  Cancelar
                </button>
              )}
            </div>
          )}
        </fieldset>
      </form>

      <section className="lista">
        <div className="cabecera-lista">
          <h2>Registradores ({registradores.length})</h2>
        </div>
        {registradores.length === 0 ? (
          <p className="ayuda">No hay registradores registrados.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Cédula</th>
                <th>Nombres y apellidos</th>
                <th>Teléfono</th>
                <th>Correo</th>
                <th>Activo</th>
                {puedeEscribir && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {registradores.map((r) => (
                <tr key={r.id}>
                  <td>{r.cedula_completa}</td>
                  <td>{r.nombre_completo}</td>
                  <td>{r.telefono || "—"}</td>
                  <td>{r.email || "—"}</td>
                  <td>{r.activo ? "Sí" : "No"}</td>
                  {puedeEscribir && (
                    <td className="acciones">
                      <button type="button" className="btn-mini" onClick={() => editarReg(r)}>
                        Editar
                      </button>
                      <button type="button" className="btn-mini peligro" onClick={() => borrarReg(r)}>
                        Eliminar
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* -- Designaciones -- */}
      <form onSubmit={guardarDis} className="seccion">
        <h2>{disEditando ? "Editar designación" : "Nueva designación (vigencia)"}</h2>
        <fieldset disabled={!puedeEscribir}>
          <div className="grid">
            <Campo label="Registro civil">
              <Select
                opciones={opcionesRC}
                value={formDis.registro_civil}
                required
                onChange={(e) => setFormDis((f) => ({ ...f, registro_civil: e.target.value }))}
              />
            </Campo>
            <Campo label="Registrador">
              <Select
                opciones={opcionesReg}
                value={formDis.registrador}
                required
                onChange={(e) => setFormDis((f) => ({ ...f, registrador: e.target.value }))}
              />
            </Campo>
            <Campo label="Cargo">
              <Select
                opciones={CARGOS}
                value={formDis.cargo}
                onChange={(e) => setFormDis((f) => ({ ...f, cargo: e.target.value }))}
              />
            </Campo>
            <Campo label="Vigente desde">
              <Input
                type="date"
                value={formDis.desde}
                required
                onChange={(e) => setFormDis((f) => ({ ...f, desde: e.target.value }))}
              />
            </Campo>
            <Campo label="Vigente hasta (vacío = vigente)">
              <Input
                type="date"
                value={formDis.hasta}
                onChange={(e) => setFormDis((f) => ({ ...f, hasta: e.target.value }))}
              />
            </Campo>
            <Campo label="Fecha de toma de posesión">
              <Input
                type="date"
                value={formDis.fecha_toma_posesion}
                onChange={(e) => setFormDis((f) => ({ ...f, fecha_toma_posesion: e.target.value }))}
              />
            </Campo>
            <Campo label="Acta / nombramiento">
              <Input
                value={formDis.acta_nombramiento}
                onChange={(e) => setFormDis((f) => ({ ...f, acta_nombramiento: e.target.value }))}
              />
            </Campo>
          </div>
          {puedeEscribir && (
            <div className="pie-form">
              <Boton>{disEditando ? "Guardar cambios" : "Registrar designación"}</Boton>
              {disEditando && (
                <button
                  type="button"
                  className="boton secundario"
                  onClick={() => {
                    setFormDis(DIS_VACIO)
                    setDisEditando(null)
                  }}
                >
                  Cancelar
                </button>
              )}
            </div>
          )}
        </fieldset>
      </form>

      <section className="lista">
        <div className="cabecera-lista">
          <h2>Historial de designaciones ({designaciones.length})</h2>
        </div>
        {designaciones.length === 0 ? (
          <p className="ayuda">No hay designaciones registradas.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Registro civil</th>
                <th>Registrador</th>
                <th>Cargo</th>
                <th>Desde</th>
                <th>Hasta</th>
                <th>Vigente</th>
                {puedeEscribir && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {designaciones.map((d) => (
                <tr key={d.id}>
                  <td>{d.registro_civil_nombre}</td>
                  <td>
                    {d.registrador_cedula} {d.registrador_nombre}
                  </td>
                  <td>{d.cargo_label}</td>
                  <td>{d.desde}</td>
                  <td>{d.hasta || "—"}</td>
                  <td>{d.vigente ? "Sí" : "No"}</td>
                  {puedeEscribir && (
                    <td className="acciones">
                      <button type="button" className="btn-mini" onClick={() => editarDis(d)}>
                        Editar
                      </button>
                      <button type="button" className="btn-mini peligro" onClick={() => borrarDis(d)}>
                        Eliminar
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* -- Consulta retroactiva -- */}
      <form onSubmit={consultar} className="seccion">
        <h2>¿Quién firmaba en una fecha?</h2>
        <div className="grid">
          <Campo label="Registro civil">
            <Select
              opciones={opcionesRC}
              value={consulta.registro_civil}
              required
              onChange={(e) => setConsulta((c) => ({ ...c, registro_civil: e.target.value }))}
            />
          </Campo>
          <Campo label="Fecha del hecho">
            <Input
              type="date"
              value={consulta.fecha}
              required
              onChange={(e) => setConsulta((c) => ({ ...c, fecha: e.target.value }))}
            />
          </Campo>
        </div>
        <div className="pie-form">
          <Boton>Consultar</Boton>
        </div>
        {resultado && (
          <div className="resultado-consulta">
            <p className="ayuda">
              {nombreRC(resultado.registro_civil)} · {resultado.fecha}
            </p>
            {resultado.vigentes.length === 0 ? (
              <p className="ayuda">No había ningún registrador designado en esa fecha.</p>
            ) : (
              <ul>
                {resultado.vigentes.map((v) => (
                  <li key={v.id}>
                    <strong>
                      {v.registrador_cedula} {v.registrador_nombre}
                    </strong>{" "}
                    — {v.cargo_label} (desde {v.desde}
                    {v.hasta ? ` hasta ${v.hasta}` : ", vigente"})
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </form>
    </div>
  )
}
