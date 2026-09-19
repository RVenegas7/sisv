import { useState } from "react"
import { iniciarSesion } from "../api/sisv"
import { Boton, Campo, Input } from "../components/ui"

export default function Login({ onLogin }) {
  const [usuario, setUsuario] = useState("")
  const [clave, setClave] = useState("")
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState("")

  async function entrar(e) {
    e.preventDefault()
    setCargando(true)
    setError("")
    try {
      const perfil = await iniciarSesion(usuario.trim(), clave)
      onLogin(perfil)
    } catch (err) {
      setError(err.message || "No se pudo iniciar sesión.")
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="login-pagina">
      <form className="login-tarjeta" onSubmit={entrar} noValidate>
        <div className="login-marca">
          <span className="logo">SISV</span>
          <h1>Sistema Integral de Salud</h1>
          <p>Ingrese con su usuario para acceder a la carga según su organización.</p>
        </div>

        {error && (
          <div className="aviso aviso-error" role="alert">
            {error}
          </div>
        )}

        <Campo label="Usuario" htmlFor="login_usuario">
          <Input id="login_usuario" value={usuario} autoComplete="username" onChange={(e) => setUsuario(e.target.value)} />
        </Campo>
        <Campo label="Clave" htmlFor="login_clave">
          <Input id="login_clave" type="password" value={clave} autoComplete="current-password" onChange={(e) => setClave(e.target.value)} />
        </Campo>

        <div className="pie-form">
          <Boton disabled={cargando}>{cargando ? "Ingresando…" : "Ingresar"}</Boton>
        </div>
      </form>

      <footer className="login-firma">Desarrollado por Rafael Venegas</footer>
    </div>
  )
}