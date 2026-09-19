import { useEffect, useMemo, useState } from "react"
import {
  actualizarConsolidado,
  crearConsolidado,
  eliminarConsolidado,
  exportarConsolidados,
  listarConsolidados,
  listarOrganizaciones,
} from "../api/sisv"
import CentroSelector from "../components/CentroSelector"
import { Boton, Campo, Input, Select } from "../components/ui"

const GRUPOS = [
  ["menor_1", "< 1 año"],
  ["de_1_4", "1 a 4 años"],
  ["de_5_6", "5 a 6 años"],
  ["de_7_9", "7 a 9 años"],
  ["de_10_11", "10 a 11 años"],
  ["de_12_14", "12 a 14 años"],
  ["de_15_19", "15 a 19 años"],
  ["de_20_24", "20 a 24 años"],
  ["de_25_44", "25 a 44 años"],
  ["de_45_59", "45 a 59 años"],
  ["de_60_64", "60 a 64 años"],
  ["de_65", "65 años y más"],
  ["edad_ignorada", "Edad Ignorada"],
]

const TIPOS = [
  ["MORBILIDAD", "Morbilidad (EPI-12)"],
  ["MORTALIDAD", "Mortalidad (EPI-14)"],
]

const TIPOS_SITUACION = [
  ["QUIMICO", "Químico"],
  ["RADIONUCLEAR", "Radionuclear"],
  ["EN_ANIMALES", "En animales"],
  ["DESASTRE_NATURAL", "Desastre natural"],
  ["ALIMENTARIO", "Alimentario"],
  ["INFECCIOSO", "Infeccioso"],
  ["INDETERMINADO", "Indeterminado"],
]

function semanaISO(fecha) {
  const d = new Date(fecha.getTime())
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() + 3 - ((d.getDay() + 6) % 7))
  const w1 = new Date(d.getFullYear(), 0, 4)
  return Math.ceil(((d - w1) / 86400000 + 1) / 7)
}

function columna(grupo, sexo) {
  return `${grupo}_${sexo}`
}

function totalesFila(fila) {
  let h = 0
  let m = 0
  for (const [grupo] of GRUPOS) {
    h += Number(fila.columnas?.[columna(grupo, "h")] || 0)
    m += Number(fila.columnas?.[columna(grupo, "m")] || 0)
  }
  return { h, m, total: h + m }
}

const ESTADO_LABEL = {
  BORRADOR: "Borrador",
  ENVIADO: "Enviado",
  CERRADO: "Cerrado",
}

