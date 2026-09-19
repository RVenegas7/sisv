import { useEffect, useRef, useState } from "react"
import { buscarCIE10, buscarCIE11, hijosCIE11, arbolCIE11 } from "../api/sisv"
import { NIVEL_LABEL } from "../constants"
import { TreeExplorer } from "./TreeExplorer"

const CERO = { cie10: null, cie11: null, subgrupo: null }

export default function CIESearch({ version, valor, onChange, id, allowClear = true }) {
  const [query, setQuery] = useState("")
  const [abierto, setAbierto] = useState(false)
  const [resultados, setResultados] = useState([])
  const [buscando, setBuscando] = useState(false)
  const [cascada, setCascada] = useState([])
  const [verArbol, setVerArbol] = useState(false)
  const debounce = useRef(null)
  const contenedorRef = useRef(null)

  const seleccion = valor && Object.keys(valor).some((k) => valor[k]) ? valor : CERO

  useEffect(() => {
    const q = query.trim()
    if (q.length < 2) {
      setResultados([])
      return
    }
    setBuscando(true)
    clearTimeout(debounce.current)
    debounce.current = setTimeout(async () => {
      try {
        const lista = version === "CIE10" ? await buscarCIE10(q) : await buscarCIE11(q)
        setResultados(lista.slice(0, 15))
        setAbierto(true)
      } catch {
        setResultados([])
      } finally {
        setBuscando(false)
      }
    }, 300)
    return () => clearTimeout(debounce.current)
  }, [query, version])

  useEffect(() => {
    function alClicFuera(e) {
      if (contenedorRef.current && !contenedorRef.current.contains(e.target)) {
        setAbierto(false)
        setVerArbol(false)
      }
    }
    document.addEventListener("mousedown", alClicFuera)
    return () => document.removeEventListener("mousedown", alClicFuera)
  }, [])

  useEffect(() => {
    setCascada([])
    setQuery("")
    setResultados([])
  }, [version])

  function finalizar(nodo) {
    onChange({ cie10: version === "CIE10" ? nodo : null, cie11: version === "CIE11" ? nodo : null, subgrupo: null })
    setCascada([])
    setQuery("")
    setAbierto(false)
  }

  async function continuarCascada(nodo, previas) {
    if (nodo.nivel >= 3 && !(nodo.nivel === 3 && nodo.requiere_subgrupo)) {
      finalizar(nodo)
      return
    }
    const siguientes = await hijosCIE11(nodo.id)
    setCascada([...previas, { titulo: nodo.titulo, opciones: siguientes, seleccion: null }])
  }

  async function elegir(nodo) {
    if (version === "CIE10") {
      finalizar(nodo)
      return
    }
    await continuarCascada(nodo, [])
  }

  async function elegirEnCascada(indice, opcion) {
    const nuevas = cascada
      .slice(0, indice + 1)
      .map((nivel, j) => (j === indice ? { ...nivel, seleccion: opcion } : nivel))
    if (opcion.nivel >= 3 && !(opcion.nivel === 3 && opcion.requiere_subgrupo)) {
      setCascada([])
      finalizar(opcion)
      return
    }
    const siguientes = await hijosCIE11(opcion.id)
    setCascada([...nuevas, { titulo: opcion.titulo, opciones: siguientes, seleccion: null }])
  }

  function claro() {
    onChange(CERO)
  }

  const tieneSeleccion = Boolean(seleccion.cie10 || seleccion.cie11)

  return (
    <div className="cie-search" ref={contenedorRef}>
      {tieneSeleccion ? (
        <div className="chip">
          <strong>{seleccion.cie10 ? seleccion.cie10.codigo : seleccion.cie11.codigo}</strong>
          <span>{seleccion.cie10 ? seleccion.cie10.descripcion : seleccion.cie11.titulo}</span>
          {seleccion.cie11?.ruta && seleccion.cie11.ruta.length > 0 && (
            <small className="ruta">
              {seleccion.cie11.ruta.map((a) => a.nivel_label).join(" › ")}
            </small>
          )}
          <small>
            {NIVEL_LABEL[seleccion.cie11?.nivel] || "CIE-10"} {seleccion.cie11?.nivel_label ? `- ${seleccion.cie11.nivel_label}` : ""}
          </small>
          {allowClear && (
            <button type="button" onClick={claro} aria-label="Quitar selección">
              ✕
            </button>
          )}
        </div>
      ) : (
        <div className="cie-input">
          <input
            id={id}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setVerArbol(false)
            }}
            onFocus={() => setAbierto(true)}
            placeholder={
              version === "CIE10"
                ? "Buscar por texto o código CIE-10 (ej. B54 o Malaria)…"
                : "Buscar por texto o código CIE-11 (ej. 1F4Z o Malaria)…"
            }
          />
          {buscando && <span className="spinner" aria-label="Buscando" />}
          {abierto && resultados.length > 0 && (
            <ul className="sugerencias">
              {resultados.map((r) => (
                <li key={`${r.codigo}-${r.id}`}>
                  <button type="button" onClick={() => elegir(r)}>
                    <span className="codigo">{r.codigo}</span>
                    <span className="titulo">
                      {r.titulo || r.descripcion}
                      {r.ruta && r.ruta.length > 0 && (
                        <small className="ruta">
                          {r.ruta.map((a) => a.nivel_label).join(" › ")}
                        </small>
                      )}
                      <small>
                        {NIVEL_LABEL[r.nivel] || "CIE-10"} | {r.codigo}
                      </small>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {abierto && query.trim().length >= 2 && resultados.length === 0 && !buscando && (
            <div className="sin-resultados">Sin resultados para «{query}»</div>
          )}
          {version === "CIE11" && !tieneSeleccion && (
            <div className="cie-tools">
              <button type="button" onClick={() => setVerArbol((v) => !v)}>
                {verArbol ? "Ocultar árbol CIE-11" : "Explorar árbol CIE-11"}
              </button>
            </div>
          )}
          {verArbol && abierto && (
            <div className="cie-arbol">
              <TreeExplorer onElegir={elegir} />
            </div>
          )}
        </div>
      )}

      {cascada.length > 0 && (
        <div className="cascada">
          <p>Selección en cascada — faltan niveles obligatorios:</p>
          {cascada.map((nivel, i) => (
            <label key={`${nivel.titulo}-${i}`}>
              <span>
                {i === cascada.length - 1 && !nivel.seleccion ? "Seleccione " : "Nivel "}
                {NIVEL_LABEL[nivel.opciones[0]?.nivel]} <em>de «{nivel.titulo}»</em>
              </span>
              <select
                value={nivel.seleccion?.id || ""}
                onChange={(e) => {
                  const op = nivel.opciones.find((o) => String(o.id) === e.target.value)
                  if (op) elegirEnCascada(i, op)
                }}
              >
                <option value="">— Elija —</option>
                {nivel.opciones.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.codigo} — {o.titulo}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </div>
      )}
    </div>
  )
}