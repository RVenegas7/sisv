import { useEffect, useState } from "react"
import { reportesMMMN } from "../api/sisv"
import { Campo, Select } from "../components/ui"

// Módulo «Registros → MM / MN»: cantidad por mes del año epidemiológico.
// Las series salen del mismo endpoint (`/registros/reportes/mm-mn-mensual/`), así que
// MM, violentas y MN siempre miden el mismo periodo y el mismo alcance.
const MESES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

const TEXTOS = {
  MM: {
    titulo: "Muertes maternas (MM) y violentas por mes",
    descripcion:
      "Muertes de mujeres con causa materna y muertes violentas del registro MMI, por mes " +
      "de ocurrencia. El indicador materno sale del registro de investigación de la oficina " +
      "(SISMAI: RENGLON_CASOSMM → CASOS_MMI); si esa fuente no está disponible se usa el " +
      "certificado y se avisa en pantalla.",
  },
  MN: {
    titulo: "Muertes neonatales (MN) por mes",
    descripcion:
      "Muertes de recién nacidos de 0 a 30 días de vida inclusive (a los 31 días ya no es " +
      "neonatal), contadas por el mes de la defunción. Lee de los certificados de defunción " +
      "cargados en SISV y respeta el alcance del usuario.",
  },
}

function opcionesAnios(hoy) {
  const anios = []
  for (let a = hoy.getFullYear(); a >= 2009; a--) anios.push([`${a}`, `${a}`])
  return anios
}

export default function RegistroMMMN({ tipo = "MM" }) {
  const hoy = new Date()
  const textos = TEXTOS[tipo] || TEXTOS.MM
  const esMM = tipo !== "MN"
  const [anio, setAnio] = useState(hoy.getFullYear())
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")

  async function cargar() {
    setCargando(true)
    setError("")
    try {
      setDatos(await reportesMMMN({ anio }))
    } catch (err) {
      setError(err.message)
      setDatos(null)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [anio, tipo])

  const meses = datos?.meses || []
  const total = datos?.total || {}
  const origen = datos?.mm_fuente === "CERTIFICADO"
    ? "certificados (la fuente legacy no respondió para este alcance)"
    : "registro de investigación de la oficina"

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>{textos.titulo}</h1>
        <p>{textos.descripcion}</p>
      </header>

      {error && (
        <div className="aviso aviso-error" role="status">
          {error}
        </div>
      )}

      <div className="formulario">
        <div className="grid">
          <Campo label="Año" htmlFor={`${tipo}-anio`}>
            <Select
              id={`${tipo}-anio`}
              opciones={opcionesAnios(hoy)}
              value={String(anio)}
              onChange={(e) => setAnio(Number(e.target.value))}
            />
          </Campo>
        </div>
        <div className="pie-form">
          <button type="button" className="btn-mini" onClick={cargar}>
            Actualizar
          </button>
        </div>
      </div>

      {cargando ? (
        <p className="ayuda">Cargando…</p>
      ) : (
        <section className="lista">
          <div className="cabecera-lista">
            <h2>
              {esMM ? "Muertes maternas violentas y no violentas" : "Muertes neonatales (0–30 días)"} — {anio}
            </h2>
            <span className="etiqueta">
              {esMM
                ? `${total.mm_mv ?? 0} MM + violentas`
                : `${total.mn ?? 0} en el año`}
            </span>
          </div>

          <table>
            <thead>
              <tr>
                <th>Mes</th>
                {esMM ? (
                  <>
                    <th className="celda-total">MM</th>
                    <th className="celda-total">Violentas</th>
                    <th className="celda-total">Total MM + violentas</th>
                    <th className="celda-total">Certificados con marca MM</th>
                  </>
                ) : (
                  <th className="celda-total">Casos</th>
                )}
              </tr>
            </thead>
            <tbody>
              {meses.map((m) => (
                <tr key={m.mes}>
                  <td>
                    {String(m.mes).padStart(2, "0")} — {m.nombre}
                  </td>
                  {esMM ? (
                    <>
                      <td className="celda-total">{m.mm}</td>
                      <td className="celda-total">{m.mv}</td>
                      <td className="celda-total">{m.mm_mv}</td>
                      <td className="celda-total">{m.mm_certificadas}</td>
                    </>
                  ) : (
                    <td className="celda-total">{m.mn}</td>
                  )}
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td>Total {anio}</td>
                {esMM ? (
                  <>
                    <td className="celda-total">{total.mm ?? 0}</td>
                    <td className="celda-total">{total.mv ?? 0}</td>
                    <td className="celda-total">{total.mm_mv ?? 0}</td>
                    <td className="celda-total">{total.mm_certificadas ?? 0}</td>
                  </>
                ) : (
                  <td className="celda-total">{total.mn ?? 0}</td>
                )}
              </tr>
            </tfoot>
          </table>

          <p className="ayuda">
            Periodo: {datos?.desde} a {datos?.hasta} (año epidemiológico, domingo–sábado).
            {esMM && ` Origen del indicador materno: ${origen}.`}
          </p>
          {esMM && (
            <>
              <p className="ayuda">
                «Violentas» son las muertes del registro MMI de muertes violentas del legacy
                (M_VIOLENTA); se muestran aparte y se suman en «Total MM + violentas».
              </p>
              <p className="ayuda">
                El legacy dejó de alimentar ese registro el 26/01/2022: desde entonces la columna
                sale en cero, y eso no quiere decir que no haya habido muertes violentas, sino que
                no se están registrando en el sistema viejo. Además, la mayoría de esas fichas no
                traen establecimiento, así que un usuario de centro solo ve las que tienen centro
                identificado.
              </p>
              <p className="ayuda">
                «Certificados con marca MM» son los que traen el aviso de embarazo/puerperio en el
                certificado. No se suman al indicador: se muestran para poder compararlos.
              </p>
            </>
          )}
        </section>
      )}
    </div>
  )
}
