import { describe, expect, it } from "vitest"

import { numeroImpreso, numeroRegistro, numeroVisible, tieneAmbosNumeros } from "./numero"

describe("referencia visible del certificado", () => {
  it("prefiere el número impreso de la defunción", () => {
    const r = { numero_certificado: "5143453", registro_numero: "LEG-CERT-999473093" }
    expect(numeroImpreso(r)).toBe("5143453")
    expect(numeroVisible(r)).toBe("5143453")
    expect(tieneAmbosNumeros(r)).toBe(true)
  })

  it("prefiere el número de planilla del nacimiento", () => {
    const r = { numero_planilla: "0072", registro_numero: "NC-2026-000072" }
    expect(numeroImpreso(r)).toBe("0072")
    expect(numeroVisible(r)).toBe("0072")
  })

  it("cae al registro legacy cuando no hay número impreso", () => {
    const r = { numero_certificado: "", registro_numero: "DEF-2026-000003" }
    expect(numeroImpreso(r)).toBe("")
    expect(numeroVisible(r)).toBe("DEF-2026-000003")
    expect(tieneAmbosNumeros(r)).toBe(false)
  })

  it("no repite la referencia si impreso y registro coinciden", () => {
    const r = { numero_certificado: "253", registro_numero: "253" }
    expect(tieneAmbosNumeros(r)).toBe(false)
  })

  it("resiste registros vacíos", () => {
    expect(numeroImpreso(null)).toBe("")
    expect(numeroRegistro(undefined)).toBe("")
    expect(numeroVisible({})).toBe("—")
  })
})
