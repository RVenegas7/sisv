# Informe de migración Oracle 10g legacy → PostgreSQL 18.6

**Fecha:** 16/09/2026
**Alcance decidido:** «Todo SISMAI + T_*» → esquemas `SISMAI`, `INBDLAR1` (T_*), `LEGACY` (T_*)
y `HISTORICO` (migrado en segunda fase).

## 1. Entorno Oracle temporal

- Contenedor `sis_oracle_legacy`, imagen `gvenzl/oracle-xe:11.2.0.2`, puerto host **1529** → 1521.
- Credenciales: `system/oracle123`; usuario de app `legacy/legacy123`.
- El directorio `legancy/` se monta como `/backup` (ro) en el contenedor.
- BD en `AL32UTF8`; `imp`/`sqlplus` disponibles.

## 2. Dumps importados

| Dump | Esquema(s) | Tablas | Observaciones |
|---|---|---|---|
| `routlar1.dmp` | `TEMP` → usuario `LEGACY` | 82 T_* | export clásico (exp 10.1.0.3.0), charset WE8ISO8859P1 |
| `BDSISMAI.DMP` | `SISMAI`, `HISTORICO`, `INBDLAR1` | 350 / 10 / 83 | export FULL, charset US7ASCII |

Advertencias benignas: FK `SISMAI.FK_RENGLON_CASOSMM` sin tabla padre y grants a usuario
`ANALISTA` inexistente, durante la importación de `BDSISMAI.DMP`.

## 3. Estructura en PostgreSQL

- DDL generado en `/tmp/opencode/legacy/ddl_legacy_postgres.sql` (435 tablas al inicio).
- Se excluyó ruido de Oracle Enterprise Manager (`SM*`, `SMP_*`); además se descartaron
  `SISMAI.PLAN_TABLE` y `SISMAI.PLAN_TABLE2` (internas de *explain plan*).
- Mapeo de tipos: `NUMBER`→`NUMERIC`, `FLOAT`→`DOUBLE PRECISION`, `DATE`→`TIMESTAMP`,
  `VARCHAR2`→`VARCHAR`, `CLOB`/`LONG`→`TEXT`.
- Los nombres se preservan en mayúsculas y **entre comillas** (ej. `sismai."RENGLONTELE"`);
  los esquemas quedaron en minúsculas (plegado estándar de PostgreSQL).

Estado final: **sismai 258**, **inbdlar1 83**, **legacy 82**, **historico 10** (433 tablas).

## 4. Volcado de datos (Oracle → CSV)

Método: procedimientos PL/SQL genéricos con `DBMS_SQL` + `UTL_FILE`
(`SYSTEM.SISV_EXPORTAR_CSV` y `SISMAI.SISV_EXPORTAR_CSV_LOB`), CSV con separador `;`,
campos entre comillas y UTF-8.

- Las tablas con columnas `LONG` (`ACTIVIDAD`, `ESTABLECIMIENTO`) se exportaron vía CTAS con
  `TO_LOB` para convertirlas a CLOB.
- Los valores `NUMBER` se formatean con `TO_CHAR(...,'TM9')` para evitar desbordes `####`.
- `C_ESTABLECIMIENTO` y `H_ESTABLECIMIENTO` son **vistas** (no tablas): no se crearon en PostgreSQL.

## 5. Carga en PostgreSQL

- Contenedor `sis_postgres_dev` (puerto 5436), BD `sis_salud_db`, usuario `sis_user`.
- Carga con `COPY ... FROM STDIN WITH (FORMAT csv, DELIMITER ';', HEADER true, QUOTE '"', NULL '')`
  mediante `psycopg` v3.
- **Resultado: las 423 tablas no-`HISTORICO` quedaron cargadas y sus conteos coinciden con Oracle.**
  (Incidencias resueltas: 4 tablas requirieron reexportar el formato numérico `TM9`; las vistas
  `C_ESTABLECIMIENTO`/`H_ESTABLECIMIENTO` no se cargan por no ser tablas.)

### Conteos verificados (Oracle exacto = PostgreSQL)

| Tabla | Filas |
|---|---|
| `SISMAI.EVENTOS_SINC` | 3.372.065 |
| `SISMAI.RENGLONTELE` | 2.663.432 |
| `SISMAI.EVENTOS_DBLINK` | 2.326.848 |
| `SISMAI.RENGLON_EPI15` | 632.665 |
| `SISMAI.NAC_MADRE` | 438.942 |
| `SISMAI.CERTNACIMIENTO` | 438.910 |
| `SISMAI.NAC_RNACIDO` | 438.646 |
| `SISMAI.CAUSA_MMEDICO` | 332.337 |
| `SISMAI.RENGLON_DSP04` | 323.004 |
| `SISMAI.CAUSA_M` | 211.258 |
| `LEGACY.T_RENGTELE` | 5.007 |
| `INBDLAR1.T_RENGTELE` | 2.592 |

