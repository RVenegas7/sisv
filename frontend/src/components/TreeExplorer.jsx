import { useEffect, useState } from "react"
import { capitulosCIE11, hijosCIE11 } from "../api/sisv"
import { NIVEL_LABEL } from "../constants"

const ES_FIN = 3

function Nodo({ nodo, onElegir, onClic }) {
  const [abierto, setAbierto] = useState(false)
  const [hijos, setHijos] = useState([])
  const [cargando, setCargando] = useState(false)
  const esHoja = nodo.nivel >= ES_FIN && !nodo.requiere_subgrupo

  async function alternar() {
    if (abierto) {
      setAbierto(false)
      return
    }
    setCargando(true)
    try {
      const lista = await hijosCIE11(nodo.id)
      setHijos(lista)
      setAbierto(true)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="arbol-nodo">
      <div className="arbol-fila">
        <button
          type="button"
          className={esHoja ? "sin-hijos" : "con-hijos"}
          onClick={() => (esHoja ? onClic(nodo) : alternar())}
        >
          <span className="flecha">
            {esHoja ? "" : cargando ? "…" : abierto ? "▼" : "▶"}
          </span>
          <span className="codigo">{nodo.codigo}</span>
          <span className="titulo">{nodo.titulo}</span>
          <small className="nivel">{nodo.nivel_label || NIVEL_LABEL[nodo.nivel]}</small>
          {nodo.requiere_subgrupo && <em className="obliga">requiere subgrupo</em>}
        </button>
        {esHoja && (
          <button type="button" className="elegir" onClick={() => onElegir(nodo)}>
            Elegir
          </button>
        )}
      </div>
      {abierto && hijos.map((h) => <Nodo key={h.id} nodo={h} onElegir={onElegir} onClic={onClic} />)}
    </div>
  )
}

export function TreeExplorer({ onElegir }) {
  const [capitulos, setCapitulos] = useState([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    capitulosCIE11()
      .then(setCapitulos)
      .catch(() => setCapitulos([]))
      .finally(() => setCargando(false))
  }, [])

  if (cargando) return <div className="arbol-vacio">Cargando capítulos…</div>
  if (capitulos.length === 0) return <div className="arbol-vacio">Sin datos CIE-11</div>

  return (
    <div className="arbol">
      {capitulos.map((n) => (
        <Nodo key={n.id} nodo={n} onElegir={onElegir} onClic={onElegir} />
      ))}
    </div>
  )
}