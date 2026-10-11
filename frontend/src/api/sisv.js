import api, { setCsrf } from "./axios"

export async function iniciarSesion(username, password) {
  const r = await api.post("/auth/login/", { username, password })
  const token = await obtenerCsrf()
  setCsrf(token)
  return r.data.data
}

export async function cerrarSesion() {
  await api.post("/auth/logout/")
  setCsrf(null)
}

export async function obtenerCsrf() {
  const r = await api.get("/auth/csrf/")
  return r.data.data.csrf
}

export async function sesionActual() {
  const r = await api.get("/auth/me/")
  return r.data.data
}

export async function buscarCIE10(q) {
  const r = await api.get("/catalogos/cie10/buscar/", { params: { q } })
  return r.data.data
}

export async function buscarCIE11(q) {
  const r = await api.get("/catalogos/cie11/buscar/", { params: { q } })
  return r.data.data
}

export async function capitulosCIE11() {
  const r = await api.get("/catalogos/cie11/", { params: { nivel: 1 } })
  return r.data.data
}

export async function hijosCIE11(padre) {
  const r = await api.get("/catalogos/cie11/", { params: { padre } })
  return r.data.data
}

export async function arbolCIE11() {
  const r = await api.get("/catalogos/cie11/arbol/")
  return r.data.data
}

export async function obtenerCIE10(id) {
  const r = await api.get(`/catalogos/cie10/${id}/`)
  return r.data.data
}

export async function obtenerCIE11(id) {
  const r = await api.get(`/catalogos/cie11/${id}/`)
  return r.data.data
}

export async function mapeosCIE10(codigo) {
  const r = await api.get("/catalogos/mapeos/", { params: { cie10: codigo } })
  return r.data.data
}

export async function mapeosCIE11(codigo) {
  const r = await api.get("/catalogos/mapeos/", { params: { cie11: codigo } })
  return r.data.data
}

export async function listarNacimientos(params = {}) {
  const r = await api.get("/registros/nacimientos/", { params })
  return { items: r.data.data, count: r.data.count, pagination: r.data.pagination }
}

export async function crearNacimiento(payload) {
  const r = await api.post("/registros/nacimientos/", payload)
  return r.data.data
}

export async function actualizarNacimiento(id, payload) {
  const r = await api.patch(`/registros/nacimientos/${id}/`, payload)
  return r.data.data
}

export async function eliminarNacimiento(id) {
  await api.delete(`/registros/nacimientos/${id}/`)
}

export async function listarDefunciones(params = {}) {
  const r = await api.get("/registros/defunciones/", { params })
  return { items: r.data.data, count: r.data.count, pagination: r.data.pagination }
}

export async function crearDefuncion(payload) {
  const r = await api.post("/registros/defunciones/", payload)
  return r.data.data
}

export async function actualizarDefuncion(id, payload) {
  const r = await api.patch(`/registros/defunciones/${id}/`, payload)
  return r.data.data
}

export async function eliminarDefuncion(id) {
  await api.delete(`/registros/defunciones/${id}/`)
}

export async function listarFichas(params = {}) {
  const r = await api.get("/registros/fichas-vigilancia/", { params })
  return { items: r.data.data, count: r.data.count, pagination: r.data.pagination }
}

export async function crearFicha(payload) {
  const r = await api.post("/registros/fichas-vigilancia/", payload)
  return r.data.data
}

export async function actualizarFicha(id, payload) {
  const r = await api.patch(`/registros/fichas-vigilancia/${id}/`, payload)
  return r.data.data
}

export async function eliminarFicha(id) {
  await api.delete(`/registros/fichas-vigilancia/${id}/`)
}

export async function obtenerDashboard(params = {}) {
  const r = await api.get("/registros/dashboard/", { params })
  return r.data.data
}

export async function obtenerReportes(params = {}) {
  const r = await api.get("/registros/reportes/", { params })
  return r.data.data
}

export async function obtenerResidentesOtrosEstados(params = {}) {
  const r = await api.get("/registros/reportes/residentes/", { params })
  return r.data.data
}

