# PLAN DE CORTE SISV ↔ SIS/LAR1 (legacy)

**Fecha:** 18/09/2026
**Objetivo:** migrar la operación de Lara al nuevo SISV **sin romper la información obligatoria que se envía semanalmente (cada martes) al nivel superior**, y sin exigir trabajo paralelo a los usuarios.

---

## 1. Resumen ejecutivo

El nivel superior **no consume la base completa**: consume un **archivo** (`routlar1_*.ZIP`, un `exp` clásico del esquema `TEMP`, tablas `T_*`) que la aplicación SIS/Centura genera cada envío. SISV puede producir **ese mismo archivo** a partir de PostgreSQL. El plan es:

1. **Esta semana:** restaurar el ciclo de replicación/sincronización en el servidor legacy (está detenido desde el 27-08-2026) y garantizar el envío del próximo martes por la vía probada.
2. **Semanas 1–2:** documentar el «contrato» de exportación (`EVENTOS_SINC` → `TEMP.T_*`), construir el generador del archivo desde SISV y **validarlo en local** contra un ZIP histórico real (sin involucrar al nivel central).
3. **Martes N (corte):** los usuarios pasan la información por legacy como siempre; esa noche se congela, se exporta fresco y se carga en PostgreSQL; al día siguiente **todos trabajan solo en SISV** (sin paralelo).
4. **Martes N+1 en adelante:** SISV emite el archivo (en «sombra» durante 2–3 envíos), hasta declarar en producción plena y retirar el legacy.

No se le pide al nivel central ninguna prueba: las validaciones son internas con semanas históricas idénticas.

---

## 2. Contexto técnico: cómo se «pasa la información» hoy

### 2.1 El artefacto que recibe el nivel superior

En `legancy/` tenemos evidencias reales:

- `routlar1_1692026_1245.ZIP` — contiene `routlar1.dmp` (~2 MB) + logs (`routlar1.log`, `copyhistlar1.log`, `bloqlar1.log`).
- `bkbdlar1_160926.tgz` — contiene `BDSISMAI.DMP` (~1,2 GB) + logs: respaldo integral de la BD.

El `routlar1.dmp` es un **`exp` clásico del esquema `TEMP`**: 82 tablas `T_*` que actúan como «sobres» por tipo de registro. Ejemplos (de `legancy/analisis/schema_routlar1.sql`):

| Sobre TEMP | Origen en SISMAI | Contenido |
|---|---|---|
| `T_CERTMORT` | `CERTIFICADO` | certificados de defunción |
| `T_RNACNACI` / `T_MADRNACI` | `CERTNACIMIENTO` / `NAC_MADRE` | nacimientos (certificado + madre) |
| `T_RENGTELE` | `RENGLONTELE` | renglones de vigilancia semanal |
| `T_RENEPI15` / `T_RENDSP04` | `RENGLON_EPI15` / `RENGLON_DSP04` | renglones EPI-15 y DSP-04 |
| `T_RCASOSMI` / `T_RCASOSMM` | `RENGLON_CASOSMI` / `RENGLON_CASOSMM` | causas materno-infantil |
| `T_MORTVIOL` | `M_VIOLENTA` | muertes violentas (atributo de certificado) |
| `T_TRATUBER` | `PROGTUBER`… | otros módulos (TB, diabetes, cirugía…) |
| `T_EVENTOS` | (índice) | lista de qué tablas/eventos van en el envío |

### 2.2 El ciclo interno (los scripts del servidor)

1. La aplicación inserta una fila en `SISMAI.EVENTOS_SINC` (`TABLA`, `EVENTO`, `FECHA`, `ID`, `STATUS`, `AMS`) por cada registro nuevo/modificado.
2. Un proceso de sincronización (`SincFich/mort/cr_repli_mort.sql`, `plcer1.sql`, `RoutLar1/*`) copia las filas referenciadas desde SISMAI a las tablas de staging `TEMP.T_*`.
3. Se ejecuta `exp` del esquema `TEMP` → `routlar1.dmp` → se comprime como `routlar1_<fecha>_<hora>.ZIP` → **se transfiere al nivel superior**.
4. El central importa y, en origen, se hace `TRUNCATE` de `TEMP.T_*` y de `EVENTOS_SINC`.

