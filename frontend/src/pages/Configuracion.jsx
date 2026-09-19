import { useEffect, useState } from "react"
import { guardarConfiguracion, listarOrganizaciones, obtenerConfiguracion } from "../api/sisv"
import { Boton, Campo, Input, Seccion, Select } from "../components/ui"
import SelectTerritorial from "../components/SelectTerritorial"

export default function Configuracion({ usuario }) {
  const permisos = usuario?.permisos || {}
  const [form, setForm] = useState({
    estado: "",
    municipio: "",
    parroquia: "",
    establecimiento: "",
    fecha_corte_cie11: "",
    organizacion_activa: "",
  })
  const [organizaciones, setOrganizaciones] = useState([])
  const [estado, setEstado] = useState({ tipo: "", texto: "" })
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    Promise.all([obtenerConfiguracion(), listarOrganizaciones()])
      .then(([cfg, orgs]) => {
        setForm({
          estado: cfg.estado || "",
          municipio: cfg.municipio || "",
          parroquia: cfg.parroquia || "",
          establecimiento: cfg.establecimiento || "",
          fecha_corte_cie11: cfg.fecha_corte_cie11 || "",
          organizacion_activa: cfg.organizacion_activa ? String(cfg.organizacion_activa) : "",
        })
        setOrganizaciones(orgs)
      })
      .catch(() => setEstado({ tipo: "error", texto: "No se pudo cargar la configuración." }))
      .finally(() => setCargando(false))
  }, [])

  function cambiar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }))
  }

  async function guardar(e) {
    e.preventDefault()
    setEstado({ tipo: "info", texto: "Guardando…" })
    try {
      const payload = {
        estado: form.estado,
        municipio: form.municipio,
        parroquia: form.parroquia,
        establecimiento: form.establecimiento,
        fecha_corte_cie11: form.fecha_corte_cie11,
        organizacion_activa: form.organizacion_activa ? Number(form.organizacion_activa) : "",
      }
      await guardarConfiguracion(payload)
      setEstado({ tipo: "ok", texto: "Configuración guardada. Los formularios de carga se precargarán con estos valores." })
    } catch (err) {
      setEstado({ tipo: "error", texto: err.message })
    }
  }

  if (cargando) return <div className="aviso aviso-info">Cargando configuración…</div>

  if (!permisos.puede_configurar) {
    return (
      <div className="pagina">
        <header className="cabecera-pagina">
          <h1>Configuración general</h1>
          <p>Valores por defecto de los formularios de carga.</p>
        </header>
        <div className="aviso aviso-info">
          Su rol (<strong>{usuario?.rol_label}</strong> o sin rol) no tiene permiso para modificar la configuración general.
          Solo un <strong>Director</strong> o el superusuario puede hacerlo.
        </div>
      </div>
    )
  }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Configuración general</h1>
        <p>Valores por defecto para los formularios de carga y fecha de corte del catálogo CIE-11.</p>
      </header>

      {estado.tipo && (
        <div className={`aviso aviso-${estado.tipo}`} role="status">
          {estado.texto}
        </div>
      )}

      <form className="formulario" onSubmit={guardar} noValidate>
        <Seccion titulo="Datos por defecto de los formularios">
          <SelectTerritorial
            valor={{ estado: form.estado, municipio: form.municipio, parroquia: form.parroquia, comunidad: "" }}
            onChange={(t) => setForm((f) => ({ ...f, estado: t.estado, municipio: t.municipio, parroquia: t.parroquia }))}
          />
          <Campo label="Establecimiento" htmlFor="cfg_establecimiento">
            <Input id="cfg_establecimiento" value={form.establecimiento} onChange={(e) => cambiar("establecimiento", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="Catálogo CIE">
          <Campo label="Fecha de corte CIE-11" htmlFor="cfg_fecha_corte">
            <Input
              id="cfg_fecha_corte"
              type="date"
              value={form.fecha_corte_cie11}
              onChange={(e) => cambiar("fecha_corte_cie11", e.target.value)}
            />
          </Campo>
          <p className="ayuda">
            Los eventos anteriores a esta fecha se clasifican con CIE-10; desde esta fecha, con CIE-11.
          </p>
        </Seccion>

        <Seccion titulo="Organización activa">
          <Campo label="Organización" htmlFor="cfg_organizacion">
            <Select
              id="cfg_organizacion"
              opciones={organizaciones.map((o) => [`${o.id}`, `${o.nivel_label} — ${o.nombre}${o.estado ? ` (${o.estado})` : ""}`])}
              value={form.organizacion_activa}
              onChange={(e) => cambiar("organizacion_activa", e.target.value)}
            />
          </Campo>
        </Seccion>

        <div className="pie-form">
          <Boton>Guardar configuración</Boton>
        </div>
      </form>
    </div>
  )
}