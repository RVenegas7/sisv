import { useEffect, useState } from "react"
import { actualizarDefuncion, crearDefuncion, eliminarDefuncion, listarDefunciones, obtenerConfiguracion } from "../api/sisv"
import SeccionCIE from "../components/SeccionCIE"
import SelectTerritorial from "../components/SelectTerritorial"
import CentroSelector from "../components/CentroSelector"
import { Boton, Campo, Input, Seccion, Select } from "../components/ui"
import { SELECCION_CIE_VACIA, seleccionDesdeRegistro, useVersionCIE, validarCIE } from "../utils/cie"

const VACIO = {
  registro_numero: "",
  lote_id: "",
  fecha_evento: "",
  hora_defuncion: "",
  fallecido_nombres: "",
  fallecido_apellidos: "",
  fallecido_cedula: "",
  sexo: "",
  fecha_nacimiento: "",
  lugar_defuncion: "ESTABLECIMIENTO",
  establecimiento: "",
  estado: "",
  municipio: "",
  parroquia: "",
  comunidad: "",
  organizacion: null,
  causa_directa: "",
  embarazo_o_puerperio: false,
  autopsia: false,
  embalsamado: false,
  certificador_nombres: "",
  certificador_cedula: "",

  nacionalidad: "",
  segundo_apellido: "",
  segundo_nombre: "",
  edad_ignorada: false,
  lugar_nacimiento: "",
  nacimiento_exterior: false,
  estado_civil: "",
  profesion: "",
  ocupacion_lugar_trabajo: "",
  sabe_leer_escribir: "",
  residencia_habitual: "",
  asistencia_medica: "",

  es_muerte_fetal: false,
  peso_nacer_gramos: "",
  edad_gestacional_semanas: "",
  tipo_embarazo: "",
  tipo_parto: "",
  asistencia_parto: "",
  madre_apellidos: "",
  madre_nombres: "",
  madre_cedula: "",
  madre_numero_gestas: "",
  madre_fecha_ultima_gesta: "",
  madre_embarazada: "",
  madre_puerperio: "",

  manera_de_morir: "",
  fecha_hecho_violento: "",
  hora_hecho_violento: "",
  descripcion_hecho_violento: "",

  causa_antecedentes: "",
  otros_estados_patologicos: "",
  diagnostico_examen_cadaver: false,
  diagnostico_examen_laboratorio: false,
  diagnostico_historia_clinica: false,
  diagnostico_interrogatorio_familiar: false,
  cirugia: false,
  fecha_ultima_cirugia: "",
  descripcion_cirugia: "",
  intervalo_enf_muerte: "",
  correo_contacto: "",
  matricula_mpps: "",

  registro_civil_nombre: "",
  folio_defuncion: "",
  numero_acta_defuncion: "",
  fecha_registro: "",
  declarante_nombres: "",
  declarante_cedula: "",
  registrador_civil_nombres: "",
  registrador_civil_cedula: "",
  gaceta: "",
  resolucion: "",
}

const ANIO_ACTUAL = new Date().getFullYear()
const ANIOS_DISPONIBLES = Array.from({ length: ANIO_ACTUAL - 2018 }, (_, i) => ANIO_ACTUAL - i)

const REQUERIDOS = ["registro_numero", "fecha_evento", "fallecido_nombres", "fallecido_apellidos", "sexo"]