### 2.3 Hallazgos del diagnóstico en vivo (18-09-2026)

Fuente: `legancy/Informe_BD_SIS_LAR1_2026-09-18.md` (detalles §3–§7).

- **CRÍTICO:** la cola `SISMAI.EVENTOS_SINC` está detenida desde el **27-08-2026 12:53:50**, con **3.372.065 eventos sin procesar**. De ellos, **3.359.781 se insertaron el 27-08** (recarga masiva, la mayoría `RENGLONTELE`/`RENGLON_EPI15`/`RENGLON_DSP04`/`DOCUMENTO`). El motor que debía exportar a `TEMP` y truncar la cola **no está corriendo** (`/home/salud/bin` vacío, scripts sin ejecutar desde 2020, cron solo de respaldo).
- **Consecuencia operativa:** desde el 27-08 **no se está replicando la información nueva de Lara al central** (aprox. 3 semanas). Los envíos del martes serían incompletos o no se están generando. Confirmación: el `routlar1.dmp` del 16-09 pesa solo ~2 MB — no caben 3,37 M de eventos → **no llegaron**.
- **ALTO:** `EVENTOS_DBLINK` (2.326.848, 100% STATUS=0) y `HISTORICO.EVENTOS_RESP` (1.927.311, 100% STATUS=0) son backlog de replicación que ningún proceso consume; crecen ~33.281/mes. Semántica de STATUS: por aclarar con quien conozca el sistema (no tocar sin respaldo).
- **MEDIO:** 16 objetos de aplicación inválidos (vistas `C_INFORMES`, `NATALIDAD`, `V_FICHAEPI13`, `C_ESTABLECIMIENTO`, …; procedimientos `SPREGTEL`, `SPDOC`, `SPREGDSP`, `SPREGEPI`; función `FIDPADRE`). Algunos participan del export → recompilar.
- **MEDIO:** tablas de errores vacías (buena señal); `HISTORICO.EVENTOS` (15.281, STATUS≠0) sí refleja procesamientos completados (976 en el último mes) → el sistema SÍ procesó eventos, lo que sugiere que el ciclo funcionó hasta que la recarga del 27-08 lo colapsó.
- **OPERATIVO:** NOARCHIVELOG, `undo_retention=900`, estadísticas de `HISTORICO` sin analizar desde 2024, credenciales triviales visibles en scripts (riesgos a mitigar, no bloquean el plan).

### 2.4 Lo que ya hicimos en el SISV (impacto de estos hallazgos)

- Migramos el espejo completo (14.067.720 filas, 0 discrepancias Oracle vs Pg) y **eliminamos las 3 colas de replicación** (`EVENTOS_SINC` 3.372.065, `EVENTOS_DBLINK` 2.326.848, `HISTORICO.EVENTOS_RESP` 1.927.311) el 18-09-2026 → quedan **430 tablas / ~6,44 M de filas reales**.
- Los scripts de futuras importaciones (`migracion/extraer_estructura.sql` y `extraer_datos_csv.sh`) ya **excluyen** estas colas (`EVENTOS_SINC/DBLINK/RESP`, `PLAN_TABLE*`, `SM*`/`SMP_*`).
- ETL a `registros`: **438.596 nacimientos** y **173.391 defunciones** cargados (49.162 defunciones en `codificacion_pendiente`, HCIE10 100% nulo en texto → requiere codificación manual).
- **Ojo para el puente:** la tabla `TEMP.T_*` y `T_EVENTOS` **sí forman parte del envío** y no deben confundirse con las colas; el esquema `legacy` (82 tablas `T_*`) ya está migrado a Pg y es la semilla del formato.

---

## 3. Principio rector: el «contrato» de intercambio no se toca

El nivel superior espera, cada martes, el archivo `routlar1_*.ZIP` en el formato que hoy produce Oracle. SISV no debe cambiar ese formato: debe **producir exactamente el mismo archivo** (o alimentarlo). Hay dos vías:

