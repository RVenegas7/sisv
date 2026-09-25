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

## 4. [COMPLETADO] Territorio (estados, municipios, parroquias, comunidades) y ASIC

- **Estado:** **completado** (24/09/2026) — territorio real descargado de la APN y base auxiliar `territorio_apn` creada.
- **Completado:**
  - Modelo `ASIC` (parroquia sede, dirección, responsable, teléfono, email, establecimientos_adscritos,
    observaciones) con endpoints `/api/territorio/asic/` (GET filtrable + POST) y `/api/territorio/asic/<id>/`
    (GET/PATCH/DELETE; borrado bloqueado si hay centros asociados). CRUD restringido a `puede_configurar`.
  - `Organizacion` vinculada a ASIC (`Organizacion.asic` + `parroquia`); cada centro queda asociado a
    ASIC + parroquia + municipio + estado (derivado del ASIC). El perfil `/auth/me/` expone
    `organizacion.asic_id`/`asic_nombre`. `sembrar_demo` crea el ASIC demo y lo vincula al Hospital
    Central de Barquisimeto.
  - Comando `manage.py descargar_territorio_apn` (login + descarga Estado→Municipio→Parroquia→Comunidad
    desde la API de la APN; arg `--usuario/--clave` o env `APN_USUARIO/APN_CLAVE`, `--borrar`,
    `--sin-comunidades`).
- **Hecho (24/09/2026):** territorio completo cargado vía APN (credenciales de desarrollador `venegas`):
  `./.venv/bin/python backend/manage.py descargar_territorio_apn --usuario <dev> --clave <clave>` → en BD
  **24 estados / 335 municipios / 1.125 parroquias / 74.631 comunidades** (la API solo entrega 24 entidades;
  el 25/1.138 es teoría). Base auxiliar `territorio_apn` en `sis_postgres_dev` (5436) poblada con
  `manage.py exportar_territorio_pg` (estados/municipios/parroquias/comunidades normalizados + vista).

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
- **ETL a `vigilancia` (23/09/2026):** decisiones tomadas con el usuario y comando
  `importar_legacy_vigilancia` implementado (--modelo todos|epi12|epi15|mmi|violenta, --borrar,
  --limite, --desde, --todo-pais). **Alcance: solo el árbol de establecimientos de Lara**
  (raíces DES LARA=67754 y DPS LARA=3441583108 → **1.022 establecimientos**, cubre 575/577
  HORIGEN y 105.732/105.734 documentos tipo 1 ≈ todo el EPI-12 real):
  - **RENGLONTELE** (SIS-04/EPI-12) → `ConsolidadoSemanal` MORBILIDAD y MORTALIDAD con
    `FilaConsolidado` (matriz 13×2); los grupos `EDADES` legacy con HCATEGORIA=1 son los 13
    oficiales; los desbordes históricos ("Menor de 7 Días", "7 a 28 Días", "Menor de 2 años") se
    suman a su grupo y "MENORES DE 25 AÑOS" va a `edad_ignorada_h` (regla oficial Hombres).
    Mapeo curado **98 enfermedades legacy → EventoENO** en `vigilancia/legacy_mapeo.py`
    (`LEGACY_ENFERMEDAD_EVENTO`/`LEGACY_ENFERMEDAD_NOMBRE`/`GRUPO_EDAD_LEGACY`). Sin equivalente
    (se reportan como «no importados»): SÍNDROME VIRAL (70.979 filas), EMPONZOÑAMIENTO OFÍDICO,
    ONCOCERCOSIS, LEPRA, ACULIADURA DE ALACRÁN, URETRITIS NO GONOCÓCCICA y el código header 67972.
  - **RENGLON_EPI15** → nuevos modelos `ConsolidadoEpi15` + `FilaEpi15` (sin matriz de edad;
    `evento` nullable conserva el `nombre_legacy`). Infraestructura/modelos/migraciones nuevas.
  - **CASOS_MMI y M_VIOLENTA** → `FichaVigilancia` con `lote_id` LEGACY-MMI/LEGACY-VIOLENTA y
    `legacy_tabla`; geo por `ORG_GEOGRAFICA` + establecimiento por `DOCUMENTO.HORIGEN` / `CERTIFICADO`.
  - Organización destino: por nombre normalizado del establecimiento contra las `Organizacion`
    activas; si no aparece, se consolida en **«Legacy regional (histórico)»** (`codigo=LEGACY-LARA`,
    nivel REGIONAL) creada al vuelo. Consolidados con traza `legacy_tabla`/`legacy_documento`;
    re-carga sin `--borrar` es idempotente (los existentes se reusan). Pruebas sqlite-safe añadidas
    (77 totales backend).
