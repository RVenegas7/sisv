import { useEffect, useMemo, useState } from "react"
import { actualizarDefuncion, actualizarFicha, actualizarNacimiento, listarCodificacion } from "../api/sisv"
import CIESearch from "../components/CIESearch"
import SeccionCIE from "../components/SeccionCIE"
import { Boton, Campo, Input, Select } from "../components/ui"
import { validarCIE } from "../utils/cie"

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

  const esLectura = !permisos.puede_editar

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

  function aplicar(reg) {
    setSeleccionado(reg)
    let sel = CERO
    if (reg.version_cie === "CIE10") sel = { c10: true, ...CERO, cie10: { id: reg.cie10, codigo: reg.cie10_detalle?.codigo, descripcion: reg.cie10_detalle?.descripcion } }
    else if (reg.version_cie === "CIE11") sel = { ...CERO, cie11: { id: reg.cie11, codigo: reg.cie11_detalle?.codigo, titulo: reg.cie11_detalle?.titulo } }
    setVerSeleccionado(sel)
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

      {esLectura && (
        <div className="aviso aviso-info">
          Su rol (<strong>{usuario?.rol_label}</strong>) es de solo lectura: no puede guardar códigos CIE.
        </div>
      )}

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