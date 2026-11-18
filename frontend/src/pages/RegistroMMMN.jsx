import { useEffect, useMemo, useState } from "react"
import { consultarCertificado, reportesMMMN, reportesMMMNDetalle } from "../api/sisv"
import DetalleCertificado from "../components/DetalleCertificado"
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

function numeroFila(f) {
  return f.numero_certificado || f.numero || "—"
}

function etiquetaTipo(f) {
  return f.tipo_label || f.tipo
}

export default function RegistroMMMN({ tipo = "MM" }) {
  const hoy = new Date()
  // «MN» se acepta como alias heredado: la pantalla pasó a llamarse MI (Muerte Infantil).
  const esMM = String(tipo).toUpperCase() !== "MI" && String(tipo).toUpperCase() !== "MN"
  const clave = esMM ? "MM" : "MI"
  const textos = TEXTOS[clave]
  const [anio, setAnio] = useState(hoy.getFullYear())
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [mesSel, setMesSel] = useState(hoy.getMonth() + 1)
  // Detalle de la semana: qué certificados componen el número de la tabla.
  const [semanaAbierta, setSemanaAbierta] = useState(null)
  const [detalle, setDetalle] = useState(null)
  const [cargandoDetalle, setCargandoDetalle] = useState(false)
  const [errorDetalle, setErrorDetalle] = useState("")
  // Certificado abierto en la ventana de detalle.
  const [filaAbierta, setFilaAbierta] = useState(null)
  const [consulta, setConsulta] = useState(null)
  const [cargandoConsulta, setCargandoConsulta] = useState(false)
  const [errorConsulta, setErrorConsulta] = useState("")

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

  // Al cambiar de mes o de año la semana abierta deja de pertenecer a la tabla.
  useEffect(() => {
    setSemanaAbierta(null)
    setDetalle(null)
    setErrorDetalle("")
  }, [mesSel, anio])

  // La ventana del certificado se cierra con Escape, como cualquier diálogo.
  useEffect(() => {
    if (!filaAbierta) return undefined
    const alTeclear = (e) => {
      if (e.key !== "Escape") return
      setFilaAbierta(null)
      setConsulta(null)
      setErrorConsulta("")
      setCargandoConsulta(false)
    }
    window.addEventListener("keydown", alTeclear)
    return () => window.removeEventListener("keydown", alTeclear)
  }, [filaAbierta])

  const mes = meses.find((m) => m.mes === mesSel) || null
  const semanas = mes?.semanas || []
  const origen = datos?.mm_fuente === "CERTIFICADO"
    ? "certificados (la fuente legacy no respondió para este alcance)"
    : "registro de investigación de la oficina"

  async function abrirSemana(s) {
    setSemanaAbierta(s)
    setDetalle(null)
    setErrorDetalle("")
    setCargandoDetalle(true)
    try {
      setDetalle(
        await reportesMMMNDetalle({
          desde: s.desde,
          hasta: s.hasta,
          tipo: esMM ? "MM" : "MI",
        })
      )
    } catch (err) {
      setErrorDetalle(err.message)
    } finally {
      setCargandoDetalle(false)
    }
  }

  function cerrarSemana() {
    setSemanaAbierta(null)
    setDetalle(null)
    setErrorDetalle("")
  }

  async function abrirFila(f) {
    setFilaAbierta(f)
    setConsulta(null)
    setErrorConsulta("")
    setCargandoConsulta(false)
    if (!f.consultable) return
    setCargandoConsulta(true)
    try {
      // Por `id`: el número impreso se repite en el histórico del legacy.
      setConsulta(await consultarCertificado(f.modulo, f.numero, f.id))
    } catch (err) {
      setErrorConsulta(err.message)
    } finally {
      setCargandoConsulta(false)
    }
  }

  function cerrarFila() {
    setFilaAbierta(null)
    setConsulta(null)
    setErrorConsulta("")
    setCargandoConsulta(false)
  }

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
                      <th className="celda-total">MI (Muerte Infantil)</th>
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
                        <th className="celda-total">MI (Muerte Infantil)</th>
                        <th className="celda-total">Neonatal (0–30 d)</th>
                        <th className="celda-total">Post-neonatal (31–364 d)</th>
                      </>
                    )}
                    <th>Certificados</th>
                  </tr>
                </thead>
                <tbody>
                  {semanas.map((s) => {
                    const casos = esMM ? s.mm + s.mv : s.mi
                    const abierta =
                      semanaAbierta?.anio === s.anio && semanaAbierta?.semana === s.semana
                    return (
                      <tr
                        key={`${s.anio}-${s.semana}`}
                        className={abierta ? "fila-activa" : undefined}
                      >
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
                        <td className="acciones">
                          <button
                            type="button"
                            className="btn-mini"
                            disabled={casos === 0}
                            title={
                              casos
                                ? `Ver los ${casos} certificados o casos de la semana ${s.semana}`
                                : `La semana ${s.semana} no registró casos`
                            }
                            onClick={() => (abierta ? cerrarSemana() : abrirSemana(s))}
                          >
                            {abierta ? "Ocultar" : `Ver certificados (${casos})`}
                          </button>
                        </td>
                      </tr>
                    )
                  })}
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
                    <td className="celda-total" />
                  </tr>
                </tfoot>
              </table>
            )}

            {semanaAbierta && (
              <div className="detalle-semana">
                <div className="cabecera-lista">
                  <h3>
                    Certificados de la semana {semanaAbierta.semana} ({rangoSemana(semanaAbierta)})
                  </h3>
                  <button type="button" className="btn-mini" onClick={cerrarSemana}>
                    Cerrar
                  </button>
                </div>
                {cargandoDetalle && <p className="ayuda">Cargando los certificados…</p>}
                {errorDetalle && (
                  <div className="aviso aviso-error" role="status">
                    {errorDetalle}
                  </div>
                )}
                {detalle && detalle.filas.length === 0 && (
                  <p className="ayuda">La semana no tiene casos registrados para este indicador.</p>
                )}
                {detalle && detalle.filas.length > 0 && (
                  <>
                    <table>
                      <thead>
                        <tr>
                          <th>Tipo</th>
                          <th>Nº certificado</th>
                          <th>Nombres</th>
                          <th>Apellidos</th>
                          <th>Cédula</th>
                          <th>Fecha</th>
                          <th>Centro</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {detalle.filas.map((f) => (
                          <tr key={`${f.tipo}-${f.modulo}-${f.id}`}>
                            <td>
                              <span className="etiqueta">{etiquetaTipo(f)}</span>
                            </td>
                            <td>
                              {numeroFila(f)}
                              {f.numero_certificado && f.numero !== f.numero_certificado && (
                                <span className="ref-secundaria">{f.numero}</span>
                              )}
                            </td>
                            <td>{f.nombres || "—"}</td>
                            <td>{f.apellidos || "—"}</td>
                            <td>{f.cedula || "—"}</td>
                            <td>{f.fecha_evento ? f.fecha_evento.split("-").reverse().join("/") : "—"}</td>
                            <td>{f.centro || "—"}</td>
                            <td className="acciones">
                              <button
                                type="button"
                                className="btn-mini"
                                onClick={() => abrirFila(f)}
                                title={
                                  f.consultable
                                    ? "Ver el certificado completo"
                                    : "Ver los datos del caso"
                                }
                              >
                                {f.consultable ? "Ver certificado" : "Ver caso"}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p className="ayuda">
                      {detalle.total.mi > 0 && (
                        <>
                          MI {detalle.total.mi} (neonatal {detalle.total.mi_neonatal},
                          post-neonatal {detalle.total.mi_postneonatal}).{" "}
                        </>
                      )}
                      {detalle.mm_fuente === "REGISTRO_INVESTIGACION"
                        ? "MM y violentas salen del registro de investigación de la oficina: ese registro no guarda el número del certificado, así que se muestran sus datos para el cotejo."
                        : "MM sale del certificado (la fuente legacy no respondió para este alcance); las violentas, del registro legacy M_VIOLENTA."}
                    </p>
                  </>
                )}
              </div>
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

      {filaAbierta && (
        <div className="modal-fondo" role="presentation" onClick={cerrarFila}>
          <div
            className="modal-caja"
            role="dialog"
            aria-modal="true"
            aria-label="Detalle del certificado"
            onClick={(e) => e.stopPropagation()}
          >
            <header className="modal-cabecera">
              <div>
                <h2>
                  {consulta
                    ? `${consulta.numero_fisico || consulta.numero} — `
                    : filaAbierta.numero_certificado
                      ? `${filaAbierta.numero_certificado} — `
                      : ""}
                  {filaAbierta.nombres} {filaAbierta.apellidos}
                </h2>
                <p className="ayuda" style={{ margin: 0 }}>
                  {etiquetaTipo(filaAbierta)} ·{" "}
                  {filaAbierta.fecha_evento
                    ? filaAbierta.fecha_evento.split("-").reverse().join("/")
                    : "sin fecha"}{" "}
                  · {filaAbierta.centro || "sin centro"}
                </p>
              </div>
              <button type="button" className="btn-mini" onClick={cerrarFila}>
                Cerrar
              </button>
            </header>

            {cargandoConsulta && <p className="ayuda">Cargando el certificado…</p>}
            {errorConsulta && (
              <div className="aviso aviso-error" role="status">
                {errorConsulta}
              </div>
            )}

            {consulta && (
              <>
                <p className="ayuda">
                  Evento: {consulta.registro.fecha_evento} ·{" "}
                  {consulta.registro.organizacion_nombre || "Sin organización"} ·{" "}
                  {consulta.registro.version_cie}
                  {consulta.numero !== consulta.numero_fisico && (
                    <> · Nº de registro: {consulta.numero}</>
                  )}
                </p>
                <DetalleCertificado bloques={consulta.detalle} />
              </>
            )}

            {!filaAbierta.consultable && !cargandoConsulta && (
              <>
                <div className="aviso aviso-info" role="status">
                  {filaAbierta.nota || "Ese caso no tiene un certificado asociado en SISV."}
                </div>
                <dl className="grid-detalle">
                  <div>
                    <dt>Nombres y apellidos</dt>
                    <dd>
                      {filaAbierta.nombres} {filaAbierta.apellidos}
                    </dd>
                  </div>
                  <div>
                    <dt>Cédula</dt>
                    <dd>{filaAbierta.cedula || "—"}</dd>
                  </div>
                  <div>
                    <dt>Fecha</dt>
                    <dd>
                      {filaAbierta.fecha_evento
                        ? filaAbierta.fecha_evento.split("-").reverse().join("/")
                        : "—"}
                    </dd>
                  </div>
                  <div>
                    <dt>Edad</dt>
                    <dd>
                      {filaAbierta.edad == null
                        ? "—"
                        : `${filaAbierta.edad} ${filaAbierta.edad_unidad || ""}`.trim()}
                    </dd>
                  </div>
                  <div>
                    <dt>Centro</dt>
                    <dd>{filaAbierta.centro || "—"}</dd>
                  </div>
                  <div>
                    <dt>Fuente</dt>
                    <dd>{filaAbierta.origen === "REGISTRO_INVESTIGACION"
                      ? "Registro de investigación (legacy)"
                      : "Registro legacy"}</dd>
                  </div>
                </dl>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