- **Pendiente:** decidir el destino de los catálogos CIE legacy (`sismai."CIE10"` y asociados).
  Ver `legancy/analisis/INFORME_MIGRACION_LEGACY.md` §8-9.

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

## 8. [COMPLETADO] Mapa de modelos legados (`models_legacy.py`)

- **Estado:** completado (21/09/2026).
- **App** `legacy` en `backend/` con la generación automática y pruebas:
  - `manage.py mapear_legacy` → genera **`backend/legacy/models_legacy.py`** con un modelo
    `managed=False` por cada una de las **430 tablas/vistas** de `sismai`/`inbdlar1`/`legacy`/`historico`
    (equivalente a `inspectdb` pero con `db_table` calificado por esquema: `"sismai"."ESTABLECIMIENTO"`
    y columna `db_column` en original, porque el nombre de campo va en minúsculas). Todos verificados
    consultables por ORM (`objects.count()` sin errores en las 430).
  - Las clases duplicadas entre esquemas se distinguen con prefijo del esquema (ej. `TUsuarios` (inbdlar1)
    vs `LegacyTUsuarios`). Las tablas sin PK (casi todas en el legacy) reciben **PK nominal** en la primera
    columna, marcada en comentario, para permitir el ORM en solo lectura.
  - Genera también **`legancy/analisis/PRIORIDADES_LEGACY.md`**: inventario priorizado de las 430 tablas
    por tier: **P1 = 32** (dominio/negocio: ESTABLECIMIENTO, USUARIOS, territorio, CIE legacy y las fuentes
    de vigilancia por integrar como RENGLONTELE/CASOS_MMI/M_VIOLENTA/INFORME_EPI), **P2 = 185**
    (operativo/registro y espejos T_*), **P3 = 213** (catálogos/colas/config). Cada P1 con conteo exacto.
  - **Pruebas** `legacy/tests.py` (5, todas pasan): esquemas y total 430, centro 130659 (STATUS='I'),
    YASMINMORB ESTATUS=2, el mapa coincide 1:1 con el catálogo real, y **lectura/escritura en un esquema
    temporal** `zz_test_legacy` que se crea y elimina en la propia prueba (no altera el flujo del sistema;
    correr con `DJANGO_DB_ENGINE=sqlite` para evitar crear base de pruebas en PostgreSQL).
- **Uso previsto:** lectura/auditoría del legado migrado y trampolín del ETL hacia los modelos nuevos
  (`registros`/`vigilancia`/`seguridad`). Los catálogos P1 son la fuente directa para poblar
  `seguridad.Organizacion` (centros) y `territorio.DivisionTerritorial`.

## 9. [COMPLETADO] Lint y pruebas automatizadas

- **Estado:** completado (23/09/2026).
- Backend (Django/DRF) usando `DJANGO_DB_ENGINE=sqlite manage.py test`:
  `./.venv/bin/python backend/manage.py test registros seguridad vigilancia territorio catalogos legacy`
  → **77 pruebas, todas pasan** (72 nuevas + 5 de legacy, 24/09/2026).
  - Base compartida en `backend/tests_sisv.py` (territorio, orgs, usuarios demo, CIE y eventos ENO con
    `setUpTestData`). Para descubrir las pruebas fue necesario añadir `__init__.py` a las apps
    `registros`, `seguridad`, `territorio` y `catalogos` (eran paquetes namespace).
  - `seguridad/tests.py`: login/logout/me, **throttle 429** del login, permisos org/usuarios.
  - `registros/tests.py`: CRUD nacimientos/defunciones/fichas, alcance CENTRO/REGIONAL/todos,
    validación CIE por `FECHA_CORTE_CIE11`, obligación de subgrupo, dashboard por `anio`(todos/particular),
    export CSV con BOM, permisos de configuración.
  - `vigilancia/tests.py`: `eventos-eno`, creación de consolidado que siembra filas, org forzada en
    CENTRO, elección de destino en REGIONAL, org obligatoria en niveles superiores, alcance, permisos,
    export CSV.
  - `territorio/tests.py`: árbol, ruta territorial y permisos CRUD de ASIC.
  - `catalogos/tests.py`: búsquedas CIE-10/CIE-11 y mapeos.
- Frontend (Vitest): `npm test` en `frontend/` → **13 pruebas pasan** (2 archivos).
  - `frontend/src/utils/cie.test.js`: `validarCIE` (CIE-10 obligatorio en históricos, subgrupo
    obligatorio), `versionParaFecha` y `seleccionDesdeRegistro` (con `vi.mock` de la API).
  - `frontend/src/api/sisv.test.js`: `iniciarSesion` (setea CSRF), `listarNacimientos`,
    `exportarReportes` (blob) con `./axios` mockeado.
  - Nada de lint configurado aún (no aplica en este repo); verificación manual sigue siendo
    `manage.py check` y `npm run build` (ambos OK tras los cambios).

