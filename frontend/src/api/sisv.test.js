import { beforeEach, describe, expect, it, vi } from "vitest"

import {
  exportarReportes, iniciarSesion, listarNacimientos, sesionActual,
} from "./sisv"

const { apiMock, setCsrfMock } = vi.hoisted(() => ({
  apiMock: {},
  setCsrfMock: vi.fn(),
}))
vi.mock("./axios", () => {
  const crearCliente = (overrides) => {
    const cliente = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
      ...overrides,
    }
    cliente.get.mockResolvedValue({ data: { data: [], count: 0, pagination: {} } })
    return cliente
  }
  apiMock.cliente = crearCliente()
  return { default: apiMock.cliente, setCsrf: setCsrfMock }
})

beforeEach(() => {
  apiMock.cliente.get.mockResolvedValue({ data: { data: [], count: 0, pagination: {} } })
  for (const m of ["post", "put", "patch", "delete"]) {
    apiMock.cliente[m].mockClear()
    apiMock.cliente[m].mockResolvedValue({ data: { data: {} } })
  }
})

describe("iniciarSesion", () => {
  it("envía credenciales y guarda el token CSRF", async () => {
    apiMock.cliente.get.mockImplementation((url) => {
      if (url === "/auth/csrf/") return Promise.resolve({ data: { data: { csrf: "tok-123" } } })
      return Promise.resolve({ data: { data: { ok: 1 } } })
    })
    apiMock.cliente.post.mockResolvedValue({ data: { data: { username: "admin" } } })
    const usuario = await iniciarSesion("admin", "secreta")
    expect(apiMock.cliente.post).toHaveBeenCalledWith("/auth/login/", { username: "admin", password: "secreta" })
    expect(usuario.username).toBe("admin")
    expect(setCsrfMock).toHaveBeenCalledWith("tok-123")
  })
})

describe("sesionActual y listados", () => {
  it("sesionActual devuelve el perfil", async () => {
    apiMock.cliente.get.mockResolvedValue({ data: { data: { username: "admin", rol: "DIRECTOR" } } })
    const perfil = await sesionActual()
    expect(apiMock.cliente.get).toHaveBeenCalledWith("/auth/me/")
    expect(perfil.rol).toBe("DIRECTOR")
  })

  it("listarNacimientos expone items, count y pagination", async () => {
    apiMock.cliente.get.mockResolvedValue({
      data: { data: [{ id: 1 }], count: 7, pagination: { pagina: 1, total: 7 } },
    })
    const resultado = await listarNacimientos({ anio: 2026 })
    expect(apiMock.cliente.get).toHaveBeenCalledWith("/registros/nacimientos/", { params: { anio: 2026 } })
    expect(resultado).toEqual({ items: [{ id: 1 }], count: 7, pagination: { pagina: 1, total: 7 } })
  })
})

describe("exportaciones", () => {
  it("exportarReportes solicita blob", async () => {
    await exportarReportes({ modulo: "nacimientos" })
    expect(apiMock.cliente.get).toHaveBeenCalledWith("/registros/reportes/exportar/", {
      params: { modulo: "nacimientos" },
      responseType: "blob",
    })
  })
})