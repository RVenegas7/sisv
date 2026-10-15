# Requerimiento — Lista oficial de registros civiles y registradores (estado Lara)

Documento para **pedir a la oficina** el listado de las oficinas de registro civil y de las
personas que han estado a su cargo. Acompaña la plantilla
[`plantillas/registros_civiles_plantilla.xlsx`](plantillas/registros_civiles_plantilla.xlsx)
(y su generador: `migracion/plantilla_registros_civiles.py`).

---

## 1. Por qué se pide

El sistema anterior (SISMAI) guardó **quién firmaba** cada certificado —el nombre y la cédula del
registrador en `CERTIFICADO.NOMREGISTRADOR` (167.447 defunciones) y del jefe civil en
`CERTNACIMIENTO.JEFECIVIL` (110.848 nacimientos)—, pero **nunca** guardó **la oficina** de registro
civil ni la **vigencia** del cargo. Se buscó en los cuatro esquemas del legacy: no hay ninguna
columna con juzgado, notaría, municipio de la oficina ni fecha de nombramiento; solo la persona.

Ya se recuperó todo lo que el legacy tenía:

| Origen | Filas | Personas |
| --- | --- | --- |
| Defunciones (`CERTIFICADO`) | 167.447 | 3.857 |
| Nacimientos (`CERTNACIMIENTO.JEFECIVIL`) | 110.848 | +233 |
| **Catálogo actual** | — | **4.090 registradores** |

Con eso SISV sabe *quién* firmaba, pero **no dónde ni desde/hasta cuándo**. Por eso el módulo
`/registradores` está vacío en su parte principal: **0 oficinas y 0 designaciones**. Es la única
pieza que no se puede deducir de la base y que solo la oficina puede entregar.

**Para qué sirve una vez cargada:**

- Responder «**¿quién firmaba el registro civil de esta parroquia en marzo de 2019?**».
- Que la tabla de `/registradores` muestre, por oficina, **cuántos registradores** ha tenido, el
  **vigente** y el detalle de los **cesantes** (historial).
- Cruzar los certificados con la oficina que los expidió (control de talonarios y series).

---

## 2. Qué se solicita

Un archivo **Excel**, con tres hojas (se envía la plantilla ya armada):

| Hoja | Contenido | Filas esperadas |
| --- | --- | --- |
| `1-Registros civiles` | Las **oficinas** (una fila por oficina) | ≈57+ (Lara) |
| `2-Registradores` | Las **personas** que ejercen o ejercieron (una fila por persona) | ≈400–800 |
| `3-Designaciones` | **Quién estuvo en qué oficina y cuándo** (una fila por periodo) | ≈57–600 |

Las tres hojas son necesarias: la 1 sin la 3 no dice quién atendía la oficina, y la 2 sin la 3 no
dice en cuál.

---

## 3. Especificación de columnas

Los encabezados de la plantilla **no se deben borrar ni renombrar** (el importador lee las columnas
por su encabezado y el orden puede cambiar). El `*` marca lo obligatorio.

### Hoja 1 — `1-Registros civiles`

| Columna | Oblig. | Formato | Ejemplo | Campo en SISV |
| --- | :-: | --- | --- | --- |
| Nombre del registro civil | sí | texto único | `Registro Civil Parroquia Concepción` | `RegistroCivil.nombre` |
| Estado | sí | texto | `Lara` | `.estado` |
| Municipio | sí | texto | `Iribarren` | `.municipio` |
| Parroquia | sí | texto | `Concepción` | `.parroquia` |
| Centro de salud adscrito | no | nombre del centro | `Hospital Central de Barquisimeto` | `.organizacion` (se busca por nombre entre los 421 centros; si no coincide, se deja vacío) |
| Activo | sí | `Sí` / `No` | `Sí` | `.activo` |
| Observaciones | no | texto libre | `Atiende también la parroquia Santa Rosa` | `.observaciones` |

### Hoja 2 — `2-Registradores`

