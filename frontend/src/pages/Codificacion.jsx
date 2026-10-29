import { useEffect, useMemo, useState } from "react"
import {
  actualizarDefuncion,
  actualizarFicha,
  actualizarNacimiento,
  confirmarCodificacion,
  consultarCertificado,
  listarCodificacion,
} from "../api/sisv"
import CIESearch from "../components/CIESearch"
import SeccionCIE from "../components/SeccionCIE"
import { Boton, Campo, Input, Select } from "../components/ui"
import { seleccionDesdeRegistro, validarCIE } from "../utils/cie"

const MODULOS = [
  ["defunciones", "Defunciones"],
  ["nacimientos", "Nacimientos"],
  ["fichas", "Fichas de vigilancia"],
]

const CERO = { cie10: null, cie11: null, subgrupo: null }

function nombres(modulo, r) {
  if (modulo === "defunciones") return `${r.fallecido_nombres || ""} ${r.fallecido_apellidos || ""}`.trim()
  if (modulo === "nacimientos") return `${r.madre_nombres || ""} ${r.madre_apellidos || ""}`.trim()
  return `${r.paciente_nombres || ""} ${r.paciente_apellidos || ""}`.trim()
}

function codigo(modulo, r) {
  if (modulo === "defunciones") return r.registro_numero
  if (modulo === "nacimientos") return r.registro_numero
  return r.codigo_notificacion || ""
}

// Las fuentes fiables salen del código ya registrado en el certificado (cross-walk de
// la OMS o el propio CIE-10 histórico); las demás salen de cruzar texto con el catálogo
// y pueden equivocarse. Ver PENDIENTES.md §41.
const FUENTES_FIABLES = ["CROSSWALK", "CIE10-LEGACY"]

function esFuenteFiable(fuente) {
  return FUENTES_FIABLES.includes(fuente)
}

function esFiable(sugerencia) {
  if (sugerencia?.origen === "LEGACY") return true
  const causa = sugerencia?.detalle?.causa_basica
  return esFuenteFiable(causa?.fuente)
}

// Precarga la selección con el código ya registrado (si lo hay) o con el sugerido.
function seleccionDesdeConsulta(data) {
  const reg = data.registro || {}
  const sug = data.sugerencia || {}
  if (reg.version_cie === "CIE10" && reg.cie10_detalle) {
    return { cie10: { ...reg.cie10_detalle }, cie11: null, subgrupo: null }
  }
  if (reg.version_cie === "CIE11" && reg.cie11_detalle) {
    return { cie10: null, cie11: { ...reg.cie11_detalle }, subgrupo: null }
  }
  if (sug.codigo) {
    if (sug.version === "CIE10") return { cie10: { codigo: sug.codigo, descripcion: sug.titulo }, cie11: null, subgrupo: null }
    return { cie10: null, cie11: { codigo: sug.codigo, titulo: sug.titulo, nivel: null }, subgrupo: null }
  }
  return CERO
}

