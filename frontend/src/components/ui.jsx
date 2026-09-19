export function Seccion({ titulo, children }) {
  return (
    <section className="seccion">
      <h2>{titulo}</h2>
      <div className="grid">{children}</div>
    </section>
  )
}

export function Campo({ label, error, children, htmlFor }) {
  return (
    <div className={`campo ${error ? "campo-error" : ""}`}>
      <label htmlFor={htmlFor}>{label}</label>
      {children}
      {error && <span className="error">{error}</span>}
    </div>
  )
}

export function Input({ error, ...props }) {
  return <input {...props} aria-invalid={Boolean(error)} />
}

export function Select({ opciones, ...props }) {
  return (
    <select {...props}>
      <option value="">— Seleccione —</option>
      {opciones.map(([valor, rotulo]) => (
        <option key={valor} value={valor}>
          {rotulo}
        </option>
      ))}
    </select>
  )
}

export function Boton({ children, ...props }) {
  return (
    <button type="submit" className="boton" {...props}>
      {children}
    </button>
  )
}