| Columna | Oblig. | Formato | Ejemplo | Campo en SISV |
| --- | :-: | --- | --- | --- |
| Nacionalidad | sí | `V` `E` `P` `I` `O` | `V` | `RegistradorCivil.nacionalidad` |
| Cédula | sí | **solo dígitos**, sin puntos ni letra | `7449239` | `.cedula` |
| Nombres | sí | texto | `NELIDA` | `.nombres` |
| Apellidos | sí | texto | `ESPINOZA` | `.apellidos` |
| Teléfono | no | texto | `0251-1234567` | `.telefono` |
| Correo | no | correo | `registro.concepcion@ejemplo.gob.ve` | `.email` |
| Activo | sí | `Sí` / `No` | `Sí` | `.activo` |
| Observaciones | no | texto libre | `También fue suplente en Cabudare` | `.observaciones` |

> **Importante:** la **cédula es la llave**. Las 4.090 personas que ya están en el catálogo se
> identifican por cédula: si la cédula coincide, **no se duplica** — se reutiliza la persona y solo
> se le agrega la designación. Por eso conviene enviar la cédula aunque la persona ya esté cargada.

### Hoja 3 — `3-Designaciones`

| Columna | Oblig. | Formato | Ejemplo | Campo en SISV |
| --- | :-: | --- | --- | --- |
| Registro civil | sí | **igual** al nombre de la hoja 1 | `Registro Civil Parroquia Concepción` | `DesignacionRegistrador.registro_civil` |
| Nacionalidad del registrador | sí | `V` `E` `P` `I` `O` | `V` | → `registrador` (con la cédula) |
| Cédula del registrador | sí | solo dígitos | `7449239` | → `registrador` |
| Cargo | sí | `TITULAR` / `SUPLENTE` / `ENCARGADO` | `TITULAR` | `.cargo` |
| Vigente desde | sí | `AAAA-MM-DD` | `2015-04-01` | `.desde` |
| Vigente hasta | no | `AAAA-MM-DD`; **vacío = sigue en el cargo** | *(vacío)* | `.hasta` |
| Fecha de toma de posesión | no | `AAAA-MM-DD` | `2015-03-27` | `.fecha_toma_posesion` |
| Acta / nombramiento | no | texto corto | `Acta 12-2015` | `.acta_nombramiento` |
| Observaciones | no | texto libre | `Encargada por vacaciones del titular` | `.observaciones` |

---

## 4. Reglas de llenado

1. **Una fila por registro.** Nada de celdas combinadas, títulos intermedios, filas de totales ni
   filas en blanco en el medio.
2. **No borrar la fila 1** (encabezado) ni renombrar las columnas. Se pueden agregar columnas de más:
   se ignoran.
3. **Fechas** en `AAAA-MM-DD` (`2019-03-15`). Si la lista ya está en otro formato (`15/03/2019`,
   `mar-2019`), se envía así y aquí se convierte; basta con avisar.
4. **Cédula**: solo números (`7449239`, no `V-7.449.239`). La nacionalidad va en su propia columna.
5. **`Activo` = `No`** para oficinas cerradas o registradores que ya no ejercen: no se borran, quedan
   en el historial (es lo que alimenta el detalle de *cesantes*).
6. **Historial completo, no solo el actual.** Si el mismo registrador tuvo dos periodos separados en
   la misma oficina, van **dos filas** en la hoja 3. Titular y suplente **pueden** coincidir en
   fechas: se permiten designaciones solapadas.
7. Si una oficina **no** tiene registro civil (o la parroquia depende de otra), indíquelo en
   observaciones en lugar de omitirla.
8. Si no se sabe una fecha exacta, se puede dejar vacía **solo** `Vigente hasta` y las columnas
   opcionales; `Vigente desde` sí se necesita para poder responder por fecha (si solo se conoce el
   año, escriba el año y avise).

---

## 5. Qué se hace con la lista

Un importador idempotente (se puede correr las veces que haga falta, no duplica):

1. **Registros civiles** (hoja 1): crea la oficina si no existe (por nombre) y resuelve el **centro
   de salud adscrito** por nombre; si el nombre no coincide con ninguno de los 421 centros, la
   oficina queda igual, sin centro, y se reporta la lista de los que no se pudieron resolver.
