import { useEffect, useMemo, useState } from "react"
import { exportarProductividad, productividad } from "../api/sisv"
import { Campo, Input, Select } from "../components/ui"

// §45/§46 — Productividad por usuario: quién dio de alta cada registro (transcripción) y
// quién confirmó el CIE (codificación), por persona, módulo y periodo. Son dos roles
// distintos y se muestran en columnas separadas; el histórico trae el login de Oracle
// (origen LEGACY) y no se mezcla con las cuentas de SISV.
const MODULOS = [
  ["", "Todos los módulos"],
  ["nacimientos", "Nacimientos"],
  ["defunciones", "Defunciones"],
  ["mm", "Muerte materna (MM)"],
  ["mi", "Muerte infantil (MI)"],
  ["violentas", "Muertes violentas"],
  ["fichas", "Fichas de vigilancia (todas)"],
  ["vigilancia", "Vigilancia / ENO"],
  ["vacunacion", "Vacunación"],
  ["anulaciones", "Anulaciones"],
]

const AGRUPAR = [
  ["mes", "Mes"],
  ["semana", "Semana epidemiológica"],
  ["dia", "Día"],
]

const NOMBRE_MODULO = {
  nacimientos: "Nacimientos",
  defunciones: "Defunciones",
  mm: "MM",
  mi: "MI",
  violentas: "Violentas",
  fichas: "Fichas",
  vigilancia: "Vigilancia (ENO)",
  vacunacion: "Vacunación",
  anulaciones: "Anulaciones",
}

// Columnas del resumen por usuario, en el orden en que se muestran.
const COLUMNAS_RESUMEN = [
  ["nacimientos", "Nac."],
  ["defunciones", "Def."],
  ["mm", "MM"],
  ["mi", "MI"],
  ["violentas", "Viol."],
  ["fichas", "Fichas"],
  ["vigilancia", "Vigil."],
  ["vacunacion", "Vacun."],
  ["anulaciones", "Anul."],
]

function iso(fecha) {
  return fecha.toISOString().slice(0, 10)
}

function descargar(blob, nombre) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = nombre
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function fmtNumero(n) {
  return Number(n || 0).toLocaleString("es-VE")
}

function EtiquetaEstado({ estado, origen }) {
  if (!estado) return <span className="ayuda">—</span>
  if (estado === "ACTIVO") return <span className="etiqueta fiable">Activo</span>
  if (estado === "CESANTE") return <span className="etiqueta revisar">Cesante</span>
  return (
    <span className="ayuda" title={`No se pudo determinar el estado (origen ${origen || "—"})`}>
      Sin dato
    </span>
  )
}

