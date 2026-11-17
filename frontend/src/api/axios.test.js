import { describe, expect, it } from "vitest"
import { mensajeDeError } from "./axios"

// §45: la aplicación habla español. axios entrega sus mensajes en inglés
// («Network Error», «timeout of 20000ms exceeded»), así que se traducen antes de
// mostrarlos; estos casos fijan los textos y evitan que vuelvan a filtrarse.
describe("mensajeDeError", () => {
  it("traduce el «Network Error» de axios cuando no hay respuesta", () => {
    const texto = mensajeDeError({ message: "Network Error", config: {}, request: {} })
    expect(texto).toContain("No se pudo conectar con el servidor")
    expect(texto).not.toMatch(/network error/i)
  })

  it("avisa del tiempo de espera agotado", () => {
    const texto = mensajeDeError({ message: "timeout of 20000ms exceeded", code: "ECONNABORTED" })
    expect(texto).toContain("El servidor tardó demasiado en responder")
  })

  it("usa el mensaje del servidor si viene en español (campo message)", () => {
    const texto = mensajeDeError({
      response: { status: 400, data: { message: "Debe indicar la organización destino." } },
    })
    expect(texto).toBe("Debe indicar la organización destino.")
  })

  it("acepta el campo detail de DRF", () => {
    const texto = mensajeDeError({
      response: { status: 403, data: { detail: "Las credenciales de autenticación no se proveyeron." } },
    })
    expect(texto).toBe("Las credenciales de autenticación no se proveyeron.")
  })

  it("toma el primer error de un objeto de validación por campo", () => {
    const texto = mensajeDeError({
      response: { status: 400, data: { cedula: ["Este campo es obligatorio."] } },
    })
    expect(texto).toBe("Este campo es obligatorio.")
  })

  it("traduce los códigos HTTP sin mensaje del servidor", () => {
    expect(mensajeDeError({ response: { status: 401, data: {} } })).toContain("Su sesión expiró")
    expect(mensajeDeError({ response: { status: 403, data: {} } })).toContain("No tiene permiso")
    expect(mensajeDeError({ response: { status: 500, data: "" } })).toContain("El servidor tuvo un problema")
  })

  it("no muestra el HTML de error de Django y cae al texto del código", () => {
    const texto = mensajeDeError({
      response: { status: 404, data: "<!DOCTYPE html><html lang=\"en\"><title>Not Found</title>" },
    })
    expect(texto).toBe("No se encontró lo solicitado.")
  })

  it("no vuelve a traducir un error ya normalizado por el interceptor", () => {
    const texto = mensajeDeError({
      message: "Su sesión expiró. Inicie sesión de nuevo.",
      __normalizado: true,
    })
    expect(texto).toBe("Su sesión expiró. Inicie sesión de nuevo.")
  })
})