2. **Registradores** (hoja 2): busca por **(nacionalidad, cédula)**. Si ya existe, **no lo toca** (no
   pisa nombre ni datos cargados a mano); si no existe, lo crea.
3. **Designaciones** (hoja 3): crea la vigencia (oficina + persona + cargo + desde/hasta). Si ya
   existe la misma terna (oficina, persona, fecha de inicio), se omite.
4. Al terminar muestra un resumen: creados / ya existentes / no resueltos, para revisar antes de dar
   por buena la carga.

Resultado visible en la aplicación:

- `/registradores`: tabla de oficinas con **nº de registradores**, **registrador vigente** y botón
  **«Ver registradores»** → *en funciones* vs *cesantes (historial)*.
- Bloque **«¿Quién firmaba en una fecha?»** por oficina.
- El estado del **despacho** de talonarios puede referenciar la oficina que expide.

---

## 6. Qué **no** hace falta enviar

- Los certificados, planillas o actas escaneadas: solo el **listado**.
- Los datos de las personas fallecidas, causas, ni nada del contenido clínico.
- Los talonarios o series: eso ya se deduce de la base.

Si la lista ya existe en otro formato (Word, PDF, una tabla suelta o un archivo de otra
institución), **se puede enviar igual**: aquí se adapta. La plantilla es una comodidad, no un
requisito.

---

## 7. Plantilla

- Archivo listo para enviar: [`docs/plantillas/registros_civiles_plantilla.xlsx`](plantillas/registros_civiles_plantilla.xlsx)
  (4 hojas: `Instrucciones`, `1-Registros civiles`, `2-Registradores`, `3-Designaciones`).
- Se regenera con `./.venv/bin/python migracion/plantilla_registros_civiles.py`
  (sin dependencias: arma el `.xlsx` con la librería estándar).
- Si cambian los campos del modelo, se ajusta el script y se vuelve a generar.

---

## 8. Mensaje listo para enviar

> **Asunto:** Solicitud de listado de registros civiles y registradores — estado Lara
>
> Buen día:
>
> Estamos completando el Sistema Integral de Salud (SISV) y necesitamos el **listado de las oficinas
> de registro civil del estado Lara**, con las personas que han estado a su cargo y las fechas
> (desde/hasta) de cada periodo.
>
> El sistema anterior solo guardaba *quién* firmaba cada certificado, nunca *en qué oficina* ni
> *desde cuándo*: es el único dato que no podemos recuperar de la base y sin él no se puede saber
> quién firmaba en una fecha determinada.
>
> Adjunto una plantilla en Excel con tres hojas (oficinas, registradores y designaciones) y las
> instrucciones en la primera hoja. Los campos marcados con `*` son obligatorios.
>
> Si la información ya está en otro formato (Word, PDF, una tabla), envíenla igual y nosotros la
> adaptamos. Si alguna parroquia no tiene registro civil, indíquenlo en observaciones.
>
> Alcance esperado: **9 municipios y 57 parroquias** (una oficina por parroquia, como mínimo),
> y el historial de registradores hacia atrás todo lo que se tenga.
>
> Gracias.

---

## 9. Alcance esperado (dato de referencia)

| Referencia | Cantidad |
| --- | --- |
| Estados | 1 (Lara) |
| Municipios | 9 |
| Parroquias | 57 |
| Comunidades (nivel más fino) | 5.517 |
| Centros de salud en SISV | 421 |

Fuente: división político-territorial cargada en `territorio.DivisionTerritorial` (API APN, 2023).

---

## 10. Estado

- [x] Catálogo de registradores desde el legacy (4.090 personas, 14/10/2026) — ver `PENDIENTES.md` §37.2.
- [x] Plantilla Excel + este requerimiento (15/10/2026).
- [ ] **Enviar el requerimiento a la oficina** (adjuntando la plantilla).
- [ ] Importar la lista cuando llegue (comando por escribir; el contrato es el §5).
