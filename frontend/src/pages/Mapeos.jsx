import { useState } from "react"
import { mapeosCIE10, mapeosCIE11 } from "../api/sisv"
import { Boton, Campo, Input } from "../components/ui"

const TIPO_MAERCO = {
  EXA: "Equivalencia exacta",
  PAR: "Equivalencia parcial",
  INE: "Inexacta (sin equivalente directo)",
}

export default function Mapeos() {
  const [direccion, setDireccion] = useState("cie10")
  const [codigo, setCodigo] = useState("")
  const [resultado, setResultado] = useState(null)
  const [buscando, setBuscando] = useState(false)
  const [error, setError] = useState("")
  const [consultado, setConsultado] = useState("")

  async function buscar(e) {
    e.preventDefault()
    const c = codigo.trim().toUpperCase()
    if (!c) return
    setBuscando(true)
    setError("")
    setResultado(null)
    try {
      const lista =
        direccion === "cie10" ? await mapeosCIE10(c) : await mapeosCIE11(c)
      setResultado(lista)
      setConsultado(c)
    } catch {
      setError("No se pudo consultar el mapeo.")
    } finally {
      setBuscando(false)
    }
  }

  const esCie10 = direccion === "cie10"

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Mapeo CIE-10 ↔ CIE-11</h1>
        <p>
          Cross-walk oficial OMS: equivalencias entre la clasificación CIE-10 (histórica) y la CIE-11 (actual)
          para los reportes históricos unificados.
        </p>
      </header>

      <form className="filtros" onSubmit={buscar}>
        <Campo label="Dirección del mapeo">
          <select value={direccion} onChange={(e) => { setDireccion(e.target.value); setResultado(null) }}>
            <option value="cie10">CIE-10 → CIE-11</option>
            <option value="cie11">CIE-11 → CIE-10</option>
          </select>
        </Campo>
        <Campo label="Código (ej. A09 o 1A00.1)">
          <Input
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            placeholder={esCie10 ? "Ej. A09" : "Ej. 1A00.1"}
          />
        </Campo>
        <div className="filtro-action">
          <Boton disabled={buscando}>{buscando ? "Consultando…" : "Consultar mapeo"}</Boton>
        </div>
      </form>

      {error && <div className="aviso aviso-error">{error}</div>}

      {resultado !== null && (
        <section className="lista">
          <h2>
            Mapeos de {esCie10 ? `CIE-10 «${consultado}» a CIE-11` : `CIE-11 «${consultado}» a CIE-10`} ({resultado.length})
          </h2>
          {resultado.length === 0 ? (
            <div className="aviso aviso-info">Sin equivalencias registradas para este código.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>{esCie10 ? "CIE-10" : "CIE-11"}</th>
                  <th>{esCie10 ? "Descripción CIE-10" : "Descripción CIE-11"}</th>
                  <th>{esCie10 ? "CIE-11" : "CIE-10"}</th>
                  <th>{esCie10 ? "Descripción CIE-11" : "Descripción CIE-10"}</th>
                  <th>Tipo de equivalencia</th>
                </tr>
              </thead>
              <tbody>
                {resultado.map((m, i) => (
                  <tr key={`${m.cie10.codigo}-${m.cie11.codigo}-${i}`}>
                    <td>{m.cie10.codigo}</td>
                    <td>{m.cie10.descripcion}</td>
                    <td>{m.cie11.codigo}</td>
                    <td>{m.cie11.titulo}</td>
                    <td>
                      <span className="etiqueta">{TIPO_MAERCO[m.tipo] || m.tipo_label}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  )
}