- **A) Puente (recomendada al inicio):** SISV exporta desde PG los registros del periodo a un staging equivalente (las tablas `T_*`, ya migradas como esquema `legacy`) y se genera el `exp` con la herramienta de Oracle. El mecanismo de emisión queda intacto → riesgo mínimo de romper el formato.
- **B) Directa (segunda etapa):** SISV genera directamente el `routlar1.dmp`/ZIP equivalente. Más limpio (deja fuera a Oracle), pero exige validación esmerada contra semanas históricas reales.

Transición recomendada: **A primero, B después de 2–3 envíos conformes.**

---

## 4. Plan por fases

### Fase 0 — Urgencia de producción (esta semana; el responsable es Rafael ya)

1. **Restaurar el ciclo de sincronización en el servidor legacy:**
   - Verificar con el nivel central qué recibieron los últimos martes (¿completo? ¿cuál fue el «último martes bueno»?).
   - Respaldar la cola antes de tocar nada: `CREATE TABLE SISMAI.EVENTOS_SINC_BK_20260918 AS SELECT * FROM SISMAI.EVENTOS_SINC;`
   - Según el árbol del informe §6.1: si el central ya recibió la data por otra vía → `TRUNCATE` con respaldo previo; si no → restaurar/repoblar `TEMP` y re-exportar.
   - Rearmar el ciclo: ubicar el proceso consumidor (scripts `RoutLar1`/`SincFich`/`plcer1.sql`), reinstaurarlo (cron o servicio) y probar un envío.
2. **Recompilar los 16 objetos inválidos de la app** (`DBMS_UTILITY.COMPILE_SCHEMA('SISMAI')` o compilación selectiva), en especial los del export.
3. **Validar el envío del próximo martes:** que el ZIP salga igual que siempre y que el central lo confirme (acuse).

### Fase 1 — Ingeniería del puente (en paralelo, 1–2 semanas)

1. **Documentar el contrato:** para cada tipo de evento en `EVENTOS_SINC` (TABLA+EVENTO) → tabla(s) `T_*` que se pueblan y con qué columnas/orden. Fuentes: `schema_routlar1.log` del informe, `BDSISMAI.LOG`, el `routlar1.dmp` de muestra, y las tablas `legacy.T_*` ya migradas.
2. **Construir el módulo de exportación de SISV:** comando tipo `manage.py exportar_rutalara --semana YYYY-WNN` que, desde PostgreSQL, genere el contenido `T_*` (y potencialmente el ZIP) equivalentes. Los datos de origen ya están (o se mapean): nacimientos, defunciones, fichas, vigilancia.
3. **Validación local sin el central:** tomar una semana histórica que ambos sistemas tengan (p. ej. semana del 19 al 25 de agosto, antes de la recarga), generar el archivo desde SISV y comparar contra el ZIP legacy real (estructura + conteos). Repetir 2–3 semanas.
4. **Completar los módulos/ventanas pendientes de SISV** (`PENDIENTES.md`): reportes/mapeos, territorio, vigilancia (ConsolidadoSemanal/fichas), etc. — deben cubrir exactamente lo que alimenta los sobres `T_*`. (La intención: que el usuario encuentre todo lo que hoy hace en legacy.)
5. **Definir y probar la carga fresca a PG** (pipeline ya existente, con exclusión de colas): el mismo que se usará la noche del corte.

### Fase 2 — Corte seco el martes N (modelo «sin paralelo»)

Secuencia del día del corte:

| Momento | Acción |
|---|---|
| Lunes-Miércoles previos | Usuarios trabajan con normalidad en legacy; se anunció la ventana de cambio. |
| Martes (día del envío) | Los usuarios pasan la información **como siempre, por legacy** — cero riesgo, formato probado. |
| Martes al confirmarse el acuse | **Congelar captura** en legacy (bloquear/avisar). |
| Martes noche | Dump fresco → cargar en PostgreSQL (filtro de colas) → **reconciliación** (conteos de esquinas, fechas, últimos IDs). |
| Miércoles | Apertura: **todos los usuarios trabajan solo en SISV.** No hay paralelo ni doble carga. |

