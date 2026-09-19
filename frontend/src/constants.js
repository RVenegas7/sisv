export const FECHA_CORTE_CIE11 = "2022-01-01"

export const NIVEL_LABEL = {
  1: "Capítulo",
  2: "Bloque",
  3: "Categoría",
  4: "Subgrupo",
}

export function versionParaFecha(fecha) {
  if (!fecha) return "CIE11"
  return fecha < FECHA_CORTE_CIE11 ? "CIE10" : "CIE11"
}