export async function obtenerReporteComparativo(params = {}) {
  const r = await api.get("/registros/reportes/comparativo/", { params })
  return r.data.data
}

export async function obtenerReporteSemanalMMI(params = {}) {
  const r = await api.get("/registros/reportes/semanal-mmi/", { params })
  return r.data.data
}

export async function exportarReporteSemanalMMI(params = {}) {
  const r = await api.get("/registros/reportes/semanal-mmi/", {
    params: { ...params, formato: "csv" },
    responseType: "blob",
  })
  return r.data
}

export async function exportarReportes(params = {}) {
  const r = await api.get("/registros/reportes/exportar/", { params, responseType: "blob" })
  return r.data
}

export async function obtenerConfiguracion() {
  const r = await api.get("/registros/configuracion/")
  return r.data.data
}

export async function guardarConfiguracion(payload) {
  const r = await api.put("/registros/configuracion/", payload)
  return r.data.data
}

export async function listarOrganizaciones() {
  const r = await api.get("/seguridad/organizaciones/")
  return r.data.data
}

export async function crearOrganizacion(payload) {
  const r = await api.post("/seguridad/organizaciones/", payload)
  return r.data.data
}

export async function actualizarOrganizacion(id, payload) {
  const r = await api.patch(`/seguridad/organizaciones/${id}/`, payload)
  return r.data.data
}

export async function eliminarOrganizacion(id) {
  await api.delete(`/seguridad/organizaciones/${id}/`)
}

export async function listarUsuarios() {
  const r = await api.get("/seguridad/usuarios/")
  return r.data.data
}

export async function crearUsuario(payload) {
  const r = await api.post("/seguridad/usuarios/", payload)
  return r.data.data
}

export async function actualizarUsuario(id, payload) {
  const r = await api.patch(`/seguridad/usuarios/${id}/`, payload)
  return r.data.data
}

export async function eliminarUsuario(id) {
  await api.delete(`/seguridad/usuarios/${id}/`)
}

export async function listarRoles() {
  const r = await api.get("/seguridad/roles/")
  return r.data.data
}

export async function nivelTerritorial(nivel, padre = 0) {
  const r = await api.get("/territorio/", { params: { nivel, padre } })
  return r.data.data
}

export async function rutaTerritorial(id) {
  const r = await api.get(`/territorio/${id}/ruta/`)
  return r.data.data
}

export async function listarAsics(params = {}) {
  const r = await api.get("/territorio/asic/", { params })
  return r.data.data
}

export async function obtenerAsic(id) {
  const r = await api.get(`/territorio/asic/${id}/`)
  return r.data.data
}

export async function crearAsic(payload) {
  const r = await api.post("/territorio/asic/", payload)
  return r.data.data
}

export async function actualizarAsic(id, payload) {
  const r = await api.patch(`/territorio/asic/${id}/`, payload)
  return r.data.data
}

export async function eliminarAsic(id) {
  await api.delete(`/territorio/asic/${id}/`)
}

export async function listarEventosENO(params = {}) {
  const r = await api.get("/vigilancia/eventos-eno/", { params })
  return r.data.data
}

export async function listarConsolidados(params = {}) {
  const r = await api.get("/vigilancia/consolidados/", { params })
  return r.data.data
}

export async function crearConsolidado(payload) {
  const r = await api.post("/vigilancia/consolidados/", payload)
  return r.data.data
}

export async function actualizarConsolidado(id, payload) {
  const r = await api.patch(`/vigilancia/consolidados/${id}/`, payload)
  return r.data.data
}

export async function eliminarConsolidado(id) {
  await api.delete(`/vigilancia/consolidados/${id}/`)
}

export async function exportarConsolidados(params = {}) {
  const r = await api.get("/vigilancia/consolidados/exportar/", { params, responseType: "blob" })
  return r.data
}

export async function listarEpi15(params = {}) {
  const r = await api.get("/vigilancia/epi15/", { params })
  return r.data.data
}