Garantías clave:
- El envío que cuenta (el del martes) sale **todavía por la vía probada**.
- La ventana de congelación es de unas horas (noche), no días → no exige esfuerzo paralelo.
- Contingencia: si la carga a PG falla esa noche, se reabre en legacy al día siguiente sin haber perdido el envío.

### Fase 3 — Primeros envíos desde SISV (martes N+1 y siguientes)

1. SISV emite el archivo del periodo (vía A o B). Transferencia igual que siempre.
2. **Validación en sombra (2–3 martes):** comparar lo emitido por SISV contra lo esperado (conteos por `T_*`, acuse del central). Mantener Oracle como **respaldo frío** (si el puente falla: re-importar la semana desde PG al staging Oracle y emitir por la vía clásica).
3. Solo tras 2–3 envíos conformes: **retirar el legacy** (queda archivado read-only, documentado como `historico`).

### Fase 4 — Cierre

- Documento final con el **contrato de intercambio** (formato `T_*`, generación, contingencia).
- Procedimiento de contingencia escrito: «regenerar un envío», «recuperar una semana», «rollback al legacy».
- Dejar Oracle fuera de línea (o como servidor de consulta histórico), con respaldo final.

---

## 5. Respuesta a los temores planteados

| Temor | Cómo lo cubre el plan |
|---|---|
| «Responsabilidad de pasar la info de un estado entero» | El martes del corte aún pasa por la vía legacy probada; SISV no emite nada oficial hasta N+1. |
| «Que se rompa la info/exportación del esquema legacy del nivel superior» | El puente (vía A) no toca el mecanismo de exportación; la validación es interna contra semanas históricas idénticas; nunca se cambia el formato. |
| «Usuarios no harán paralelo» | El corte seco en una noche elimina el paralelo; no hay doble carga. |
| «El central se niega a probar 2 días» | No se pide cooperación al central; las pruebas son locales y el primer envío real ya es el martes. |

---

## 3.1 Regla «CIE-11 sí, pero la exportación siempre en CIE-10»

El nivel central (motor legacy) **solo entiende CIE-10**: los sobres `T_*` que consume llevan campos
`HCIE10` / `HCAUSA_CIE10` / `HCAUSABAS_CIE10` (claves al catálogo CIE-10 del central). Si en el `routlar1.dmp`
un campo `HCIE10` llevara un código CIE-11, el central lo rechazaría (código no válido) o quedaría pendiente.

**Regla del puente (no negociable):**

- El registro se guarda en SISV con **CIE-11** (`cie11_id`, para reportes modernos) **y** su `cie10_legacy` intacto.
- Lo que viaja en el sobre `T_*` es **SIEMPRE CIE-10**, derivado así:
  1. mapeo **EXA** → se escribe el CIE-10 exacto;
  2. mapeo **PAR/INE** → se escribe el mejor equivalente CIE-10 (igual a como hoy deciden las codificadoras);
  3. **sin equivalente** → se exporta como hoy lo acepta el central: código **en observación** (texto), conservando el CIE-11 dentro de SISV. **No se pierde información.**
- Consecuencia: **codificar CIE-11 no rompe la exportación ni lo enviado al nivel superior**, y de hecho reduce el trabajo manual de las codificadoras (búsqueda automática + CIE-10 derivado por cross-walk, con la observación solo como respaldo).

### Estado real de la cola de codificación (analizado en PostgreSQL, 18/09/2026)

De las **49.162 defunciones** con `codificacion_pendiente`:

| Grupo | Casos | Tratamiento |
|---|---|---|
| Con `cie11_sugerido` (mapeo INE/PAR ya resuelto) | 225 | automatizable: proponer CIE-11 + CIE-10 derivado al codificador |
| Con `cie10_legacy` preservado | 245 | ya tienen su CIE-10 original; faltará validar equivalencia CIE-11 |
| Sin código ni sugerencia (causa solo en texto libre de `CAUSA_MMEDICO`) | ~48.937 | requieren revisión humana de la causa textual |

