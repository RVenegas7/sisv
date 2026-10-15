import { useEffect, useState } from "react"
import {
  crearNovedad,
  crearTalonario,
  detalleTalonario,
  eliminarNovedad,
  eliminarTalonario,
  exportarDespacho,
  listarOrganizaciones,
  listarTalonarios,
  reporteCertificados,
  reportePendientes,
  reporteSeriesDeducidas,
} from "../api/sisv"
import CentroSelector from "../components/CentroSelector"
import { Boton, Campo, Input, Select } from "../components/ui"

const TIPOS = [
  ["NACIMIENTO", "Nacimiento"],
  ["DEFUNCION", "Defunción"],
]

const ESTADOS_NOVEDAD = [
  ["DANADO", "Dañado"],
  ["EN_TRANSITO", "En tránsito"],
  ["DEVUELTO", "Devuelto"],
]

const ETIQUETA_ESTATUS = {
  CARGADO: "Cargado",
  SIN_ASIGNAR: "Sin asignar",
  DANADO: "Dañado",
  EN_TRANSITO: "En tránsito",
  DEVUELTO: "Devuelto",
}

const FORMA_VACIA = {
  tipo: "DEFUNCION",
  centro: null,
  fecha_entrega: "",
  serie_desde: "",
  cantidad: "",
  responsable_recibe: "",
  responsable_entrega: "",
  observaciones: "",
}

function descargar(blob, nombre) {
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement("a")
  enlace.href = url
  enlace.download = nombre
  enlace.click()
  URL.revokeObjectURL(url)
}

