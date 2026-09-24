import { useEffect, useState } from "react"
import {
  actualizarAsic,
  crearAsic,
  eliminarAsic,
  listarAsics,
  nivelTerritorial,
  obtenerAsic,
} from "../api/sisv"
import { Boton, Campo, Input, Select } from "../components/ui"

const VACIO = {
  codigo: "",
  nombre: "",
  estado: "",
  municipio: "",
  parroquia: "",
  direccion: "",
  responsable: "",
  telefono: "",
  email: "",
  establecimientos_adscritos: 0,
  observaciones: "",
  activo: true,
}

export default function Asic({ usuario }) {
  const puedeConfigurar = Boolean(usuario?.permisos?.puede_configurar)

  const [asics, setAsics] = useState([])
  const [cargando, setCargando] = useState(true)
  const [form, setForm] = useState(VACIO)
  const [editandoId, setEditandoId] = useState(null)
  const [estado, setEstado] = useState({ tipo: "", texto: "" })

  const [estados, setEstados] = useState([])
  const [municipios, setMunicipios] = useState([])
  const [parroquias, setParroquias] = useState([])
  const [comunidades, setComunidades] = useState([])
  const [sel, setSel] = useState({ estado: "", municipio: "", parroquia: "" })
  const [comunidadesSel, setComunidadesSel] = useState([])

  function avisar(tipo, texto) {
    setEstado({ tipo, texto })
  }

  async function cargarAsics() {
    try {
      const datos = await listarAsics()
      setAsics(datos)
    } catch (e) {
      avisar("error", e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargarAsics()
    nivelTerritorial("ESTADO")
      .then(setEstados)
      .catch(() => setEstados([]))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function pedir(nivel, padre) {
    try {
      return await nivelTerritorial(nivel, padre)
    } catch {
      return []
    }
  }

  async function cambiarEstado(id) {
    setSel({ estado: id, municipio: "", parroquia: "" })
    setMunicipios([])
    setParroquias([])
    setComunidades([])
    setComunidadesSel([])
    if (id) setMunicipios(await pedir("MUNICIPIO", id))
  }

  async function cambiarMunicipio(id) {
    setSel((s) => ({ ...s, municipio: id, parroquia: "" }))
    setParroquias([])
    setComunidades([])
    setComunidadesSel([])
    if (id) setParroquias(await pedir("PARROQUIA", id))
  }

  async function cambiarParroquia(id) {
    setSel((s) => ({ ...s, parroquia: id }))
    setComunidades([])
    setComunidadesSel([])
    if (id) setComunidades(await pedir("COMUNIDAD", id))
  }

  function alternarComunidad(id) {
    setComunidadesSel((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )
  }

  function nuevo() {
    setForm(VACIO)
    setSel({ estado: "", municipio: "", parroquia: "" })
    setComunidades([])
    setComunidadesSel([])
    setEditandoId(null)
  }

  async function editar(a) {
    setEditandoId(a.id)
    setForm({
      codigo: a.codigo,
      nombre: a.nombre,
      direccion: a.direccion || "",
      responsable: a.responsable || "",
      telefono: a.telefono || "",
      email: a.email || "",
      establecimientos_adscritos: a.establecimientos_adscritos || 0,
      observaciones: a.observaciones || "",
      activo: a.activo,
    })
    setComunidadesSel((a.comunidades || []).map((c) => c.id))
    if (a.parroquia_id) {
      const ruta = await obtenerAsic(a.id)
      setSel({ estado: "", municipio: "", parroquia: String(a.parroquia_id) })
      const est = await pedir("ESTADO")
      setEstados(est)
      const es = est.filter((x) => x.nombre === ruta.estado)
      const estId = es.length ? es[0].id : 0
      if (estId) {
        await cambiarEstado(String(estId))
        const muns = await pedir("MUNICIPIO", estId)
        setMunicipios(muns)
        const mu = muns.filter((x) => x.nombre === ruta.municipio)
        const muId = mu.length ? mu[0].id : 0
        if (muId) {
          await cambiarMunicipio(String(muId))
          const pars = await pedir("PARROQUIA", muId)
          setParroquias(pars)
          const pa = pars.filter((x) => x.nombre === ruta.parroquia)
          const paId = pa.length ? pa[0].id : 0
          if (paId) {
            await cambiarParroquia(String(paId))
          }
        }
      }
    }
  }

  async function guardar(e) {
    e.preventDefault()
    const payload = {
      codigo: form.codigo,
      nombre: form.nombre,
      parroquia: sel.parroquia ? Number(sel.parroquia) : null,
      direccion: form.direccion,
      responsable: form.responsable,
      telefono: form.telefono,
      email: form.email,
      establecimientos_adscritos: Number(form.establecimientos_adscritos) || 0,
      observaciones: form.observaciones,
      activo: form.activo,
      comunidades: comunidadesSel,
    }
    try {
      if (editandoId) {
        await actualizarAsic(editandoId, payload)
        avisar("ok", `ASIC «${payload.nombre}» actualizado.`)
      } else {
        await crearAsic(payload)
        avisar("ok", `ASIC «${payload.nombre}» creado.`)
      }
      nuevo()
      await cargarAsics()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function borrar(a) {
    if (!window.confirm(`¿Eliminar el ASIC «${a.nombre}» (${a.codigo})?`)) return
    try {
      await eliminarAsic(a.id)
      avisar("ok", `ASIC «${a.nombre}» eliminado.`)
      await cargarAsics()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Áreas de Salud Integral (ASIC)</h1>
        <p>Áreas de salud integral comunitaria: parroquia sede y comunidades del territorio que integran cada ASIC.</p>
      </header>

      {estado.tipo && (
        <p className={`aviso ${estado.tipo}`} role="status">
          {estado.texto}
        </p>
      )}

      <button type="button" className="boton enlace" onClick={nuevo}>
        + Nuevo ASIC
      </button>

      <form onSubmit={guardar} className="seccion">
        <h2>{editandoId ? "Editar ASIC" : "Crear ASIC"}</h2>
        <fieldset disabled={!puedeConfigurar}>
          <div className="grid">
            <Campo label="Código" htmlFor="asic-codigo">
              <Input
                id="asic-codigo"
                value={form.codigo}
                required
                onChange={(e) => setForm((f) => ({ ...f, codigo: e.target.value }))}
              />
            </Campo>
            <Campo label="Nombre" htmlFor="asic-nombre">
              <Input
                id="asic-nombre"
                value={form.nombre}
                required
                onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
              />
            </Campo>
            <Campo label="Estado">
              <Select
                opciones={estados.map((t) => [`${t.id}`, t.nombre])}
                value={sel.estado}
                onChange={(e) => cambiarEstado(e.target.value)}
              />
            </Campo>
            <Campo label="Municipio">
              <Select
                opciones={municipios.map((t) => [`${t.id}`, t.nombre])}
                value={sel.municipio}
                disabled={!sel.estado}
                onChange={(e) => cambiarMunicipio(e.target.value)}
              />
            </Campo>
            <Campo label="Parroquia sede">
              <Select
                opciones={parroquias.map((t) => [`${t.id}`, t.nombre])}
                value={sel.parroquia}
                disabled={!sel.municipio}
                onChange={(e) => cambiarParroquia(e.target.value)}
              />
            </Campo>
            <Campo label="Establecimientos adscritos" htmlFor="asic-est">
              <Input
                id="asic-est"
                type="number"
                min="0"
                value={form.establecimientos_adscritos}
                onChange={(e) => setForm((f) => ({ ...f, establecimientos_adscritos: e.target.value }))}
              />
            </Campo>
            <Campo label="Dirección" htmlFor="asic-dir">
              <Input
                id="asic-dir"
                value={form.direccion}
                onChange={(e) => setForm((f) => ({ ...f, direccion: e.target.value }))}
              />
            </Campo>
            <Campo label="Responsable" htmlFor="asic-resp">
              <Input
                id="asic-resp"
                value={form.responsable}
                onChange={(e) => setForm((f) => ({ ...f, responsable: e.target.value }))}
              />
            </Campo>
            <Campo label="Teléfono" htmlFor="asic-tel">
              <Input
                id="asic-tel"
                value={form.telefono}
                onChange={(e) => setForm((f) => ({ ...f, telefono: e.target.value }))}
              />
            </Campo>
            <Campo label="Correo" htmlFor="asic-email">
              <Input
                id="asic-email"
                type="email"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              />
            </Campo>
            <Campo label="Observaciones" htmlFor="asic-obs">
              <Input
                id="asic-obs"
                value={form.observaciones}
                onChange={(e) => setForm((f) => ({ ...f, observaciones: e.target.value }))}
              />
            </Campo>
            <Campo label="Activo">
              <Select
                opciones={[
                  ["true", "Sí"],
                  ["false", "No"],
                ]}
                value={String(form.activo)}
                onChange={(e) => setForm((f) => ({ ...f, activo: e.target.value === "true" }))}
              />
            </Campo>
          </div>

          {sel.parroquia && (
            <fieldset className="subseccion">
              <legend>Comunidades del territorio ({comunidades.length})</legend>
              {comunidades.length === 0 ? (
                <p className="ayuda">Esta parroquia no tiene comunidades registradas.</p>
              ) : (
                <div className="lista-checkboxes">
                  {comunidades.map((c) => (
                    <label key={c.id} className="caja item-fila">
                      <input
                        type="checkbox"
                        checked={comunidadesSel.includes(c.id)}
                        onChange={() => alternarComunidad(c.id)}
                      />
                      {c.nombre}
                    </label>
                  ))}
                </div>
              )}
            </fieldset>
          )}
        </fieldset>
        {puedeConfigurar && (
          <div className="pie-form">
            <Boton>{editandoId ? "Guardar cambios del ASIC" : "Crear ASIC"}</Boton>
            {editandoId && (
              <button type="button" className="boton secundario" onClick={nuevo}>
                Cancelar
              </button>
            )}
          </div>
        )}
      </form>

      <section className="lista">
        <div className="cabecera-lista">
          <h2>ASIC registrados</h2>
          <p className="ayuda">Recuerde: autorización solo para responsables (DIRECTOR / superusuario).</p>
        </div>
        {cargando ? (
          <p className="ayuda">Cargando ASIC…</p>
        ) : asics.length === 0 ? (
          <p className="ayuda">No hay ASIC registrados.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Ubicación</th>
                <th>Comunidades</th>
                <th>Centros</th>
                {puedeConfigurar && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {asics.map((a) => (
                <tr key={a.id}>
                  <td>{a.codigo}</td>
                  <td>{a.nombre}</td>
                  <td>
                    {a.estado || "—"} · {a.municipio || "—"} · {a.parroquia || "—"}
                  </td>
                  <td>{a.comunidad_count}</td>
                  <td>{a.centros}</td>
                  {puedeConfigurar && (
                    <td className="acciones">
                      <button type="button" className="btn-mini" onClick={() => editar(a)}>
                        Editar
                      </button>
                      <button type="button" className="btn-mini peligro" onClick={() => borrar(a)}>
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
    </div>
  )
}