const OPCIONES = {
  SEXO: [
    ["F", "Femenino"],
    ["M", "Masculino"],
    ["I", "Indeterminado"],
  ],
  LUGAR: [
    ["ESTABLECIMIENTO", "Establecimiento de salud"],
    ["DOMICILIO", "Domicilio"],
    ["VIA_PUBLICA", "Vía pública"],
    ["OTRO", "Otro"],
  ],
  NACIONALIDAD: [
    ["", "—"],
    ["V", "Venezolana"],
    ["E", "Extranjera"],
    ["P", "Pasaporte"],
    ["I", "Ignorado"],
    ["O", "Otra"],
  ],
  ESTADO_CIVIL: [
    ["", "—"],
    ["SOLTERO", "Soltero(a)"],
    ["CASADO", "Casado(a)"],
    ["VIUDO", "Viudo(a)"],
    ["DIVORCIADO", "Divorciado(a)"],
    ["UNIDO", "Unido(a)"],
    ["SEPARADO", "Separado(a)"],
  ],
  SI_NO_IGNORADO: [
    ["", "—"],
    ["SI", "Sí"],
    ["NO", "No"],
    ["IGNORADO", "Ignorado"],
  ],
  TIPO_EMBARAZO: [
    ["", "—"],
    ["UNICO", "Único"],
    ["MULTIPLE", "Múltiple"],
  ],
  TIPO_PARTO: [
    ["", "—"],
    ["VAGINAL", "Vaginal"],
    ["CESAREA", "Cesárea"],
    ["INSTRUMENTAL", "Instrumental"],
    ["OTRO", "Otro"],
  ],
  PERIODO_PUERPERIO: [
    ["", "—"],
    ["NIUNA", "No corresponde"],
    ["DENTRO42D", "Dentro de 42 días"],
    ["DENTRO12M", "Dentro de 12 meses"],
    ["IGNORADO", "Ignorado"],
  ],
  MANERA_DE_MORIR: [
    ["", "—"],
    ["ENFERMEDAD", "Enfermedad"],
    ["ACCIDENTE", "Accidente"],
    ["AGRESION", "Agresión"],
    ["AUTOINFLIGIDA", "Autoinfligida"],
    ["NO_DETERMINADA", "No determinada"],
    ["ESTUDIO_FORENSE", "Estudio forense"],
  ],
}

function validar(form, cieVersion, cieSeleccion) {
  const errores = {}
  for (const campo of REQUERIDOS) {
    if (!String(form[campo] ?? "").trim()) {
      errores[campo] = "Campo obligatorio"
    }
  }
  const errorCie = validarCIE(cieVersion, cieSeleccion)
  if (errorCie) errores.cie = errorCie
  return errores
}

function mostrarCIE(r) {
  if (r.cie10_detalle) return `${r.cie10_detalle.codigo} (CIE-10)`
  if (r.cie11_detalle) return `${r.cie11_detalle.codigo} (CIE-11)`
  return "—"
}