export default function Despacho({ usuario }) {
  const puedeDespachar = Boolean(usuario?.permisos?.puede_despachar)
  // Sin organización (superusuario) cuenta como multicentro: debe elegir el
  // centro destino igual que la regional, y los reportes muestran el filtro.
  const esMulticentro =
    !usuario?.organizacion ||
    ["REGIONAL", "GOBERNACION", "MINISTERIO"].includes(usuario.organizacion.nivel)

  const [talonarios, setTalonarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [estado, setEstado] = useState({ tipo: "", texto: "" })
  const [form, setForm] = useState(FORMA_VACIA)
  const [filtro, setFiltro] = useState({ tipo: "", anio: "" })
  const [detalle, setDetalle] = useState(null)
  const [novedad, setNovedad] = useState({ numero: "", estado: "DANADO", justificacion_numero: "", fecha_salio_centro: "" })
  const [centros, setCentros] = useState([])

  const [repCert, setRepCert] = useState({ tipo: "DEFUNCION", centro: "", desde: "", hasta: "" })
  const [porCentro, setPorCentro] = useState([])
  const [filasCert, setFilasCert] = useState([])
  const [centroDetalle, setCentroDetalle] = useState(null)
  const [repPend, setRepPend] = useState({ tipo: "", centro: "", solo_pendientes: true })
  const [filasPend, setFilasPend] = useState([])

  const [repSeries, setRepSeries] = useState({
    tipo: "DEFUNCION",
    anio: String(new Date().getFullYear()),
    tolerancia: 10,
    densidad: 0.5,
    redondeo: 0,
  })
  const [series, setSeries] = useState([])
  const [respRecibe, setRespRecibe] = useState("Por confirmar")

  function avisar(tipo, texto) {
    setEstado({ tipo, texto })
  }

  async function cargar() {
    try {
      const { items } = await listarTalonarios({
        tipo: filtro.tipo || undefined,
        anio: filtro.anio || undefined,
      })
      setTalonarios(items)
    } catch (e) {
      avisar("error", e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
    if (esMulticentro) {
      listarOrganizaciones()
        .then((orgs) => setCentros(orgs.filter((o) => o.nivel === "CENTRO")))
        .catch(() => setCentros([]))
    }
  }, [filtro.tipo, filtro.anio]) // eslint-disable-line react-hooks/exhaustive-deps

  async function guardar(e) {
    e.preventDefault()
    if (esMulticentro && !form.centro) {
      avisar("error", "Seleccione el centro de salud al que se asigna el talonario.")
      return
    }
    const cantidad = Number(form.cantidad)
    if (!Number.isInteger(cantidad) || cantidad < 1) {
      avisar("error", "Indique la cantidad de certificados asignados (un entero mayor que cero).")
      return
    }
    const payload = {
      tipo: form.tipo,
      centro: form.centro,
      fecha_entrega: form.fecha_entrega,
      serie_desde: Number(form.serie_desde),
      cantidad,
      responsable_recibe: form.responsable_recibe,
      responsable_entrega: form.responsable_entrega,
      observaciones: form.observaciones,
    }
    try {
      await crearTalonario(payload)
      avisar("ok", "Talonario registrado.")
      setForm(FORMA_VACIA)
      await cargar()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function borrar(t) {
    if (!window.confirm(`¿Eliminar el talonario ${t.serie_desde}-${t.serie_hasta} de ${t.centro_nombre}?`)) return
    try {
      await eliminarTalonario(t.id)
      avisar("ok", "Talonario eliminado.")
      if (detalle?.talonario?.id === t.id) setDetalle(null)
      await cargar()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function verDetalle(t) {
    try {
      setDetalle(await detalleTalonario(t.id))
      setNovedad({ numero: "", estado: "DANADO", justificacion_numero: "", fecha_salio_centro: "" })
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function guardarNovedad(e) {
    e.preventDefault()
    try {
      await crearNovedad({
        talonario: detalle.talonario.id,
        numero: Number(novedad.numero),
        estado: novedad.estado,
        justificacion_numero: novedad.justificacion_numero,
        fecha_salio_centro: novedad.fecha_salio_centro || null,
      })
      avisar("ok", "Novedad registrada.")
      await verDetalle(detalle.talonario)
      await cargar()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function borrarNovedad(id) {
    try {
      await eliminarNovedad(id)
      avisar("ok", "Novedad eliminada.")
      await verDetalle(detalle.talonario)
      await cargar()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function verCertificados(e) {
    e?.preventDefault()
    try {
      const datos = await reporteCertificados({
        tipo: repCert.tipo,
        centro: repCert.centro || undefined,
        desde: repCert.desde || undefined,
        hasta: repCert.hasta || undefined,
        agrupado: 1,
      })
      setPorCentro(datos.items)
      setFilasCert([])
      setCentroDetalle(null)
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function verDetalleCentro(centroId) {
    try {
      const datos = await reporteCertificados({
        tipo: repCert.tipo,
        centro: centroId,
        desde: repCert.desde || undefined,
        hasta: repCert.hasta || undefined,
      })
      setFilasCert(datos.items)
      setCentroDetalle(porCentro.find((f) => String(f.centro_id) === String(centroId)) || null)
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function verPendientes(e) {
    e?.preventDefault()
    try {
      const datos = await reportePendientes({
        tipo: repPend.tipo || undefined,
        centro: repPend.centro || undefined,
        solo_pendientes: repPend.solo_pendientes ? "1" : "0",
      })
      setFilasPend(datos.items)
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function verSeries(e) {
    e?.preventDefault()
    try {
      const datos = await reporteSeriesDeducidas({
        tipo: repSeries.tipo,
        anio: repSeries.anio || undefined,
        tolerancia: repSeries.tolerancia,
        densidad: repSeries.densidad,
        redondeo: repSeries.redondeo,
      })
      setSeries(datos.items)
      if (datos.items.length === 0) {
        avisar("ok", "No se dedujo ninguna serie con esos parámetros.")
      }
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function crearDesdeSerie(c) {
    if (!respRecibe.trim()) {
      avisar("error", "Indique el responsable que recibe antes de registrar el talonario.")
      return
    }
    try {
      await crearTalonario({
        tipo: repSeries.tipo,
        centro: c.centro_id,
        fecha_entrega: c.fecha_desde,
        serie_desde: c.serie_desde,
        serie_hasta: c.serie_hasta,
        responsable_recibe: respRecibe,
      })
      avisar("ok", `Talonario ${c.serie_desde}–${c.serie_hasta} registrado para ${c.centro}.`)
      await verSeries()
      await cargar()
    } catch (err) {
      avisar("error", err.message)
    }
  }

  async function exportar(ruta, params, nombre) {
    try {
      const blob = await exportarDespacho(ruta, params)
      descargar(blob, nombre)
    } catch (err) {
      avisar("error", err.message)
    }
  }

  const opcionesCentros = centros.map((c) => [String(c.id), c.nombre])
  const desdeNum = Number(form.serie_desde)
  const cantidadNum = Number(form.cantidad)
  const hastaCalculada =
    Number.isInteger(desdeNum) && desdeNum >= 1 && Number.isInteger(cantidadNum) && cantidadNum >= 1
      ? desdeNum + cantidadNum - 1
      : null
  const novedadesPorNumero = {}
  if (detalle) {
    for (const c of detalle.certificados) {
      if (["DANADO", "EN_TRANSITO", "DEVUELTO"].includes(c.estatus)) novedadesPorNumero[c.numero] = c
    }
  }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Despacho de certificados</h1>
        <p>
          Control de talonarios de certificados de nacimiento y defunción entregados a los centros,
          y de los certificados retornados, dañados o aún sin justificar.
        </p>
      </header>

      {estado.tipo && (
        <p className={`aviso ${estado.tipo}`} role="status">
          {estado.texto}
        </p>
      )}

      {puedeDespachar && (
        <form onSubmit={guardar} className="seccion">
          <h2>Registrar entrega de talonario</h2>
          <div className="grid">
            <Campo label="Tipo de certificado">
              <Select
                opciones={TIPOS}
                value={form.tipo}
                onChange={(e) => setForm((f) => ({ ...f, tipo: e.target.value }))}
              />
            </Campo>
            <CentroSelector
              usuario={usuario}
              value={form.centro}
              onChange={(id) => setForm((f) => ({ ...f, centro: id }))}
            />
            <Campo label="Fecha de entrega" htmlFor="tal-fecha">
              <Input
                id="tal-fecha"
                type="date"
                required
                value={form.fecha_entrega}
                onChange={(e) => setForm((f) => ({ ...f, fecha_entrega: e.target.value }))}
              />
            </Campo>
            <Campo label="Serie desde" htmlFor="tal-desde">
              <Input
                id="tal-desde"
                type="number"
                min="1"
                required
                value={form.serie_desde}
                onChange={(e) => setForm((f) => ({ ...f, serie_desde: e.target.value }))}
              />
            </Campo>
            <Campo label="Cantidad asignada" htmlFor="tal-cantidad">
              <Input
                id="tal-cantidad"
                type="number"
                min="1"
                required
                value={form.cantidad}
                onChange={(e) => setForm((f) => ({ ...f, cantidad: e.target.value }))}
              />
            </Campo>
            <Campo label="Serie hasta (automática)" htmlFor="tal-hasta">
              <Input
                id="tal-hasta"
                type="number"
                readOnly
                value={hastaCalculada || ""}
              />
            </Campo>
            <Campo label="Responsable que recibe" htmlFor="tal-recibe">
              <Input
                id="tal-recibe"
                required
                value={form.responsable_recibe}
                onChange={(e) => setForm((f) => ({ ...f, responsable_recibe: e.target.value }))}
              />
            </Campo>
            <Campo label="Responsable que entrega" htmlFor="tal-entrega">
              <Input
                id="tal-entrega"
                value={form.responsable_entrega}
                onChange={(e) => setForm((f) => ({ ...f, responsable_entrega: e.target.value }))}
              />
            </Campo>
            <Campo label="Observaciones" htmlFor="tal-obs">
              <Input
                id="tal-obs"
                value={form.observaciones}
                onChange={(e) => setForm((f) => ({ ...f, observaciones: e.target.value }))}
              />
            </Campo>
          </div>
          <div className="pie-form">
            <Boton>Registrar talonario</Boton>
          </div>
        </form>
      )}

      <section className="lista">
        <div className="cabecera-lista">
          <h2>Talonarios entregados</h2>
          <div className="filtros">
            <Select
              opciones={TIPOS}
              value={filtro.tipo}
              onChange={(e) => setFiltro((f) => ({ ...f, tipo: e.target.value }))}
            />
            <Input
              placeholder="Año"
              value={filtro.anio}
              onChange={(e) => setFiltro((f) => ({ ...f, anio: e.target.value }))}
            />
          </div>
        </div>
        {cargando ? (
          <p className="ayuda">Cargando talonarios…</p>
        ) : talonarios.length === 0 ? (
          <p className="ayuda">No hay talonarios registrados.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Centro</th>
                <th>Serie</th>
                <th>Fecha entrega</th>
                <th>Usados</th>
                <th>Sin asignar</th>
                <th>Dañados</th>
                <th>En tránsito</th>
                <th>Devueltos</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {talonarios.map((t) => (
                <tr key={t.id}>
                  <td>{t.tipo_label}</td>
                  <td>{t.centro_nombre}</td>
                  <td>
                    {t.serie_desde}–{t.serie_hasta} ({t.cantidad})
                  </td>
                  <td>{t.fecha_entrega}</td>
                  <td>{t.resumen?.usados}</td>
                  <td>{t.resumen?.faltantes_total}</td>
                  <td>{t.resumen?.danados}</td>
                  <td>{t.resumen?.en_transito}</td>
                  <td>{t.resumen?.devueltos}</td>
                  <td className="acciones">
                    <button type="button" className="btn-mini" onClick={() => verDetalle(t)}>
                      Detalle
                    </button>
                    {puedeDespachar && (
                      <button type="button" className="btn-mini peligro" onClick={() => borrar(t)}>
                        Eliminar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {detalle && (
        <section className="lista">
          <div className="cabecera-lista">
            <h2>
              Detalle {detalle.talonario.tipo_label} {detalle.talonario.serie_desde}–
              {detalle.talonario.serie_hasta} · {detalle.talonario.centro_nombre}
            </h2>
            <button type="button" className="btn-mini" onClick={() => setDetalle(null)}>
              Cerrar
            </button>
          </div>
          <p className="ayuda">
            Usados: {detalle.resumen.usados} · Sin asignar: {detalle.resumen.faltantes_total} ·
            Dañados: {detalle.resumen.danados} · En tránsito: {detalle.resumen.en_transito} ·
            Devueltos: {detalle.resumen.devueltos}
          </p>

          {puedeDespachar && (
            <form onSubmit={guardarNovedad} className="subseccion">
              <h3>Registrar novedad (dañado, en tránsito o devuelto)</h3>
              <div className="grid">
                <Campo label="Nº certificado" htmlFor="nov-num">
                  <Input
                    id="nov-num"
                    type="number"
                    min={detalle.talonario.serie_desde}
                    max={detalle.talonario.serie_hasta}
                    required
                    value={novedad.numero}
                    onChange={(e) => setNovedad((n) => ({ ...n, numero: e.target.value }))}
                  />
                </Campo>
                <Campo label="Estatus">
                  <Select
                    opciones={ESTADOS_NOVEDAD}
                    value={novedad.estado}
                    onChange={(e) => setNovedad((n) => ({ ...n, estado: e.target.value }))}
                  />
                </Campo>
                <Campo label="Nº de acta de justificación" htmlFor="nov-just">
                  <Input
                    id="nov-just"
                    value={novedad.justificacion_numero}
                    onChange={(e) => setNovedad((n) => ({ ...n, justificacion_numero: e.target.value }))}
                  />
                </Campo>
                <Campo label="Fecha en que salió del centro" htmlFor="nov-fecha">
                  <Input
                    id="nov-fecha"
                    type="date"
                    value={novedad.fecha_salio_centro}
                    onChange={(e) => setNovedad((n) => ({ ...n, fecha_salio_centro: e.target.value }))}
                  />
                </Campo>
              </div>
              <div className="pie-form">
                <Boton>Registrar novedad</Boton>
              </div>
            </form>
          )}

          <table>
            <thead>
              <tr>
                <th>Nº</th>
                <th>Estatus</th>
                <th>Nombres</th>
                <th>Apellidos</th>
                <th>Fecha</th>
                {puedeDespachar && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {detalle.certificados.map((c) => (
                <tr key={c.numero}>
                  <td>{c.numero}</td>
                  <td>
                    <span className={`etiqueta ${c.estatus.toLowerCase()}`}>
                      {ETIQUETA_ESTATUS[c.estatus] || c.estatus}
                    </span>
                  </td>
                  <td>{c.nombres || "—"}</td>
                  <td>{c.apellidos || "—"}</td>
                  <td>{c.fecha || "—"}</td>
                  {puedeDespachar && (
                    <td className="acciones">
                      {novedadesPorNumero[c.numero] ? (
                        <button
                          type="button"
                          className="btn-mini peligro"
                          onClick={() => borrarNovedad(novedadesPorNumero[c.numero].id)}
                        >
                          Quitar novedad
                        </button>
                      ) : (
                        "—"
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <section className="lista">
        <h2>Reporte 1 · Certificados usados por centro</h2>
        <form onSubmit={verCertificados} className="filtros">
          <Select
            opciones={TIPOS}
            value={repCert.tipo}
            onChange={(e) => setRepCert((r) => ({ ...r, tipo: e.target.value }))}
          />
          {esMulticentro && (
            <Select
              opciones={opcionesCentros}
              value={repCert.centro}
              onChange={(e) => setRepCert((r) => ({ ...r, centro: e.target.value }))}
            />
          )}
          <Input
            type="date"
            value={repCert.desde}
            onChange={(e) => setRepCert((r) => ({ ...r, desde: e.target.value }))}
          />
          <Input
            type="date"
            value={repCert.hasta}
            onChange={(e) => setRepCert((r) => ({ ...r, hasta: e.target.value }))}
          />
          <button type="submit" className="btn-mini">
            Ver consolidado
          </button>
          <button
            type="button"
            className="btn-mini"
            onClick={() =>
              centroDetalle
                ? exportar(
                    "certificados",
                    { tipo: repCert.tipo, centro: centroDetalle.centro_id, desde: repCert.desde || undefined, hasta: repCert.hasta || undefined },
                    `certificados_${repCert.tipo.toLowerCase()}_${centroDetalle.centro_id}.csv`,
                  )
                : exportar(
                    "certificados",
                    { tipo: repCert.tipo, centro: repCert.centro || undefined, desde: repCert.desde || undefined, hasta: repCert.hasta || undefined, agrupado: 1 },
                    `certificados_por_centro_${repCert.tipo.toLowerCase()}.csv`,
                  )
            }
          >
            CSV
          </button>
        </form>

        {!centroDetalle && porCentro.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Centro</th>
                <th>Certificados usados</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {porCentro.map((f) => (
                <tr key={f.centro_id ?? f.centro}>
                  <td>{f.centro}</td>
                  <td>{f.cantidad}</td>
                  <td>
                    <button type="button" className="btn-mini" onClick={() => verDetalleCentro(f.centro_id)}>
                      Ver detalle
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {centroDetalle && (
          <>
            <p className="detalle-titulo">
              Certificados usados · <strong>{centroDetalle.centro}</strong> ({filasCert.length})
              <button type="button" className="btn-mini" onClick={() => { setCentroDetalle(null); setFilasCert([]) }}>
                ← Volver al consolidado
              </button>
            </p>
            <table>
              <thead>
                <tr>
                  <th>Nº Certificado</th>
                  <th>Persona</th>
                  <th>Nombres</th>
                  <th>Apellidos</th>
                  <th>Fecha</th>
                  <th>Centro</th>
                </tr>
              </thead>
              <tbody>
                {filasCert.map((f, i) => (
                  <tr key={`${f.numero}-${i}`}>
                    <td>{f.numero}</td>
                    <td>{f.persona || "—"}</td>
                    <td>{f.nombres}</td>
                    <td>{f.apellidos}</td>
                    <td>{f.fecha}</td>
                    <td>{f.centro}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </section>

      <section className="lista">
        <h2>Reporte 2 · Certificados no retornados ni justificados</h2>
        <form onSubmit={verPendientes} className="filtros">
          <Select
            opciones={TIPOS}
            value={repPend.tipo}
            onChange={(e) => setRepPend((r) => ({ ...r, tipo: e.target.value }))}
          />
          {esMulticentro && (
            <Select
              opciones={opcionesCentros}
              value={repPend.centro}
              onChange={(e) => setRepPend((r) => ({ ...r, centro: e.target.value }))}
            />
          )}
          <label className="caja item-fila">
            <input
              type="checkbox"
              checked={repPend.solo_pendientes}
              onChange={(e) => setRepPend((r) => ({ ...r, solo_pendientes: e.target.checked }))}
            />
            Solo pendientes (sin asignar / en tránsito)
          </label>
          <button type="submit" className="btn-mini">
            Ver
          </button>
          <button
            type="button"
            className="btn-mini"
            onClick={() =>
              exportar(
                "pendientes",
                { tipo: repPend.tipo || undefined, centro: repPend.centro || undefined, solo_pendientes: repPend.solo_pendientes ? "1" : "0" },
                "certificados_pendientes.csv",
              )
            }
          >
            CSV
          </button>
        </form>
        {filasPend.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Nº Certificado</th>
                <th>Serie</th>
                <th>Centro</th>
                <th>Estatus</th>
                <th>Fecha entrega</th>
              </tr>
            </thead>
            <tbody>
              {filasPend.map((f, i) => (
                <tr key={`${f.talonario_id}-${f.numero}-${i}`}>
                  <td>{f.tipo}</td>
                  <td>{f.numero}</td>
                  <td>{f.serie}</td>
                  <td>{f.centro}</td>
                  <td>
                    <span className={`etiqueta ${f.estatus.toLowerCase()}`}>
                      {ETIQUETA_ESTATUS[f.estatus] || f.estatus}
                    </span>
                  </td>
                  <td>{f.fecha_entrega}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="lista">
        <h2>Deducir talonarios desde la base de datos</h2>
        <p className="ayuda">
          El sistema anterior nunca registró la entrega de talonarios, así que la serie de cada
          centro se <strong>infiere</strong> de los certificados ya cargados (su número impreso).
          Revise las series propuestas y registre el talonario del centro correspondiente.
          Con <strong>Redondeo</strong> el rango se estira hasta el corte de decena más cercano
          (las series van de «múltiplo de 10 + 1» a «múltiplo de 10»), sin pisar números que ya
          sabemos usados por otro centro.
        </p>
        <form onSubmit={verSeries} className="filtros">
          <Select
            opciones={TIPOS}
            value={repSeries.tipo}
            onChange={(e) => setRepSeries((r) => ({ ...r, tipo: e.target.value }))}
          />
          <Input
            placeholder="Año"
            value={repSeries.anio}
            onChange={(e) => setRepSeries((r) => ({ ...r, anio: e.target.value }))}
          />
          <Campo label="Hueco máximo">
            <Input
              type="number"
              min="1"
              value={repSeries.tolerancia}
              onChange={(e) => setRepSeries((r) => ({ ...r, tolerancia: e.target.value }))}
            />
          </Campo>
          <Campo label="Densidad mínima">
            <Input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={repSeries.densidad}
              onChange={(e) => setRepSeries((r) => ({ ...r, densidad: e.target.value }))}
            />
          </Campo>
          <Campo label="Redondeo (0–9)">
            <Input
              type="number"
              min="0"
              max="9"
              value={repSeries.redondeo}
              onChange={(e) => setRepSeries((r) => ({ ...r, redondeo: e.target.value }))}
            />
          </Campo>
          <button type="submit" className="btn-mini">
            Deducir series
          </button>
          <button
            type="button"
            className="btn-mini"
            onClick={() =>
              exportar(
                "series-deducidas",
                {
                  tipo: repSeries.tipo,
                  anio: repSeries.anio || undefined,
                  tolerancia: repSeries.tolerancia,
                  densidad: repSeries.densidad,
                  redondeo: repSeries.redondeo,
                },
                `series_deducidas_${repSeries.tipo.toLowerCase()}.csv`,
              )
            }
          >
            CSV
          </button>
        </form>

        {puedeDespachar && series.length > 0 && (
          <div className="filtros">
            <Campo label="Responsable que recibe (para los que registre)" htmlFor="series-recibe">
              <Input
                id="series-recibe"
                value={respRecibe}
                onChange={(e) => setRespRecibe(e.target.value)}
              />
            </Campo>
          </div>
        )}

        {series.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Centro</th>
                <th>Serie propuesta</th>
                <th>Usados</th>
                <th>Extensión</th>
                <th>Densidad</th>
                <th>Fechas</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {series.map((c, i) => (
                <tr key={`${c.centro_id}-${c.serie_desde}-${i}`}>
                  <td>{c.centro}</td>
                  <td>
                    {c.serie_desde}–{c.serie_hasta}
                    {c.redondeado && (
                      <span className="etiqueta" title="Rango observado; estirado al corte de decena">
                        {" "}
                        redondeado ({c.serie_desde_observada}–{c.serie_hasta_observada})
                      </span>
                    )}
                  </td>
                  <td>{c.usados}</td>
                  <td>{c.extension}</td>
                  <td>{c.densidad}</td>
                  <td>
                    {c.fecha_desde} → {c.fecha_hasta}
                  </td>
                  <td className="acciones">
                    {c.ya_registrado ? (
                      <span className="etiqueta cargado">Ya registrado</span>
                    ) : puedeDespachar ? (
                      <button type="button" className="btn-mini" onClick={() => crearDesdeSerie(c)}>
                        Registrar talonario
                      </button>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
