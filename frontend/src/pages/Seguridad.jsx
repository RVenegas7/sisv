import { useEffect, useState } from "react"
import {
  crearOrganizacion,
  actualizarOrganizacion,
  eliminarOrganizacion,
  crearUsuario,
  actualizarUsuario,
  eliminarUsuario,
  listarOrganizaciones,
  listarRoles,
  listarUsuarios,
} from "../api/sisv"
import { Boton, Campo, Input, Select } from "../components/ui"

const NIVELES = [
  ["MINISTERIO", "Ministerio de Salud"],
  ["GOBERNACION", "Gobernación"],
  ["REGIONAL", "Dirección Regional"],
  ["CENTRO", "Centro de salud"],
]

const ESTADO_VACIO_USUARIO = {
  nombre: "",
  username: "",
  password: "",
  rol: "TRANSCRIPTOR",
  organizacion: "",
  activo: true,
  es_superusuario: false,
}

const ESTADO_VACIO_ORG = {
  codigo: "",
  nombre: "",
  nivel: "CENTRO",
  estado: "",
  municipio: "",
  padre: "",
}

export default function Seguridad({ usuario }) {
  const permisos = usuario?.permisos || {}
  const puedeConfigurar = Boolean(permisos.puede_configurar)
  const esSuper = Boolean(usuario?.es_superusuario)

  const [organizaciones, setOrganizaciones] = useState([])
  const [roles, setRoles] = useState([])
  const [usuarios, setUsuarios] = useState([])
  const [cargando, setCargando] = useState(true)

  const [formUsuario, setFormUsuario] = useState(ESTADO_VACIO_USUARIO)
  const [editandoUsuario, setEditandoUsuario] = useState(null)
  const [formOrg, setFormOrg] = useState(ESTADO_VACIO_ORG)
  const [editandoOrg, setEditandoOrg] = useState(null)
  const [estado, setEstado] = useState({ tipo: "", texto: "" })

  function cargarTodo() {
    return Promise.all([listarOrganizaciones(), listarRoles()])
      .then(([orgs, rls]) => {
        setOrganizaciones(orgs)
        setRoles(rls)
      })
      .catch((e) => avisar("error", e.message))
  }

  function avisar(tipo, texto) {
    setEstado({ tipo, texto })
  }

  useEffect(() => {
    const tareas = [cargarTodo()]
    if (puedeConfigurar) {
      tareas.push(listarUsuarios().then(setUsuarios).catch((e) => avisar("error", e.message)))
    }
    Promise.all(tareas).finally(() => setCargando(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  /* ---------- Usuarios ---------- */

  function usuarioAForm(u) {
    setFormUsuario({
      nombre: u.nombre === u.username ? "" : u.nombre,
      username: u.username,
      password: "",
      rol: u.rol || "TRANSCRIPTOR",
      organizacion: u.organizacion_id ? String(u.organizacion_id) : "",
      activo: u.activo,
      es_superusuario: Boolean(u.es_superusuario),
    })
    setEditandoUsuario(u)
  }

  function nuevoUsuario() {
    setFormUsuario(ESTADO_VACIO_USUARIO)
    setEditandoUsuario(null)
  }

  async function guardarUsuario(e) {
    e.preventDefault()
    const payload = {
      nombre: formUsuario.nombre,
      username: formUsuario.username,
      rol: formUsuario.rol,
      organizacion: formUsuario.organizacion ? Number(formUsuario.organizacion) : "",
      activo: formUsuario.activo,
    }
    if (esSuper) payload.es_superusuario = formUsuario.es_superusuario
    if (formUsuario.password) payload.password = formUsuario.password
    try {
      if (editandoUsuario) {
        await actualizarUsuario(editandoUsuario.id, payload)
        avisar("ok", `Usuario «${payload.username}» actualizado.`)
      } else {
        await crearUsuario(payload)
        avisar("ok", `Usuario «${payload.username}» creado.`)
      }
      nuevoUsuario()
      await listarUsuarios().then(setUsuarios)
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function borrarUsuario(u) {
    if (!window.confirm(`¿Eliminar el usuario «${u.username}»? Esta acción no se puede deshacer.`)) return
    try {
      await eliminarUsuario(u.id)
      avisar("ok", `Usuario «${u.username}» eliminado.`)
      if (editandoUsuario?.id === u.id) nuevoUsuario()
      await listarUsuarios().then(setUsuarios)
    } catch (err) {
      avisar("error", err.message)
    }
  }

  /* ---------- Organizaciones ---------- */

  function orgAForm(o) {
    setFormOrg({
      codigo: o.codigo,
      nombre: o.nombre,
      nivel: o.nivel,
      estado: o.estado,
      municipio: o.municipio,
      padre: o.padre_id ? String(o.padre_id) : "",
    })
    setEditandoOrg(o)
  }

  function nuevaOrg() {
    setFormOrg(ESTADO_VACIO_ORG)
    setEditandoOrg(null)
  }

  async function guardarOrg(e) {
    e.preventDefault()
    const payload = {
      codigo: formOrg.codigo,
      nombre: formOrg.nombre,
      nivel: formOrg.nivel,
      estado: formOrg.estado,
      municipio: formOrg.municipio,
      padre: formOrg.padre ? Number(formOrg.padre) : "",
    }
    try {
      if (editandoOrg) {
        await actualizarOrganizacion(editandoOrg.id, payload)
        avisar("ok", `Organización «${payload.nombre}» actualizada.`)
      } else {
        await crearOrganizacion(payload)
        avisar("ok", `Organización «${payload.nombre}» creada.`)
      }
      nuevaOrg()
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function borrarOrg(o) {
    if (
      !window.confirm(
        `¿Eliminar la organización «${o.nombre}»? No se podrá si tiene usuarios o sub-organizaciones asignadas.`
      )
    )
      return
    try {
      await eliminarOrganizacion(o.id)
      avisar("ok", `Organización «${o.nombre}» eliminada.`)
      if (editandoOrg?.id === o.id) nuevaOrg()
      await cargarTodo()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  const porNivel = (nivel) => organizaciones.filter((o) => o.nivel === nivel)

  if (cargando) return <div className="aviso aviso-info">Cargando seguridad y organización…</div>

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Seguridad y organización</h1>
        <p>Estructura multicliente del SISV: organizaciones, dependencias jerárquicas, roles y usuarios.</p>
      </header>

      {estado.tipo && (
        <div className={`aviso aviso-${estado.tipo}`} role="status">
          {estado.texto}
        </div>
      )}

      {puedeConfigurar ? (
        <>
          <section className="lista">
            <div className="cabecera-seccion">
              <h2>Usuarios</h2>
            </div>
            <form className="formulario" onSubmit={guardarUsuario} noValidate>
              <div className="grid">
                <Campo label="Nombre" htmlFor="us_nombre">
                  <Input id="us_nombre" value={formUsuario.nombre} onChange={(e) => setFormUsuario((f) => ({ ...f, nombre: e.target.value }))} />
                </Campo>
                <Campo label="Usuario (login)" htmlFor="us_username">
                  <Input id="us_username" value={formUsuario.username} onChange={(e) => setFormUsuario((f) => ({ ...f, username: e.target.value }))} />
                </Campo>
                <Campo label={editandoUsuario ? "Nueva clave (opcional)" : "Clave"} htmlFor="us_password">
                  <Input id="us_password" type="password" value={formUsuario.password} onChange={(e) => setFormUsuario((f) => ({ ...f, password: e.target.value }))} />
                </Campo>
                <Campo label="Rol" htmlFor="us_rol">
                  <Select
                    id="us_rol"
                    opciones={roles.map((r) => [r.valor, r.rotulo])}
                    value={formUsuario.rol}
                    onChange={(e) => setFormUsuario((f) => ({ ...f, rol: e.target.value }))}
                  />
                </Campo>
                <Campo label="Organización" htmlFor="us_org">
                  <Select
                    id="us_org"
                    opciones={organizaciones.map((o) => [`${o.id}`, `${o.nivel_label} — ${o.nombre}${o.estado ? ` (${o.estado})` : ""}`])}
                    value={formUsuario.organizacion}
                    onChange={(e) => setFormUsuario((f) => ({ ...f, organizacion: e.target.value }))}
                  />
                </Campo>
              </div>
              <div className="filas-campo">
                <label className="caja">
                  <input type="checkbox" checked={formUsuario.activo} onChange={(e) => setFormUsuario((f) => ({ ...f, activo: e.target.checked }))} />
                  Activo
                </label>
                {esSuper && (
                  <label className="caja">
                    <input type="checkbox" checked={formUsuario.es_superusuario} onChange={(e) => setFormUsuario((f) => ({ ...f, es_superusuario: e.target.checked }))} />
                    Superusuario
                  </label>
                )}
              </div>
              <div className="pie-form">
                <Boton>{editandoUsuario ? "Guardar cambios de usuario" : "Crear usuario"}</Boton>
                {editandoUsuario && (
                  <button type="button" className="btn-mini" onClick={nuevoUsuario}>
                    Cancelar edición
                  </button>
                )}
              </div>
            </form>

            {usuarios.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Nombre</th>
                    <th>Rol</th>
                    <th>Organización</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {usuarios.map((u) => (
                    <tr key={u.id} className={editandoUsuario?.id === u.id ? "fila-editando" : ""}>
                      <td>
                        {u.username}
                        {u.es_superusuario && <span className="etiqueta">super</span>}
                      </td>
                      <td>{u.nombre}</td>
                      <td>{u.rol_label || "—"}</td>
                      <td>{u.organizacion_nombre || "—"}</td>
                      <td>{u.activo ? "Activo" : "Inactivo"}</td>
                      <td className="acciones">
                        <button type="button" className="btn-mini" onClick={() => usuarioAForm(u)}>
                          Editar
                        </button>
                        {u.id !== usuario.id && (
                          <button type="button" className="btn-mini peligro" onClick={() => borrarUsuario(u)}>
                            Eliminar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="aviso aviso-info">Aún no hay usuarios registrados.</div>
            )}
          </section>

          <section className="lista">
            <div className="cabecera-seccion">
              <h2>Organizaciones</h2>
            </div>
            <form className="formulario" onSubmit={guardarOrg} noValidate>
              <div className="grid">
                <Campo label="Código" htmlFor="or_codigo">
                  <Input id="or_codigo" value={formOrg.codigo} onChange={(e) => setFormOrg((f) => ({ ...f, codigo: e.target.value }))} />
                </Campo>
                <Campo label="Nombre" htmlFor="or_nombre">
                  <Input id="or_nombre" value={formOrg.nombre} onChange={(e) => setFormOrg((f) => ({ ...f, nombre: e.target.value }))} />
                </Campo>
                <Campo label="Nivel" htmlFor="or_nivel">
                  <Select id="or_nivel" opciones={NIVELES} value={formOrg.nivel} onChange={(e) => setFormOrg((f) => ({ ...f, nivel: e.target.value }))} />
                </Campo>
                <Campo label="Depende de" htmlFor="or_padre">
                  <Select
                    id="or_padre"
                    opciones={organizaciones
                      .filter((o) => o.id !== editandoOrg?.id)
                      .map((o) => [`${o.id}`, `${o.nivel_label} — ${o.nombre}`])}
                    value={formOrg.padre}
                    onChange={(e) => setFormOrg((f) => ({ ...f, padre: e.target.value }))}
                  />
                </Campo>
                <Campo label="Estado" htmlFor="or_estado">
                  <Input id="or_estado" value={formOrg.estado} onChange={(e) => setFormOrg((f) => ({ ...f, estado: e.target.value }))} />
                </Campo>
                <Campo label="Municipio" htmlFor="or_municipio">
                  <Input id="or_municipio" value={formOrg.municipio} onChange={(e) => setFormOrg((f) => ({ ...f, municipio: e.target.value }))} />
                </Campo>
              </div>
              <div className="pie-form">
                <Boton>{editandoOrg ? "Guardar cambios de organización" : "Crear organización"}</Boton>
                {editandoOrg && (
                  <button type="button" className="btn-mini" onClick={nuevaOrg}>
                    Cancelar edición
                  </button>
                )}
              </div>
            </form>

            {porNivel("MINISTERIO")
              .concat(porNivel("GOBERNACION"), porNivel("REGIONAL"), porNivel("CENTRO"))
              .map((o) => {
                const hijos = organizaciones.filter((h) => h.padre_id === o.id)
                return (
                  <table key={o.id}>
                    <tbody>
                      <tr className="fila-jerarquia">
                        <td colSpan={6}>
                          <strong>
                            {o.codigo} — {o.nivel_label} — {o.nombre}
                          </strong>
                          {o.estado && <span> · {o.estado}</span>}
                          {o.municipio && <span> · {o.municipio}</span>}
                          <span className="acciones-der">
                            <button type="button" className="btn-mini" onClick={() => orgAForm(o)}>
                              Editar
                            </button>
                            <button type="button" className="btn-mini peligro" onClick={() => borrarOrg(o)}>
                              Eliminar
                            </button>
                          </span>
                        </td>
                      </tr>
                      {hijos.map((h) => (
                        <tr key={h.id}>
                          <td>{h.codigo}</td>
                          <td>{h.nivel_label}</td>
                          <td>{h.nombre}</td>
                          <td>{o.nombre}</td>
                          <td>{h.estado || "—"}</td>
                          <td>{h.municipio || "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
              })}
            {organizaciones.length === 0 && (
              <div className="aviso aviso-info">No hay organizaciones registradas. Cree la primera con el formulario.</div>
            )}
          </section>
        </>
      ) : (
        <div className="aviso aviso-info">
          Su rol (<strong>{usuario?.rol_label || "sin rol"}</strong>) no tiene permiso para crear, editar o eliminar usuarios y
          organizaciones. Solo un <strong>Director</strong> o el superusuario puede administrarlos.
        </div>
      )}

      {!puedeConfigurar && porNivel("MINISTERIO").concat(porNivel("GOBERNACION")).map((o) => {
        const hijos = organizaciones.filter((h) => h.padre_id === o.id)
        return (
          <section className="lista" key={o.id}>
            <h2>
              {o.nivel_label} — {o.nombre}
            </h2>
            {hijos.length > 0 && (
              <table>
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Nivel</th>
                    <th>Nombre</th>
                    <th>Estado</th>
                    <th>Municipio</th>
                  </tr>
                </thead>
                <tbody>
                  {hijos.map((h) => (
                    <tr key={h.id}>
                      <td>{h.codigo}</td>
                      <td>{h.nivel_label}</td>
                      <td>{h.nombre}</td>
                      <td>{h.estado || "—"}</td>
                      <td>{h.municipio || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        )
      })}

      {roles.length > 0 && (
        <section className="lista">
          <h2>Roles de usuario</h2>
          <table>
            <thead>
              <tr>
                <th>Rol</th>
                <th>Descripción prevista</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((r) => (
                <tr key={r.valor}>
                  <td>
                    <strong>{r.rotulo}</strong> <small>({r.valor})</small>
                  </td>
                  <td>
                    {r.valor === "TRANSCRIPTOR" && "Carga registros de nacimiento, defunción y vigilancia."}
                    {r.valor === "CODIFICADOR" && "Valida y codifica diagnósticos CIE-10 / CIE-11."}
                    {r.valor === "EPIDEMIOLOGO" && "Consulta reportes e indicadores de vigilancia."}
                    {r.valor === "VIGILANCIA" && "Carga y revisa el consolidado semanal, fichas y alertas epidemiológicas."}
                    {r.valor === "SECRETARIA" && "Consulta y habilita trámites administrativos (solo lectura de registros)."}
                    {r.valor === "DIRECTOR" && "Administra configuración, organización y usuarios."}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}