# Pendientes — SISV (Sistema Integral de Salud)

## 1. [COMPLETADO] Firma «Desarrollado por Rafael Venegas» en toda la aplicación

- **Estado:** completado (19/09/2026).
- **Descripción:** firma **«Desarrollado por Rafael Venegas»** en toda la aplicación.
- **Alcance implementado:**
  - Frontend: pie de página (`footer.firma-app`) al final del contenido de la app y pantalla de
    login (`footer.login-firma`, ya existente, ahora con estilo fijo abajo a la derecha).
  - Backend: `/api/` (ApiRoot) incluye `desarrollado_por: "Rafael Venegas"` en la respuesta.
- **Fecha de registro:** 12/09/2026. Fecha de cierre: 19/09/2026.

## 2. [COMPLETADO] Carga de catálogos reales CIE-10 y CIE-11 (ambos en español)

- **Estado:** ambos catálogos **cargados y en español** (13/09/2026) y operativos de punta a punta.
- **CIE-11** (release `2026-01` en español vía contenedor `servicio-cie11`):
  37.211 registros en `catalogos_cie11` (28 capítulos, 1.360 bloques, 19.884 categorías, 15.939 subgrupos),
  jerarquía capítulo→bloque→categoría→subgrupo completa, `requiere_subgrupo` marcado (2.736). Comando:
  `manage.py importar_cie11_oms` (recorre la API local de `whoicd/icd-api`; requiere el contenedor levantado).
- **CIE-10 en español** (13/09/2026): 14.208 códigos en `catalogos_cie10` (21 capítulos, 2.034 de 3 dígitos +
  12.174 de 4 dígitos). Fuente: dataset jerarquizado español de `verasativa/CIE-10` (scrape de la página oficial
  OMS `icd.who.int/browse10/2019/es` + catálogo Chile MINSAL/DEIS), `backend/catalogos/data/cie10_es_oms_icdcodeinfo.csv`,
  normalizado a formato OMS con punto (`A000`→`A00.0`). Cobertura 12.026/12.221 del catálogo OMS 2019 (98,4%).
  Comando: `manage.py importar_cie --cie10-es <csv>`.
- **Nota OMS:** el CDN `icdcdn.who.int` y la ICD-API solo sirven CIE-10 en **inglés** (`…es…`/`spa` → 404) y ya no
  ofrecen `DBCIE.db` (archive.org: 0 resultados). La traducción española oficial (OPS/OMS Vol. 1, hecha por el
  Centro Venezolano de Clasificación) solo existe en PDF.
- **Fechas:** el corte por versión sigue en `2022-01-01` (`version_cie_por_fecha`): eventos ≥ corte → CIE-11,
  anteriores → CIE-10. La **data legacy CIE-10 en español ya se puede registrar** (POST de FichaVigilancia con
  `J18.9` «Neumonía, no especificada» y `version_cie=CIE10` verificado: 201).
- **Fix (13/09/2026):** `cargar_eventos_eno` ahora extrae correctamente los códigos CIE-11 con prefijo numérico
  (`1A00`, `1B10-1B1Z`, `1C60-1C62.3`, …) — antes se truncan sin el dígito inicial por el regex de `extraer_codigos`.
  123 eventos actualizados (112 con códigos CIE-11).
- **Enriquecido (13/09/2026):** cómo `cargar_eventos_eno` duplicaba los códigos (`1A00 / 1A00`) se corrigió con el comando
  `enriquecer_eno_cie`: deduplica `codigos_cie11` y deriva `codigos_cie10` de cada evento usando el cross-walk
  (`MapeoCIE`), expandiendo rangos (ej. `1B10-1B1Z`→A15-A19, `5A10-5A14`→E10-E12). Resultado: **98 eventos
  actualizados, 63 con CIE-10 derivado** (49 sin mapeo, ej. dengue: el mapeo OMS 11→10 apunta a `A97.x` no cubierto
  por el scrape español). El frontend de `/vigilancia` muestra ambos (CIE-11 y CIE-10).

