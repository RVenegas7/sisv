import { useEffect, useMemo, useState } from "react"
import { reportesMMMN } from "../api/sisv"
import { Campo, Select } from "../components/ui"

// Módulo «Registros → Muerte Materna (MM) / Muerte Infantil (MI)»: cantidad por
// mes del año epidemiológico y, en cascada, por semana epidemiológica del mes
// elegido. Las series salen del mismo endpoint
// (`/registros/reportes/mm-mi-mensual/`, con `mm-mn-mensual/` como alias heredado en
// el backend), así que MM, violentas, MI y sus desgloses siempre miden el mismo
// periodo y el mismo alcance.
const MESES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

const TEXTOS = {
  MM: {
    titulo: "Muerte materna (MM) y violentas, por mes y semana",
    descripcion:
      "Muertes de mujeres con causa materna y muertes violentas del registro MMI, " +
      "por mes de ocurrencia y, en cascada, por semana epidemiológica. El indicador " +
      "materno sale del registro de investigación de la oficina (SISMAI: " +
      "RENGLON_CASOSMM → CASOS_MMI); si esa fuente no está disponible se usa el " +
      "certificado y se avisa en pantalla.",
  },
  MI: {
    titulo: "Muerte infantil (MI), por mes y semana",
    descripcion:
      "Muertes de menores de 1 año (0 a 364 días de vida), contadas por el mes de la " +
      "defunción y, en cascada, por semana epidemiológica, con el desglose neonatal " +
      "(0–30 días) y post-neonatal (31–364 días). Lee de los certificados de " +
      "defunción cargados en SISV y respeta el alcance del usuario.",
  },
}

function opcionesAnios(hoy) {
  const anios = []
  for (let a = hoy.getFullYear(); a >= 2009; a--) anios.push([`${a}`, `${a}`])
  return anios
}

function opcionesMeses(meses) {
  return meses.map((m) => [String(m.mes), `${String(m.mes).padStart(2, "0")} — ${m.nombre}`])
}

function rangoSemana(s) {
  const d = (iso) => {
    const [a, mes, dia] = iso.split("-")
    return `${dia}/${mes}`
  }
  return `${d(s.desde)} – ${d(s.hasta)}`
}