Totales migrados: **SISMAI 12.063.776 + INBDLAR1 38.790 + LEGACY 22.562 = 12.125.128 filas**
de la primera fase, más **HISTORICO 1.942.592** en la segunda fase → **14.067.720 filas**.

### Segunda fase: `HISTORICO`

Exportada vía `/tmp/opencode/export_historico.sql` y cargada dirigidamente. Las 10 tablas:
`EVENTOS_RESP` 1.927.311, `EVENTOS` 15.281; `ERRORES*`/`EVENTO2`/`EVENTOS_DBLINK` en 0.
**Reconciliación final `verificar_conteos.py`:** 0 discrepancias Oracle vs PostgreSQL en las
**433 tablas** de los cuatro esquemas.


## 6. CIE-10 / CIE-11 en el legacy (punto de atención)

El legacy **no contiene CIE-11**. Su validación CIE-10 vive **dentro del esquema `SISMAI`** y
se migró tal cual, **sin fusionarse** con los catálogos del sistema nuevo:

| Tabla legacy | Filas | Contenido |
|---|---|---|
| `sismai."CIE10"` | 16.627 | catálogo CIE-10 con códigos con punto (`W60.5`) |
| `sismai."VALIDARCIE10"` | 14.304 | códigos de validación sin punto (`T222`) |
| `sismai."CODIF_CIE10"` | 498 | equivalencia `CODIFICADOR` → CIE-10 |
| `sismai."CATEGORIA_CIE10"` | 4 | niveles: Capítulo=10, Grupo=20, Categoría=30, Subcategoría=40 |

**No hay colisión** con los catálogos del sistema nuevo (`catalogos_cie10`, `catalogos_cie11`,
`catalogos_mapeocie`, en el esquema `public`), porque el CIE legacy está en el esquema `sismai`
y con nombres propios entre comillas.

Calidad observada en el legacy (a revisar antes de usarlo para reportes):
- 2 códigos CIE-10 duplicados y 10 malformados (<3 caracteres).
- `CODIF_CIE10` incluye mapeos erróneos: «MENINGITIS VIRAL (A87)»→`G00` y
  «SÍNDROME DE GUILLÁIN BARRÉ (G61.0)»→`A98.4` (Ébola).

## 7. ETL legacy → modelos de `registros` (Nacimiento / Defuncion)

Comando: `manage.py importar_legacy_registros [--modelo nacimientos|defunciones|todos] [--limite N] [--borrar]`.

- **Preservación CIE-10:** cada registro guarda el código original en `cie10_legacy`; se resuelve el
  catálogo nuevo `catalogos_cie10` (incluidos los 154 códigos legacy importados con `origen=LEGACY`).
  Los códigos de rango `.X` (`I64.X`, `K85.X`) caen a su categoría base.
- **CIE-11:** solo se asigna a eventos ≥ corte (`version_cie_por_fecha`, 2022-01-01) y únicamente con
  mapeo **EXA**; si no hay EXA se guarda `cie11_sugerido` (mapeo INE/PAR) y `codificacion_pendiente=True`.
  Los eventos pre-corte quedan con `cie11_id=NULL`.
- **Trazabilidad:** `legacy_tabla`, `legacy_id`, `lote_id` (`LEGACY-CERTNACIMIENTO` / `LEGACY-CERTIFICADO`).

Resultado de la carga completa:

| Modelo | Creados | Oracle | Versión CIE-11 | CIE-11 asignado | Pendientes codificación |
|---|---|---|---|---|---|
| `Nacimiento` | 438.596 | 438.646 (−50 huérfanos sin `CERTNACIMIENTO`) | 85.781 | 0 | **0** |
| `Defuncion` | 173.391 | 173.391 | 49.084 | 151 (EXA) | **49.162** |

- **Sexo:** en los datos legacy el código está **invertido** respecto al catálogo `sismai.SEXO`
  (que rotula 1=MASCULINO/2=FEMENINO): verificado sobre los nombres reales → **1=Femenino, 2=Masculino**.
- **Nacimientos:** el legacy no trae ningún CIE; por decisión del usuario **no** se marcan como
  pendientes (`codificacion_pendiente=False`).
- **Depuración de datos basura:** `NAC_MADRE` tenía certificados duplicados (17) → se dedupeó con
  `DISTINCT ON`; se descartaron peso/talla/edad gestacional/folio fuera de rango.
- **Cola del codificador (defunciones):** 49.162 pendientes (49.084 post-corte + 249 pre-corte sin
  código), de los cuales 225 tienen sugerencia INE disponible. La causa de `CAUSA_MMEDICO` está solo
  en texto (`CAUSA1/2/3`, `HCIE10` nulo al 100%) → requiere codificación manual.

