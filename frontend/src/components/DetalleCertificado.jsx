// Bloques de solo lectura de un certificado ya registrado
// (`presentacion.detalle_certificado`): grupo → campos con su rótulo y valor.
// Lo usan la consulta de codificación y el detalle semanal de MM / MI.
export default function DetalleCertificado({ bloques = [] }) {
  if (!bloques.length) {
    return <p className="ayuda">Este registro no tiene datos que mostrar.</p>
  }
  return (
    <div className="detalle-certificado">
      {bloques.map((b) => (
        <section key={b.grupo} className="seccion">
          <h3>{b.grupo}</h3>
          <dl className="grid-detalle">
            {b.campos.map((c) => (
              <div key={c.campo}>
                <dt>{c.etiqueta}</dt>
                <dd>{c.valor}</dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
    </div>
  )
}
