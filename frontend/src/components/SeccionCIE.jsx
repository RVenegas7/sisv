import CIESearch from "./CIESearch"
import { Campo, Select } from "./ui"
import { versionParaFecha } from "../constants"

export default function SeccionCIE({
  titulo = "Clasificación CIE",
  etiqueta = "Código CIE",
  requerido = true,
  fechaEvento,
  version,
  setVersion,
  versionManual,
  setVersionManual,
  seleccion,
  setSeleccion,
  error,
}) {
  const autoVersion = versionParaFecha(fechaEvento)
  return (
    <section className="seccion">
      <h2>{titulo}</h2>
      <div className="grid">
        <Campo label="Versión del catálogo" htmlFor="version_cie">
          <Select
            id="version_cie"
            opciones={[
              ["CIE11", "CIE-11 (catálogo actual)"],
              ["CIE10", "CIE-10 (histórico, antes de 2022)"],
            ]}
            value={version}
            onChange={(e) => {
              setVersion(e.target.value)
              setVersionManual(true)
              setSeleccion({ cie10: null, cie11: null, subgrupo: null })
            }}
          />
        </Campo>
      </div>
      <p className="ayuda">
        Según la fecha del evento{" "}
        {fechaEvento ? (
          <strong>
            {autoVersion === "CIE10" ? "se exige CIE-10" : "opera con CIE-11"}
            {versionManual && autoVersion !== version ? " (hay selección manual distinta)" : ""}
          </strong>
        ) : (
          "se sugiere la versión automáticamente"
        )}
        .
      </p>
      <div className="campo-cie">
        <label>
          {etiqueta} {requerido && <em className="requerido">(obligatorio)</em>}
        </label>
        <CIESearch version={version} valor={seleccion} onChange={setSeleccion} id="cie_search" />
        {requerido && <span className="obligatorio-ayuda">La selección debe completarse antes de enviar.</span>}
        {error && <span className="error">{error}</span>}
      </div>
    </section>
  )
}