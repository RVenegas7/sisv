import { beforeEach, describe, expect, it, vi } from "vitest"

import { versionParaFecha } from "../constants"
import { seleccionDesdeRegistro, validarCIE } from "./cie"

const { mockObtenerCIE11 } = vi.hoisted(() => ({ mockObtenerCIE11: vi.fn() }))
vi.mock("../api/sisv", () => ({
  obtenerCIE11: (id) => mockObtenerCIE11(id),
}))

describe("validarCIE", () => {
  it("exige CIE-10 en eventos históricos", () => {
    expect(validarCIE("CIE10", { cie10: null })).toMatch(/CIE-10/)
    expect(validarCIE("CIE10", { cie10: { codigo: "A15.0" } })).toBe("")
  })

  it("exige CIE-11 en eventos actuales", () => {
    expect(validarCIE("CIE11", { cie11: null })).toMatch(/CIE-11/)
  })

  it("exige subgrupo obligatorio en categorías", () => {
    const categoria = { nivel: 3, requiere_subgrupo: true }
    expect(validarCIE("CIE11", { cie11: categoria })).toMatch(/subgrupo obligatorio/)
  })

  it("acepta categoría sin subgrupo obligatorio y subgrupos", () => {
    expect(validarCIE("CIE11", { cie11: { nivel: 3, requiere_subgrupo: false } })).toBe("")
    expect(validarCIE("CIE11", { cie11: { nivel: 4, requiere_subgrupo: false } })).toBe("")
  })
})

describe("versionParaFecha", () => {
  it("usa la fecha de corte 2022-01-01", () => {
    expect(versionParaFecha("2020-05-01")).toBe("CIE10")
    expect(versionParaFecha("2022-01-01")).toBe("CIE11")
    expect(versionParaFecha("2023-05-01")).toBe("CIE11")
    expect(versionParaFecha(null)).toBe("CIE11")
  })
})

describe("seleccionDesdeRegistro", () => {
  beforeEach(() => {
    mockObtenerCIE11.mockReset()
  })

  it("devuelve selección vacía sin registro", async () => {
    expect(await seleccionDesdeRegistro(null)).toEqual({ cie10: null, cie11: null, subgrupo: null })
    expect(await seleccionDesdeRegistro({ version_cie: "CIE10", cie10_detalle: null })).toEqual({
      cie10: null, cie11: null, subgrupo: null,
    })
  })

  it("carga subgrupo cuando el registro apunta a uno", async () => {
    mockObtenerCIE11.mockResolvedValue({ id: 42, codigo: "CA40.0", nivel: 4 })
    const resultado = await seleccionDesdeRegistro({
      version_cie: "CIE11",
      cie10: null,
      cie11: 42,
      cie11_detalle: { id: 99, codigo: "CA40", nivel: 3 },
    })
    expect(resultado.cie11.codigo).toBe("CA40")
    expect(resultado.subgrupo.id).toBe(42)
  })

  it("no pide el subgrupo si el registro usa la categoría", async () => {
    const resultado = await seleccionDesdeRegistro({
      version_cie: "CIE11",
      cie11: 99,
      cie11_detalle: { id: 99, codigo: "CA40", nivel: 3 },
    })
    expect(resultado.subgrupo).toBeNull()
    expect(mockObtenerCIE11).not.toHaveBeenCalled()
  })

  it("tolera fallo al buscar el subgrupo", async () => {
    mockObtenerCIE11.mockRejectedValue(new Error("red"))
    const resultado = await seleccionDesdeRegistro({
      version_cie: "CIE11",
      cie11: 42,
      cie11_detalle: { id: 99, codigo: "CA40", nivel: 3 },
    })
    expect(resultado.subgrupo).toBeNull()
    expect(resultado.cie11.id).toBe(99)
  })
})