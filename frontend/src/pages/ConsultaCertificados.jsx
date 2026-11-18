import { useState } from "react"
import { consultarCertificado } from "../api/sisv"
import DetalleCertificado from "../components/DetalleCertificado"
import { Boton, Campo, Input } from "../components/ui"

// Consulta de certificados en solo lectura (§49): validar un nacimiento o una
// defunción con el papel en la mano, sin entrar al espacio de codificación.
// Acepta el Nº impreso (MSDS / planilla), el Nº de registro completo
// (`LEG-CERT-998706314`) o su final numérico (`998706314`).

const MODULOS = [
  ["defunciones", "Defunciones"],
  ["nacimientos", "Nacimientos"],
]

function persona(modulo, r = {}) {
  if (modulo === "nacimientos") {
    return `Madre: ${`${r.madre_nombres || ""} ${r.madre_apellidos || ""}`.trim() || "sin nombre"}`
  }
  return `${r.fallecido_nombres || ""} ${r.fallecido_apellidos || ""}`.trim() || "Sin nombre"
}

export default function ConsultaCertificados() {
  const [modulo, setModulo] = useState("defunciones")
  const [numero, setNumero] = useState("")
  const [consulta, setConsulta] = useState(null)
  const [estado, setEstado] = useState({ tipo: "", texto: "" })

  function aviso(tipo, texto) {
    setEstado({ tipo, texto })
  }

  function cambiarModulo(m) {
    setModulo(m)
    setConsulta(null)
    aviso("", "")
  }

  function mostrar(data) {
    setConsulta(data)
    setNumero(data.numero_fisico || data.numero || "")
    aviso("", "")
  }

  async function consultar() {
    const valor = numero.trim()
    if (!valor) {
      aviso("error", "Escriba el Nº impreso o el Nº de registro del certificado.")
      return
    }
    aviso("info", "Consultando certificado…")
    try {
      mostrar(await consultarCertificado(modulo, valor))
    } catch (err) {
      setConsulta(null)
      aviso("error", err.message)
    }
  }

  async function abrirCandidato(c) {
    aviso("info", `Abriendo ${c.registro_numero}…`)
    try {
      mostrar(await consultarCertificado(modulo, "", c.id))
    } catch (err) {
      setConsulta(null)
      aviso("error", err.message)
    }
  }

  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <div>
          <h1>Consulta de certificados</h1>
          <p className="ayuda">
            Busque un nacimiento o una defunción para <strong>validar la información</strong> contra
            el papel. Acepta el Nº impreso (MSDS o planilla), el Nº de registro completo
            (<code>LEG-CERT-998706314</code>) o solo su final numérico (<code>998706314</code>, 8
            dígitos o más). Es de solo lectura y respeta el alcance de su usuario.
          </p>
        </div>
      </header>

      <div className="filas-campo" style={{ marginBottom: "0.8rem" }}>
        {MODULOS.map(([k, r]) => (
          <button
            key={k}
            type="button"
            className={`btn-mini ${modulo === k ? "activo" : ""}`}
            onClick={() => cambiarModulo(k)}
          >
            {r}
          </button>
        ))}
      </div>

      <div className="formulario">
        <div className="grid">
          <Campo label="Nº impreso (MSDS/planilla) o Nº de registro" htmlFor="consulta-num">
            <Input
              id="consulta-num"
              value={numero}
              onChange={(e) => setNumero(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  consultar()
                }
              }}
              placeholder={
                modulo === "nacimientos"
                  ? "Ej. 12330398 (planilla), LEG-RN-999772242 o 999772242"
                  : "Ej. 4959776010 (MSDS), LEG-CERT-998706314 o 998706314"
              }
            />
          </Campo>
        </div>
        <div className="pie-form">
          <Boton type="button" onClick={consultar}>
            Consultar
          </Boton>
          {consulta && (
            <button
              type="button"
              className="btn-mini"
              onClick={() => {
                setConsulta(null)
                setNumero("")
                aviso("", "")
              }}
            >
              Cerrar consulta
            </button>
          )}
        </div>
      </div>

      {estado.tipo && (
        <div className={`aviso aviso-${estado.tipo}`} role="status">
          {estado.texto}
        </div>
      )}

      {consulta && (
        <section className="panel" style={{ marginTop: "1rem" }}>
          <header className="cabecera-seccion">
            <h2>
              {consulta.numero_fisico || consulta.numero} — {persona(modulo, consulta.registro)}
            </h2>
            <p className="ayuda" style={{ margin: 0 }}>
              Evento: {consulta.registro?.fecha_evento || "—"} ·{" "}
              {consulta.registro?.organizacion_nombre || "Sin organización"}
            </p>
            <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
              Nº impreso (MSDS/planilla):{" "}
              <strong>{consulta.numero_fisico || "—"}</strong> · Nº de registro:{" "}
              <strong>{consulta.numero}</strong>
            </p>
            {consulta.numero_origen === "fisico" && consulta.coincidencias === 1 && (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                Encontrado por el número impreso del certificado.
              </p>
            )}
            {consulta.numero_origen === "registro" && (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                Encontrado por el Nº de registro completo.
              </p>
            )}
            {consulta.numero_origen === "registro_sufijo" && consulta.coincidencias === 1 && (
              <p className="ayuda" style={{ margin: "0.2rem 0 0" }}>
                Encontrado por el final del Nº de registro.
              </p>
            )}
            {consulta.aviso && (
              <div className="aviso aviso-info" role="status" style={{ marginTop: "0.5rem" }}>
                {consulta.aviso}
                {(consulta.candidatos || []).length > 0 && (
                  <>
                    <p className="ayuda" style={{ margin: "0.4rem 0 0" }}>
                      Abra el certificado correcto:
                    </p>
                    <ul style={{ margin: "0.2rem 0 0 1rem" }}>
                      {consulta.candidatos.map((c) => (
                        <li key={c.id}>
                          <button
                            type="button"
                            className="btn-mini"
                            onClick={() => abrirCandidato(c)}
                            title="Abrir este certificado"
                          >
                            {c.fecha_evento} · {c.organizacion_nombre || "Sin centro"} ·{" "}
                            <span className="ayuda">{c.registro_numero}</span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
          </header>

          <DetalleCertificado bloques={consulta.detalle} />
        </section>
      )}
    </div>
  )
}
