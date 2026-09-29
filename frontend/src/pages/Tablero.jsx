import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { obtenerDashboard } from "../api/sisv"

const MESES = [
  "Ene", "Feb", "Mar", "Abr", "May", "Jun",
  "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

// Avisa cuando la informacion del tablero esta incompleta. Sin esto, un grafico
// con un corte de captura en medio se lee igual que uno completo y alguien se
// lleva una conclusion equivocada. Los numeros del aviso salen de `cobertura`, que
// el backend calcula sobre la base real: no es texto fijo.
function AvisoCobertura({ cobertura }) {
  if (!cobertura || cobertura.completo) return null
  const { por_modulo = {}, meses_sin_datos = [], atraso_dias = 0 } = cobertura
  const atrasados = Object.values(por_modulo)
    .filter((m) => m.atraso_dias != null && m.atraso_dias > 45)
    .sort((a, b) => b.atraso_dias - a.atraso_dias)

  return (
    <div className="aviso aviso-cobertura" role="status">
      <strong>Los totales de este tablero no están completos: hay un corte de captura en la serie.</strong>
      <ul>
        {atrasados.map((m) => (
          <li key={m.etiqueta}>
            {m.etiqueta}: sin datos desde el <b>{m.ultima_fecha}</b> ({m.atraso_dias} días de atraso).
          </li>
        ))}
        {meses_sin_datos.length > 0 && (
          <li>Sin ningún registro en: {meses_sin_datos.join(", ")}.</li>
        )}
        {atraso_dias > 45 && (
          <li>
            Los totales de {atraso_dias} días no se pueden usar todavía: la carga de la
            recuperación del 29/09 sigue en curso.
          </li>
        )}
      </ul>
    </div>
  )
}

// La muerte materna tiene dos fuentes y no son la misma. El certificado de defuncion
// trae un campo de "presencia de embarazo" que es un aviso del certificador, no un
// registro: en 2026 lo diligencia en 7 de las 18 muertes que documenta el registro de
// investigacion de la oficina. Por eso el tablero muestra el total del registro y deja
// el del certificado a la vista, en vez de sumar los dos o mostrar el menor sin decir
// de donde sale.
function AvisoMuerteMaterna({ mmi }) {
  if (!mmi || mmi.mm_fuente !== "REGISTRO_INVESTIGACION") return null
  const sinMarcar = (mmi.mm || 0) - (mmi.mm_certificadas || 0)
  if (sinMarcar <= 0) return null
  return (
    <div className="aviso aviso-cobertura" role="status">
      <strong>Las muertes maternas se cuentan con el registro de investigación de la oficina.</strong>{" "}
      En el periodo, el certificado de defunción marcó embarazo o puerperio en{" "}
      <b>{mmi.mm_certificadas}</b> de <b>{mmi.mm}</b>; las otras <b>{sinMarcar}</b> están en el
      registro de investigación y no en el certificado. El certificado no se rellena siempre,
      por eso el total sale del registro y no de la suma de los dos.
    </div>
  )
}

const MODULOS = ["nacimientos", "defunciones", "fichas"]
const MODULO_LABEL = { nacimientos: "Nacimientos", defunciones: "Defunciones", fichas: "Vigilancia" }
const COLORES = { nacimientos: "#0b7a4b", defunciones: "#b91c1c", fichas: "#0f5aa0" }

function maximo(mensual) {
  return Math.max(1, ...Object.values(mensual).flatMap((serie) => Object.values(serie)))
}

function SumaSerie({ serie }) {
  const total = MODULOS.reduce((acc, m) => acc + (serie[m] || 0), 0)
  return <b>{total}</b>
}

export default function Tablero() {
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState("")
  const [anio, setAnio] = useState(new Date().getFullYear())

  useEffect(() => {
    setDatos(null)
    setError("")
    obtenerDashboard({ anio })
      .then(setDatos)
      .catch((e) => setError(e.message))
  }, [anio])

  if (error) return <div className="aviso aviso-error">No se pudo cargar el tablero: {error}</div>
  if (!datos) return <div className="aviso aviso-info">Cargando indicadores…</div>

  const meses = [...new Set(Object.values(datos.mensual).flatMap((s) => Object.keys(s)))].sort()
  const max = maximo(datos.mensual)

  return (
    <div className="pagina">
      <header className="cabecera-pagina cabecera-con-control">
        <div>
          <h1>Tablero de indicadores</h1>
          <p>Resumen de nacimientos, defunciones y fichas de vigilancia del SISV.</p>
        </div>
        <div className="selector-anio">
          <label htmlFor="anio-dash">Año</label>
          <select
            id="anio-dash"
            value={anio}
            onChange={(e) => setAnio(e.target.value === "todos" ? "todos" : Number(e.target.value))}
          >
            {datos.anios_disponibles.map((a) => (
              <option key={a} value={a}>
                {a} {a === new Date().getFullYear() ? "(activo)" : ""}
              </option>
            ))}
            <option value="todos">Todos los años</option>
          </select>
        </div>
      </header>

      <AvisoCobertura cobertura={datos.cobertura} />
      <AvisoMuerteMaterna mmi={datos.mortalidad_materno_infantil} />

      <section className="tarjetas">
        {[
          ["Nacimientos", datos.totales.nacimientos, "/nacimientos", COLORES.nacimientos],
          ["Defunciones", datos.totales.defunciones, "/defunciones", COLORES.defunciones],
          ["MM (muertes maternas)", datos.mortalidad_materno_infantil?.mm || 0, "/defunciones", "#e11d48"],
          ["MN (0–27 días)", datos.mortalidad_materno_infantil?.mn || 0, "/defunciones", "#f59e0b"],
          ["Fichas de vigilancia", datos.totales.fichas, "/vigilancia", COLORES.fichas],
          ["Consolidados ENO", datos.consolidados_semanales?.total || 0, "/vigilancia", "#7c3aed"],
          ["Registros totales", datos.totales.total, null, "#6b7280"],
        ].map(([rotulo, valor, url, color]) => (
          <article key={rotulo} className="tarjeta" style={{ borderTopColor: color }}>
            <span>{rotulo}</span>
            <strong>{valor}</strong>
            {rotulo.startsWith("MM (") && (
              <small className="tarjeta-nota">
                {datos.mortalidad_materno_infantil?.mm_fuente === "REGISTRO_INVESTIGACION"
                  ? `registro de investigación · ${datos.mortalidad_materno_infantil?.mm_certificadas || 0} en certificados`
                  : "según certificado de defunción"}
              </small>
            )}
            {url && <Link to={url}>Cargar registro →</Link>}
          </article>
        ))}
      </section>

      <div className="dash-grid">
        <section className="panel">
          <h2>Registros por estado (centro/evento)</h2>
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

      <section className="panel">
        <h2>Comparativa por semana epidemiológica (SE)</h2>
        {Object.keys(datos.por_semana).length === 0 ? (
          <p className="ayuda">Sin registros en este período.</p>
        ) : (
          <table className="tabla-dash">
            <thead>
              <tr>
                <th>Semana</th>
                {MODULOS.map((m) => (
                  <th key={m}>{MODULO_LABEL[m]}</th>
                ))}
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(datos.por_semana).map(([se, serie]) => (
                <tr key={se}>
                  <td>SE-{se}</td>
                  {MODULOS.map((m) => (
                    <td key={m}>{serie[m] || 0}</td>
                  ))}
                  <td><SumaSerie serie={serie} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="panel">
        <h2>Por centro médico</h2>
        {Object.keys(datos.por_centro).length === 0 ? (
          <p className="ayuda">Sin registros en este período.</p>
        ) : (
          <table className="tabla-dash">
            <thead>
              <tr>
                <th>Centro</th>
                {MODULOS.map((m) => (
                  <th key={m}>{MODULO_LABEL[m]}</th>
                ))}
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(datos.por_centro).map(([c, serie]) => (
                <tr key={c}>
                  <td>{c}</td>
                  {MODULOS.map((m) => (
                    <td key={m}>{serie[m] || 0}</td>
                  ))}
                  <td><SumaSerie serie={serie} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="panel">
        <h2>Por ASIC</h2>
        {Object.keys(datos.por_asic).length === 0 ? (
          <p className="ayuda">Sin registros en este período.</p>
        ) : (
          <table className="tabla-dash">
            <thead>
              <tr>
                <th>ASIC</th>
                {MODULOS.map((m) => (
                  <th key={m}>{MODULO_LABEL[m]}</th>
                ))}
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(datos.por_asic).map(([a, serie]) => (
                <tr key={a}>
                  <td>{a}</td>
                  {MODULOS.map((m) => (
                    <td key={m}>{serie[m] || 0}</td>
                  ))}
                  <td><SumaSerie serie={serie} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}