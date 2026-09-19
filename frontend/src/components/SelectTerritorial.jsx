import { useEffect, useRef, useState } from "react"
import { nivelTerritorial } from "../api/sisv"
import { Campo, Select } from "./ui"

const VACIO = { estado: "", municipio: "", parroquia: "", comunidad: "" }

export default function SelectTerritorial({ valor = VACIO, onChange }) {
  const [estados, setEstados] = useState([])
  const [municipios, setMunicipios] = useState([])
  const [parroquias, setParroquias] = useState([])
  const [comunidades, setComunidades] = useState([])
  const [sel, setSel] = useState(VACIO)
  const [cargando, setCargando] = useState("")
  const prefillUsado = useRef("")
  const cache = useRef({})

  async function obtener(nivel, padre) {
    const clave = `${nivel}-${padre || 0}`
    if (cache.current[clave]) return cache.current[clave]
    setCargando(clave)
    try {
      const datos = await nivelTerritorial(nivel, padre)
      cache.current[clave] = datos
      return datos
    } finally {
      setCargando("")
    }
  }

  useEffect(() => {
    obtener("ESTADO", 0).then(setEstados).catch(() => setEstados([]))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const deseados = {
      estado: valor.estado || "",
      municipio: valor.municipio || "",
      parroquia: valor.parroquia || "",
      comunidad: valor.comunidad || "",
    }
    const clave = JSON.stringify(deseados)
    if (clave === prefillUsado.current || estados.length === 0) return

    if (!Object.values(deseados).some(Boolean)) {
      prefillUsado.current = clave
      setSel(VACIO)
      setMunicipios([])
      setParroquias([])
      setComunidades([])
      return
    }

    const est = estados.find((e) => e.nombre === deseados.estado)
    if (!est) return
    prefillUsado.current = clave
    rellenarCadena(est, deseados)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [valor, estados])

  async function rellenarCadena(est, deseados) {
    setSel((s) => ({ ...s, estado: String(est.id) }))
    const muns = await obtener("MUNICIPIO", est.id)
    setMunicipios(muns)
    const mu = deseados.municipio && muns.find((m) => m.nombre === deseados.municipio)
    if (mu) {
      setSel((s) => ({ ...s, municipio: String(mu.id) }))
      const pars = await obtener("PARROQUIA", mu.id)
      setParroquias(pars)
      const par = deseados.parroquia && pars.find((p) => p.nombre === deseados.parroquia)
      if (par) {
        setSel((s) => ({ ...s, parroquia: String(par.id) }))
        const coms = await obtener("COMUNIDAD", par.id)
        setComunidades(coms)
        const com = deseados.comunidad && coms.find((c) => c.nombre === deseados.comunidad)
        if (com) setSel((s) => ({ ...s, comunidad: String(com.id) }))
        else if (deseados.comunidad) setSel((s) => ({ ...s, comunidad: deseados.comunidad }))
      }
    }
  }

  function emitir(nombres) {
    const limpio = { estado: nombres.estado || "", municipio: nombres.municipio || "", parroquia: nombres.parroquia || "", comunidad: nombres.comunidad || "" }
    prefillUsado.current = JSON.stringify(limpio)
    onChange(limpio)
  }

  async function cambiarEstado(id) {
    const est = estados.find((x) => String(x.id) === String(id))
    setSel({ ...VACIO, estado: String(id) })
    setMunicipios([])
    setParroquias([])
    setComunidades([])
    emitir({ estado: est?.nombre || "", municipio: "", parroquia: "", comunidad: "" })
    if (est) {
      const m = await obtener("MUNICIPIO", est.id)
      setMunicipios(m)
    }
  }

  async function cambiarMunicipio(id) {
    const mu = municipios.find((x) => String(x.id) === String(id))
    setSel((s) => ({ ...s, municipio: String(id), parroquia: "", comunidad: "" }))
    setParroquias([])
    setComunidades([])
    emitir({ estado: estados.find((e) => String(e.id) === String(sel.estado))?.nombre || "", municipio: mu?.nombre || "", parroquia: "", comunidad: "" })
    if (mu) {
      const p = await obtener("PARROQUIA", mu.id)
      setParroquias(p)
    }
  }

  async function cambiarParroquia(id) {
    const par = parroquias.find((x) => String(x.id) === String(id))
    setSel((s) => ({ ...s, parroquia: String(id), comunidad: "" }))
    setComunidades([])
    emitir({
      estado: estados.find((e) => String(e.id) === String(sel.estado))?.nombre || "",
      municipio: municipios.find((m) => String(m.id) === String(sel.municipio))?.nombre || "",
      parroquia: par?.nombre || "",
      comunidad: "",
    })
    if (par) {
      const c = await obtener("COMUNIDAD", par.id)
      setComunidades(c)
    }
  }

  function cambiarComunidadTexto(texto) {
    setSel((s) => ({ ...s, comunidad: texto }))
    emitir({
      estado: estados.find((e) => String(e.id) === String(sel.estado))?.nombre || "",
      municipio: municipios.find((m) => String(m.id) === String(sel.municipio))?.nombre || "",
      parroquia: parroquias.find((p) => String(p.id) === String(sel.parroquia))?.nombre || "",
      comunidad: texto,
    })
  }

  function cambiarComunidad(id) {
    const com = comunidades.find((x) => String(x.id) === String(id))
    setSel((s) => ({ ...s, comunidad: String(id) }))
    emitir({
      estado: estados.find((e) => String(e.id) === String(sel.estado))?.nombre || "",
      municipio: municipios.find((m) => String(m.id) === String(sel.municipio))?.nombre || "",
      parroquia: parroquias.find((p) => String(p.id) === String(sel.parroquia))?.nombre || "",
      comunidad: com?.nombre || "",
    })
  }

  return (
    <div className="grid" style={{ gridColumn: "1 / -1" }}>
      <Campo label="Estado">
        <Select opciones={estados.map((e) => [`${e.id}`, e.nombre])} value={sel.estado} onChange={(e) => cambiarEstado(e.target.value)} />
      </Campo>
      <Campo label="Municipio">
        <Select
          opciones={municipios.map((m) => [`${m.id}`, m.nombre])}
          value={sel.municipio}
          disabled={!sel.estado}
          onChange={(e) => cambiarMunicipio(e.target.value)}
        />
      </Campo>
      <Campo label="Parroquia">
        <Select
          opciones={parroquias.map((p) => [`${p.id}`, p.nombre])}
          value={sel.parroquia}
          disabled={!sel.municipio}
          onChange={(e) => cambiarParroquia(e.target.value)}
        />
      </Campo>
      <Campo label="Comunidad">
        <input
          type="text"
          list="comunidades-list"
          value={sel.comunidad}
          disabled={!sel.parroquia}
          onChange={(e) => cambiarComunidadTexto(e.target.value)}
          placeholder={sel.parroquia ? "Escribe el nombre de la comunidad" : "Selecciona primero la parroquia"}
        />
        <datalist id="comunidades-list">
          {comunidades.map((c) => (
            <option key={c.id} value={c.nombre} />
          ))}
        </datalist>
      </Campo>
      {cargando && (
        <p className="ayuda" style={{ gridColumn: "1 / -1" }}>
          Cargando opciones territoriales…
        </p>
      )}
    </div>
  )
}