function BloqueDetalle({ bloques }) {
  return (
    <div className="detalle-certificado">
      {bloques.map((b) => (
        <section key={b.grupo} className="seccion">
          <h3>{b.grupo}</h3>
          <dl className="grid-detalle">
            {b.campos.map((c) => (
              <div key={c.campo}>
                <dt>{c.etiqueta}</dt>
                <dd>{c.valor}</dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
    </div>
  )
}

export default function Codificacion({ usuario }) {
  const permisos = usuario?.permisos || {}
  const hoy = new Date()
  const [modulo, setModulo] = useState("defunciones")
  const [resumen, setResumen] = useState({ defunciones: 0, nacimientos: 0, fichas: 0 })
  const [lista, setLista] = useState([])
  const [paginacion, setPaginacion] = useState(null)
  const [q, setQ] = useState("")
  const [anio, setAnio] = useState(hoy.getFullYear())
  const [seleccionado, setSeleccionado] = useState(null)
  const [verSeleccionado, setVerSeleccionado] = useState(null)
  const [versionManual, setVersionManual] = useState(false)
  const [estadoUI, setEstadoUI] = useState({ tipo: "", texto: "" })

  const [numeroConsulta, setNumeroConsulta] = useState("")
  const [consulta, setConsulta] = useState(null)
  const [seleccionConsulta, setSeleccionConsulta] = useState(CERO)
  const [versionConsulta, setVersionConsulta] = useState("CIE11")
  const [versionManualConsulta, setVersionManualConsulta] = useState(false)

  const esLectura = !permisos.puede_editar
  const puedeCodificar = Boolean(permisos.puede_codificar)
  const soloLectura = !permisos.puede_editar && !puedeCodificar

  function aviso(tipo, texto) {
    setEstadoUI({ tipo, texto })
  }

  async function cargar(pagina = 1, m = modulo, query = q, anioSel = anio) {
    try {
      const params = { modulo: m, q: query, pagina, anio: anioSel }
      const r = await listarCodificacion(params)
      setResumen(r.resumen || { defunciones: 0, nacimientos: 0, fichas: 0 })
      setLista(r.data || [])
      setPaginacion(r.pagination || null)
      setModulo(m)
    } catch (err) {
      aviso("error", err.message)
      setLista([])
    }
  }

  useEffect(() => {
    cargar(1, modulo, "", "todos")
  }, [])

  function cambiarModulo(m) {
    setSeleccionado(null)
    setVerSeleccionado(null)
    setQ("")
    cargar(1, m, "", "todos")
  }

  async function aplicar(reg) {
    setSeleccionado(reg)
    // Misma precarga que las páginas de carga: conserva el subgrupo CIE-11
    // (reg.cie11 = id del subgrupo cuando lo hay; cie11_detalle = categoría).
    setVerSeleccionado(await seleccionDesdeRegistro(reg))
    setVersionManual(false)
    aviso("", "")
  }

  async function guardarCIE() {
    if (!seleccionado || esLectura) return
    const version = seleccionado.version_cie || "CIE11"
    const errorCie = validarCIE(version, verSeleccionado)
    if (errorCie) {
      aviso("error", errorCie)
      return
    }
    const payload = {
      version_cie: version,
      cie10: version === "CIE10" ? verSeleccionado?.cie10?.id : null,
      cie11: version === "CIE11" ? verSeleccionado?.cie11?.id : null,
    }
    aviso("info", "Guardando codificación…")
    try {
      const fn = {
        defunciones: actualizarDefuncion,
        nacimientos: actualizarNacimiento,
        fichas: actualizarFicha,
      }[modulo]
      const actualizado = await fn(seleccionado.id, payload)
      aviso("ok", `Código CIE guardado (${codigo(modulo, actualizado)}).`)
      setSeleccionado(null)
      setVerSeleccionado(null)
      await cargar(paginacion?.pagina || 1)
    } catch (err) {
      aviso("error", err.message)
    }
  }

  async function consultarPorNumero() {
    const num = numeroConsulta.trim()
    if (!num) {
      aviso("error", "Escriba el número del certificado.")
      return
    }
    aviso("info", "Consultando certificado…")
    try {
      const data = await consultarCertificado(modulo, num)
      setConsulta(data)
      setVersionConsulta(data.registro?.version_cie || "CIE11")
      setVersionManualConsulta(false)
      setSeleccionConsulta(seleccionDesdeConsulta(data))
      aviso("", "")
    } catch (err) {
      setConsulta(null)
      aviso("error", err.message)
    }
  }

  function usarCandidato(c) {
    if (versionConsulta === "CIE10") {
      setSeleccionConsulta({ cie10: { codigo: c.codigo, descripcion: c.titulo }, cie11: null, subgrupo: null })
    } else {
      setSeleccionConsulta({ cie10: null, cie11: { codigo: c.codigo, titulo: c.titulo, nivel: c.nivel }, subgrupo: null })
    }
  }

  async function confirmarConsulta() {
    if (!consulta || !puedeCodificar) return
    const codigoSel = seleccionConsulta?.cie11?.codigo || seleccionConsulta?.cie10?.codigo
    if (!codigoSel) {
      aviso("error", "No hay código para confirmar.")
      return
    }
    aviso("info", "Confirmando codificación…")
    try {
      const actualizado = await confirmarCodificacion({
        modulo,
        numero: consulta.numero,
        codigo: codigoSel,
        version_cie: versionConsulta,
      })
      const conf = actualizado.cie11_detalle || actualizado.cie10_detalle
      aviso("ok", `Codificación confirmada: ${conf?.codigo || codigoSel}.`)
      await consultarPorNumero()
    } catch (err) {
      aviso("error", err.message)
    }
  }

  const sugerido = seleccionado?.cie11_sugerido_detalle
  const totalPendientes = useMemo(
    () => Object.values(resumen || {}).reduce((a, b) => a + (Number(b) || 0), 0),
    [resumen]
  )

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Codificación CIE</h1>
        <p>
          Bandeja de codificación: defunciones, nacimientos y fichas de vigilancia pendientes de
          clasificación CIE. Seleccione un registro y asigne el código (el buscador sugiere el
          cross-walk CIE-10→CIE-11).
        </p>
      </header>

      {estadoUI.tipo && (
        <div className={`aviso aviso-${estadoUI.tipo}`} role="status">
          {estadoUI.texto}
        </div>
      )}

      {soloLectura && (
        <div className="aviso aviso-info">
          Su rol (<strong>{usuario?.rol_label}</strong>) es de solo lectura: no puede guardar códigos CIE.
        </div>
      )}

      {puedeCodificar && (
        <div className="aviso aviso-info">
          Rol <strong>{usuario?.rol_label}</strong>: consulte un certificado por el número impreso (o el de
          registro), revise los datos ya registrados y confirme la codificación CIE (sugerida automáticamente
          por el catálogo). El certificado no se puede editar desde aquí.
        </div>
      )}

      <div className="formulario">
        <div className="grid">
          <Campo label="Consultar certificado por número impreso o de registro" htmlFor="cod-num">
            <Input
              id="cod-num"
              value={numeroConsulta}
              onChange={(e) => setNumeroConsulta(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  consultarPorNumero()
                }
              }}
              placeholder="Ej. 5143453 (impreso), DEF-2026-000003…"
            />
          </Campo>
        </div>
        <div className="pie-form">
          <Boton type="button" onClick={consultarPorNumero}>
            Consultar
          </Boton>
          {consulta && (
            <button
              type="button"
              className="btn-mini"
              onClick={() => {
                setConsulta(null)
                setNumeroConsulta("")
              }}
            >
              Cerrar consulta
            </button>
          )}
        </div>
      </div>

      <div className="filas-campo" style={{ marginBottom: "0.8rem" }}>
        {MODULOS.map(([k, r]) => (
          <button
            key={k}
            type="button"
            className={`btn-mini ${modulo === k ? "activo" : ""}`}
            onClick={() => cambiarModulo(k)}
          >
            {r} ({resumen?.[k] ?? 0})
          </button>
        ))}
        <span className="ayuda" style={{ marginLeft: "0.6rem" }}>
          Total pendientes: <strong>{totalPendientes}</strong>
        </span>
      </div>

      {consulta && (
        <section className="panel" style={{ marginTop: "1rem" }}>
          <header className="cabecera-seccion">
            <h2>
              {consulta.numero_fisico || consulta.numero} — {nombres(modulo, consulta.registro)}
              <span className="etiqueta">{consulta.registro.version_cie}</span>
            </h2>
            <p className="ayuda" style={{ margin: 0 }}>
              Evento: {consulta.registro.fecha_evento} ·{" "}
              {consulta.registro.organizacion_nombre || "Sin organización"}
              {consulta.registro.cie10_legacy ? ` · CIE-10 legacy: ${consulta.registro.cie10_legacy}` : ""}
            </p>
            {consulta.numero_fisico && (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                Nº impreso: <strong>{consulta.numero_fisico}</strong> · Nº de registro:{" "}
                {consulta.numero}
              </p>
            )}
            {consulta.numero_origen === "fisico" && consulta.coincidencias === 1 && (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                Encontrado por el número impreso del certificado.
              </p>
            )}
            {consulta.aviso && (
              <div className="aviso aviso-info" role="status" style={{ marginTop: "0.5rem" }}>
                {consulta.aviso}
                {(consulta.candidatos || []).length > 0 && (
                  <ul style={{ margin: "0.4rem 0 0 1rem" }}>
                    {consulta.candidatos.map((c) => (
                      <li key={c.id}>
                        {c.fecha_evento} · {c.organizacion_nombre || "Sin centro"} ·{" "}
                        <span className="ayuda">{c.registro_numero}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
            {consulta.registro.codificado_en ? (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                <span className="etiqueta">Confirmado</span> por{" "}
                <strong>{consulta.registro.codificado_por_nombre || "—"}</strong> el{" "}
                {new Date(consulta.registro.codificado_en).toLocaleString()}
              </p>
            ) : (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                <span className="etiqueta">Pendiente de confirmación</span> · la codificación{" "}
                {consulta.registro.cie11_detalle || consulta.registro.cie10_detalle ? (
                  <>ya registrada: <strong>
                    {consulta.registro.cie11_detalle?.codigo || consulta.registro.cie10_detalle?.codigo}
                  </strong></>
                ) : (
                  <>aún no registrada</>
                )}
              </p>
            )}
          </header>

          <BloqueDetalle bloques={consulta.detalle} />

          <section className="seccion">
            <h3>Sugerencia de codificación</h3>
            {consulta.sugerencia?.codigo ? (
              <>
                <p className="ayuda">
                  {esFiable(consulta.sugerencia) ? (
                    <>
                      <span className="etiqueta fiable" title="Viene del código ya registrado en el certificado">
                        Fiable
                      </span>{" "}
                      Propuesta desde el código del certificado:{" "}
                      <strong>{consulta.sugerencia.codigo}</strong> — {consulta.sugerencia.titulo}
                    </>
                  ) : (
                    <>
                      <span className="etiqueta revisar" title="Salió de cruzar el texto con el catálogo: puede ser errónea">
                        Revisar
                      </span>{" "}
                      Propuesta por texto (el nombre se parece a{" "}
                      <strong>{consulta.sugerencia.codigo}</strong> — {consulta.sugerencia.titulo}
                      ), no por el código del certificado. <strong>Compárela con la causa escrita</strong>
                      {" "}antes de confirmar: hay casos en que el parecido de palabras engaña.
                    </>
                  )}
                </p>
                <ul className="sugerencias-cat">
                  {(consulta.sugerencia.detalle?.candidatos || []).map((c) => (
                    <li key={`${c.codigo}-${c.titulo}`}>
                      <button
                        type="button"
                        className="btn-mini"
                        disabled={!puedeCodificar}
                        onClick={() => usarCandidato(c)}
                        title="Usar este código"
                      >
                        {esFuenteFiable(c.fuente) ? "✓ " : "? "}
                        <strong>{c.codigo}</strong> — {c.titulo}
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="ayuda">No hay texto de causa para sugerir un código automáticamente.</p>
            )}
          </section>

          {puedeCodificar && (
            <SeccionCIE
              titulo="Codificación CIE a confirmar"
              etiqueta="Código de la causa"
              fechaEvento={consulta.registro.fecha_evento}
              version={versionConsulta}
              setVersion={(v) => {
                setVersionConsulta(v)
                setVersionManualConsulta(true)
                setSeleccionConsulta(CERO)
              }}
              versionManual={versionManualConsulta}
              setVersionManual={setVersionManualConsulta}
              seleccion={seleccionConsulta}
              setSeleccion={setSeleccionConsulta}
            />
          )}

          <div className="pie-form">
            <Boton type="button" disabled={!puedeCodificar} onClick={confirmarConsulta}>
              {puedeCodificar ? "Confirmar codificación CIE" : "Solo lectura"}
            </Boton>
            {!puedeCodificar && (
              <span className="ayuda">Su rol no puede confirmar codificaciones.</span>
            )}
          </div>
        </section>
      )}

      {!seleccionado && (
        <div className="formulario">
          <div className="grid">
            <Campo label="Buscar por nº de registro o nombre" htmlFor="cod-q">
              <Input
                id="cod-q"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    cargar(1)
                  }
                }}
                placeholder="Registro, nombre…"
              />
            </Campo>
            <Campo label="Año" htmlFor="cod-anio">
              <Select
                id="cod-anio"
                opciones={[
                  [String(hoy.getFullYear()), String(hoy.getFullYear())],
                  [String(hoy.getFullYear() - 1), String(hoy.getFullYear() - 1)],
                  ["todos", "Todos los años"],
                ]}
                value={String(anio)}
                onChange={(e) => {
                  const v = e.target.value === "todos" ? "todos" : Number(e.target.value)
                  setAnio(v)
                  cargar(1, modulo, q, v)
                }}
              />
            </Campo>
          </div>
          <div className="pie-form">
            <Boton type="button" onClick={() => cargar(1)}>
              Consultar
            </Boton>
          </div>
        </div>
      )}

      {seleccionado && (
        <section className="panel" style={{ marginTop: "1rem" }}>
          <header className="cabecera-seccion">
            <h2>
              {codigo(modulo, seleccionado)} — {nombres(modulo, seleccionado)}
              <span className="etiqueta">{seleccionado.version_cie}</span>
            </h2>
            <p className="ayuda" style={{ margin: 0 }}>
              Evento: {seleccionado.fecha_evento} · {seleccionado.organizacion_nombre || "Sin organización"}
              {seleccionado.causa_directa ? ` · Causa: ${seleccionado.causa_directa}` : ""}
              {seleccionado.estado ? ` · ${seleccionado.estado}/${seleccionado.municipio || ""}` : ""}
            </p>
            {seleccionado.cie10_legacy && (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                Código CIE-10 original (legacy): <strong>{seleccionado.cie10_legacy}</strong>
              </p>
            )}
            {sugerido && (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                Sugerencia cross-walk: <strong>{sugerido.codigo}</strong> — {sugerido.titulo}
              </p>
            )}
            <button type="button" className="btn-mini" style={{ marginTop: "0.6rem" }} onClick={() => { setSeleccionado(null); setVerSeleccionado(null); cargar(paginacion?.pagina || 1) }}>
              ← Volver a la lista
            </button>
          </header>

          <SeccionCIE
            titulo="Clasificación CIE"
            etiqueta="Código de la causa"
            fechaEvento={seleccionado.fecha_evento}
            version={seleccionado.version_cie || "CIE11"}
            setVersion={(v) => setSeleccionado((s) => ({ ...s, version_cie: v }))}
            versionManual={versionManual}
            setVersionManual={setVersionManual}
            seleccion={verSeleccionado}
            setSeleccion={setVerSeleccionado}
          />
          <div className="pie-form">
            <Boton type="button" disabled={esLectura} onClick={guardarCIE}>
              Guardar código CIE
            </Boton>
          </div>
        </section>
      )}

      {!seleccionado && (
        <section className="lista">
          <h2>Pendientes de codificación ({paginacion?.total ?? lista.length})</h2>
          {lista.length === 0 ? (
            <p className="ayuda">No hay registros pendientes para este módulo.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Nº registro</th>
                  <th>Nº impreso</th>
                  <th>Fecha</th>
                  <th>Persona / madre / paciente</th>
                  <th>Centro</th>
                  <th>Codificación</th>
                  <th>CIE legacy</th>
                  <th className="acciones">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {lista.map((r) => (
                  <tr key={r.id}>
                    <td>{codigo(modulo, r)}</td>
                    <td>{r.numero_certificado || r.numero_planilla || "—"}</td>
                    <td>{r.fecha_evento}</td>
                    <td>{nombres(modulo, r)}</td>
                    <td>{r.organizacion_nombre || "—"}</td>
                    <td>
                      {r.codificacion_pendiente ? <span className="etiqueta">Pendiente</span> : <span>OK</span>}
                    </td>
                    <td>{r.cie10_legacy || "—"}</td>
                    <td className="acciones">
                      <button type="button" className="btn-mini" onClick={() => aplicar(r)}>
                        Codificar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {paginacion && paginacion.paginas > 1 && (
            <div className="paginacion">
              <button
                type="button"
                className="btn-mini"
                disabled={paginacion.pagina <= 1}
                onClick={() => cargar(paginacion.pagina - 1)}
              >
                ‹ Anterior
              </button>
              <span>
                Página {paginacion.pagina} de {paginacion.paginas}
              </span>
              <button
                type="button"
                className="btn-mini"
                disabled={paginacion.pagina >= paginacion.paginas}
                onClick={() => cargar(paginacion.pagina + 1)}
              >
                Siguiente ›
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  )
}