export default function RegistroMMMN({ tipo = "MM" }) {
  const hoy = new Date()
  // «MN» se acepta como alias heredado: la pantalla pasó a llamarse MI (<1 año).
  const esMM = String(tipo).toUpperCase() !== "MI" && String(tipo).toUpperCase() !== "MN"
  const clave = esMM ? "MM" : "MI"
  const textos = TEXTOS[clave]
  const [anio, setAnio] = useState(hoy.getFullYear())
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [mesSel, setMesSel] = useState(hoy.getMonth() + 1)

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

  const meses = useMemo(() => datos?.meses || [], [datos])
  const total = datos?.total || {}

  // Al cambiar de año, el mes de la cascada se recoloca: el mes en curso si el año
  // es el actual, y si no el último mes que traiga semanas.
  useEffect(() => {
    if (!meses.length) return
    const conSemanas = meses.filter((m) => (m.semanas || []).length)
    const enCurso = anio === hoy.getFullYear() ? hoy.getMonth() + 1 : null
    if (enCurso && conSemanas.some((m) => m.mes === enCurso)) {
      setMesSel(enCurso)
    } else if (conSemanas.length) {
      setMesSel(conSemanas[conSemanas.length - 1].mes)
    } else {
      setMesSel(enCurso || 1)
    }
  }, [meses, anio])

  const mes = meses.find((m) => m.mes === mesSel) || null
  const semanas = mes?.semanas || []
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
          <Campo label="Año" htmlFor={`${clave}-anio`}>
            <Select
              id={`${clave}-anio`}
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
        <>
          <section className="lista">
            <div className="cabecera-lista">
              <h2>
                {esMM
                  ? "Muertes maternas violentas y no violentas"
                  : "Muertes infantiles (menores de 1 año)"} — {anio}
              </h2>
              <span className="etiqueta">
                {esMM
                  ? `${total.mm_mv ?? 0} MM + violentas`
                  : `${total.mi ?? 0} MI en el año`}
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
                    <>
                      <th className="celda-total">MI (&lt;1 año)</th>
                      <th className="celda-total">Neonatal (0–30 d)</th>
                      <th className="celda-total">Post-neonatal (31–364 d)</th>
                    </>
                  )}
                  <th className="celda-total">Semanas</th>
                </tr>
              </thead>
              <tbody>
                {meses.map((m) => (
                  <tr
                    key={m.mes}
                    className={m.mes === mesSel ? "fila-activa" : undefined}
                  >
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
                      <>
                        <td className="celda-total">{m.mi}</td>
                        <td className="celda-total">{m.mi_neonatal}</td>
                        <td className="celda-total">{m.mi_postneonatal}</td>
                      </>
                    )}
                    <td className="celda-total">
                      <button
                        type="button"
                        className="btn-mini"
                        onClick={() => setMesSel(m.mes)}
                        disabled={(m.semanas || []).length === 0}
                        title={
                          (m.semanas || []).length
                            ? `Ver las ${m.semanas.length} semanas de ${m.nombre}`
                            : `Sin semanas registradas en ${m.nombre}`
                        }
                      >
                        {(m.semanas || []).length}
                      </button>
                    </td>
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
                    <>
                      <td className="celda-total">{total.mi ?? 0}</td>
                      <td className="celda-total">{total.mi_neonatal ?? 0}</td>
                      <td className="celda-total">{total.mi_postneonatal ?? 0}</td>
                    </>
                  )}
                  <td className="celda-total">
                    {meses.reduce((n, m) => n + (m.semanas || []).length, 0)}
                  </td>
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
            {!esMM && (
              <p className="ayuda">
                «MI» son los menores de 1 año. «Neonatal» es 0 a 30 días inclusive (a los 31 ya no
                es neonatal) y «post-neonatal» de 31 a 364 días; el total de MI es la suma de los
                dos. La edad sale de la declarada en el certificado y, si no la trae, de la fecha de
                nacimiento; cuando no hay ninguna de las dos la defunción no se puede clasificar,
                así que las cifras son un mínimo.
              </p>
            )}
          </section>

          <section className="lista">
            <div className="cabecera-lista">
              <h2>Detalle por semana epidemiológica</h2>
              <span className="etiqueta">
                {mes ? `${semanas.length} semanas en ${mes.nombre}` : "sin mes"}
              </span>
            </div>

            <div className="formulario">
              <div className="grid">
                <Campo label="Mes" htmlFor={`${clave}-mes`}>
                  <Select
                    id={`${clave}-mes`}
                    opciones={opcionesMeses(meses)}
                    value={String(mesSel)}
                    onChange={(e) => setMesSel(Number(e.target.value))}
                  />
                </Campo>
              </div>
            </div>

            {semanas.length === 0 ? (
              <p className="ayuda">
                {mes
                  ? `${mes.nombre} de ${anio} no tiene semanas con datos cargados todavía.`
                  : "Seleccione un mes."}
              </p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Semana</th>
                    <th>Periodo</th>
                    {esMM ? (
                      <>
                        <th className="celda-total">MM</th>
                        <th className="celda-total">Violentas</th>
                        <th className="celda-total">Total MM + violentas</th>
                      </>
                    ) : (
                      <>
                        <th className="celda-total">MI (&lt;1 año)</th>
                        <th className="celda-total">Neonatal (0–30 d)</th>
                        <th className="celda-total">Post-neonatal (31–364 d)</th>
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {semanas.map((s) => (
                    <tr key={`${s.anio}-${s.semana}`}>
                      <td>Semana {s.semana}</td>
                      <td>{rangoSemana(s)}</td>
                      {esMM ? (
                        <>
                          <td className="celda-total">{s.mm}</td>
                          <td className="celda-total">{s.mv}</td>
                          <td className="celda-total">{s.mm_mv}</td>
                        </>
                      ) : (
                        <>
                          <td className="celda-total">{s.mi}</td>
                          <td className="celda-total">{s.mi_neonatal}</td>
                          <td className="celda-total">{s.mi_postneonatal}</td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={2}>Suma de las semanas</td>
                    {esMM ? (
                      <>
                        <td className="celda-total">
                          {semanas.reduce((n, s) => n + s.mm, 0)}
                        </td>
                        <td className="celda-total">
                          {semanas.reduce((n, s) => n + s.mv, 0)}
                        </td>
                        <td className="celda-total">
                          {semanas.reduce((n, s) => n + s.mm_mv, 0)}
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="celda-total">
                          {semanas.reduce((n, s) => n + s.mi, 0)}
                        </td>
                        <td className="celda-total">
                          {semanas.reduce((n, s) => n + s.mi_neonatal, 0)}
                        </td>
                        <td className="celda-total">
                          {semanas.reduce((n, s) => n + s.mi_postneonatal, 0)}
                        </td>
                      </>
                    )}
                  </tr>
                </tfoot>
              </table>
            )}

            <p className="ayuda">
              La semana epidemiológica va de domingo a sábado y pertenece al mes donde
              <strong> empieza</strong> (su domingo). Como puede cruzar el cambio de mes, la suma
              de las semanas puede diferir en unos pocos casos del total mensual, que es por mes
              calendario; el año completo sí cuadra.
            </p>
            <p className="ayuda">
              Se listan todas las semanas que ya empezaron en el mes; una semana en cero
              significa que el indicador no registró casos en ella.
            </p>
          </section>
        </>
      )}
    </div>
  )
}
