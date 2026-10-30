// Referencia visible del certificado (§31.2).
//
// El número que el operario tiene en el papel es el **impreso** (`numero_certificado`
// en defunciones, `numero_planilla` en nacimientos); el `registro_numero` legacy
// (`LEG-CERT-…`, `DEF-2026-…`) es la PK de Oracle y solo se usa de respaldo cuando el
// registro no trae número impreso (certificados capturados a mano o importados antes
// del backfill de §31).

/** Número impreso del certificado, o cadena vacía si no lo trae. */
export function numeroImpreso(registro) {
  if (!registro) return ""
  const valor = registro.numero_certificado ?? registro.numero_planilla
  return valor == null ? "" : String(valor).trim()
}

/** Número de registro legacy, o cadena vacía si no lo trae. */
export function numeroRegistro(registro) {
  return registro?.registro_numero ? String(registro.registro_numero) : ""
}

/** Lo que se muestra como «Nº»: el impreso y, si falta, el de registro. */
export function numeroVisible(registro) {
  return numeroImpreso(registro) || numeroRegistro(registro) || "—"
}

/** true cuando hay que mostrar el número de registro como referencia secundaria. */
export function tieneAmbosNumeros(registro) {
  const impreso = numeroImpreso(registro)
  return Boolean(impreso) && impreso !== numeroRegistro(registro)
}