export default function Productividad() {
  const hoy = useMemo(() => new Date(), [])
  const [desde, setDesde] = useState(iso(new Date(hoy.getFullYear(), 0, 1)))
  const [hasta, setHasta] = useState(iso(hoy))
  const [modulo, setModulo] = useState("")
  const [agrupar, setAgrupar] = useState("mes")
  const [usuario, setUsuario] = useState("")
  const [soloActivos, setSoloActivos] = useState(false)
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [exportando, setExportando] = useState("")

  const filtros = useMemo(
    () => ({ desde, hasta, modulo, agrupar, usuario: usuario.trim() }),
    [desde, hasta, modulo, agrupar, usuario]
  )

  async function cargar() {
    setCargando(true)
    setError("")
    try {
      setDatos(await productividad(filtros))
    } catch (err) {
      setError(err.message)
      setDatos(null)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [filtros])

  async function exportar(resumen = false) {
    setExportando(resumen ? "resumen" : "detalle")
    try {
      const params = resumen ? { ...filtros, resumen: 1 } : filtros
      const blob = await exportarProductividad(params)
      const sufijo = resumen ? "resumen" : "detalle"
      descargar(blob, `productividad_${sufijo}_${desde}_${hasta}.csv`)
    } catch (err) {
      setError(err.message)
    } finally {
      setExportando("")
    }
  }

  const filas = datos?.filas || []
  const resumenUsuarios = datos?.resumen_usuarios || []
  const total = datos?.total || {}
  const sinAtribuir = (datos?.sin_atribuir || []).filter((s) => s.total > 0)
  const pendientesSinAtribuir = sinAtribuir.reduce((n, s) => n + s.sin_atribuir, 0)
  const resumenVisible = soloActivos
    ? resumenUsuarios.filter((r) => r.estado === "ACTIVO")
    : resumenUsuarios
  const activos = resumenUsuarios.filter((r) => r.estado === "ACTIVO").length

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Productividad por usuario</h1>
        <p>
          Cuántos registros cargó cada persona y cuántos codificó, por persona, módulo y
          periodo. «Transcritos» es el alta del registro; «codificados» es la confirmación
          del CIE, que puede hacer otra persona. Respeta el alcance del usuario (centro o
          estado).
        </p>
      </header>

      {error && (
        <div className="aviso aviso-error" role="status">
          {error}
        </div>
      )}

      <div className="formulario">
        <div className="grid">
          <Campo label="Desde" htmlFor="prod-desde">
            <Input id="prod-desde" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} />
          </Campo>
          <Campo label="Hasta" htmlFor="prod-hasta">
            <Input id="prod-hasta" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} />
          </Campo>
          <Campo label="Módulo" htmlFor="prod-modulo">
            <Select id="prod-modulo" opciones={MODULOS} value={modulo} onChange={(e) => setModulo(e.target.value)} />
          </Campo>
          <Campo label="Agrupar por" htmlFor="prod-agrupar">
            <select id="prod-agrupar" value={agrupar} onChange={(e) => setAgrupar(e.target.value)}>
              {AGRUPAR.map(([valor, rotulo]) => (
                <option key={valor} value={valor}>
                  {rotulo}
                </option>
              ))}
            </select>
          </Campo>
          <Campo label="Usuario o login" htmlFor="prod-usuario">
            <Input
              id="prod-usuario"
              type="search"
              placeholder="p. ej. laraepid o YOLISIMORT"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
            />
          </Campo>
        </div>
        <div className="pie-form">
          <label className="campo-check">
            <input
              type="checkbox"
              checked={soloActivos}
              onChange={(e) => setSoloActivos(e.target.checked)}
            />{" "}
            Solo usuarios activos ({fmtNumero(activos)} de {fmtNumero(resumenUsuarios.length)})
          </label>
          <button type="button" className="btn-mini" onClick={cargar}>
            Actualizar
          </button>
          <button
            type="button"
            className="btn-mini"
            onClick={() => exportar(false)}
            disabled={exportando !== "" || !filas.length}
          >
            {exportando === "detalle" ? "Exportando…" : "Exportar detalle (CSV)"}
          </button>
          <button
            type="button"
            className="btn-mini"
            onClick={() => exportar(true)}
            disabled={exportando !== "" || !resumenUsuarios.length}
          >
            {exportando === "resumen" ? "Exportando…" : "Exportar resumen (CSV)"}
          </button>
        </div>
      </div>

      {cargando ? (
        <p className="ayuda">Cargando…</p>
      ) : (
        <>
          <section className="lista">
            <div className="cabecera-lista">
              <h2>Resumen por usuario y módulo</h2>
              <span className="etiqueta">
                {fmtNumero(total.transcritos)} transcritos · {fmtNumero(total.codificados)} codificados
              </span>
            </div>

            {resumenVisible.length === 0 ? (
              <p className="ayuda">
                No hay actividad atribuida a personas en el periodo. Revise las fechas: el
                periodo cuenta la fecha del alta en SISV y, en el histórico, la fecha de
                trabajo del legacy.
              </p>
            ) : (
              <div className="tabla-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Persona</th>
                      <th>Origen</th>
                      <th>Estado</th>
                      {COLUMNAS_RESUMEN.map(([clave, rotulo]) => (
                        <th className="celda-total" key={clave} title={NOMBRE_MODULO[clave]}>
                          {rotulo}
                        </th>
                      ))}
                      <th className="celda-total">Transcritos</th>
                      <th className="celda-total">Codificados</th>
                      <th className="celda-total">Pendientes CIE</th>
                      <th className="celda-total">Días</th>
                      <th className="celda-total">Prom./día</th>
                      <th>Última actividad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resumenVisible.map((r, i) => (
                      <tr key={`${r.origen}-${r.usuario}-${i}`}>
                        <td>
                          {r.nombre || r.usuario || "—"}
                          {r.nombre && r.usuario ? <span className="ayuda"> · {r.usuario}</span> : null}
                          {r.cargo ? <span className="ayuda"> ({r.cargo})</span> : null}
                        </td>
                        <td>
                          <span className={`etiqueta ${r.origen === "LEGACY" ? "revisar" : "fiable"}`}>
                            {r.origen === "LEGACY" ? "Legacy" : "SISV"}
                          </span>
                        </td>
                        <td>
                          <EtiquetaEstado estado={r.estado} origen={r.origen} />
                        </td>
                        {COLUMNAS_RESUMEN.map(([clave]) => (
                          <td className="celda-total" key={clave}>
                            {r[clave] ? fmtNumero(r[clave]) : "—"}
                          </td>
                        ))}
                        <td className="celda-total">{fmtNumero(r.transcritos)}</td>
                        <td className="celda-total">{fmtNumero(r.codificados)}</td>
                        <td className="celda-total">{fmtNumero(r.pendientes)}</td>
                        <td className="celda-total">{fmtNumero(r.dias_trabajados)}</td>
                        <td className="celda-total">{Number(r.promedio_dia || 0).toFixed(2)}</td>
                        <td>{r.ultima_actividad || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colSpan={3}>Total del periodo</td>
                      {COLUMNAS_RESUMEN.map(([clave]) => {
                        const suma = resumenVisible.reduce((n, r) => n + (r[clave] || 0), 0)
                        return (
                          <td className="celda-total" key={clave}>
                            {suma ? fmtNumero(suma) : "—"}
                          </td>
                        )
                      })}
                      <td className="celda-total">
                        {fmtNumero(resumenVisible.reduce((n, r) => n + r.transcritos, 0))}
                      </td>
                      <td className="celda-total">
                        {fmtNumero(resumenVisible.reduce((n, r) => n + r.codificados, 0))}
                      </td>
                      <td className="celda-total">
                        {fmtNumero(resumenVisible.reduce((n, r) => n + r.pendientes, 0))}
                      </td>
                      <td className="celda-total" />
                      <td className="celda-total" />
                      <td />
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}
            <p className="ayuda">
              «Fichas» suma MM + MI + violentas + las fichas sin clasificar; «Anulaciones» va
              aparte y <strong>no</strong> se suma a «Transcritos», porque anular no es
              transcribir. Los días son los días distintos con actividad en cualquier módulo.
            </p>
          </section>

          <section className="lista">
            <div className="cabecera-lista">
              <h2>Detalle por persona, módulo y periodo</h2>
            </div>

            {filas.length === 0 ? (
              <p className="ayuda">
                No hay transcripciones atribuidas en el periodo. Si esperaba datos, revise las
                fechas: el periodo cuenta la fecha del alta en SISV y, en el histórico, la fecha
                de trabajo del legacy.
              </p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Persona</th>
                    <th>Origen</th>
                    <th>Módulo</th>
                    <th>Periodo</th>
                    <th className="celda-total">Transcritos</th>
                    <th className="celda-total">Días trabajados</th>
                    <th className="celda-total">Promedio/día</th>
                    <th className="celda-total">Codificados</th>
                    <th className="celda-total">Pendientes CIE</th>
                  </tr>
                </thead>
                <tbody>
                  {filas.map((f, i) => (
                    <tr key={`${f.origen}-${f.usuario}-${f.modulo}-${f.periodo}-${i}`}>
                      <td>
                        {f.nombre || f.usuario || "—"}
                        {f.nombre && f.usuario ? <span className="ayuda"> · {f.usuario}</span> : null}
                        {f.cargo ? <span className="ayuda"> ({f.cargo})</span> : null}
                      </td>
                      <td>
                        <span className={`etiqueta ${f.origen === "LEGACY" ? "revisar" : "fiable"}`}>
                          {f.origen === "LEGACY" ? "Legacy" : "SISV"}
                        </span>
                      </td>
                      <td>{NOMBRE_MODULO[f.modulo] || f.modulo}</td>
                      <td>{f.periodo}</td>
                      <td className="celda-total">{fmtNumero(f.transcritos)}</td>
                      <td className="celda-total">{fmtNumero(f.dias_trabajados)}</td>
                      <td className="celda-total">{Number(f.promedio_dia || 0).toFixed(2)}</td>
                      <td className="celda-total">{fmtNumero(f.codificados)}</td>
                      <td className="celda-total">{fmtNumero(f.pendientes)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={4}>Total del periodo</td>
                    <td className="celda-total">{fmtNumero(total.transcritos)}</td>
                    <td className="celda-total" />
                    <td className="celda-total" />
                    <td className="celda-total">{fmtNumero(total.codificados)}</td>
                    <td className="celda-total">{fmtNumero(total.pendientes)}</td>
                  </tr>
                </tfoot>
              </table>
            )}
          </section>

          {sinAtribuir.length > 0 && (
            <section className="lista">
              <div className="cabecera-lista">
                <h2>Registros sin atribuir</h2>
                {pendientesSinAtribuir > 0 && (
                  <span className="etiqueta revisar">{fmtNumero(pendientesSinAtribuir)} sin atribución</span>
                )}
              </div>
              <table>
                <thead>
                  <tr>
                    <th>Módulo</th>
                    <th className="celda-total">Registros del periodo (fecha del evento)</th>
                    <th className="celda-total">Atribuidos</th>
                    <th className="celda-total">Sin atribuir</th>
                  </tr>
                </thead>
                <tbody>
                  {sinAtribuir.map((s) => (
                    <tr key={s.modulo}>
                      <td>{NOMBRE_MODULO[s.modulo] || s.modulo}</td>
                      <td className="celda-total">{fmtNumero(s.total)}</td>
                      <td className="celda-total">{fmtNumero(s.atribuidos)}</td>
                      <td className="celda-total">{fmtNumero(s.sin_atribuir)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="ayuda">
                «Sin atribuir» no es «no trabajó»: son registros que el sistema no puede
                atribuir a una persona. Tras los backfills del §46 quedan solo los que no
                existen en el espejo (las 17.371 defunciones de <code>lara_2019_2020</code>).
                Esta tabla cuenta por <strong>fecha del evento</strong> (el único campo de
                fecha que tienen todos los registros), así que su total no tiene por qué
                coincidir con las filas de arriba, que cuentan por fecha de transcripción.
              </p>
            </section>
          )}

          <p className="ayuda">
            Periodo consultado: {datos?.desde} a {datos?.hasta}. «Días trabajados» son los días
            distintos con al menos una transcripción y «promedio/día» = transcritos ÷ días
            trabajados del periodo. En el histórico la fecha es la de trabajo del legacy
            (certificado de nacimiento, operación de la defunción y de la ficha).
          </p>

          {(datos?.notas || []).length > 0 && (
            <section className="lista">
              <div className="cabecera-lista">
                <h2>Cómo se lee este reporte</h2>
              </div>
              {datos.notas.map((nota, i) => (
                <p className="ayuda" key={i}>
                  {nota}
                </p>
              ))}
            </section>
          )}
        </>
      )}
    </div>
  )
}