export default function CargaDefunciones({ usuario }) {
  const permisos = usuario?.permisos || {}
  const [form, setForm] = useState(VACIO)
  const {
    version: cieVersion,
    setVersion: setCieVersion,
    versionManual,
    setVersionManual,
    seleccion: cieSeleccion,
    setSeleccion: setCieSeleccion,
  } = useVersionCIE(form.fecha_evento)
  const [errores, setErrores] = useState({})
  const [estado, setEstado] = useState({ tipo: "", texto: "" })
  const [lista, setLista] = useState([])
  const [paginacion, setPaginacion] = useState(null)
  const [anioLista, setAnioLista] = useState(ANIO_ACTUAL)
  const [soloPendientes, setSoloPendientes] = useState(false)
  const [editandoId, setEditandoId] = useState(null)

  async function cargarLista(pagina = 1, anio = anioLista, pendientes = soloPendientes) {
    try {
      const resp = await listarDefunciones({
        pagina,
        por_pagina: 100,
        anio,
        ...(pendientes ? { pendientes: 1 } : {}),
      })
      setLista(resp.items)
      setPaginacion(resp.pagination)
      return resp.items
    } catch {
      setLista([])
      setPaginacion(null)
      return []
    }
  }

  useEffect(() => {
    cargarLista()
    obtenerConfiguracion()
      .then((cfg) => {
        if (cfg.estado || cfg.municipio || cfg.parroquia || cfg.establecimiento) {
          setForm((f) => ({
            ...f,
            estado: cfg.estado || "",
            municipio: cfg.municipio || "",
            parroquia: cfg.parroquia || "",
            establecimiento: cfg.establecimiento || "",
          }))
        }
        if (cfg.organizacion_activa) {
          setForm((f) => ({ ...f, organizacion: cfg.organizacion_activa }))
        }
      })
      .catch(() => {})
  }, [])

  function cambiar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }))
  }

  function cancelarEdicion() {
    setEditandoId(null)
    setForm(VACIO)
    setErrores({})
    setEstado({ tipo: "", texto: "" })
    setCieSeleccion(SELECCION_CIE_VACIA)
    setCieVersion("CIE11")
    setVersionManual(false)
  }

  async function cargarEdicion(reg) {
    setForm({ ...VACIO, ...reg })
    setEditandoId(reg.id)
    setErrores({})
    setEstado({ tipo: "info", texto: `Editando certificado #${reg.id}.` })
    setCieVersion(reg.version_cie || "CIE11")
    setVersionManual(true)
    setCieSeleccion(await seleccionDesdeRegistro(reg))
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  async function borrar(reg) {
    if (!window.confirm(`¿Eliminar el certificado #${reg.id} (${reg.registro_numero})?`)) return
    try {
      await eliminarDefuncion(reg.id)
      if (lista.length === 1 && paginacion?.pagina > 1) {
        await cargarLista(paginacion.pagina - 1)
      } else {
        await cargarLista(paginacion?.pagina || 1)
      }
      setEstado({ tipo: "ok", texto: `Certificado #${reg.id} eliminado.` })
    } catch (err) {
      setEstado({ tipo: "error", texto: err.message })
    }
  }

  async function enviar(e) {
    e.preventDefault()
    const erroresForm = validar(form, cieVersion, cieSeleccion)
    setErrores(erroresForm)
    if (Object.keys(erroresForm).length) {
      setEstado({ tipo: "error", texto: "Corrija los campos marcados en rojo." })
      return
    }
    setEstado({ tipo: "info", texto: "Enviando registro…" })
    try {
      const payload = {
        ...form,
        version_cie: cieVersion,
        organizacion:
          usuario?.organizacion?.nivel === "CENTRO" ? usuario.organizacion.id : form.organizacion ?? null,
        cie10: cieVersion === "CIE10" ? cieSeleccion.cie10.id : null,
        cie11: cieVersion === "CIE11" ? cieSeleccion.cie11.id : null,
        cie10_detalle: cieVersion === "CIE10" ? cieSeleccion.cie10 : null,
        cie11_detalle: cieVersion === "CIE11" ? cieSeleccion.cie11 : null,
      }
      if (editandoId) {
        await actualizarDefuncion(editandoId, payload)
        setEstado({ tipo: "ok", texto: `Certificado #${editandoId} actualizado.` })
      } else {
        const creado = await crearDefuncion(payload)
        setEstado({ tipo: "ok", texto: `Certificado creado: ${creado.registro_numero} #${creado.id}` })
      }
      setLista(await cargarLista(paginacion?.pagina || 1))
      cancelarEdicion()
    } catch (err) {
      setEstado({ tipo: "error", texto: err.message })
    }
  }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <h1>Registro de Defunciones</h1>
        <p>Certificado de Defunción (EV-14) - SISV. La causa básica se clasifica contra CIE-10 (histórico) o CIE-11 (actual) según la fecha.</p>
      </header>

      {estado.tipo && (
        <div className={`aviso aviso-${estado.tipo}`} role="status">
          {estado.texto}
        </div>
      )}

      {editandoId && (
        <div className="aviso aviso-editando">
          Editando el certificado de defunción <strong>#{editandoId}</strong>.
          <button type="button" className="btn-mini" onClick={cancelarEdicion}>
            Cancelar edición
          </button>
        </div>
      )}

      <form className="formulario" onSubmit={enviar} noValidate>
        {!permisos.puede_escribir && (
          <div className="aviso aviso-info">
            Su rol (<strong>{usuario?.rol_label}</strong>) es de solo lectura: no está habilitada la carga de certificados.
          </div>
        )}
        <fieldset disabled={!permisos.puede_escribir}>
        <Seccion titulo="1. Certificado de defunción">
          <Campo label="Nº de certificado" htmlFor="registro_numero" error={errores.registro_numero}>
            <Input
              id="registro_numero"
              value={form.registro_numero}
              error={errores.registro_numero}
              onChange={(e) => cambiar("registro_numero", e.target.value)}
              placeholder="DEF-YYYY-XXXXXX"
            />
          </Campo>
          <Campo label="Lote de carga (opcional)" htmlFor="lote_id">
            <Input id="lote_id" value={form.lote_id} onChange={(e) => cambiar("lote_id", e.target.value)} />
          </Campo>
          <Campo label="Fecha de defunción" htmlFor="fecha_evento" error={errores.fecha_evento}>
            <Input
              id="fecha_evento"
              type="date"
              value={form.fecha_evento}
              error={errores.fecha_evento}
              onChange={(e) => cambiar("fecha_evento", e.target.value)}
            />
          </Campo>
          <Campo label="Hora" htmlFor="hora_defuncion">
            <Input id="hora_defuncion" type="time" value={form.hora_defuncion} onChange={(e) => cambiar("hora_defuncion", e.target.value)} />
          </Campo>
          <Campo label="Lugar de defunción" htmlFor="lugar_defuncion">
            <Select id="lugar_defuncion" opciones={OPCIONES.LUGAR} value={form.lugar_defuncion} onChange={(e) => cambiar("lugar_defuncion", e.target.value)} />
          </Campo>
          <Campo label="Establecimiento" htmlFor="establecimiento">
            <Input id="establecimiento" value={form.establecimiento} onChange={(e) => cambiar("establecimiento", e.target.value)} />
          </Campo>
          <SelectTerritorial
            valor={{ estado: form.estado, municipio: form.municipio, parroquia: form.parroquia, comunidad: form.comunidad }}
            onChange={(t) => setForm((f) => ({ ...f, ...t }))}
          />
        </Seccion>

        <Seccion titulo="2. Sección I — Identificación del fallecido(a)">
          <Campo label="Primer nombre" htmlFor="fallecido_nombres" error={errores.fallecido_nombres}>
            <Input id="fallecido_nombres" value={form.fallecido_nombres} error={errores.fallecido_nombres} onChange={(e) => cambiar("fallecido_nombres", e.target.value)} />
          </Campo>
          <Campo label="Segundo nombre" htmlFor="segundo_nombre">
            <Input id="segundo_nombre" value={form.segundo_nombre} onChange={(e) => cambiar("segundo_nombre", e.target.value)} />
          </Campo>
          <Campo label="Primer apellido" htmlFor="fallecido_apellidos" error={errores.fallecido_apellidos}>
            <Input id="fallecido_apellidos" value={form.fallecido_apellidos} error={errores.fallecido_apellidos} onChange={(e) => cambiar("fallecido_apellidos", e.target.value)} />
          </Campo>
          <Campo label="Segundo apellido" htmlFor="segundo_apellido">
            <Input id="segundo_apellido" value={form.segundo_apellido} onChange={(e) => cambiar("segundo_apellido", e.target.value)} />
          </Campo>
          <Campo label="Nacionalidad" htmlFor="nacionalidad">
            <Select id="nacionalidad" opciones={OPCIONES.NACIONALIDAD} value={form.nacionalidad} onChange={(e) => cambiar("nacionalidad", e.target.value)} />
          </Campo>
          <Campo label="Cédula / documento (opcional)" htmlFor="fallecido_cedula">
            <Input id="fallecido_cedula" value={form.fallecido_cedula} onChange={(e) => cambiar("fallecido_cedula", e.target.value)} placeholder="V-12345678" />
          </Campo>
          <Campo label="Sexo" htmlFor="sexo" error={errores.sexo}>
            <Select id="sexo" opciones={OPCIONES.SEXO} value={form.sexo} onChange={(e) => cambiar("sexo", e.target.value)} />
          </Campo>
          <Campo label="Fecha de nacimiento" htmlFor="fecha_nacimiento">
            <Input id="fecha_nacimiento" type="date" value={form.fecha_nacimiento} onChange={(e) => cambiar("fecha_nacimiento", e.target.value)} />
          </Campo>
          <label className="checkbox">
            <input type="checkbox" checked={form.edad_ignorada} onChange={(e) => cambiar("edad_ignorada", e.target.checked)} />
            Edad ignorada
          </label>
          <Campo label="Lugar de nacimiento" htmlFor="lugar_nacimiento">
            <Input id="lugar_nacimiento" value={form.lugar_nacimiento} onChange={(e) => cambiar("lugar_nacimiento", e.target.value)} />
          </Campo>
          <label className="checkbox">
            <input type="checkbox" checked={form.nacimiento_exterior} onChange={(e) => cambiar("nacimiento_exterior", e.target.checked)} />
            Nacimiento en el exterior
          </label>
          <Campo label="Estado civil" htmlFor="estado_civil">
            <Select id="estado_civil" opciones={OPCIONES.ESTADO_CIVIL} value={form.estado_civil} onChange={(e) => cambiar("estado_civil", e.target.value)} />
          </Campo>
          <Campo label="Profesión" htmlFor="profesion">
            <Input id="profesion" value={form.profesion} onChange={(e) => cambiar("profesion", e.target.value)} />
          </Campo>
          <Campo label="Ocupación y lugar de trabajo" htmlFor="ocupacion_lugar_trabajo">
            <Input id="ocupacion_lugar_trabajo" value={form.ocupacion_lugar_trabajo} onChange={(e) => cambiar("ocupacion_lugar_trabajo", e.target.value)} />
          </Campo>
          <Campo label="Sabe leer y escribir" htmlFor="sabe_leer_escribir">
            <Select id="sabe_leer_escribir" opciones={OPCIONES.SI_NO_IGNORADO} value={form.sabe_leer_escribir} onChange={(e) => cambiar("sabe_leer_escribir", e.target.value)} />
          </Campo>
          <Campo label="Dirección de residencia habitual" htmlFor="residencia_habitual">
            <Input id="residencia_habitual" value={form.residencia_habitual} onChange={(e) => cambiar("residencia_habitual", e.target.value)} />
          </Campo>
          <Campo label="Asistencia médica" htmlFor="asistencia_medica">
            <Select id="asistencia_medica" opciones={OPCIONES.SI_NO_IGNORADO} value={form.asistencia_medica} onChange={(e) => cambiar("asistencia_medica", e.target.value)} />
          </Campo>
          <CentroSelector usuario={usuario} value={form.organizacion} onChange={(v) => cambiar("organizacion", v)} />
        </Seccion>

        <Seccion titulo="3. Sección II — Menores de un año, muerte fetal y datos de la madre">
          <label className="checkbox">
            <input type="checkbox" checked={form.es_muerte_fetal} onChange={(e) => cambiar("es_muerte_fetal", e.target.checked)} />
            Es muerte fetal
          </label>
          <Campo label="Peso al nacer (g)" htmlFor="peso_nacer_gramos">
            <Input id="peso_nacer_gramos" type="number" min="0" value={form.peso_nacer_gramos} onChange={(e) => cambiar("peso_nacer_gramos", e.target.value)} />
          </Campo>
          <Campo label="Semanas de gestación" htmlFor="edad_gestacional_semanas">
            <Input id="edad_gestacional_semanas" type="number" min="0" max="45" value={form.edad_gestacional_semanas} onChange={(e) => cambiar("edad_gestacional_semanas", e.target.value)} />
          </Campo>
          <Campo label="Tipo de embarazo" htmlFor="tipo_embarazo">
            <Select id="tipo_embarazo" opciones={OPCIONES.TIPO_EMBARAZO} value={form.tipo_embarazo} onChange={(e) => cambiar("tipo_embarazo", e.target.value)} />
          </Campo>
          <Campo label="Tipo de parto" htmlFor="tipo_parto">
            <Select id="tipo_parto" opciones={OPCIONES.TIPO_PARTO} value={form.tipo_parto} onChange={(e) => cambiar("tipo_parto", e.target.value)} />
          </Campo>
          <Campo label="Asistencia del parto" htmlFor="asistencia_parto">
            <Input id="asistencia_parto" value={form.asistencia_parto} onChange={(e) => cambiar("asistencia_parto", e.target.value)} placeholder="Médico, enfermera, partera…" />
          </Campo>
          <h3 className="subseccion">Datos de la madre</h3>
          <Campo label="Apellidos de la madre" htmlFor="madre_apellidos">
            <Input id="madre_apellidos" value={form.madre_apellidos} onChange={(e) => cambiar("madre_apellidos", e.target.value)} />
          </Campo>
          <Campo label="Nombres de la madre" htmlFor="madre_nombres">
            <Input id="madre_nombres" value={form.madre_nombres} onChange={(e) => cambiar("madre_nombres", e.target.value)} />
          </Campo>
          <Campo label="Cédula de la madre" htmlFor="madre_cedula">
            <Input id="madre_cedula" value={form.madre_cedula} onChange={(e) => cambiar("madre_cedula", e.target.value)} />
          </Campo>
          <Campo label="Número de gestas" htmlFor="madre_numero_gestas">
            <Input id="madre_numero_gestas" type="number" min="0" value={form.madre_numero_gestas} onChange={(e) => cambiar("madre_numero_gestas", e.target.value)} />
          </Campo>
          <Campo label="Fecha de la última gesta" htmlFor="madre_fecha_ultima_gesta">
            <Input id="madre_fecha_ultima_gesta" type="date" value={form.madre_fecha_ultima_gesta} onChange={(e) => cambiar("madre_fecha_ultima_gesta", e.target.value)} />
          </Campo>
          <Campo label="Estaba embarazada" htmlFor="madre_embarazada">
            <Select id="madre_embarazada" opciones={OPCIONES.SI_NO_IGNORADO} value={form.madre_embarazada} onChange={(e) => cambiar("madre_embarazada", e.target.value)} />
          </Campo>
          <Campo label="En puerperio de" htmlFor="madre_puerperio">
            <Select id="madre_puerperio" opciones={OPCIONES.PERIODO_PUERPERIO} value={form.madre_puerperio} onChange={(e) => cambiar("madre_puerperio", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="4. Sección V — Muerte violenta">
          <Campo label="Manera de morir" htmlFor="manera_de_morir">
            <Select id="manera_de_morir" opciones={OPCIONES.MANERA_DE_MORIR} value={form.manera_de_morir} onChange={(e) => cambiar("manera_de_morir", e.target.value)} />
          </Campo>
          <Campo label="Fecha del hecho violento" htmlFor="fecha_hecho_violento">
            <Input id="fecha_hecho_violento" type="date" value={form.fecha_hecho_violento} onChange={(e) => cambiar("fecha_hecho_violento", e.target.value)} />
          </Campo>
          <Campo label="Hora del hecho violento" htmlFor="hora_hecho_violento">
            <Input id="hora_hecho_violento" type="time" value={form.hora_hecho_violento} onChange={(e) => cambiar("hora_hecho_violento", e.target.value)} />
          </Campo>
          <Campo label="Breve descripción del hecho violento" htmlFor="descripcion_hecho_violento">
            <Input id="descripcion_hecho_violento" value={form.descripcion_hecho_violento} onChange={(e) => cambiar("descripcion_hecho_violento", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="5. Sección VI — Certificación médica">
          <Campo label="Causa inmediata (línea a)" htmlFor="causa_directa">
            <Input id="causa_directa" value={form.causa_directa} onChange={(e) => cambiar("causa_directa", e.target.value)} />
          </Campo>
          <Campo label="Causas antecedentes (línea b, c, d)" htmlFor="causa_antecedentes">
            <Input id="causa_antecedentes" value={form.causa_antecedentes} onChange={(e) => cambiar("causa_antecedentes", e.target.value)} />
          </Campo>
          <Campo label="Otros estados patológicos" htmlFor="otros_estados_patologicos">
            <Input id="otros_estados_patologicos" value={form.otros_estados_patologicos} onChange={(e) => cambiar("otros_estados_patologicos", e.target.value)} />
          </Campo>
          <Campo label="Intervalo entre inicio y muerte" htmlFor="intervalo_enf_muerte">
            <Input id="intervalo_enf_muerte" value={form.intervalo_enf_muerte} onChange={(e) => cambiar("intervalo_enf_muerte", e.target.value)} placeholder="Ej.: años, meses, días, horas" />
          </Campo>
          <label className="checkbox">
            <input type="checkbox" checked={form.embarazo_o_puerperio} onChange={(e) => cambiar("embarazo_o_puerperio", e.target.checked)} />
            Defunción materna (embarazo/puerperio)
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.autopsia} onChange={(e) => cambiar("autopsia", e.target.checked)} />
            Se realizó autopsia
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.embalsamado} onChange={(e) => cambiar("embalsamado", e.target.checked)} />
            Embalsamado
          </label>
          <h3 className="subseccion">Diagnóstico confirmado por</h3>
          <label className="checkbox">
            <input type="checkbox" checked={form.diagnostico_examen_cadaver} onChange={(e) => cambiar("diagnostico_examen_cadaver", e.target.checked)} />
            Examen del cadáver
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.diagnostico_examen_laboratorio} onChange={(e) => cambiar("diagnostico_examen_laboratorio", e.target.checked)} />
            Examen de laboratorio
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.diagnostico_historia_clinica} onChange={(e) => cambiar("diagnostico_historia_clinica", e.target.checked)} />
            Historia clínica
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.diagnostico_interrogatorio_familiar} onChange={(e) => cambiar("diagnostico_interrogatorio_familiar", e.target.checked)} />
            Interrogatorio familiar o testigo
          </label>
          <h3 className="subseccion">Cirugía</h3>
          <label className="checkbox">
            <input type="checkbox" checked={form.cirugia} onChange={(e) => cambiar("cirugia", e.target.checked)} />
            Tuvo alguna cirugía
          </label>
          <Campo label="Fecha de la última cirugía" htmlFor="fecha_ultima_cirugia">
            <Input id="fecha_ultima_cirugia" type="date" value={form.fecha_ultima_cirugia} onChange={(e) => cambiar("fecha_ultima_cirugia", e.target.value)} />
          </Campo>
          <Campo label="Breve descripción de la cirugía" htmlFor="descripcion_cirugia">
            <Input id="descripcion_cirugia" value={form.descripcion_cirugia} onChange={(e) => cambiar("descripcion_cirugia", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="6. Médico certificador">
          <Campo label="Apellidos y nombres del médico responsable" htmlFor="certificador_nombres">
            <Input id="certificador_nombres" value={form.certificador_nombres} onChange={(e) => cambiar("certificador_nombres", e.target.value)} />
          </Campo>
          <Campo label="Cédula" htmlFor="certificador_cedula">
            <Input id="certificador_cedula" value={form.certificador_cedula} onChange={(e) => cambiar("certificador_cedula", e.target.value)} />
          </Campo>
          <Campo label="Matrícula MPPS" htmlFor="matricula_mpps">
            <Input id="matricula_mpps" value={form.matricula_mpps} onChange={(e) => cambiar("matricula_mpps", e.target.value)} />
          </Campo>
          <Campo label="Correo electrónico de contacto" htmlFor="correo_contacto">
            <Input id="correo_contacto" type="email" value={form.correo_contacto} onChange={(e) => cambiar("correo_contacto", e.target.value)} />
          </Campo>
        </Seccion>

        <Seccion titulo="7. Sección VII — Registro civil">
          <Campo label="Nombre del registro civil" htmlFor="registro_civil_nombre">
            <Input id="registro_civil_nombre" value={form.registro_civil_nombre} onChange={(e) => cambiar("registro_civil_nombre", e.target.value)} />
          </Campo>
          <Campo label="Número del acta de defunción" htmlFor="numero_acta_defuncion">
            <Input id="numero_acta_defuncion" value={form.numero_acta_defuncion} onChange={(e) => cambiar("numero_acta_defuncion", e.target.value)} />
          </Campo>
          <Campo label="Folio del acta" htmlFor="folio_defuncion">
            <Input id="folio_defuncion" value={form.folio_defuncion} onChange={(e) => cambiar("folio_defuncion", e.target.value)} />
          </Campo>
          <Campo label="Fecha de registro" htmlFor="fecha_registro">
            <Input id="fecha_registro" type="date" value={form.fecha_registro} onChange={(e) => cambiar("fecha_registro", e.target.value)} />
          </Campo>
          <Campo label="Declarante (apellidos y nombres)" htmlFor="declarante_nombres">
            <Input id="declarante_nombres" value={form.declarante_nombres} onChange={(e) => cambiar("declarante_nombres", e.target.value)} />
          </Campo>
          <Campo label="Cédula del declarante" htmlFor="declarante_cedula">
            <Input id="declarante_cedula" value={form.declarante_cedula} onChange={(e) => cambiar("declarante_cedula", e.target.value)} />
          </Campo>
          <Campo label="Registrador civil (apellidos y nombres)" htmlFor="registrador_civil_nombres">
            <Input id="registrador_civil_nombres" value={form.registrador_civil_nombres} onChange={(e) => cambiar("registrador_civil_nombres", e.target.value)} />
          </Campo>
          <Campo label="Cédula del registrador civil" htmlFor="registrador_civil_cedula">
            <Input id="registrador_civil_cedula" value={form.registrador_civil_cedula} onChange={(e) => cambiar("registrador_civil_cedula", e.target.value)} />
          </Campo>
          <Campo label="Gaceta" htmlFor="gaceta">
            <Input id="gaceta" value={form.gaceta} onChange={(e) => cambiar("gaceta", e.target.value)} />
          </Campo>
          <Campo label="Resolución" htmlFor="resolucion">
            <Input id="resolucion" value={form.resolucion} onChange={(e) => cambiar("resolucion", e.target.value)} />
          </Campo>
        </Seccion>

        <SeccionCIE
          titulo="8. Clasificación CIE (causa básica de defunción)"
          etiqueta="Causa de defunción"
          fechaEvento={form.fecha_evento}
          version={cieVersion}
          setVersion={setCieVersion}
          versionManual={versionManual}
          setVersionManual={setVersionManual}
          seleccion={cieSeleccion}
          setSeleccion={setCieSeleccion}
          error={errores.cie}
        />

        </fieldset>

        <div className="pie-form">
          <Boton disabled={!permisos.puede_escribir}>{editandoId ? "Guardar cambios del certificado" : "Guardar certificado de defunción"}</Boton>
        </div>
      </form>

      <section className="lista">
        <div className="cabecera-lista">
          <h2>Certificados registrados</h2>
          <div className="selector-anio">
            <label className="caja">
              <input
                type="checkbox"
                checked={soloPendientes}
                onChange={(e) => {
                  const v = e.target.checked
                  setSoloPendientes(v)
                  cargarLista(1, anioLista, v)
                }}
              />
              Solo pendientes de codificación ({paginacion?.total ?? lista.length})
            </label>
            <label htmlFor="anio-defunciones">Año</label>
            <select
              id="anio-defunciones"
              value={anioLista}
              onChange={(e) => {
                const v = e.target.value === "todos" ? "todos" : Number(e.target.value)
                setAnioLista(v)
                cargarLista(1, v)
              }}
            >
              {ANIOS_DISPONIBLES.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
              <option value="todos">Todos los años</option>
            </select>
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Nº</th>
              <th>Fecha</th>
              <th>Fallecido</th>
              <th>Sexo</th>
              <th>Lugar</th>
              <th>Municipio</th>
              <th>CIE</th>
              <th>Centro</th>
              <th>Codificación</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {lista.map((r) => (
              <tr key={r.id}>
                <td>{r.registro_numero}</td>
                <td>{r.fecha_evento}</td>
                <td>{r.fallecido_nombres} {r.fallecido_apellidos}</td>
                <td>{r.sexo}</td>
                <td>{r.lugar_defuncion}</td>
                <td>{r.municipio || "—"}</td>
                <td>{mostrarCIE(r)}</td>
                <td>{r.organizacion_nombre || "—"}</td>
                <td>
                  {r.codificacion_pendiente ? <span className="etiqueta">Pendiente</span> : <span>OK</span>}
                </td>
                <td className="acciones">
                  {permisos.puede_editar && (
                    <button type="button" className="btn-mini" onClick={() => cargarEdicion(r)}>
                      Editar
                    </button>
                  )}
                  {permisos.puede_eliminar && (
                    <button type="button" className="btn-mini peligro" onClick={() => borrar(r)}>
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {paginacion && (
          <div className="paginacion">
            <button
              type="button"
              className="btn-mini"
              disabled={paginacion.pagina <= 1}
              onClick={() => cargarLista(paginacion.pagina - 1)}
            >
              ‹ Anterior
            </button>
            <span>
              Página {paginacion.pagina} de {paginacion.paginas}
            </span>
            <button
              type="button"
              className="btn-mini"
              disabled={paginacion.pagina >= paginacion.paginas}
              onClick={() => cargarLista(paginacion.pagina + 1)}
            >
              Siguiente ›
            </button>
          </div>
        )}
      </section>
    </div>
  )
}