export default function Vigilancia({ usuario }) {
  const permisos = usuario?.permisos || {}
  const orgUsuario = usuario?.organizacion
  const hoy = new Date()
  const [lista, setLista] = useState([])
  const [nuevo, setNuevo] = useState({
    anio: hoy.getFullYear(),
    semana: semanaISO(hoy),
    tipo: "MORBILIDAD",
    organizacion: null,
  })
  const [centros, setCentros] = useState([])
  const [consolidado, setConsolidado] = useState(null)
  const [filas, setFilas] = useState([])
  const [situaciones, setSituaciones] = useState([])
  const [alertas, setAlertas] = useState([])
  const [tab, setTab] = useState("informe")
  const [vistaInforme, setVistaInforme] = useState("evento")
  const [estadoUI, setEstadoUI] = useState({ tipo: "", texto: "" })
  const [errores, setErrores] = useState({})

  const esCentro = orgUsuario?.nivel === "CENTRO"
  const esLectura = !permisos.puede_escribir
  const cerrado = consolidado?.estado === "CERRADO"
  const bloqueado = esLectura || cerrado || !consolidado

  useEffect(() => {
    cargarLista()
  }, [])

  useEffect(() => {
    if (esCentro) return
    listarOrganizaciones()
      .then((orgs) => {
        if (!orgUsuario) {
          setCentros(orgs)
          return
        }
        let cs = orgs.filter((o) => o.nivel === "CENTRO")
        if (["REGIONAL", "GOBERNACION"].includes(orgUsuario.nivel) && orgUsuario.estado) {
          cs = cs.filter((o) => o.estado === orgUsuario.estado)
        }
        setCentros(cs)
      })
      .catch(() => setCentros([]))
  }, [esCentro, orgUsuario?.nivel, orgUsuario?.estado])

  async function cargarLista() {
    try {
      setLista(await listarConsolidados())
    } catch {
      setLista([])
    }
  }

  function aviso(tipo, texto) {
    setEstadoUI({ tipo, texto })
  }

  function ordenFila(f) {
    const d = f.evento_detalle || {}
    return d.orden_epi12 || d.orden_epi14 || 0
  }

  function aplicarConsolidado(cons) {
    const filasOrdenadas = [...cons.filas].sort((a, b) => ordenFila(a) - ordenFila(b))
    setConsolidado(cons)
    setFilas(filasOrdenadas)
    setSituaciones(cons.situaciones_especiales || [])
    setAlertas(cons.alertas_epidemias || [])
    setErrores({})
  }

  async function crearNuevo(e) {
    e.preventDefault()
    if (esLectura) return
    const payload = {
      anio: Number(nuevo.anio),
      semana: Number(nuevo.semana),
      tipo: nuevo.tipo,
    }
    if (nuevo.organizacion) payload.organizacion = nuevo.organizacion
    else if (!esCentro && orgUsuario) payload.organizacion = orgUsuario.id
    aviso("info", "Creando consolidado…")
    try {
      const cons = await crearConsolidado(payload)
      aplicarConsolidado(cons)
      aviso("ok", `Consolidado ${cons.tipo_label} ${cons.anio}-S${String(cons.semana).padStart(2, "0")} creado (${cons.filas.length} filas).`)
      setTab("informe")
      await cargarLista()
      window.scrollTo({ top: 0, behavior: "smooth" })
    } catch (err) {
      aviso("error", err.message)
    }
  }

  async function cargar(cons) {
    try {
      const detalle = await listarConsolidados({ anio: cons.anio, semana: cons.semana, tipo: cons.tipo })
      const el = detalle.find((x) => x.id === cons.id) || cons
      aplicarConsolidado(el)
      aviso("info", `Consolidado cargado: ${el.organizacion_nombre} — ${el.tipo_label} ${el.anio}-S${String(el.semana).padStart(2, "0")} (${EL_STATE(cons.estado)}).`)
      setTab("informe")
    } catch (err) {
      aviso("error", err.message)
    }
  }

  function cambiarCelda(eventoId, col, valor) {
    const n = Math.max(0, Number(valor) || 0)
    setFilas((prev) =>
      prev.map((f) =>
        f.evento === eventoId ? { ...f, columnas: { ...f.columnas, [col]: n } } : f
      )
    )
  }

  async function guardar(filtros, mensaje) {
    if (esLectura || !consolidado) return
    aviso("info", "Guardando…")
    try {
      const payload = {
        filas: filas.map((f) => ({ evento: f.evento, columnas: f.columnas })),
      }
      if (filtros.situaciones) {
        payload.situaciones_especiales = situaciones
      }
      if (filtros.alertas) {
        payload.alertas_epidemias = alertas
      }
      const cons = await actualizarConsolidado(consolidado.id, payload)
      aplicarConsolidado(cons)
      aviso("ok", mensaje || "Consolidado guardado.")
    } catch (err) {
      aviso("error", err.message)
    }
  }

  async function moverEstado(estadoNuevo) {
    if (!consolidado || esLectura) return
    try {
      const cons = await actualizarConsolidado(consolidado.id, { estado: estadoNuevo })
      aplicarConsolidado(cons)
      aviso("ok", `Consolidado marcado como ${ESTADO_LABEL[estadoNuevo]}.`)
      await cargarLista()
    } catch (err) {
      aviso("error", err.message)
    }
  }

  async function eliminar() {
    if (!consolidado || !window.confirm("¿Eliminar este consolidado semanal?")) return
    try {
      await eliminarConsolidado(consolidado.id)
      setConsolidado(null)
      setFilas([])
      setSituaciones([])
      setAlertas([])
      aviso("ok", "Consolidado eliminado.")
      await cargarLista()
    } catch (err) {
      aviso("error", err.message)
    }
  }

  function salir() {
    setConsolidado(null)
    setFilas([])
    setSituaciones([])
    setAlertas([])
    setTab("informe")
    setVistaInforme("evento")
    setErrores({})
    cargarLista()
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  async function exportar() {
    try {
      const blob = await exportarConsolidados({
        anio: consolidado?.anio || nuevo.anio,
        semana: consolidado?.semana || nuevo.semana,
        tipo: consolidado?.tipo || nuevo.tipo,
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `consolidado_vigilancia_${Date.now()}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      aviso("error", err.message)
    }
  }

  function organizacionDestinoLabel(id) {
    if (orgUsuario && id === orgUsuario.id) return orgUsuario.nombre
    const c = centros.find((x) => x.id === id)
    return c ? c.nombre : ""
  }

  const opcionesOrg = useMemo(() => {
    const opciones = []
    if (!esCentro && orgUsuario) {
      opciones.push([`${orgUsuario.id}`, `${orgUsuario.nombre} (suma de dependientes)`])
    }
    centros.forEach((c) => opciones.push([`${c.id}`, c.nombre]))
    return opciones
  }, [esCentro, orgUsuario, centros])

  const totalGeneral = filas.reduce((acc, f) => acc + totalesFila(f).total, 0)

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Vigilancia Epidemiológica</h1>
        <p>
          Consolidado Semanal de Enfermedades y Eventos de Notificación Obligatoria (ENO) — SIS-04/EPI-12 (morbilidad)
          y SIS-04/EPI-14 (mortalidad). Los consolidados de nivel municipal/regional se generan como suma de los
          establecimientos dependientes y son editables antes de enviarse.
        </p>
      </header>

      {estadoUI.tipo && (
        <div className={`aviso aviso-${estadoUI.tipo}`} role="status">
          {estadoUI.texto}
        </div>
      )}

      {esLectura && (
        <div className="aviso aviso-info">
          Su rol (<strong>{usuario?.rol_label}</strong>) es de solo lectura: no puede crear ni editar consolidados.
        </div>
      )}

      <form className="formulario" onSubmit={crearNuevo} noValidate>
        <fieldset disabled={esLectura}>
          <div className="grid">
            <Campo label="Año" htmlFor="ano">
              <Select
                id="ano"
                opciones={[hoy.getFullYear(), hoy.getFullYear() - 1, hoy.getFullYear() - 2].map((a) => [`${a}`, `${a}`])}
                value={String(nuevo.anio)}
                onChange={(e) => setNuevo((n) => ({ ...n, anio: Number(e.target.value) }))}
              />
            </Campo>
            <Campo label="Semana epidemiológica (1-53)" htmlFor="semana">
              <Select
                id="semana"
                opciones={Array.from({ length: 53 }, (_, i) => [`${i + 1}`, `Semana ${i + 1}`])}
                value={String(nuevo.semana)}
                onChange={(e) => setNuevo((n) => ({ ...n, semana: Number(e.target.value) }))}
              />
            </Campo>
            <Campo label="Tipo de consolidado" htmlFor="tipo">
              <Select
                id="tipo"
                opciones={TIPOS}
                value={nuevo.tipo}
                onChange={(e) => setNuevo((n) => ({ ...n, tipo: e.target.value }))}
              />
            </Campo>
            {!esCentro && opcionesOrg.length > 0 && (
              <Campo label="Organización / establecimiento" htmlFor="org_destino">
                <Select
                  id="org_destino"
                  opciones={opcionesOrg}
                  value={nuevo.organizacion ? String(nuevo.organizacion) : ""}
                  onChange={(e) => setNuevo((n) => ({ ...n, organizacion: e.target.value ? Number(e.target.value) : null }))}
                />
              </Campo>
            )}
          </div>
        </fieldset>
        <div className="pie-form">
          <Boton disabled={esLectura}>Crear / abrir consolidado semanal</Boton>
          <button type="button" className="btn-mini" style={{ marginLeft: "0.6rem" }} onClick={exportar}>
            Exportar CSV
          </button>
        </div>
      </form>

      {consolidado && (
        <>
          <div className="cabecera-seccion" style={{ marginTop: "1.2rem" }}>
            <h2>
              {consolidado.tipo_label} — Año {consolidado.anio} · Semana {consolidado.semana}
              <span className="etiqueta">{ESTADO_LABEL[consolidado.estado]}</span>
            </h2>
            <p className="ayuda" style={{ margin: 0 }}>
              {consolidado.organizacion_nombre} · {consolidado.origen_label}
              {consolidado.estado === "CERRADO" && " · Este consolidado está cerrado (solo lectura)."}
            </p>
            <button type="button" className="btn-mini" style={{ marginTop: "0.6rem" }} onClick={salir}>
              ← Volver a la lista de consolidados
            </button>
          </div>

          <div className="filas-campo">
            {[
              ["informe", "Informe (matriz)"],
              ["situaciones", "Situaciones especiales"],
              ["alertas", "Alertas / epidemias"],
            ].map(([k, r]) => (
              <button
                key={k}
                type="button"
                className={`btn-mini ${tab === k ? "activo" : ""}`}
                onClick={() => setTab(k)}
              >
                {r}
              </button>
            ))}
          </div>

          {tab === "informe" && (
            <>
              {cerrado && <div className="aviso aviso-info">Consolidado cerrado: los datos son de solo lectura.</div>}
              <div className="filas-campo" style={{ marginBottom: "0.8rem" }}>
                <button
                  type="button"
                  className={`btn-mini ${vistaInforme === "evento" ? "activo" : ""}`}
                  onClick={() => setVistaInforme("evento")}
                >
                  Por enfermedad
                </button>
                <button
                  type="button"
                  className={`btn-mini ${vistaInforme === "matriz" ? "activo" : ""}`}
                  onClick={() => setVistaInforme("matriz")}
                >
                  Matriz completa
                </button>
              </div>

              {vistaInforme === "evento" && (
                <InformePorEnfermedad
                  filas={filas}
                  bloqueado={bloqueado}
                  onCambiarCelda={cambiarCelda}
                />
              )}

              {vistaInforme === "matriz" && (
              <div className="matriz">
                <table className="tabla-matriz">
                  <thead>
                    <tr>
                      <th rowSpan={2}>Ord.</th>
                      <th rowSpan={2} className="col-enfermedad">Enfermedad / Evento</th>
                      {GRUPOS.map(([grupo, rotulo]) => (
                        <th key={grupo} colSpan={2} className="col-grupo">
                          {rotulo}
                        </th>
                      ))}
                      <th rowSpan={2}>Total H</th>
                      <th rowSpan={2}>Total M</th>
                      <th rowSpan={2}>Total</th>
                    </tr>
                    <tr>
                      {GRUPOS.map(([grupo]) => (
                        <FragmentoHM key={grupo} />
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filas.map((f) => {
                      const t = totalesFila(f)
                      const det = f.evento_detalle || {}
                      return (
                        <tr key={f.evento}>
                          <td className="celda-orden">{det.orden_epi12 || det.orden_epi14 || "—"}</td>
                          <td className="col-enfermedad">
                            <span className="evento-nombre">{det.nombre}</span>
                            {det.codigos_cie11 && <small className="cod-cie"> CIE-11: {det.codigos_cie11}</small>}
                            {det.codigos_cie10 && <small className="cod-cie">CIE-10: {det.codigos_cie10}</small>}
                          </td>
                          {GRUPOS.map(([grupo]) => (
                            <FragmentoCeldas
                              key={grupo}
                              grupo={grupo}
                              f={f}
                              bloqueado={bloqueado}
                              onChange={cambiarCelda}
                            />
                          ))}
                          <td className="celda-total">{t.h}</td>
                          <td className="celda-total">{t.m}</td>
                          <td className="celda-total">{t.total}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colSpan={2}>Totales</td>
                      {GRUPOS.map(([grupo]) => {
                        const h = filas.reduce((acc, f) => acc + Number(f.columnas?.[columna(grupo, "h")] || 0), 0)
                        const m = filas.reduce((acc, f) => acc + Number(f.columnas?.[columna(grupo, "m")] || 0), 0)
                        return (
                          <td colSpan={2} key={grupo}>
                            {h} / {m}
                          </td>
                        )
                      })}
                      <td className="celda-total">{filas.reduce((acc, f) => acc + totalesFila(f).h, 0)}</td>
                      <td className="celda-total">{filas.reduce((acc, f) => acc + totalesFila(f).m, 0)}</td>
                      <td className="celda-total">{totalGeneral}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
              )}
              <p className="ayuda" style={{ marginTop: "0.6rem" }}>
                Nota: cuando la edad es ignorada, el conteo se registra en la columna Hombres (regla del formulario
                EPI-12/14). Los totales se calculan automáticamente.
              </p>
              <div className="pie-form">
                <Boton type="button" disabled={bloqueado} onClick={() => guardar({}, "Filas guardadas (borrador).")}>
                  Guardar borrador
                </Boton>
                {!cerrado && (
                  <>
                    <button type="button" className="btn-mini" style={{ marginLeft: "0.6rem" }} disabled={esLectura} onClick={() => moverEstado("ENVIADO")}>
                      Marcar enviado
                    </button>
                    <button type="button" className="btn-mini" style={{ marginLeft: "0.6rem" }} disabled={esLectura} onClick={() => moverEstado("CERRADO")}>
                      Cerrar consolidado
                    </button>
                  </>
                )}
                {permisos.puede_eliminar && (
                  <button type="button" className="btn-mini peligro" style={{ marginLeft: "0.6rem" }} onClick={eliminar}>
                    Eliminar
                  </button>
                )}
              </div>
            </>
          )}

          {tab === "situaciones" && (
            <SituacionesBloque
              editable={!bloqueado}
              items={situaciones}
              setItems={setSituaciones}
              onGuardar={() => guardar({ situaciones: true }, "Situaciones especiales guardadas.")}
            />
          )}

          {tab === "alertas" && (
            <AlertasBloque
              editable={!bloqueado}
              items={alertas}
              setItems={setAlertas}
              onGuardar={() => guardar({ alertas: true }, "Alertas / epidemias guardadas.")}
            />
          )}
        </>
      )}

      {!consolidado && lista.length > 0 && (
        <section className="lista">
          <h2>Consolidados registrados ({lista.length})</h2>
          <table>
            <thead>
              <tr>
                <th>Año-Semana</th>
                <th>Tipo</th>
                <th>Organización</th>
                <th>Estado</th>
                <th>Origen</th>
                <th>Total casos</th>
                <th className="acciones">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {lista.map((c) => (
                <tr key={c.id}>
                  <td>{c.anio}-S{String(c.semana).padStart(2, "0")}</td>
                  <td>{c.tipo_label}</td>
                  <td>{c.organizacion_nombre}</td>
                  <td>{c.estado_label}</td>
                  <td>{c.origen_label}</td>
                  <td>{c.total_casos}</td>
                  <td className="acciones">
                    <button type="button" className="btn-mini" onClick={() => cargar(c)}>
                      Abrir
                    </button>
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

function InformePorEnfermedad({ filas, bloqueado, onCambiarCelda }) {
  const [filtro, setFiltro] = useState("")
  const [indice, setIndice] = useState(0)

  const coincidencias = useMemo(() => {
    const q = filtro.trim().toLowerCase()
    if (!q) return filas
    return filas.filter((f) => {
      const det = f.evento_detalle || {}
      const hayarTexto =
        [det.nombre, det.codigos_cie11, det.codigos_cie10, String(det.orden_epi12 || ""), String(det.orden_epi14 || "")]
          .filter(Boolean)
          .join(" ")
          .toLowerCase()
      return hayarTexto.includes(q)
    })
  }, [filas, filtro])

  const idxClamp = Math.min(indice, Math.max(coincidencias.length - 1, 0))
  const f = coincidencias[idxClamp]

  function ir(fila) {
    setFiltro("")
    setIndice(Math.max(filas.findIndex((x) => x.evento === fila.evento), 0))
  }

  return (
    <div className="panel-enfermedad">
      <div className="buscar-evento">
        <Input
          type="search"
          placeholder="Buscar por nombre, orden o código CIE…"
          value={filtro}
          onChange={(e) => {
            setFiltro(e.target.value)
            setIndice(0)
          }}
        />
        {filtro && (
          <span className="resultados-busqueda">
            {coincidencias.length === 0
              ? "Sin coincidencias"
              : `${coincidencias.length} ${coincidencias.length === 1 ? "coincidencia" : "coincidencias"}`}
          </span>
        )}
      </div>

      {filtro && coincidencias.length > 0 && (
        <ul className="lista-coincidencias">
          {coincidencias.slice(0, 12).map((fila) => {
            const det = fila.evento_detalle || {}
            return (
              <li key={fila.evento}>
                <button type="button" className="btn-mini" style={{ marginRight: "0.5rem" }} onClick={() => ir(fila)}>
                  Seleccionar
                </button>
                <span className="celda-orden">{det.orden_epi12 || det.orden_epi14 || "—"}</span> {det.nombre}
              </li>
            )
          })}
        </ul>
      )}

      {f ? (
        <div className="detalle-evento">
          <div className="cabecera-seccion" style={{ marginTop: 0 }}>
            <h3>
              <span className="celda-orden">{f.evento_detalle?.orden_epi12 || f.evento_detalle?.orden_epi14 || "—"}</span>{" "}
              <span className="evento-nombre">{f.evento_detalle?.nombre}</span>
            </h3>
            <p className="ayuda" style={{ margin: 0 }}>
              {f.evento_detalle?.codigos_cie11 && <>CIE-11: {f.evento_detalle.codigos_cie11}</>}
              {f.evento_detalle?.codigos_cie10 && (
                <> {f.evento_detalle.codigos_cie11 ? "·" : ""} CIE-10: {f.evento_detalle.codigos_cie10}</>
              )}
            </p>
          </div>

          <div className="navegacion-evento">
            <button
              type="button"
              className="btn-mini"
              disabled={bloqueado || idxClamp <= 0}
              onClick={() => setIndice(idxClamp - 1)}
            >
              ← Anterior
            </button>
            <span className="contador">
              {idxClamp + 1} de {coincidencias.length}
            </span>
            <button
              type="button"
              className="btn-mini"
              disabled={bloqueado || idxClamp >= coincidencias.length - 1}
              onClick={() => setIndice(idxClamp + 1)}
            >
              Siguiente →
            </button>
          </div>

          <table className="tabla-grupos">
            <thead>
              <tr>
                <th>Grupo etario</th>
                <th>Hombres</th>
                <th>Mujeres</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {GRUPOS.map(([grupo, rotulo]) => {
                const h = columna(grupo, "h")
                const m = columna(grupo, "m")
                const esIgnorada = grupo === "edad_ignorada"
                return (
                  <tr key={grupo}>
                    <td className="celda-grupo">{rotulo}</td>
                    <td className="celda-num">
                      <input
                        type="number"
                        min="0"
                        value={Number(f.columnas?.[h] || 0)}
                        disabled={bloqueado}
                        onChange={(e) => onCambiarCelda(f.evento, h, e.target.value)}
                        aria-label={`${f.evento_detalle?.nombre} ${rotulo} hombres`}
                      />
                    </td>
                    <td className="celda-num">
                      <input
                        type="number"
                        min="0"
                        value={esIgnorada ? 0 : Number(f.columnas?.[m] || 0)}
                        disabled={bloqueado || esIgnorada}
                        onChange={(e) => onCambiarCelda(f.evento, m, e.target.value)}
                        aria-label={`${f.evento_detalle?.nombre} ${rotulo} mujeres`}
                      />
                    </td>
                    <td className="celda-total">
                      {Number(f.columnas?.[h] || 0) + Number(f.columnas?.[m] || 0)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
            <tfoot>
              <tr>
                <td>Totales de este evento</td>
                <td className="celda-total">{totalesFila(f).h}</td>
                <td className="celda-total">{totalesFila(f).m}</td>
                <td className="celda-total">{totalesFila(f).total}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      ) : (
        <p className="ayuda">No hay eventos que coincidan con la búsqueda.</p>
      )}
    </div>
  )
}

function FragmentoHM() {
  return (
    <>
      <th className="celda-sexo">H</th>
      <th className="celda-sexo">M</th>
    </>
  )
}

function FragmentoCeldas({ grupo, f, bloqueado, onChange }) {
  const h = columna(grupo, "h")
  const m = columna(grupo, "m")
  const esIgnorada = grupo === "edad_ignorada"
  return (
    <>
      <td className="celda-num">
        <input
          type="number"
          min="0"
          value={Number(f.columnas?.[h] || 0)}
          disabled={bloqueado}
          onChange={(e) => onChange(f.evento, h, e.target.value)}
          aria-label={`${f.evento_detalle?.nombre} ${grupo} hombres`}
        />
      </td>
      <td className="celda-num">
        <input
          type="number"
          min="0"
          value={esIgnorada ? 0 : Number(f.columnas?.[m] || 0)}
          disabled={bloqueado || esIgnorada}
          onChange={(e) => onChange(f.evento, m, e.target.value)}
          aria-label={`${f.evento_detalle?.nombre} ${grupo} mujeres`}
        />
      </td>
    </>
  )
}

const EL_STATE = (s) => ESTADO_LABEL[s] || s

function SituacionesBloque({ editable, items, setItems, onGuardar }) {
  return (
    <>
      <p className="ayuda">
        Situaciones especiales no incluidas en los 114 ENO/eventos (químicos, radionucleares, en animales, desastres
        naturales, alimentarios, infecciosos, indeterminados).
      </p>
      <fieldset disabled={!editable} style={{ border: 0, padding: 0, margin: 0 }}>
        {items.map((s, i) => (
          <div className="panel" key={i} style={{ marginBottom: "0.8rem" }}>
            <div className="grid">
              <Campo label="Tipo de evento" htmlFor={`sit-${i}-tipo`}>
                <Select
                  id={`sit-${i}-tipo`}
                  opciones={TIPOS_SITUACION}
                  value={s.tipo_evento}
                  onChange={(e) => setItems((items) => items.map((x, ix) => (ix === i ? { ...x, tipo_evento: e.target.value } : x)))}
                />
              </Campo>
              <Campo label="Comunidad" htmlFor={`sit-${i}-com`}>
                <Input id={`sit-${i}-com`} value={s.comunidad || ""} onChange={(e) => setItems((items) => items.map((x, ix) => (ix === i ? { ...x, comunidad: e.target.value } : x)))} />
              </Campo>
              <Campo label="Casos" htmlFor={`sit-${i}-casos`}>
                <Input id={`sit-${i}-casos`} type="number" min="0" value={s.casos || 0} onChange={(e) => setItems((items) => items.map((x, ix) => (ix === i ? { ...x, casos: Number(e.target.value) || 0 } : x)))} />
              </Campo>
              <Campo label="Muertes" htmlFor={`sit-${i}-muertes`}>
                <Input id={`sit-${i}-muertes`} type="number" min="0" value={s.muertes || 0} onChange={(e) => setItems((items) => items.map((x, ix) => (ix === i ? { ...x, muertes: Number(e.target.value) || 0 } : x)))} />
              </Campo>
              <Campo label="Descripción del evento" htmlFor={`sit-${i}-desc`}>
                <Input id={`sit-${i}-desc`} value={s.descripcion || ""} onChange={(e) => setItems((items) => items.map((x, ix) => (ix === i ? { ...x, descripcion: e.target.value } : x)))} />
              </Campo>
              <Campo label="Medidas tomadas" htmlFor={`sit-${i}-med`}>
                <Input id={`sit-${i}-med`} value={s.medidas_tomadas || ""} onChange={(e) => setItems((items) => items.map((x, ix) => (ix === i ? { ...x, medidas_tomadas: e.target.value } : x)))} />
              </Campo>
            </div>
            <button type="button" className="btn-mini peligro" onClick={() => setItems((items) => items.filter((_, ix) => ix !== i))}>
              Quitar situación
            </button>
          </div>
        ))}
        <div className="pie-form">
          <button type="button" className="btn-mini" disabled={!editable} onClick={() => setItems((items) => [...items, { tipo_evento: "INFECCIOSO", comunidad: "", casos: 0, muertes: 0, descripcion: "", medidas_tomadas: "" }])}>
            + Añadir situación especial
          </button>
          <Boton type="button" disabled={!editable} onClick={onGuardar}>
            Guardar situaciones
          </Boton>
        </div>
      </fieldset>
    </>
  )
}

function AlertasBloque({ editable, items, setItems, onGuardar }) {
  const [clase, setClase] = useState("ALERTA")
  const [enfermedad, setEnfermedad] = useState("")
  const [casos, setCasos] = useState(0)
  const [muertes, setMuertes] = useState(0)
  const [grave, setGrave] = useState(false)
  const [inusitado, setInusitado] = useState(false)
  const [nacional, setNacional] = useState(false)
  const [fechaInicio, setFechaInicio] = useState("")
  const [fechaFin, setFechaFin] = useState("")
  const [unidadGeo, setUnidadGeo] = useState("")
  const [unidadSan, setUnidadSan] = useState("")

  function añadir(e) {
    e.preventDefault()
    if (!enfermedad.trim() && !items.length) {
      // se permite declarar una alerta con enfermedad en blanco si ya hay datos
    }
    setItems((prev) => [
      ...prev,
      {
        clase,
        enfermedad: enfermedad.trim(),
        casos: Number(casos) || 0,
        muertes: Number(muertes) || 0,
        grave,
        inusitado,
        impacto_nacional: nacional,
        fecha_inicio: fechaInicio || null,
        fecha_fin: fechaFin || null,
        unidad_geografica: unidadGeo,
        unidad_sanitaria: unidadSan,
      },
    ])
    setEnfermedad("")
    setCasos(0)
    setMuertes(0)
    setGrave(false)
    setInusitado(false)
    setNacional(false)
    setFechaInicio("")
    setFechaFin("")
    setUnidadGeo("")
    setUnidadSan("")
  }

  return (
    <>
      <p className="ayuda">
        Situaciones de alerta y de epidemia por evento (fecha de inicio/fin, unidad geográfica y sanitaria,
        marcadores grave / inusitado / nacional).
      </p>
      <ul className="mini-filas">
        {items.map((a, i) => (
          <li key={i}>
            <span>
              <strong>{a.clase === "EPIDEMIA" ? "Epidemia" : "Alerta"}:</strong> {a.enfermedad || "—"} · casos {a.casos} ·
              muertes {a.muertes} {a.grave ? "· grave" : ""} {a.inusitado ? "· inusitado" : ""}{" "}
              {a.impacto_nacional ? "· nacional" : ""}
            </span>
            <span className="acciones-der">
              <button type="button" className="btn-mini peligro" disabled={!editable} onClick={() => setItems((x) => x.filter((_, ix) => ix !== i))}>
                Quitar
              </button>
            </span>
          </li>
        ))}
      </ul>
      <form className="formulario" onSubmit={añadir} noValidate>
        <fieldset disabled={!editable}>
          <div className="grid">
            <Campo label="Clase" htmlFor="alert-clase">
              <Select
                id="alert-clase"
                opciones={[["ALERTA", "Situación de alerta"], ["EPIDEMIA", "Situación de epidemia"]]}
                value={clase}
                onChange={(e) => setClase(e.target.value)}
              />
            </Campo>
            <Campo label="Enfermedad" htmlFor="alert-enf">
              <Input id="alert-enf" value={enfermedad} onChange={(e) => setEnfermedad(e.target.value)} />
            </Campo>
            <Campo label="Casos" htmlFor="alert-casos">
              <Input id="alert-casos" type="number" min="0" value={casos} onChange={(e) => setCasos(e.target.value)} />
            </Campo>
            <Campo label="Muertes" htmlFor="alert-muertes">
              <Input id="alert-muertes" type="number" min="0" value={muertes} onChange={(e) => setMuertes(e.target.value)} />
            </Campo>
            <Campo label="Fecha de inicio" htmlFor="alert-fi">
              <Input id="alert-fi" type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)} />
            </Campo>
            <Campo label="Fecha fin" htmlFor="alert-ff">
              <Input id="alert-ff" type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} />
            </Campo>
            <Campo label="Unidad geográfica" htmlFor="alert-ug">
              <Input id="alert-ug" value={unidadGeo} onChange={(e) => setUnidadGeo(e.target.value)} />
            </Campo>
            <Campo label="Unidad sanitaria" htmlFor="alert-us">
              <Input id="alert-us" value={unidadSan} onChange={(e) => setUnidadSan(e.target.value)} />
            </Campo>
            <Campo label="Marcadores" htmlFor="alert-marc">
              <div className="filas-campo">
                <label className="checkbox"><input type="checkbox" checked={grave} onChange={(e) => setGrave(e.target.checked)} /> Grave</label>
                <label className="checkbox"><input type="checkbox" checked={inusitado} onChange={(e) => setInusitado(e.target.checked)} /> Inusitado</label>
                <label className="checkbox"><input type="checkbox" checked={nacional} onChange={(e) => setNacional(e.target.checked)} /> Nacional</label>
              </div>
            </Campo>
          </div>
          <div className="pie-form">
            <Boton type="submit" disabled={!editable}>Añadir alerta / epidemia</Boton>
          </div>
        </fieldset>
      </form>
      <div className="pie-form">
        <Boton type="button" disabled={!editable} onClick={onGuardar}>
          Guardar alertas / epidemias
        </Boton>
      </div>
    </>
  )
}