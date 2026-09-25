import { useEffect, useMemo, useState } from "react"
import { exportarEpi15, listarEpi15, obtenerEpi15 } from "../api/sisv"
import { Boton, Campo, Select } from "../components/ui"

const ESTADO_LABEL = {
  BORRADOR: "Borrador",
  ENVIADO: "Enviado",
  CERRADO: "Cerrado",
}

export default function Epi15({ usuario }) {
  const hoy = new Date()
  const [lista, setLista] = useState([])
  const [anio, setAnio] = useState(hoy.getFullYear())
  const [semana, setSemana] = useState("")
  const [seleccionado, setSeleccionado] = useState(null)
  const [filas, setFilas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [estadoUI, setEstadoUI] = useState({ tipo: "", texto: "" })

  function aviso(tipo, texto) {
    setEstadoUI({ tipo, texto })
  }

  async function cargar() {
    setCargando(true)
    try {
      const params = {}
      if (anio) params.anio = anio
      if (semana) params.semana = semana
      setLista(await listarEpi15(params))
    } catch (err) {
      aviso("error", err.message)
      setLista([])
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  async function abrir(cons) {
    try {
      const detalle = await obtenerEpi15(cons.id)
      setSeleccionado(detalle)
      setFilas(detalle.filas || [])
      aviso("ok", `Consolidado EPI-15 cargado: ${detalle.organizacion_nombre} — ${detalle.anio}-S${String(detalle.semana).padStart(2, "0")}.`)
    } catch (err) {
      aviso("error", err.message)
    }
  }

  async function exportar() {
    try {
      const params = {}
      if (anio) params.anio = anio
      if (semana) params.semana = semana
      const blob = await exportarEpi15(params)
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `consolidado_epi15_${Date.now()}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      aviso("error", err.message)
    }
  }

  const totalCasos = useMemo(
    () => filas.reduce((acc, f) => acc + Number(f.total || 0), 0),
    [filas]
  )

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Consolidado semanal EPI-15</h1>
        <p>
          SIS-04/EPI-15 (morbilidad registrada): consolidados semanales por enfermedad/evento de notificación.
          Datos leídos del legado SISMAI (RENGLON_EPI15/INFORME_EPI); solo lectura.
        </p>
      </header>

      {estadoUI.tipo && (
        <div className={`aviso aviso-${estadoUI.tipo}`} role="status">
          {estadoUI.texto}
        </div>
      )}

      <div className="formulario">
        <div className="grid">
          <Campo label="Año" htmlFor="epi15-anio">
            <Select
              id="epi15-anio"
              opciones={opcionesAnios(hoy)}
              value={String(anio)}
              onChange={(e) => setAnio(Number(e.target.value))}
            />
          </Campo>
          <Campo label="Semana (1-53, opcional)" htmlFor="epi15-semana">
            <Select
              id="epi15-semana"
              opciones={[["", "Todas"], ...Array.from({ length: 53 }, (_, i) => [`${i + 1}`, `Semana ${i + 1}`])]}
              value={String(semana)}
              onChange={(e) => setSemana(e.target.value)}
            />
          </Campo>
        </div>
        <div className="pie-form">
          <Boton type="button" onClick={cargar}>
            Consultar
          </Boton>
          <button type="button" className="btn-mini" style={{ marginLeft: "0.6rem" }} onClick={exportar}>
            Exportar CSV
          </button>
        </div>
      </div>

      {seleccionado && (
        <section className="panel" style={{ marginTop: "1rem" }}>
          <header className="cabecera-seccion">
            <h2>
              {seleccionado.organizacion_nombre} — Año {seleccionado.anio} · Semana {seleccionado.semana}
              <span className="etiqueta">{ESTADO_LABEL[seleccionado.estado] || seleccionado.estado}</span>
            </h2>
            <p className="ayuda" style={{ margin: 0 }}>
              Origen: {seleccionado.origen} · Tabla legacy: {seleccionado.legacy_tabla}{" "}
              {seleccionado.legacy_documento ? `· ${seleccionado.legacy_documento}` : ""}
            </p>
            <button type="button" className="btn-mini" style={{ marginTop: "0.6rem" }} onClick={() => { setSeleccionado(null); setFilas([]) }}>
              ← Volver a la lista
            </button>
          </header>

          <div className="matriz">
            <table className="tabla-matriz">
              <thead>
                <tr>
                  <th>Código</th>
                  <th className="col-enfermedad">Enfermedad / Evento</th>
                  <th>Primeras consultas</th>
                  <th>Subsiguientes</th>
                  <th>Columna X</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {filas.map((f) => (
                  <tr key={f.id}>
                    <td>{f.codigo_legacy || "—"}</td>
                    <td className="col-enfermedad">
                      <span className="evento-nombre">{f.evento_nombre}</span>
                    </td>
                    <td className="celda-total">{f.casosp}</td>
                    <td className="celda-total">{f.casoss}</td>
                    <td className="celda-total">{f.casosx}</td>
                    <td className="celda-total">{f.total}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan={2}>Totales</td>
                  <td className="celda-total">{filas.reduce((acc, f) => acc + Number(f.casosp || 0), 0)}</td>
                  <td className="celda-total">{filas.reduce((acc, f) => acc + Number(f.casoss || 0), 0)}</td>
                  <td className="celda-total">{filas.reduce((acc, f) => acc + Number(f.casosx || 0), 0)}</td>
                  <td className="celda-total">{totalCasos}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </section>
      )}

      {!seleccionado && (
        <section className="lista">
          <h2>Consolidados registrados ({lista.length})</h2>
          {cargando ? (
            <p className="ayuda">Cargando…</p>
          ) : lista.length === 0 ? (
            <p className="ayuda">No hay consolidados EPI-15 para el filtro seleccionado.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Año-Semana</th>
                  <th>Organización</th>
                  <th>Estado</th>
                  <th>Origen</th>
                  <th>Filas</th>
                  <th className="acciones">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {lista.map((c) => (
                  <tr key={c.id}>
                    <td>{c.anio}-S{String(c.semana).padStart(2, "0")}</td>
                    <td>{c.organizacion_nombre}</td>
                    <td>{c.estado_label || c.estado}</td>
                    <td>{c.origen}</td>
                    <td>{Array.isArray(c.filas) ? c.filas.length : 0}</td>
                    <td className="acciones">
                      <button type="button" className="btn-mini" onClick={() => abrir(c)}>
                        Abrir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  )
}

function opcionesAnios(hoy) {
  const años = []
  for (let a = hoy.getFullYear(); a >= hoy.getFullYear() - 5; a--) años.push([`${a}`, `${a}`])
  return años
}