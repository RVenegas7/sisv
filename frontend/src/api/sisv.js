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