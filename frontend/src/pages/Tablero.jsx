import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { obtenerDashboard } from "../api/sisv"

const MESES = [
  "Ene", "Feb", "Mar", "Abr", "May", "Jun",
  "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

function maximo(mensual) {
  return Math.max(1, ...Object.values(mensual).flatMap((serie) => Object.values(serie)))
}

export default function Tablero() {
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState("")

  useEffect(() => {
    obtenerDashboard().then(setDatos).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="aviso aviso-error">No se pudo cargar el tablero: {error}</div>
  if (!datos) return <div className="aviso aviso-info">Cargando indicadores…</div>

  const meses = [...new Set(Object.values(datos.mensual).flatMap((s) => Object.keys(s)))].sort()
  const max = maximo(datos.mensual)
  const MODULO_LABEL = { nacimientos: "Nacimientos", defunciones: "Defunciones", fichas: "Vigilancia" }
  const COLORES = { nacimientos: "#0b7a4b", defunciones: "#b91c1c", fichas: "#0f5aa0" }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Tablero de indicadores</h1>
        <p>Resumen de nacimientos, defunciones y fichas de vigilancia del SISV.</p>
      </header>

      <section className="tarjetas">
        {[
          ["Nacimientos", datos.totales.nacimientos, "/nacimientos", COLORES.nacimientos],
          ["Defunciones", datos.totales.defunciones, "/defunciones", COLORES.defunciones],
          ["Fichas de vigilancia", datos.totales.fichas, "/vigilancia", COLORES.fichas],
          ["Consolidados ENO", datos.consolidados_semanales?.total || 0, "/vigilancia", "#7c3aed"],
          ["Registros totales", datos.totales.total, null, "#6b7280"],
        ].map(([rotulo, valor, url, color]) => (
          <article key={rotulo} className="tarjeta" style={{ borderTopColor: color }}>
            <span>{rotulo}</span>
            <strong>{valor}</strong>
            {url && <Link to={url}>Cargar registro →</Link>}
          </article>
        ))}
      </section>

      <div className="dash-grid">
        <section className="panel">
          <h2>Registros por estado</h2>
          {Object.keys(datos.por_estado).length === 0 && <p className="ayuda">Sin registros aún.</p>}
          <ul className="barras">
            {Object.entries(datos.por_estado).map(([estado, n]) => (
              <li key={estado}>
                <span>{estado}</span>
                <div className="barra-via">
                  <div
                    style={{ width: `${Math.max(2, (n / Math.max(...Object.values(datos.por_estado))) * 100)}%` }}
                  />
                </div>
                <b>{n}</b>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel">
          <h2>Por versión CIE</h2>
          <ul className="barras">
            {Object.entries(datos.por_version).map(([version, n]) => (
              <li key={version}>
                <span>{version}</span>
                <div className="barra-via">
                  <div
                    className={version === "CIE10" ? "fill-oscuro" : ""}
                    style={{ width: `${Math.max(2, (n / Math.max(...Object.values(datos.por_version))) * 100)}%` }}
                  />
                </div>
                <b>{n}</b>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel">
          <h2>Salud materno-infantil</h2>
          <ul className="mini-filas">
            <li><span>Nacidos vivos</span><b>{datos.nacimientos_salud.nacidos_vivos}</b></li>
            {Object.entries(datos.nacimientos_salud.por_sexo).map(([s, n]) => (
              <li key={s}><span>Sexo {s === "F" ? "femenino" : s === "M" ? "masculino" : s}</span><b>{n}</b></li>
            ))}
            {Object.entries(datos.nacimientos_salud.por_tipo_parto).map(([t, n]) => (
              <li key={t}><span>Parto {t.toLowerCase()}</span><b>{n}</b></li>
            ))}
          </ul>
        </section>

        <section className="panel">
          <h2>Vigilancia por clasificación</h2>
          <ul className="mini-filas">
            {Object.entries(datos.vigilancia_salud.por_clasificacion).map(([c, n]) => (
              <li key={c}><span>{c}</span><b>{n}</b></li>
            ))}
          </ul>
        </section>

        <section className="panel">
          <h2>Consolidados semanales (ENO)</h2>
          <ul className="mini-filas">
            <li><span>Consolidados</span><b>{datos.consolidados_semanales?.total || 0}</b></li>
            <li><span>Casos acumulados</span><b>{datos.consolidados_semanales?.casos || 0}</b></li>
            {Object.entries(datos.consolidados_semanales?.por_tipo || {}).map(([t, n]) => (
              <li key={t}>
                <span>{t === "MORBILIDAD" ? "Morbilidad (EPI-12)" : t === "MORTALIDAD" ? "Mortalidad (EPI-14)" : t}</span>
                <b>{n}</b>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="panel">
        <h2>Registros por mes</h2>
        <table className="tabla-mensual">
          <thead>
            <tr>
              <th>Mes</th>
              {Object.keys(datos.mensual).map((m) => (
                <th key={m}>{MODULO_LABEL[m]}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {meses.map((mes) => (
              <tr key={mes}>
                <td>
                  {MESES[Number(mes.slice(5)) - 1]} {mes.slice(0, 4)}
                </td>
                {Object.keys(datos.mensual).map((m) => (
                  <td key={m}>
                    <div className="celda-barra">
                      <div
                        className="relleno"
                        style={{
                          background: COLORES[m],
                          width: `${(datos.mensual[m][mes] || 0) / max * 100}%`,
                        }}
                      />
                      {datos.mensual[m][mes] || 0}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}