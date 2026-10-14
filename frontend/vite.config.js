import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

// Puertos donde suele vivir el backend Django. En este equipo el 8000 lo ocupa otro
// contenedor (banco de sangre), así que si no viene VITE_API_PROXY se busca el primer
// puerto que responda como SISV en /api/ (el /api/ de otros servicios no responde 200).
const PUERTOS_API = [8000, 8001, 8002, 8003]

async function detectarApi() {
  if (process.env.VITE_API_PROXY) return process.env.VITE_API_PROXY
  for (const puerto of PUERTOS_API) {
    try {
      const respuesta = await fetch(`http://127.0.0.1:${puerto}/api/`, {
        redirect: "manual",
        signal: AbortSignal.timeout(400),
      })
      if (respuesta.status === 200) return `http://127.0.0.1:${puerto}`
    } catch {
      // puerto cerrado o sin respuesta: se prueba el siguiente
    }
  }
  return "http://127.0.0.1:8000"
}

export default defineConfig(async ({ command, mode }) => {
  // Solo al servir en desarrollo: `npm test` (mode=test) y `npm run build` no sondean.
  const enDev = command === "serve" && mode === "development" && !process.env.VITEST
  const api = enDev
    ? await detectarApi()
    : process.env.VITE_API_PROXY || "http://127.0.0.1:8000"
  return {
    plugins: [react()],
    server: {
      host: true,
      port: 5173,
      proxy: {
        "/api": api,
      },
    },
  }
})