## 8. Fichas de vigilancia individuales en el legacy (hallazgo)

Revisión de todas las tablas de fichas. **Sí existen fuentes individuales**, aunque el modelo
`registros.FichaVigilancia` no se cargó (decisión: **solo documentar por ahora**):

| Fuente | Filas | Contenido |
|---|---|---|
| `sismai."CASOS_MMI"` | 10.742 (2009–2026) | caso materno-infantil individual: nombre, `EDAD`+`UNIDAD_EDAD` (M/D/A), `HSEXO` (también invertido), `FECHAOCURRENCIA`, residencia |
| `sismai."RENGLON_CASOSMI"` | 9.992 (enlazados a `CASOS_MMI`) | causa con `HCAUSA_CIE10`/`HCAUSABAS_CIE10`, establecimiento, edad gestacional → **ficha individual con CIE-10** |
| `sismai."M_VIOLENTA"` | 12.409 | violencia (`TIPO_M`: accidente 4.226, homicidio 4.007, suicidio 410…), **100% enlazada a `CERTIFICADO`** (atributo de defunciones ya importadas) |
| `sismai."INFORME_EPI"` | 298 | agregado (`CASOSP`/`CASOSS`/`CASOSX`) → territorio de `vigilancia.ConsolidadoSemanal` |

**Vacías:** `FICHAS_EPIDEMIOLOGICAS`, `FICHA_ACCIDENTE`, `FICHAEPI13`, `FICHADOLORTORACICO`,
`ACCIDENTELABORAL`, `HECHOS_VIOLENTOS`, `SEG_EVOL_PACIENTE`. `FICHADELDOLOR` (30) es catálogo;
`PACIENTE_FICHA_EPI` (5.326) solo demografía sin ficha (cabecera vacía).

## 10. Corrección post-migración: eliminación de colas de replicación (18/09/2026)

El diagnóstico en vivo (`legancy/Informe_BD_SIS_LAR1_2026-09-18.md`, 18-09) reveló que parte
significativa de lo migrado era **infraestructura de replicación muerta**, no datos:

| Tabla eliminada en PostgreSQL | Filas | Contexto |
|---|---|---|
| `sismai."EVENTOS_SINC"` | 3.372.065 | cola de sincronización **detenida desde 27-08-2026** (3,36 M insertadas ese día, nunca procesadas; MAX `FECHA` 2026-08-27 12:53:50) |
| `sismai."EVENTOS_DBLINK"` | 2.326.848 | backlog 100 % STATUS=0, ningún proceso lo consume |
| `historico."EVENTOS_RESP"` | 1.927.311 | 100 % STATUS=0, mismo origen |

- Representaban **~54 % de las 14.067.720 filas** cargadas (7.626.224).
- Se conserva `historico."EVENTOS"` (15.281, STATUS≠0): es el log real de procesamientos completados.
- Estado final tras el `DROP` (verificado en `sis_postgres_dev`): **430 tablas / ~6.441.496 filas**
  (sismai 256 tablas, historico 9, inbdlar1 83, legacy 82).
- **Regla operativa:** `EVENTOS_SINC`/`EVENTOS_DBLINK`/`EVENTOS_RESP` no se usan para ETL ni reportes
  (la recarga masiva del 27-08 duplicaría la vigilancia real: RENGLONTELE 2,32 M, RENGLON_EPI15 490 K,
  RENGLON_DSP04 303 K están en la cola y **también** en sus tablas reales).
- Futuros re-dumps: **excluir/filtrar estas 3 tablas** (crecen ~33.281/mes en el origen).
  Ya quedó aplicado en `migracion/extraer_estructura.sql` (excluye `EVENTOS_SINC`,
  `EVENTOS_DBLINK`, `EVENTOS_RESP`, `PLAN_TABLE`, `PLAN_TABLE2` y `SM*`/`SMP_*`) y en
  `migracion/extraer_datos_csv.sh` (variable `EXCLUIR` con el mismo listado).

## 9. Pendientes derivados

1. Decidir el mapeo de fichas individuales (`CASOS_MMI`/`RENGLON_CASOSMI` → `FichaVigilancia`;
   `M_VIOLENTA` → ficha de violencia o campo en `Defuncion` o `SituacionEspecial`).
2. Decidir si `INFORME_EPI` y la vigilancia agregada (`RENGLONTELE`, `RENGLON_EPI15`) se migran a
   `vigilancia.ConsolidadoSemanal`.
3. Decidir si los catálogos CIE legacy se usan como están, se limpian o se reemplazan por
   `catalogos_cie10` / `catalogos_mapeocie` (cross-walk OMS).
