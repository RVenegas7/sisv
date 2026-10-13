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

api.interceptors.request.use((cfg) => {
  const metodo = (cfg.method || "get").toLowerCase()
  if (csrfToken && !["get", "head", "options"].includes(metodo)) {
    cfg.headers["X-CSRFToken"] = csrfToken
  }
  return cfg
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 403 && !err.config.__csrfRetried) {
      // Un 403 puede ser el token CSRF rotado: se pide otro una vez y se reintenta.
      err.config.__csrfRetried = true
      try {
        const r = await api.get("/auth/csrf/")
        setCsrf(r.data.data.csrf)
        err.config.headers["X-CSRFToken"] = r.data.data.csrf
        return api(err.config)
      } catch {
        // Si persiste, cae al reject con el msg original
        return Promise.reject(err)
      }
    }
    const msg = err.response?.data?.message || err.message || "Error de red"
    const errors = err.response?.data?.errors
    if (err.response?.status === 401) {
      window.dispatchEvent(new CustomEvent("sisv:no-sesion"))
    }
    return Promise.reject({ message: msg, errors })
  }
)

export default api