## 3. [COMPLETADO] Carga de mapeos / cross-walk CIE-10 ↔ CIE-11

- **Estado:** **importado** (13/09/2026) — `catalogos_mapeocie` con **11.879 equivalencias**.
- Fuente: **`mapping.zip` oficial de la OMS** (release 2025-01, descargado de
  `icdcdn.who.int/static/releasefiles/2025-01/mapping.zip`): contiene `10To11MapToOneCategory.txt`,
  `10To11MapToMultipleCategories.txt`, `11To10MapToOneCategory.txt`, etc.
- Comando: `manage.py importar_mapeos <ruta-a-mapping.zip> --solo-categorias [--borrar]`. El importador:
  - normaliza códigos CIE-10 (con/sin punto), toma la base de CIE-11 descartando postcoordinación `&…`;
  - ignora rangos/bloques y solo guarda categorías con código real en **ambos** catálogos en español;
  - clasifica el **tipo** por round-trip con el archivo `11To10MapToOneCategory.txt`:
    `EXA` (exacto, 5.008) si `c10→c11` y `c11→c10` son idénticos, `PAR` (parcial, 773) si hay
    postcoordinación o destinos múltiples, `INE` (inexacto, 6.098) en el resto.
- Verificado: 341 omitidos son CIE-10 no cubiertos por el scrape español (ej. `A09.0`, `A92.5`, `A97`, `B18.00`).
  Endpoint `/api/catalogos/mapeos/?cie10=<codigo>` devuelve equivalencias con título CIE-11 en español.

## 4. [PENDIENTE] Territorio (estados, municipios, parroquias, comunidades)

- **Estado:** pendiente — la tabla `territorio_divisionterritorial` está vacía; los registros demo no tienen org geográfica completa.
- Paso 1: `manage.py cargar_territorio --solo-estados` (25 estados).
- Paso 2: importar municipios/parroquias/comunidades desde la API externa (falta obtener registro y permisos del usuario).

## 5. [COMPLETADO] Migración Oracle 10g → PostgreSQL (datos del sistema legado)

- **Estado:** **estructura y datos migrados** (16/09/2026) desde un Oracle XE 11.2 temporal
  (`sis_oracle_legacy`, puerto 1529) hacia `sis_postgres_dev`.
- Alcance: esquemas `sismai` (258 tablas), `inbdlar1` (83), `legacy` (82) y `historico` (10)
  en PostgreSQL → **14.067.720 filas** cargadas por `COPY` CSV. **Reconciliación final: 0 discrepancias
  Oracle vs PostgreSQL en las 433 tablas.**
- **Limpieza de colas de replicación (18/09/2026):** el diagnóstico en vivo (SIS/LAR1)
  confirmó que `EVENTOS_SINC` (3.372.065, detenida desde 27-08), `EVENTOS_DBLINK` (2.326.848)
  y `HISTORICO.EVENTOS_RESP` (1.927.311) eran **colas de sincronización nunca procesadas**
  (≈54 % de las filas migradas, sin valor operativo). Se eliminaron de PostgreSQL:
  quedan **430 tablas / ~6.441.496 filas** de datos reales (se conserva `historico."EVENTOS"`
  15.281, único log de eventos completados). Fuente del hallazgo:
  `legancy/Informe_BD_SIS_LAR1_2026-09-18.md`. No usar `EVENTOS_SINC/*` en ETL ni reportes
  (riesgo de doble conteo: la recarga masiva del 27-08 replica toda la vigilancia).
  En futuros re-dumps del servidor, **excluir/filtrar `EVENTOS_SINC`, `EVENTOS_DBLINK`,
  `EVENTOS_RESP`** (crecen ~33.281/mes).