export async function obtenerEpi15(id) {
  const r = await api.get(`/vigilancia/epi15/${id}/`)
  return r.data.data
}

export async function exportarEpi15(params = {}) {
  const r = await api.get("/vigilancia/epi15/exportar/", { params, responseType: "blob" })
  return r.data
}

export async function listarCodificacion(params = {}) {
  const r = await api.get("/registros/codificacion/", { params })
  return r.data
}

export async function consultarCertificado(modulo, numero) {
  const r = await api.get("/registros/consulta/", { params: { modulo, numero } })
  return r.data.data
}

export async function confirmarCodificacion(payload) {
  const r = await api.post("/registros/consulta/confirmar/", payload)
  return r.data.data
}

export async function listarTalonarios(params = {}) {
  const r = await api.get("/despacho/talonarios/", { params })
  return { items: r.data.data, count: r.data.count }
}

export async function crearTalonario(payload) {
  const r = await api.post("/despacho/talonarios/", payload)
  return r.data.data
}

export async function actualizarTalonario(id, payload) {
  const r = await api.patch(`/despacho/talonarios/${id}/`, payload)
  return r.data.data
}

export async function eliminarTalonario(id) {
  await api.delete(`/despacho/talonarios/${id}/`)
}

export async function detalleTalonario(id) {
  const r = await api.get(`/despacho/talonarios/${id}/certificados/`)
  return r.data.data
}

export async function crearNovedad(payload) {
  const r = await api.post("/despacho/novedades/", payload)
  return r.data.data
}

export async function eliminarNovedad(id) {
  await api.delete(`/despacho/novedades/${id}/`)
}

export async function reporteCertificados(params = {}) {
  const r = await api.get("/despacho/reportes/certificados/", { params })
  return r.data.data
}

export async function reportePendientes(params = {}) {
  const r = await api.get("/despacho/reportes/pendientes/", { params })
  return r.data.data
}

export async function exportarDespacho(ruta, params = {}) {
  const r = await api.get(`/despacho/reportes/${ruta}/`, {
    params: { ...params, formato: "csv" },
    responseType: "blob",
  })
  return r.data
}

// -- Registradores civiles (§24.2) ------------------------------------------

export async function listarRegistrosCiviles(params = {}) {
  const r = await api.get("/registradores/registros-civiles/", { params })
  return { items: r.data.data, count: r.data.count }
}

export async function crearRegistroCivil(payload) {
  const r = await api.post("/registradores/registros-civiles/", payload)
  return r.data.data
}

export async function actualizarRegistroCivil(id, payload) {
  const r = await api.patch(`/registradores/registros-civiles/${id}/`, payload)
  return r.data.data
}

export async function eliminarRegistroCivil(id) {
  await api.delete(`/registradores/registros-civiles/${id}/`)
}

export async function listarRegistradores(params = {}) {
  const r = await api.get("/registradores/registradores/", { params })
  return { items: r.data.data, count: r.data.count }
}

export async function crearRegistrador(payload) {
  const r = await api.post("/registradores/registradores/", payload)
  return r.data.data
}

export async function actualizarRegistrador(id, payload) {
  const r = await api.patch(`/registradores/registradores/${id}/`, payload)
  return r.data.data
}

export async function eliminarRegistrador(id) {
  await api.delete(`/registradores/registradores/${id}/`)
}

export async function listarDesignaciones(params = {}) {
  const r = await api.get("/registradores/designaciones/", { params })
  return { items: r.data.data, count: r.data.count }
}

export async function crearDesignacion(payload) {
  const r = await api.post("/registradores/designaciones/", payload)
  return r.data.data
}

export async function actualizarDesignacion(id, payload) {
  const r = await api.patch(`/registradores/designaciones/${id}/`, payload)
  return r.data.data
}

export async function eliminarDesignacion(id) {
  await api.delete(`/registradores/designaciones/${id}/`)
}

export async function quienFirmaba(registroCivil, fecha) {
  const r = await api.get("/registradores/quien-firmaba/", {
    params: { registro_civil: registroCivil, fecha },
  })
  return r.data.data
}
