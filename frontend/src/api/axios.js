import axios from "axios"

let csrfToken = null

export function setCsrf(token) {
  csrfToken = token
}

const api = axios.create({
  baseURL: "/api",
  timeout: 20000,
  withCredentials: true,
})

// Todos los textos que ve el usuario van en español: axios trae los suyos en inglés
// («Network Error», «timeout of 20000ms exceeded», «Request failed with status code 500»),
// así que aquí se traducen antes de que lleguen a las pantallas.
const MENSAJES_ESTADO = {
  400: "La solicitud no es válida. Revise los datos e intente de nuevo.",
  401: "Su sesión expiró. Inicie sesión de nuevo.",
  403: "No tiene permiso para realizar esta acción. Si el problema continúa, recargue la página.",
  404: "No se encontró lo solicitado.",
  409: "El registro cambió mientras lo editaba. Recargue la página e intente de nuevo.",
  413: "El archivo o la solicitud es demasiado grande.",
  429: "Demasiados intentos seguidos. Espere un momento antes de volver a intentarlo.",
  500: "El servidor tuvo un problema al procesar la solicitud. Intente de nuevo en unos minutos.",
  502: "El servicio no respondió correctamente. Intente de nuevo en unos minutos.",
  503: "El servicio no está disponible en este momento. Intente de nuevo en unos minutos.",
  504: "El servidor tardó demasiado en responder. Intente de nuevo en unos minutos.",
}

const SIN_CONEXION =
  "No se pudo conectar con el servidor. Verifique su conexión y que el servicio esté en línea."
const TIEMPO_AGOTADO = "El servidor tardó demasiado en responder. Intente de nuevo."

/** Primer texto legible de una respuesta de error de DRF o de SISV. */
function primerTexto(valor) {
  if (!valor) return ""
  if (typeof valor === "string") {
    const texto = valor.trim()
    // Una página HTML de error de Django no se le muestra al usuario.
    return texto.startsWith("<") ? "" : texto
  }
  if (Array.isArray(valor)) {
    for (const item of valor) {
      const texto = primerTexto(item)
      if (texto) return texto
    }
    return ""
  }
  if (typeof valor === "object") {
    for (const clave of ["message", "detail", "error", "mensaje"]) {
      const texto = primerTexto(valor[clave])
      if (texto) return texto
    }
    const texto = primerTexto(valor.errors)
    if (texto) return texto
    for (const item of Object.values(valor)) {
      const texto = primerTexto(item)
      if (texto) return texto
    }
  }
  return ""
}

/**
 * Mensaje de error en español para cualquier fallo de la API.
 *
 * Orden: texto del servidor (ya en español) → mensaje por código HTTP → mensaje de red.
 * Se exporta para poder probarlo sin depender de una petición real.
 */
export function mensajeDeError(err) {
  if (!err) return "Ocurrió un error inesperado."
  if (err.__normalizado) return err.message || "Ocurrió un error inesperado."

  const mensaje = String(err.message || "")
  if (err.code === "ECONNABORTED" || err.code === "ETIMEDOUT" || /timeout/i.test(mensaje)) {
    return TIEMPO_AGOTADO
  }
  if (!err.response) return SIN_CONEXION

  const { data, status } = err.response || {}
  const delServidor = primerTexto(data)
  if (delServidor) return delServidor
  return (
    MENSAJES_ESTADO[status] ||
    `El servidor respondió con un error (${status || "desconocido"}). Intente de nuevo.`
  )
}

api.interceptors.request.use((cfg) => {
  const metodo = (cfg.method || "get").toLowerCase()
  if (csrfToken && !["get", "head", "options"].includes(metodo)) {
    cfg.headers["X-CSRFToken"] = csrfToken
  }
  return cfg
})

function rechazo(err) {
  return { message: mensajeDeError(err), errors: err.response?.data?.errors, __normalizado: true }
}

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 403 && err.config && !err.config.__csrfRetried) {
      // Un 403 puede ser el token CSRF rotado: se pide otro una vez y se reintenta.
      err.config.__csrfRetried = true
      try {
        const r = await api.get("/auth/csrf/")
        setCsrf(r.data.data.csrf)
        err.config.headers["X-CSRFToken"] = r.data.data.csrf
        return api(err.config)
      } catch {
        // Si persiste, cae al rechazo normal.
        return Promise.reject(rechazo(err))
      }
    }
    if (err.response?.status === 401) {
      window.dispatchEvent(new CustomEvent("sisv:no-sesion"))
    }
    return Promise.reject(rechazo(err))
  }
)

export default api