- Detalle completo en `legancy/analisis/INFORME_MIGRACION_LEGACY.md`.
- **CIE:** el CIE-10 legacy (`sismai."CIE10"`, `"VALIDARCIE10"`, `"CODIF_CIE10"`, `"CATEGORIA_CIE10"`)
  se migró **separado** de los catálogos nuevos (`catalogos_cie10`/`cie11`/`mapeocie`), sin fusión.
- **ETL a `registros`:** comando `importar_legacy_registros` cargó **438.596 nacimientos** y
  **173.391 defunciones**, preservando el CIE-10 original en `cie10_legacy`, resolviendo el catálogo
  nuevo (154 códigos legacy importados con `origen=LEGACY`) y dejando **49.162 defunciones** en
  `codificacion_pendiente` para el codificador (CIE-11 post-corte / causa solo en texto).
- **Pendiente:** decidir el mapeo de fichas individuales (`CASOS_MMI`/`M_VIOLENTA`) y de la vigilancia
  agregada (`RENGLONTELE`, `RENGLON_EPI15`, `INFORME_EPI`) a `vigilancia.ConsolidadoSemanal`; decidir
  el destino de los catálogos CIE legacy. Ver `legancy/analisis/INFORME_MIGRACION_LEGACY.md` §8-9.

## 6. [COMPLETADO] Módulo de Vigilancia (modernización de ventanas legacy)

- **Estado:** **implementado** (13/09/2026) — spec aprobada por el guardián del dominio (12/09/2026), backend (app `vigilancia`) y frontend (`Vigilancia.jsx`) operativos.
- Normativa del MPPS obtenida y archivada en `docs/normativa/` (formularios oficiales SIS-04/EPI-12 morbilidad y SIS-04/EPI-14 mortalidad, y Manual de Normas SIVIGILA/Muerte Materna-Infantil), **especificación funcional aprobada** en `docs/especificacion-modulo-vigilancia.md`.
- La captura de referencia corresponde al **Consolidado Semanal de ENO (SIS-04/EPI-12)**; el módulo cubre: notificación individual (FichaVigilancia ya existente), **consolidado semanal agregado** (nuevo) y situaciones especiales/alertas/epidemias (nuevo).
- **Decisiones validadas (12/09/2026):** grupos etarios = los del formulario (13, <1 … 65+, Edad Ignorada); regla «edad ignorada» → columna Hombres confirmada; **consolidación editable por nivel superior** (municipio/región precargan la suma de sus establecimientos y la ratifican/editan, flujo SIVIGILA local→municipal→regional→nacional).
- **Prioridad de diseño:** la base de referencia es la **norma internacional** (OMS/RSPI 2005, CIE) y las **normas y leyes venezolanas** vigentes (MPPS/SIE, LEO 36.579, Manual SIVIGILA). Las capturas sirven de referencia; no son la fuente normativa principal.
- **Implementado:** 5 modelos (`EventoENO`, `ConsolidadoSemanal`, `FilaConsolidado`, `SituacionEspecial`, `AlertaEpidemia`), comando `cargar_eventos_eno` (123 eventos desde EPI-12/EPI-14), `sembrar_demo` (consolidado demo de vigilancia), API `/api/vigilancia/` (eventos-eno, consolidados CRUD, exportar CSV), página `/vigilancia` (matriz 13 grupos × 2 sexos, situaciones especiales, alertas/epidemias, estados BORRADOR/ENVIADO/CERRADO), `/vigilancia/fichas` conserva la carga individual. Todos los endpoints verificados con el cliente de pruebas de Django.

## 7. [COMPLETADO] Configuración del sistema legado (`legancy_conf`)

- **Estado:** completado (19/09/2026) — carpeta `legancy_conf/` creada con plantillas.
- Contenido: `README_legancy_conf.md` (guía y reglas de conexión al Oracle 10g),
  `credenciales.env.ejemplo` (→ `credenciales.env`, no versionado), `tnsnames.ora.ejemplo`
  (→ `tnsnames.ora`, no versionado) y `conectar_legacy.sh` (prueba de conexión con `sqlplus`).
