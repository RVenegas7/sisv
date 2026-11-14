import { useEffect, useMemo, useState } from "react"
import { exportarProductividad, productividad } from "../api/sisv"
import { Campo, Input, Select } from "../components/ui"

// §45 — Productividad por usuario: quién dio de alta cada certificado (transcripción) y
// quién confirmó el CIE (codificación), por persona y por periodo. Son dos roles
// distintos y se muestran en columnas separadas; el histórico de natalidad trae el login
// de Oracle (origen LEGACY) y no se mezcla con las cuentas de SISV.
const MODULOS = [
  ["", "Todos los módulos"],
  ["nacimientos", "Nacimientos"],
  ["defunciones", "Defunciones"],
  ["fichas", "Fichas de vigilancia"],
]

const AGRUPAR = [
  ["mes", "Mes"],
  ["semana", "Semana epidemiológica"],
  ["dia", "Día"],
]

const NOMBRE_MODULO = {
  nacimientos: "Nacimientos",
  defunciones: "Defunciones",
  fichas: "Fichas",
}

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

export default function Productividad() {
  const hoy = useMemo(() => new Date(), [])
  const [desde, setDesde] = useState(iso(new Date(hoy.getFullYear(), 0, 1)))
  const [hasta, setHasta] = useState(iso(hoy))
  const [modulo, setModulo] = useState("")
  const [agrupar, setAgrupar] = useState("mes")
  const [usuario, setUsuario] = useState("")
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState("")
  const [exportando, setExportando] = useState(false)

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

  async function exportar() {
    setExportando(true)
    try {
      const blob = await exportarProductividad(filtros)
      descargar(blob, `productividad_${desde}_${hasta}.csv`)
    } catch (err) {
      setError(err.message)
    } finally {
      setExportando(false)
    }
  }

  const filas = datos?.filas || []
  const total = datos?.total || {}
  const sinAtribuir = (datos?.sin_atribuir || []).filter((s) => s.total > 0)
  const pendientes = sinAtribuir.reduce((n, s) => n + s.sin_atribuir, 0)

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Productividad por usuario</h1>
        <p>
          Cuántos certificados cargó cada persona y cuántos codificó, por persona y
          periodo. «Transcritos» es el alta del certificado; «codificados» es la
          confirmación del CIE, que puede hacer otra persona. Respeta el alcance del
          usuario (centro o estado).
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
              placeholder="p. ej. laraepid o MARINAT"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
            />
          </Campo>
        </div>
        <div className="pie-form">
          <button type="button" className="btn-mini" onClick={cargar}>
            Actualizar
          </button>
          <button type="button" className="btn-mini" onClick={exportar} disabled={exportando || !filas.length}>
            {exportando ? "Exportando…" : "Exportar CSV"}
          </button>
        </div>
      </div>

      {cargando ? (
        <p className="ayuda">Cargando…</p>
      ) : (
        <>
          <section className="lista">
            <div className="cabecera-lista">
              <h2>Transcripciones y codificaciones por persona</h2>
              <span className="etiqueta">
                {fmtNumero(total.transcritos)} transcritos · {fmtNumero(total.codificados)} codificados
              </span>
            </div>

            {filas.length === 0 ? (
              <p className="ayuda">
                No hay transcripciones atribuidas en el periodo. Si esperaba datos, revise las
                fechas: el periodo cuenta la fecha del alta en SISV y, en el histórico, la del
                certificado.
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
                {pendientes > 0 && (
                  <span className="etiqueta revisar">{fmtNumero(pendientes)} sin atribución</span>
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
                «Sin atribuir» no es «no trabajó»: son certificados que el sistema no puede
                atribuir a una persona. Las defunciones del sistema anterior no guardan quién las
                transcribió; en natalidad el histórico sí trae el login y por eso aparece como
                origen Legacy. Esta tabla cuenta por <strong>fecha del evento</strong> (el único
                campo de fecha que tienen todos los registros), así que su total no tiene por qué
                coincidir con las filas de arriba, que cuentan por fecha de transcripción o de
                certificado.
              </p>
            </section>
          )}

          <p className="ayuda">
            Periodo consultado: {datos?.desde} a {datos?.hasta}. «Días trabajados» son los días
            distintos con al menos una transcripción y «promedio/día» = transcritos ÷ días
            trabajados del periodo. La fecha es la del alta en SISV y, en el histórico de
            natalidad, la del certificado (es la que usa el reporte de la oficina).
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
