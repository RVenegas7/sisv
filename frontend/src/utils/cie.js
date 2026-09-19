import { useEffect, useState } from "react"
import { obtenerCIE10, obtenerCIE11 } from "../api/sisv"
import { versionParaFecha } from "../constants"

export const SELECCION_CIE_VACIA = { cie10: null, cie11: null, subgrupo: null }

export function validarCIE(version, seleccion) {
  if (version === "CIE10") {
    if (!seleccion.cie10) return "Seleccione un código CIE-10 (obligatorio para este evento)."
    return ""
  }
  if (!seleccion.cie11) return "Seleccione un código CIE-11 (obligatorio para este evento)."
  if (seleccion.cie11.nivel === 3 && seleccion.cie11.requiere_subgrupo) {
    return "Esta categoría CIE-11 exige seleccionar un subgrupo obligatorio."
  }
  return ""
}

export function useVersionCIE(fechaEvento) {
  const [version, setVersion] = useState("CIE11")
  const [versionManual, setVersionManual] = useState(false)
  const [seleccion, setSeleccion] = useState(SELECCION_CIE_VACIA)

  useEffect(() => {
    if (!versionManual && fechaEvento) {
      const auto = versionParaFecha(fechaEvento)
      setVersion(auto)
      if (auto === "CIE10") setSeleccion(SELECCION_CIE_VACIA)
    }
  }, [fechaEvento, versionManual])

  return { version, setVersion, versionManual, setVersionManual, seleccion, setSeleccion }
}

export async function seleccionDesdeRegistro(reg) {
  if (!reg || !reg.version_cie) return SELECCION_CIE_VACIA
  if (reg.version_cie === "CIE10") {
    if (!reg.cie10_detalle) return SELECCION_CIE_VACIA
    return { cie10: reg.cie10_detalle, cie11: null, subgrupo: null }
  }
  if (reg.cie11_detalle) {
    const categoria = reg.cie11_detalle
    if (reg.cie11 && Number(reg.cie11) !== Number(categoria.id)) {
      try {
        const subgrupo = await obtenerCIE11(reg.cie11)
        return { cie10: null, cie11: categoria, subgrupo }
      } catch {
        return { cie10: null, cie11: categoria, subgrupo: null }
      }
    }
    return { cie10: null, cie11: categoria, subgrupo: null }
  }
  return SELECCION_CIE_VACIA
}