- Seguridad: `.gitignore` raíz ignora `legancy_conf/*.env` y `legancy_conf/tnsnames.ora`.

## 8. [PENDIENTE] Mapa de modelos legados (`models_legacy.py`)

- **Estado:** pendiente — ejecutar `manage.py inspectdb` contra Oracle para extraer el mapa de tablas, analizarlas y ordenarlas por prioridades. Escribir pruebas de lectura/escritura sin alterar el flujo del sistema.

## 9. [PENDIENTE] Lint y pruebas automatizadas

- **Estado:** pendiente — Django y React aún no tienen lint/tests configurados.
- Verificación manual vigente: `manage.py check`, cliente de pruebas de Django y `npm run build`.

## 10. [COMPLETADO] Repositorio Git

- **Estado:** completado (19/09/2026) — repositorio inicializado y publicado.
- Remoto: `git@github.com:RVenegas7/sisv.git`, rama `main`. Llave SSH dedicada `~/.ssh/sisv_github` (registrada en la cuenta RVenegas7; entrada `github.com` en `~/.ssh/config`).
- Commit inicial `bbfe9e0` (backend + frontend + catálogos + vigilancia + migración legacy).
- No versionados (`.gitignore`): `.venv`, `node_modules`, dumps/backups legacy (`legancy/*.DMP|tgz|zip`), `legancy_conf/*.env` y `tnsnames.ora`, `borrar/`.

## 11. [PENDIENTE - REVISAR] Despliegue en producción (Proxmox 9.2)

- **Estado:** pendiente **revisar y explicar mejor**; el usuario no lo entiende por ahora.
- Qué significa (para decidir más adelante): cuando el sistema esté listo, pasará del equipo de desarrollo a un **servidor de producción**, que en este caso sería una máquina virtual con **Proxmox 9.2**. Allí PostgreSQL se instala **nativo** (sin Docker) y la base se exporta/importa con `pg_dump` (no con `mysqldump` como se planeaba antes).
- Se descarta por ahora mientras el proyecto siga en desarrollo local.

## 12. [PENDIENTE] Revisión de seguridad contra ataques

- **Estado:** pendiente (registrado 19/09/2026).
- Revisar y endurecer el sistema contra ataques, al menos:
  - **OWASP Top 10:** inyección (SQL/ORM), XSS, CSRF (ya hay token), autenticación/sesiones,
    exposición de datos sensibles, cabeceras de seguridad (HSTS, CSP, X-Frame-Options, etc.).
  - Backend Django: `DEBUG=False`, secretos por variable de entorno, `ALLOWED_HOSTS` restringido,
    límites de tasa (rate limiting) en `/api/auth/`, validación estricta de entradas en registros
    (CE 12: validación CIE por fecha, alcance multicentro, permisos).
  - Frontend: sanitización de salida, no exponer tokens en el cliente, manejo de errores sin fuga
    de info interna.
  - Revisar `requirements.txt` y dependencias npm por vulnerabilidades conocidas
    (pip-audit / npm audit).

## 13. [PENDIENTE] Responsive (celular / tablet / computador)

- **Estado:** pendiente (registrado 19/09/2026).
- Validar que la aplicación sea **responsiva**: probar y ajustar vistas en celular, tablet y
  computador (breakpoints de `styles.css`), especialmente:
  - Panel lateral (`aside.panel-lateral`) y navegación en pantallas pequeñas.
  - Tablas de registros, reportes y la matriz 13×2 del consolidado de vigilancia (scroll horizontal).
  - Formularios de carga (Nacimientos, Defunciones, Fichas) y selectores CIE.
  - `meta viewport` ya presente en `index.html`; revisar toques, zeugma de ancho y legibilidad.

---

*Registro creado el 12/09/2026.*