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
  (err) => {
    const msg = err.response?.data?.message || err.message || "Error de red"
    const errors = err.response?.data?.errors
    if (err.response?.status === 401) {
      window.dispatchEvent(new CustomEvent("sisv:no-sesion"))
    }
    return Promise.reject({ message: msg, errors })
  }
)

export default api