## 10. [COMPLETADO] Repositorio Git

- **Estado:** completado (19/09/2026) — repositorio inicializado y publicado.
- Remoto: `git@github.com:RVenegas7/sisv.git`, rama `main`. Llave SSH dedicada `~/.ssh/sisv_github` (registrada en la cuenta RVenegas7; entrada `github.com` en `~/.ssh/config`).
- Commit inicial `bbfe9e0` (backend + frontend + catálogos + vigilancia + migración legacy).
- No versionados (`.gitignore`): `.venv`, `node_modules`, dumps/backups legacy (`legancy/*.DMP|tgz|zip`), `legancy_conf/*.env` y `tnsnames.ora`, `borrar/`.

## 11. [PENDIENTE - REVISAR] Despliegue en producción (Proxmox 9.2)

- **Estado:** pendiente **revisar y explicar mejor**; el usuario no lo entiende por ahora.
- Qué significa (para decidir más adelante): cuando el sistema esté listo, pasará del equipo de desarrollo a un **servidor de producción**, que en este caso sería una máquina virtual con **Proxmox 9.2**. Allí PostgreSQL se instala **nativo** (sin Docker) y la base se exporta/importa con `pg_dump` (no con `mysqldump` como se planeaba antes).
- Se descarta por ahora mientras el proyecto siga en desarrollo local.

## 12. [COMPLETADO] Revisión de seguridad contra ataques

