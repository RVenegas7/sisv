import { useEffect, useState } from "react"
import { exportarReportes, obtenerReporteComparativo, obtenerReportes } from "../api/sisv"
import { Boton, Campo, Input, Select } from "../components/ui"

const MODULOS = [
  ["", "Todos los módulos"],
  ["nacimientos", "Nacimientos"],
  ["defunciones", "Defunciones"],
  ["fichas", "Fichas de vigilancia"],
  ["consolidados", "Consolidados semanales (ENO)"],
]
const MODULO_LABEL = { nacimientos: "Nacimientos", defunciones: "Defunciones", fichas: "Vigilancia" }
const TIPO_ENO = { MORBILIDAD: "Morbilidad (EPI-12)", MORTALIDAD: "Mortalidad (EPI-14)" }
const ESTADO_ENO = { BORRADOR: "Borrador", ENVIADO: "Enviado", CERRADO: "Cerrado" }
const ORIGEN_ENO = { PROPIO: "Propio", CONSOLIDADO_SUPERIOR: "Consolidado de superiores" }

export default function Reportes() {
  const [filtros, setFiltros] = useState({ modulo: "", desde: "", hasta: "", estado: "" })
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [aviso, setAviso] = useState("")
  const [anios, setAnios] = useState({ anio1: "", anio2: "" })
  const [comparativo, setComparativo] = useState(null)
  const [cargandoComparativo, setCargandoComparativo] = useState(false)

  async function correr() {
    setCargando(true)
    try {
      const params = Object.fromEntries(Object.entries(filtros).filter(([, v]) => v))
      const d = await obtenerReportes(params)
      setDatos(d)
    } catch {
      setDatos(null)
    } finally {
      setCargando(false)
    }
  }

  async function exportarCsv() {
    try {
      const params = Object.fromEntries(Object.entries(filtros).filter(([, v]) => v))
      const blob = await exportarReportes(params)
      const url = URL.createObjectURL(blob)
      const enlace = document.createElement("a")
      enlace.href = url
      enlace.download = `reporte_sisv_${new Date().toISOString().slice(0, 10)}.csv`
      enlace.click()
      URL.revokeObjectURL(url)
    } catch {
      setAviso("No se pudo exportar el reporte.")
    }
  }

  useEffect(() => {
    correr()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const anioActual = new Date().getFullYear()
  const anosComparativos = Array.from({ length: 12 }, (_, i) => anioActual - 8 + i)

  async function correrComparativo() {
    setCargandoComparativo(true)
    try {
      const a1 = Number(anios.anio1) || anioActual
      const a2 = Number(anios.anio2) || anioActual - 1
      const d = await obtenerReporteComparativo({ anio1: a1, anio2: a2 })
      setComparativo(d)
    } catch (e) {
      setAviso(e.message)
      setComparativo(null)
    } finally {
      setCargandoComparativo(false)
    }
  }

  const tieneDatos =
    datos &&
    (Object.keys(datos.totales).length > 0 ||
      (datos.consolidados_semanales && Object.keys(datos.consolidados_semanales).length > 0))

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Reportes</h1>
        <p>Consulte y exporte los registros del sistema según módulo, rango de fechas o estado.</p>
      </header>

      <form
        className="filtros"
        onSubmit={(e) => {
          e.preventDefault()
          correr()
        }}
      >
        <Campo label="Módulo">
          <Select opciones={MODULOS} value={filtros.modulo} onChange={(e) => setFiltros({ ...filtros, modulo: e.target.value })} />
        </Campo>
        <Campo label="Desde">
          <Input type="date" value={filtros.desde} onChange={(e) => setFiltros({ ...filtros, desde: e.target.value })} />
        </Campo>
        <Campo label="Hasta">
          <Input type="date" value={filtros.hasta} onChange={(e) => setFiltros({ ...filtros, hasta: e.target.value })} />
        </Campo>
        <Campo label="Estado">
          <Input value={filtros.estado} placeholder="Ej. Táchira" onChange={(e) => setFiltros({ ...filtros, estado: e.target.value })} />
        </Campo>
        <div className="filtro-action">
          <Boton>Cargar reporte</Boton>
          <button type="button" className="boton" onClick={exportarCsv}>
            Exportar CSV
          </button>
        </div>
      </form>

      {aviso && <div className="aviso aviso-error">{aviso}</div>}

      {cargando && <div className="aviso aviso-info">Generando reporte…</div>}

      {datos && !cargando && !tieneDatos && (
        <div className="aviso aviso-info">Sin registros para los criterios seleccionados.</div>
      )}

      {datos && tieneDatos && (
        <>
          <section className="lista">
            <h2>Totales por módulo</h2>
            <table>
              <thead>
                <tr>
                  <th>Módulo</th>
                  <th>Registros</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(datos.totales).map(([m, n]) => (
                  <tr key={m}>
                    <td>{MODULO_LABEL[m]}</td>
                    <td>{n}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="lista">
            <h2>Registros por estado</h2>
            {Object.entries(datos.por_estado).map(([m, estados]) => (
              <details key={m} open>
                <summary>{MODULO_LABEL[m]}</summary>
                <table>
                  <thead>
                    <tr>
                      <th>Estado</th>
                      <th>Cantidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(estados).map(([e, n]) => (
                      <tr key={e}>
                        <td>{e}</td>
                        <td>{n}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </details>
            ))}
          </section>

          {datos.consolidados_semanales && Object.keys(datos.consolidados_semanales).length > 0 && (
            <section className="lista">
              <h2>Consolidados semanales (ENO)</h2>
              <p className="ayuda">
                Resumen de los consolidados SIS-04/EPI-12 (morbilidad) y EPI-14 (mortalidad) en el alcance.
              </p>
              <table>
                <thead>
                  <tr>
                    <th>Consolidados</th>
                    <th>Casos acumulados</th>
                    <th>Por tipo</th>
                    <th>Por estado</th>
                    <th>Por origen</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{datos.consolidados_semanales.total}</td>
                    <td>{datos.consolidados_semanales.casos}</td>
                    <td>
                      {Object.entries(datos.consolidados_semanales.por_tipo).map(([t, n]) => (
                        <div key={t}>{TIPO_ENO[t] || t}: {n}</div>
                      ))}
                    </td>
                    <td>
                      {Object.entries(datos.consolidados_semanales.por_estado).map(([e, n]) => (
                        <div key={e}>{ESTADO_ENO[e] || e}: {n}</div>
                      ))}
                    </td>
                    <td>
                      {Object.entries(datos.consolidados_semanales.por_origen).map(([o, n]) => (
                        <div key={o}>{ORIGEN_ENO[o] || o}: {n}</div>
                      ))}
                    </td>
                  </tr>
                </tbody>
              </table>
            </section>
          )}

          {datos.por_capitulo_cie11 && (
            <section className="lista">
              <h2>Por capítulo CIE-11 (histórico unificado)</h2>
              <p className="ayuda">
                Los registros CIE-10 históricos se agrupan según su equivalencia CIE-11 (cross-walk); los sin
                equivalencia aparecen por separado.
              </p>
              {Object.entries(datos.por_capitulo_cie11).map(([m, capitulos]) => (
                <details key={m} open>
                  <summary>{MODULO_LABEL[m]}</summary>
                  <table>
                    <thead>
                      <tr>
                        <th>Capítulo</th>
                        <th>Cantidad</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(capitulos).map(([c, n]) => (
                        <tr key={c}>
                          <td>{c}</td>
                          <td>{n}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </details>
              ))}
            </section>
          )}
        </>
      )}

      <section className="lista comparativo">
        <h2>Comparativo anual por semana epidemiológica</h2>
        <p className="ayuda">
          Compara dos años para ver la tendencia semanal de nacimientos, defunciones, muertes maternas (M) y
          vigilancia materno-infantil (MMI, lotes LEGACY-MMI/LEGACY-VIOLENTA).
        </p>
        <form
          className="filtros"
          onSubmit={(e) => {
            e.preventDefault()
            correrComparativo()
          }}
        >
          <Campo label="Año 1">
            <Select
              opciones={anosComparativos.map((a) => [String(a), String(a)])}
              value={anios.anio1}
              onChange={(e) => setAnios({ ...anios, anio1: e.target.value })}
            />
          </Campo>
          <Campo label="Año 2">
            <Select
              opciones={anosComparativos.map((a) => [String(a), String(a)])}
              value={anios.anio2}
              onChange={(e) => setAnios({ ...anios, anio2: e.target.value })}
            />
          </Campo>
          <div className="filtro-action">
            <Boton>Comparar</Boton>
          </div>
        </form>

        {cargandoComparativo && <div className="aviso aviso-info">Calculando comparativo…</div>}

        {comparativo && !cargandoComparativo && (
          <>
            <div className="resumen-anios">
              <span>
                <strong>{comparativo.anio1}</strong>
              </span>
              <span>vs</span>
              <span>
                <strong>{comparativo.anio2}</strong>
              </span>
            </div>
            {comparativo.series.map((s) => (
              <details key={s.clave} open={s.clave === "muertes_maternas"}>
                <summary>
                  {s.rotulo} · {comparativo.anio1}: {comparativo.totales[s.clave][comparativo.anio1]} ·{" "}
                  {comparativo.anio2}: {comparativo.totales[s.clave][comparativo.anio2]}
                </summary>
                <GraficoLineas
                  serie={s}
                  anio1={comparativo.anio1}
                  anio2={comparativo.anio2}
                  semanas={comparativo.semanas}
                />
              </details>
            ))}
          </>
        )}
      </section>
    </div>
  )
}

function GraficoLineas({ serie, anio1, anio2, semanas }) {
  const W = 900
  const H = 220
  const M = 32
  const colores = { anio1: "#1f5fa6", anio2: "#c24a2d" }

  const datos1 = semanas.map((s) => Number(serie.anio1[s]) || 0)
  const datos2 = semanas.map((s) => Number(serie.anio2[s]) || 0)
  const maximo = Math.max(1, ...datos1, ...datos2)
  const pasoX = (W - M * 2) / Math.max(1, semanas.length - 1)

  function ptos(datos) {
    return semanas
      .map((s, i) => {
        const x = M + i * pasoX
        const y = H - M - (datos[i] / maximo) * (H - M * 2)
        return `${x},${y}`
      })
      .join(" ")
  }

  const etiquetas = semanas.filter((_, i) => i % 10 === 0)

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="grafico-svg" role="img" aria-label={`${serie.rotulo}: evolución semanal`}>
      <line x1={M} y1={H - M} x2={W - M} y2={H - M} stroke="#666" strokeWidth="1" />
      <line x1={M} y1={M} x2={M} y2={H - M} stroke="#666" strokeWidth="1" />
      {etiquetas.map((s) => {
        const x = M + (semanas.indexOf(s) === -1 ? 0 : semanas.indexOf(s)) * pasoX
        return (
          <g key={`tic-${s}`}>
            <line x1={x} y1={H - M} x2={x} y2={H - M + 5} stroke="#666" strokeWidth="1" />
            <text x={x} y={H - M + 16} textAnchor="middle" fontSize="9" fill="#555">
              S{s}
            </text>
          </g>
        )
      })}
      <polyline points={ptos(datos1)} fill="none" stroke={colores.anio1} strokeWidth="2" />
      <polyline
        points={ptos(datos2)}
        fill="none"
        stroke={colores.anio2}
        strokeWidth="2"
        strokeDasharray="6 4"
      />
      <g className="leyenda">
        <circle cx={M + 10} cy={10} r={4} fill={colores.anio1} />
        <text x={M + 20} y={14} fontSize="11">
          {anio1}
        </text>
        <circle cx={M + 70} cy={10} r={4} fill={colores.anio2} />
        <text x={M + 80} y={14} fontSize="11">
          {anio2}
        </text>
      </g>
    </svg>
  )
}