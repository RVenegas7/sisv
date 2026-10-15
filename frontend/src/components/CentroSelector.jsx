import { useEffect, useState } from "react"
import { listarOrganizaciones } from "../api/sisv"
import { Campo, Select } from "./ui"

export default function CentroSelector({ usuario, value, onChange }) {
  const org = usuario?.organizacion
  const esCentro = org?.nivel === "CENTRO"
  // Sin organización (superusuario) se comporta como multicentro: elige cualquier
  // centro. Antes devolvía null y el formulario quedaba sin pedir el centro.
  const esMulticentro =
    !org || ["REGIONAL", "GOBERNACION", "MINISTERIO"].includes(org.nivel)
  const [centros, setCentros] = useState([])

  useEffect(() => {
    if (!esMulticentro) return
    listarOrganizaciones()
      .then((orgs) => {
        let cs = orgs.filter((o) => o.nivel === "CENTRO")
        if (org?.nivel === "REGIONAL" && org.estado) {
          cs = cs.filter((o) => o.estado === org.estado)
        }
        setCentros(cs)
      })
      .catch(() => setCentros([]))
  }, [esMulticentro, org?.nivel, org?.estado])

  if (esCentro && org) {
    return (
      <p className="ayuda" style={{ gridColumn: "1 / -1" }}>
        Registros vinculados a: <strong>{org.nombre}</strong> ({org.nivel_label})
      </p>
    )
  }

  if (!esMulticentro) return null

  return (
    <Campo label="Centro de salud destino" htmlFor="centro_destino">
      <Select
        id="centro_destino"
        opciones={centros.map((c) => [`${c.id}`, `${c.nombre}${c.municipio ? ` (${c.municipio})` : ""}`])}
        value={value ? String(value) : ""}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
      />
    </Campo>
  )
}