→ La automatización cubre un **0,5 %** de la cola; el grueso es revisión humana. SISV ayuda con el flujo de
«cola del codificador» (búsqueda inteligente `CIESearch`, agrupación, priorización) para que **2 personas no
detengan el trabajo entrante**. La reunión con las codificadoras debe definir si la «observación» que hoy exige
el central se replica igual o se enriquece con la equivalencia automática.

---

## 6. Decisiones tomadas (18/09/2026)

1. **Vía de emisión inicial:** (A) **puente vía Oracle `TEMP.T_*`/`exp`**. (B) generación directa desde PG: **planificada como segunda etapa** tras 2–3 envíos conformes.
2. **Fecha objetivo del corte:** **martes 29/09/2026**.
3. **Alcance funcional «día 1»:** **TODOS los módulos y ventanas de SISV operativos** (nacimientos, defunciones, fichas, vigilancia, reportes/mapeos, configuración; cubrir `PENDIENTES.md`).
4. **Orden de arranque:** **Fase 0 (producción) primero**, luego Fase 1 en paralelo.

### Cronograma alrededor del corte (martes)

| Fecha | Hito | Fase |
|---|---|---|
| 22/09 (mar) | **Envío por legacy** que valida la sinc restaurada (acuse del central) | 0 |
| 22–29/09 | Contrato `EVENTOS_SINC→T_*` + puente + validación local histórica; completar módulos día 1 | 1 |
| **29/09 (mar)** | **CORTE:** envío por legacy confirmado → congelar → dump fresco → PG → reconciliación → apertura 30/09 solo SISV | 2 |
| 06/10 (mar) | **Primer envío desde SISV** (sombra 1) | 3 |
| 13 y 20/10 (mar) | Sombra 2 y 3; tras 3 envíos conformes → decidir retiro del legacy | 3

---

## 7. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Replicación rota desde el 27-08 → lag de ~3 semanas ante el central | Determinar «último martes bueno», re-exportar lo no enviado con respaldo previo (Fase 0). |
| Backlog `EVENTOS_DBLINK`/`EVENTOS_RESP` | No tocar sin definir la semántica de STATUS; archivar antes de depurar. No afecta el formato del envío. |
| Pérdida de datos durante re-exportación | Respaldos puntuales previos (`*_BK_*`), nunca truncar a ciegas. |
| SISV no emite el archivo idéntico al esperado | Validación en sombra 2–3 martes; Oracle como respaldo frío. |
| Usuarios sin entrenamiento en SISV la semana del corte | Período de uso en «paralelo de entrenamiento» NO obligatorio: se sugiere un overlay de capacitación en los 5 días hábiles previos con datos de prueba, nunca con carga real. |
| Conversion/encoding (WE8ISO8859P1/US7ASCII) | Auditar texto de causas en los sobres T_* antes del primer envío real. |

---

## 8. Evidencias y fuentes

- `legancy/Informe_BD_SIS_LAR1_2026-09-18.md` — diagnóstico en vivo completo.
- `legancy/analisis/INFORME_MIGRACION_LEGACY.md` — registro de la migración y correcciones (nuevo §10).
- `legancy/analisis/schema_routlar1.sql` — DDL del esquema `TEMP` (los sobres).
- `legancy/routlar1_1692026_1245.ZIP` + `routlar1.log`/`copyhistlar1.log`/`bloqlar1.log` — muestra real del envío.
- `legancy/BDSISMAI.LOG` — bitácora del `exp` integral.
- `PENDIENTES.md`, `AGENTS.md` — estado y alcance del SISV.
- PostgreSQL `sis_postgres_dev` (5436) — verificación de conteos: **430 tablas / ~6,44 M de filas** tras el DROP de colas.
- Análisis de codificación (18/09/2026): consulta en `registros_defuncion` → 49.162 pendientes; 225 con `cie11_sugerido`; 245 con `cie10_legacy`; ~48.937 sin código ni sugerencia.

---

## 9. Notas en curso

- **Punto 8 del usuario:** pendiente de recordar y agregar (se comunicará).
- Reunión con las codificadoras (pendiente): definir flujo de codificación CIE-11 y la «observación» del puente.