- **Estado:** completado (23/09/2026). Resumen de lo aplicado:
  - **Autenticación global en la API:** `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES` =
    `IsAuthenticated`; solo `LoginView`, `LogoutView`, `MeView`, `CsrfView` y `ApiRoot` quedan
    públicos (`AllowAny`). Sin sesión, cualquier dato devuelve `403` (verificado en vivo con curl).
  - **Rate limiting en `/api/auth/login/`:** `seguridad/throttle.py` — 5 intentos/5 min por IP+usuario,
    bloqueo de 15 min → `429`. Probado en unittest.
  - **CSRF:** se quitó `csrf_exempt` de login/logout; el frontend ya envía `X-CSRFToken`
    (interceptor de axios). Verificado el flujo completo login→datos vía curl (cookie + CSRF + Origin).
  - **Sesiones y cabeceras:** `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE="Lax"`,
    `CSRF_COOKIE_SAMESITE="Lax"`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_REFERRER_POLICY="same-origin"`,
    `X_FRAME_OPTIONS="DENY"`, HSTS cuando `DEBUG=False`.
  - **Permisos finos ya operativos:** crear/editar → TRANSCRIPTOR/CODIFICADOR/DIRECTOR/super;
    eliminar/configurar → DIRECTOR/super; EPIDEMIÓLOGO solo lectura (también en consolidados y ASIC).
    Todo cubierto por las pruebas de §9.
  - **Dependencias auditadas:** `pip-audit` → `sqlparse>=0.6.0` en `requirements.txt` (**0 vulnerabilidades**);
    `npm audit` → `vite ^8.3.0`, `@vitejs/plugin-react ^6.1.1`, `react-router-dom ^7.18.4`
    (**0 vulnerabilidades**). Frontend sin `dangerouslySetInnerHTML` (grep verificado).
  - **Pendiente consciente:** CSP no activado (Vite inyecta estilos; se revisaría en producción Proxmox,
    sección 11). Secretos de BD/sesiones siguen vía `.env` (dotenv ya cargado).

## 13. [COMPLETADO] Responsive (celular / tablet / computador)

- **Estado:** completado (19/09/2026).
- `meta viewport` ya existía en `index.html`. Breakpoints en `styles.css`:
  - **≤1100px (tablet apaisado):** panel lateral reducido a 220px y `main` con menos padding.
  - **≤820px (tablet vertical / celular):** layout de una columna; el `aside.panel-lateral` pasa a
    **drawer deslizable** (`transform: translateX`) con **botón hamburguesa** `menu-boton` fijo y
    `menu-backdrop` para cerrar al tocar fuera; los enlaces de navegación cierran el menú al hacer clic.
    Las tablas (registros, reportes, matriz 13×2, tabla-grupos, tabla-mensual) toman `min-width: max-content`
    dentro de contenedores con **scroll horizontal** (`overflow-x: auto`). Inputs/selects/textareas a
    **16px** (evita el zoom automático de iOS), `.btn-mini` con área táctil mínima y `.pie-form` en columna
    (botones a ancho completo).
  - **≤480px (celular):** `.grid` y `.filtros` a una columna (formularios de carga), tarjetas apiladas,
    stats a ancho completo, jerarquía tipográfica del título y acciones de jerarquía sin flotar.
- Verificación: `npm run build` (vite) sin errores.

## 14. [EN CURSO] Trabajo del 24/09/2026 — codificación pendiente, solo-Lara y sin demo

- **Roles nuevos:** `ROL_VIGILANCIA` (escribe: crear/editar registros, como
  TRANSCRIPTOR/CODIFICADOR/DIRECTOR) y `ROL_SECRETARIA` (solo lectura, no escribe/edita/elimina/configura)
  agregados a `Perfil.ROL_CHOICES` (`backend/seguridad/models.py`), `permisos_de` actualizado y migración
  `0003_alter_perfil_rol` aplicada. `Seguridad.jsx` muestra las descripciones de los roles.
- **Solo datos del estado Lara + sin data demo (guardado):**
  - Criterio acordado: **Centro Lara + domicilio Lara** — eliminar solo los registros cuyo centro de salud
    **no** es del árbol de Lara (raíces DES LARA=67754 y DPS LARA=3441583108) y los de residencia ≠ Lara;
    las defunciones en domicilio con residencia Lara (84.893) se conservan. `estado` en los legacy es la
    **residencia** (madre/fallecido), no el centro.
  - Comando: `backend/registros/management/commands/limpiar_legacy_no_lara.py` (dry-run por defecto;
    `--ejecutar` aplica). **Ejecutado.** Conteos finales: **Nacimientos 438.577, Defunciones 171.115,
    Fichas 0, Consolidados 0**. Se eliminaron los lotes `LOTE-*`, las fichas demo y el consolidado sin
    `legacy_tabla`; **usuarios y organizaciones demo se conservan** (admin, laraepid, hbcentral,
    codificadora, epi, dir, tester_legacy).
- **Bandeja de codificación (`codificacion_pendiente`):** las **49.162 defunciones** pendientes de
  CIE se ven en **`/defunciones` (CargaDefunciones.jsx)** con el filtro **«Solo pendientes de
  codificación»** (checkbox sobre la tabla). Backend: endpoint de defunciones acepta `?pendientes=1`
  (filtra `codificacion_pendiente=True`); el serializer de `Defuncion` expone `codificacion_pendiente`
  y `cie10_legacy`. El codificador abre cada registro con **Editar** y aplica `CIESearch`
  (versión por fecha del evento); al guardar, `validar_seleccion_cie` marca `codificacion_pendiente=False`.
- **Exportar BDs a la oficina (24/09/2026):** `dumps/sis_salud_db_20260924.dump` (176M) y
  `dumps/territorio_apn_20260924.dump` (594K) generados con `docker exec sis_postgres_dev pg_dump -U
  sis_user -Fc` + `docker cp` a `dumps/`.
- **Pendiente (próxima sesión):**
  - Módulo CRUD de **ASIC ↔ comunidades del territorio**: asociar a cada ASIC sus comunidades
    (`DivisionTerritorial` nivel COMUNIDAD bajo la parroquia sede), endpoint + UI.
  - Reporte **comparativo entre dos años por semana epidemiológica** con gráfico: series **MMI**
    (fichas materno-infantil de lotes LEGACY-MMI/VIOLENTA), **M** (muertes maternas,
    `embarazo_o_puerperio=True`), **Nacimientos** y **Muertes** (defunciones).
  - Actualizar el repositorio (git add/commit/push) al cerrar esta tanda.

## 15. [COMPLETADO] ASIC ↔ comunidades del territorio y reporte comparativo anual

- **ASIC ↔ comunidades (completado 24/09/2026):**
  - Modelo: M2M `ASIC.comunidades` → `DivisionTerritorial` (nivel COMUNIDAD) relacionada como
    `asics_territoriales`; migración `territorio/0003_asic_comunidades` aplicada.
  - API: `_serializar_asic` expone `comunidades` (id/nombre/codigo) y `comunidad_count` (con
    `prefetch_related`); POST y PATCH de `/api/territorio/asic/` aceptan `comunidades` (lista de ids o
    CSV), validando que sean nivel COMUNIDAD (400 con mensaje si no). `activo` y `centros` se conservan.
  - Frontend: página **`/asic`** (`Asic.jsx`, grupo Sistema) con formulario de creación/edición
    (código, nombre, parroquia sede por cascada estado→municipio→parroquia, establecimientos, director,
    teléfono/email, activo), **checkbox de comunidades** de la parroquia seleccionada y tabla de ASIC con
    ubicación, nº de comunidades y centros. Edición precarga el árbol territorial según la sede.
  - Permisos: administrar ASIC sigue siendo solo `puede_configurar` (DIRECTOR/superusuario).
  - Pruebas: `territorio/tests.py` ampliado (11 pruebas) — asociar comunidades, rechazo de ids de otro
    nivel, limpieza con lista vacía.
- **Reporte comparativo anual por semana (completado 24/09/2026):**
  - Endpoint **`/api/registros/reportes/comparativo/?anio1=&anio2=`** (`ReporteComparativoView`):
    series **nacimientos**, **muertes** (defunciones), **muertes_maternas** (M, `embarazo_o_puerperio=True`)
    y **mmi** (fichas de lotes `LEGACY-MMI`/`LEGACY-VIOLENTA`), por semana epidemiológica (ISO, 1–53),
    respetando el alcance del usuario. Devuelve también totales por año y lista de series listas para el gráfico.
  - Frontend: sección **«Comparativo anual por semana epidemiológica»** en `/reportes` (Reportes.jsx):
    selector de dos años, y por cada serie un `<details>` con resumen (rotulo + totales por año) y un
    **gráfico de líneas SVG** (`GraficoLineas`, sin dependencias): `anio1` línea sólida, `anio2` punteada,
    ejes S semana y leyenda de años. Los 0 se rellenan para las 53 semanas.
  - Nota: la serie **MMI aparece en 0** porque las fichas `LEGACY-MMI`/`LEGACY-VIOLENTA` aún no se cargan
    (el ETL de `CASOS_MMI`/`M_VIOLENTA` → `FichaVigilancia` no se ha ejecutado en producción de datos;
    ver §5); la infraestructura del reporte ya la contempla.
  - Prueba backend `test_reporte_comparativo` (año1=2023 con un nacimiento, series y totales correctos).
- **Estado global del día:** bandeja de codificación (checklist en `/defunciones`), solo Lara + sin demo,
  roles VIGILANCIA/SECRETARIA, exportación de BDs, ASIC↔comunidades y reporte comparativo ya están en el
  código; pendiente solo **actualizar el repositorio** y (opcional) la corrida completa del ETL de vigilancia.

## 16. [EN CURSO] Punto crítico EVENTOS_SINC y verificación MM/MN (24/09/2026)

- **Punto crítico EVENTOS_SINC → NO RESUELTO por el envío del 22/09:**
  - El último envío semanal (`routlar1_2292026_1238.ZIP`, 22/09/2026 12:38) fue importado a
    `sis_postgres_dev` (82/82 tablas `legacy`, 27.472 filas) y verificado: consolida **PERIODO=37/2026**
    (T_RESUMEN 10 filas), pero **NO contiene el backlog** — `T_RENGTELE` 5.520 renglones (no millones) y
    `T_EVENTOS` cubre solo 2026-09-16→22 (9.496 filas). El espejo `SISMAI.EVENTOS_SINC` sigue con
    **3.372.065 filas estancadas desde 2026-08-27 12:53:50** (3.359.781 del 27/08 con STATUS NULL);
    `EVENTOS_DBLINK` 2.326.848 y `HISTORICO.EVENTOS_RESP` 1.927.311, ambos 100% STATUS=0.
  - **Scripts de diagnóstico (solo lectura; NO corrigen):** `migracion/verificar_sinc_eventos_sinc.sql`
    (8 secciones: cola, DBLINK/RESP, bitácoras, errores, sobres TEMP, veredicto) y
    `migracion/verificar_sinc_live.sh` (conexión SSH a 192.168.5.200 con sshpass/expect/manual). Validados
    contra el espejo Oracle XE; **pendiente ejecutarlos en vivo** en el servidor (requiere red de
    oficina / VPN y herramienta de contraseña).
  - **Scripts de corrección (24/09/2026, listos para el servidor):**
    `migracion/corregir_sinc_eventos_sinc.sql` + `migracion/corregir_sinc_live.sh`. El SQL hace en
    orden: [A] **respaldo puntual idempotente** de la cola (`EVENTOS_SINC_BK_<AAAA-MM-DD>`, verifica la
    fecha del servidor con `SYSDATE`, no duplica si ya existe y contrasta el conteo contra `EVENTOS_SINC`);
    [B] recompila el esquema `SISMAI` (`DBMS_UTILITY.COMPILE_SCHEMA`) y lista inválidos antes/después
    (referencia: 16 objetos); [C] indicadores de remediación (cola →0 y `TEMP.*` con semanas 29-36);
    [D] **purga comentada** (`TRUNCATE EVENTOS_SINC DROP STORAGE`) que se habilita SOLO manualmente cuando
    el sitio central confirme que la carga del 27-08 llegó por otra vía. Validado el flujo [A]/[B] contra
    el espejo Oracle XE (`sis_oracle_legacy`), respaldo de prueba eliminado después. Ejecutar en vivo con
    `./migracion/corregir_sinc_live.sh` (sshpass/expect/manual), mejor como usuario DBA `oracle`.
  - **Checklist para el día del acceso (oficina/VPN):** 1) `verificar_sinc_live.sh` (estado actual);
    2) si procede, `corregir_sinc_live.sh` (respaldo + recompilar + indicadores); 3) confirmar con el
    sitio central el «último martes bueno» y si llegó el `DOCUMENTO_DENGUE` del 27-08; 4) restaurar el
    componente consumidor (`RoutLar1`/`SincFich`/`plcer1.sql`, `/home/salud/bin`) o el cron, antes de
    descomentar [D]; 5) verificar el envío del martes 29/09 (que lleve el backlog en `TEMP.T_*`).
  - **Pendiente: revisar la generación de los 5 archivos del ZIP del martes** (`routlar1_*.ZIP`):
    `bloqlar1.log`, `copyhistlar1.log`, `repllar1.log`, `routlar1.log` y `routlar1.dmp` (los 5 presentes
    en todos los ZIP de `enviados/`). Verificar en el servidor que el proceso que los produce
    (`RoutLar1`/scripts de `/home/salud/bin`, mtime 2020 según informe §5.1) sigue generándolos
    correctamente el día del envío y que `routlar1.dmp` no crece con el backlog.
  - **Pendiente: revisar los scripts de sincronización en `192.168.5.200` y el archivo que generan
    (mañana en la oficina):** el nivel central indica que **desde legacy hay que correr la sincronización**
    y que **esta genera un archivo**; revisar ese archivo generado. El paso de esa sincronización que
    **falló fue «nacimientos»**: no consiguió el script/archivo que **orquesta los demás** (falta el
    componente que ejecuta todo lo demás, tipo `RoutLar1`/`plcer1.sql` según informe §5.1/§6.1).
  - **Pendiente: definir dónde queda el respaldo de la cola (espacio por red):** la copia de los ~3,37 M
    filas de `EVENTOS_SINC` (≥ ~1-2 GB) se haría **en el equipo local donde corremos los scripts**
    (115 GB libres en `/home`), transfiriéndola **por red desde el servidor** (SSH/scp, el server está en
    `192.168.5.200`); no hay share SMB/NFS actualmente. Confirmar mañana si el servidor permite `scp`
    de la tabla exportada (por ejemplo `exp ... tables=EVENTOS_SINC file=colon_28.X.dmp` y traerla por
    SSH) o si el acceso por red es viable en oficina.
  - **Riesgos de la corrección en vivo (y sus mitigaciones, 24/09/2026):** el script **nunca toca** el
    esquema `TEMP.*` (lo que se exporta al central) ni modifica la cola original (solo la lee y copia);
    la única operación destructiva ([D] TRUNCATE) queda comentada y manual. Los tres riesgos residuales
    reales son: (a) **espacio/undo del respaldo** — copiar 3.37M de filas consume tablespace; mitigado con
    el pre-check `A.0` (listado de tablespaces con <2 GB libres: si no hay espacio, el CTAS falla limpio y
    se detiene, no rompe la app); (b) **`COMPILE_SCHEMA` bloquea objetos en uso** — mitigado con
    advertencia de ejecutar en **ventana de mantenimiento** (fuera de operación y del `exp` diario de las
    13:00); (c) **colisión con el respaldo lógico diario de las 13:00** (`exp respaldo/respaldo`, ~1.2 GB
    y undo_retention=900 s con riesgo ORA-01555) — mitigado ejecutando la corrección en madrugada o lunes
    tarde. En todos los casos el peor escenario es un error controlado (ORA-0165x/ORA-1555) que **no
    daña** el sistema ni el envío; los objetos que sigan inválidos tras [B] quedan igual que ahora.
  - **Pendiente (seguimiento 29/09/2026):** el envío automático del martes 29/09 **solo llevará lo que esté
    en `TEMP.T_*`** (lo nuevo desde el último ruteo); **sin intervención manual en el servidor (reprocesar
    `EVENTOS_SINC` / migración Fase 0 del PLAN_CORTE) el backlog NO llegará** al nivel central.
- **Verificación MM/MN con la Lcda (24/09/2026):** reporta **MM=0 y MN=228** acumulado 2026→semana 37.
  - Hallazgo: **la BD SISV tiene defunciones solo hasta el 27/08/2026** (`sismai.CERTIFICADO`: max
    `FECHAOPERACION` 16/09, max `FECHA_M` 27/08) — el mismo corte del punto crítico. Semanas 36-37 sin datos.
  - Con la data existente a 2026→SE35: MM (flag `embarazo_o_puerperio`) = **7** (todas pendientes de
    codificación, 6 Lara + 1 Portuguesa), MN (edad 0-27 días con `fecha_nacimiento`) = **213**. No cuadra
    con MM=0/MN=228: faltan las semanas 36-37 (~400 defunciones) y ~15 defunciones neonatales no
    clasificables (sin fecha de nacimiento ni CIE, `codificacion_pendiente=t`).
  - **Pendiente:** el tablero/reportes no exponen **MN**. Adicionar serie **`muertes_neonatales`** (edad
    0-27 días) a `ReporteComparativoView`/dashboard y considerar MM=**codificadas/confirmadas** (hoy el
    reporte usa el flag bruto del certificado, que incluye puerperio/pendientes). Reconciliar con la Lcda
    qué fuente oficial usar (ENO semanal vs certificados).
- **MM/MN implementado (24/09/2026):** serie `muertes_neonatales` (MN, 0-27 días) + MM restringida a
  **codificadas** (`codificacion_pendiente=False`) en `ReporteComparativoView`/`DashboardView`; tarjetas
  «MM codificadas»/«MN (0-27 días)» en `Tablero.jsx`; ayuda y `details` en `Reportes.jsx`. Auditoría
  `auditoria/*.csv` (6 pendientes + 1 codificada + 213 MN) con regenerador `auditoria/exportar_auditoria_mm_mn.py`.
  **Descuadra con la Lcda (MM=0/MN=228)** por el corte 27/08 (faltan SE36-37). Verificado: 77/77 tests + build.
- **Organizaciones asignadas a legacy (24/09/2026):** comando `asignar_organizacion_legacy [--ejecutar]` crea
  org CENTRO bajo Dir. Epidemiología Lara por cada establecimiento del árbol Lara presente en los registros
  (414 creadas, 182 reutilizadas/deduplicadas por nombre normalizado) y asigna `organizacion_id` a
  **nacimientos 438.577 / defunciones 86.223** (fichas legacy no traen centro); las 84.892 defunciones de
  domicilio quedan sin org y agrupan por residencia (Lara). El dashboard/reportes ahora agrupan
  `por_estado` por **`organizacion__estado`** (evento) con fallback al estado del registro
  (helper `_por_estado_evento`, COALESCE) → todo Lara; `por_centro` muestra los centros reales. Backend
  reiniciado (pid 34702). Verificado: 77/77 tests + build + dashboard 2026 `{'Lara': 15629}`.
- **Reporte «residentes de otros estados» (24/09/2026):** endpoint `GET /api/registros/reportes/residentes/`
  (`desde`/`hasta`) + vista `ResidentesOtrosEstadosView` (helper `_residentes_otros_estados`) que agrupa
  nacidos/fallecidos ocurridos en el estado predeterminado (Lara, derive del alcance del usuario) **con
  residencia en otro estado**, por estado de residencia **mayor→menor**. En `Reportes.jsx` checkbox
  «Residentes de otros estados (evento en Lara)» (usa `desde`/`hasta` del filtro, respeta alcance).
  2026 en BD: nac 139 residentes externos (Yaracuy 95, Portuguesa 28…) y def 155 (Portuguesa 77,
  Yaracuy 21…). Nota: en nacimientos `estado` hereda la residencia de la madre solo cuando no hay
  localidad de ocurrencia, por eso el granular de «residencia» es aproximado.
- **`repllar1.log` ausente en envíos post-corte (24/09/2026):** en `enviados/` TODOS los ZIP pre-críticos
  (15/10/2025…04/08/2026, 10 archivos) traen **5 archivos**; el contenido de `repllar1.log` (24.237 B) es la
  bitácora de la fase de **replicación/poblado de `TEMP.T_*`** (crea tablas + conteo por sobre que coincide
  exacto con los `filas exportadas` de `routlar1.log`). Los envíos del **08/09, 16/09 y 22/09** solo traen
  **4 archivos (sin `repllar1.log`)** y `routlar1.log`/`bloqlar1.log` pasan a español (cambió NLS_LANG).
  → **SÍ se relaciona con el hallazgo crítico:** la desaparición del log coincide con el corte del motor de
  sincronización (27/08/2026): esa fase ya no se ejecuta ni deja bitácora en el envío. **Monitorizar en el
  próximo envío:** el ZIP debe llevar los 5 archivos; si falta `repllar1.log`, la replicación no corrió.
- **Línea base pre-crítica validada → contrato del sobre DETERMINADO (24/09/2026, tarea 3):** importada
  `enviados/routlar1_482026_1526.ZIP` (**04/08/2026, SE-32**, último envío completo pre-corte) en Oracle XE
  (`gvenzl/oracle-xe:11.2.0.2`, contenedor `sis_oracle_legacy`, esquema `IMPORT29`: 82 tablas `T_*`) y
  contrastada con espejo `sis_postgres_dev`. **Hallazgo clave:** el sobre NO se arma por fecha del
  certificado; replica **el estado consolidado de las filas que tuvieron ≥1 evento en `EVENTOS_SINC`
  durante la ventana del ruteo** — `T_EVENTOS` del propio ZIP es el manifiesto exacto de lo que viaja
  (columnas `TABLA`+`ID`+`EVENTO` 1=INSERT/2=UPDATE+`FECHA`, ventana 29/07→04/08; también 3=DELETE,
  `STATUS`, `AMS`). **Regla validada al 100%:** «viaja la fila si su **último** evento en la ventana es
  INSERT(1) o UPDATE(2); si el último es DELETE(3) no viaja» → reproduce EXACTO los conteos del
  `routlar1.log`: `CERTIFICADO` 398, `CERTNACIMIENTO` 422, `DOCUMENTO` 413 (2 deletes excluidos),
  `RENGLONTELE` 5746 (32 deletes excluidos), `CAUSA_M`/`RENGLON_EPI15`/`CASOSMMI` 198/429/24,
  `MONITOR_BASEDEDATOS` 49, etc. (23 tablas con filas; `T_AUDITORIA` 9118 viaja completa sin eventos).
  El sobre del 04/08 incluye además pendientes acumulados previos (5 certificados con último evento fuera
  de la ventana RESP) → usa la cola **completa** (`EVENTOS_SINC`), no solo la ventana RESP. Todos los IDs
  existen en PG (`CERTNACIMIENTO` 438.910 / `CERTIFICADO` 173.391): 422/422 y 398/398. **Comando
  construido:** `manage.py exportar_rutalara --semana 2026-W32` (o `--desde/--hasta`; sin rango = cola
  completa; `--eventos <schema.tabla>`, default `sismai.EVENTOS`; `--salida DIR`; `--solo-eventos`).
  Emite ZIP con `T_EVENTOS.csv` + CSV por tabla `T_*` (columnas del spec
  `backend/registros/data/rutarala_spec.json`, de `schema_routlar1.sql`) + `_conteos.txt`. Validado con el
  manifiesto del sobre cargado en `sismai.eventos_se32` (9.862 eventos): 9531 filas viajeras, conteos
  idénticos al sobre salvo `RENGLONTELE` 5741 vs 5746 (5 renglones eliminados después del cierre del
  sobre, verificados con evento 1+3 del 04/08 en `EVENTOS_RESP`). El generador T_* de SISV debe emitir por
  eventos de modificación (INSERT/UPDATE + fechas), no por `FECHAOPERACION`/`FECHADEFUNCION`, y enlaza
  directamente con el punto crítico (la cola `EVENTOS_SINC` estancada es la fuente de verdad del sobre).
  Los ZIP del 08/09/16/09 y 22/09 (4 archivos) son posteriores al corte y **no** deben usarse como
  referencia.
- **Validación automática `exportar_rutalara --comparar` (24/09/2026):** el comando acepta
  `--comparar <routlar1_*.ZIP>` y parsea su `routlar1.log` para comparar conteos por tabla. Contra el ZIP
  SE-32 con el manifiesto completo (`sismai.eventos_se32`, 9.862 eventos): **81/83 tablas coinciden
  EXACTO** (T_EVENTOS 9862, CERTIFICADO 398, NACIMIENTOS 422, RESUMEN 9, USUARIOS 7, etc.). Dos DIF
  esperados y explicados: (1) `T_AUDITORIA` 9118 vs 0 — viaja **completa** sin eventos (bitácora), la
  fuente `AUDITORIA` no está espejada en `sismai` (falta por mapear/copiar en SISV); (2) `T_RENGTELE`
  5746 vs 5741 — 5 renglones con evento 1+3 del 04/08 (borrados justo después del corte; el sobre refleja
  el estado a 15:26 y el espejo PG el estado actual). El contrato queda **cerrado**: la regla «último
  evento 1/2 en el período = viaja» es la correcta. `T_EVENTOS` del generador lleva TODOS los eventos del
  período (1/2/3), como el manifiesto real.

---

*Registro creado el 12/09/2026.*