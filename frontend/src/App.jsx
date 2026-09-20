import { useEffect, useState } from "react"
import { NavLink, Navigate, Route, Routes } from "react-router-dom"
import { cerrarSesion, obtenerCsrf, sesionActual } from "./api/sisv"
import { setCsrf } from "./api/axios"
import CargaNacimientos from "./pages/CargaNacimientos"
import CargaDefunciones from "./pages/CargaDefunciones"
import CargaFichasVigilancia from "./pages/CargaFichasVigilancia"
import Vigilancia from "./pages/Vigilancia"
import Tablero from "./pages/Tablero"
import Reportes from "./pages/Reportes"
import Mapeos from "./pages/Mapeos"
import Configuracion from "./pages/Configuracion"
import Seguridad from "./pages/Seguridad"
import Login from "./pages/Login"

const NAVEGACION = [
  { enlace: "/", rotulo: "Tablero", fin: true },
  {
    grupo: "Registros",
    items: [
      { enlace: "/nacimientos", rotulo: "Nacimientos" },
      { enlace: "/defunciones", rotulo: "Defunciones" },
      { enlace: "/vigilancia", rotulo: "Consolidado semanal", exacto: true },
      { enlace: "/vigilancia/fichas", rotulo: "Fichas de vigilancia" },
    ],
  },
  { enlace: "/reportes", rotulo: "Reportes" },
  {
    grupo: "Catálogos clínicos",
    items: [
      { enlace: "/mapeos", rotulo: "Mapeos CIE-10 ↔ CIE-11" },
    ],
  },
  {
    grupo: "Sistema",
    items: [
      { enlace: "/configuracion", rotulo: "Configuración" },
      { enlace: "/seguridad", rotulo: "Seguridad" },
    ],
  },
]

function Credencial({ usuario, onSalir }) {
  const org = usuario.organizacion
  return (
    <div className="credencial">
      <div className="datos">
        <strong>{usuario.nombre}</strong>
        <span>
          {usuario.rol_label || "Sin rol"} · {org ? org.nombre : "Sin organización"}
        </span>
      </div>
      <button type="button" className="btn-mini" onClick={onSalir}>
        Salir
      </button>
    </div>
  )
}

export default function App() {
  const [cargandoSesion, setCargandoSesion] = useState(true)
  const [usuario, setUsuario] = useState(null)
  const [menuAbierto, setMenuAbierto] = useState(false)

  function cerrarMenu() {
    setMenuAbierto(false)
  }

  useEffect(() => {
    async function cargarSesion() {
      try {
        const u = await sesionActual()
        try {
          setCsrf(await obtenerCsrf())
        } catch {
          /* sin CSRF solo fallan los métodos no-GET; se reintenta al navegar */
        }
        setUsuario(u)
      } catch {
        setUsuario(null)
      } finally {
        setCargandoSesion(false)
      }
    }
    cargarSesion()
  }, [])

  useEffect(() => {
    function sinSesion() {
      setUsuario(null)
    }
    window.addEventListener("sisv:no-sesion", sinSesion)
    return () => window.removeEventListener("sisv:no-sesion", sinSesion)
  }, [])

  async function salir() {
    try {
      await cerrarSesion()
    } catch {
      /* sin importar el backend, se cierra localmente */
    }
    setUsuario(null)
  }

  if (cargandoSesion) return <div className="login-pagina"><p>Cargando sesión…</p></div>
  if (!usuario) return <Login onLogin={setUsuario} />

  const esMulticentro = ["REGIONAL", "GOBERNACION", "MINISTERIO"].includes(usuario.organizacion?.nivel)

  return (
    <div className={`app ${menuAbierto ? "menu-abierto" : ""}`}>
      <button
        type="button"
        className="menu-boton"
        aria-label={menuAbierto ? "Cerrar menú" : "Abrir menú"}
        aria-expanded={menuAbierto}
        onClick={() => setMenuAbierto((v) => !v)}
      >
        {menuAbierto ? "✕" : "☰"}
      </button>
      {menuAbierto && <div className="menu-backdrop" onClick={cerrarMenu} />}
      <aside className="panel-lateral">
        <div className="marca">
          <span className="logo">SISV</span>
          <span className="subtitulo">Sistema Integral de Salud</span>
        </div>
        <Credencial usuario={usuario} onSalir={salir} />
        <nav className="menu">
          {NAVEGACION.map((item, i) =>
            item.grupo ? (
              <div className="grupo-menu" key={`${item.grupo}-${i}`}>
                <span className="cabecera-grupo">{item.grupo}</span>
                {item.items.map((sub) => (
                  <NavLink key={sub.enlace} to={sub.enlace} end={sub.exacto} onClick={cerrarMenu}>
                    {sub.rotulo}
                  </NavLink>
                ))}
              </div>
            ) : (
              <NavLink key={item.enlace} to={item.enlace} onClick={cerrarMenu}>
                {item.rotulo}
              </NavLink>
            )
          )}
        </nav>
        <a className="api-enlace" href="http://127.0.0.1:8000/api/" target="_blank" rel="noreferrer" onClick={cerrarMenu}>
          Documentación API
        </a>
      </aside>

      <main className="contenido">
        <Routes>
          <Route path="/" element={<Tablero />} />
          <Route path="/nacimientos" element={<CargaNacimientos usuario={usuario} multicentro={esMulticentro} />} />
          <Route path="/defunciones" element={<CargaDefunciones usuario={usuario} multicentro={esMulticentro} />} />
          <Route path="/vigilancia" element={<Vigilancia usuario={usuario} />} />
          <Route path="/vigilancia/fichas" element={<CargaFichasVigilancia usuario={usuario} multicentro={esMulticentro} />} />
          <Route path="/reportes" element={<Reportes />} />
          <Route path="/mapeos" element={<Mapeos />} />
          <Route path="/configuracion" element={<Configuracion usuario={usuario} />} />
          <Route path="/seguridad" element={<Seguridad usuario={usuario} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <footer className="firma-app">Desarrollado por Rafael Venegas</footer>
      </main>
    </div>
  )
}