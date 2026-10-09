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
- **EPI-15 visible en la app (24/09/2026):** añadido `GET /api/vigilancia/epi15/`,
  `GET /api/vigilancia/epi15/<id>/` y `GET /api/vigilancia/epi15/exportar/` (lista/detalle/CSV,
  respetan alcance, solo lectura — datos del legado `RENGLON_EPI15`). Frontend: menú
  **Registros → «Consolidado EPI-15»** (`/vigilancia/epi15`, página `Epi15.jsx`): filtros
  año/semana, lista de consolidados, detalle con eventos (primeras consultas / subsiguientes /
  columna X / totales) y exportar CSV. Verificado con el cliente de pruebas de Django: 15.855
  consolidados (2026-S8 AMB. AUYAMAL), `manage.py check` OK, `npm run build` OK.

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

## 14. [COMPLETADO] Trabajo del 24/09/2026 — codificación pendiente, solo-Lara y sin demo

> **Cierre (02/10/2026):** todo lo de esta tanda está en el código. Lo que aquí figuraba como
> «pendiente (próxima sesión)» lo cerraron §15 (ASIC↔comunidades y comparativo anual), §17
> (diagnóstico del servidor) y las secciones siguientes. Solo queda el paso manual de actualizar
> el repositorio, que no es trabajo de esta lista.

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
  codificación»** (checkbox sobre la tabla) y en el nuevo módulo dedicado **`/codificacion`**
  (**Codificacion.jsx**, menú **Registros → Codificación**). Backend: endpoint de defunciones acepta
  `?pendientes=1` (filtra `codificacion_pendiente=True`); **`GET /api/registros/codificacion/`**
  (`CodificacionView`) devuelve `resumen` de pendientes por módulo (defunciones/nacimientos/fichas,
  respetando alcance) más la lista filtrable del módulo (`?modulo=&q=&anio=&pagina=&por_pagina=`,
  paginado). El serializer de `Defuncion` expone `codificacion_pendiente`, `cie10_legacy` y ahora
  `cie11_sugerido` + `cie11_sugerido_detalle` (cross-walk). La bandeja abre cada registro con la
  `SeccionCIE` reutilizable (versión por fecha del evento + `CIESearch`), muestra el CIE legacy y la
  sugerencia, y **edita solo los campos CIE** (PATCH parcial de `version_cie`/`cie10`/`cie11`); al
  guardar, `validar_seleccion_cie` marca `codificacion_pendiente=False`. Se corrigió `_validar_cie`
  para PATCHes parciales sin `fecha_evento` en el payload: ahora usa la `fecha_evento` de la instancia
  para decidir la versión exigida.
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

## 16. [SUPERADO POR §17 Y §22] Punto crítico EVENTOS_SINC y verificación MM/MN (24/09/2026)

> ⚠ **DATO DESACTUALIZADO (25/09/2026):** el «espejo `SISMAI.EVENTOS_SINC` con 3.372.065 filas
> estancadas desde 27/08» de este punto ya **no describe la cola viva**. Verificado en el servidor
> real: la tabla fue **DROP y recreada el 21/09 09:08:37** y hoy tiene **16.741 filas**; en
> PostgreSQL la tabla `sismai.EVENTOS_SINC` **ya no existe**. El backlog de 3,37 M solo consta en
> los dumps de los ZIP. Ver **§17** (diagnóstico en vivo del 25/09/2026).

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

## 17. [DIAGNÓSTICO CERRADO — el seguimiento vive en §22] Diagnóstico en vivo del servidor SISMAI (25/09/2026)

Trabajo realizado **en el servidor real** `192.168.5.200` (Oracle 10.1.0.3.0, SID `lar1`), con
acceso SSH de solo lectura. **No se ejecutó ningún DDL ni DML en producción.** Continúa y
**corrige** lo registrado en §16.

### 17.1 La cola viva ya NO tiene el backlog — fue destruida

- `SISMAI.EVENTOS_SINC` tiene **16.741 filas**, todas con `FECHA = 2026-09-21 09:08:37`
  (`REG_VACUNACION` 9.876, `PACIENTE_FICHA_EPI` 5.226, `PACIENTE_COND_ESPE` 1.639; `STATUS` NULL).
- El objeto (y `HISTORICO.ERRORES_SINC`) fue **creado** el `2026-09-21 09:08:37` → coincide con
  `SincFich/crear.sql`, que hace `DROP TABLE` y recrea. **No fue un TRUNCATE ni un drenaje.**
  Los 3,37 M de §16 **ya no existen en la cola viva**; el único soporte local son los ZIP.
- `SISMAI.EVENTOS_SINC` **no tiene ninguna restricción ni índice** (`USER_CONSTRAINTS` y
  `USER_INDEXES` vacíos): sin clave única `(TABLA,ID)`, cualquier reejecución duplica en silencio.
- Sin eventos posteriores al 21/09: el motor sigue sin programación visible en el servidor Linux.
- Espejo en PostgreSQL (verificado 25/09): `sismai."EVENTOS"` **0**, `legacy."T_EVENTOS"` 7.802,
  `inbdlar1."T_EVENTOS"` 18.680 → **PG no contiene el backlog**; no sirve como sustituto.
  (Nota de nombres: el esquema es legacy con mayúsculas, requiere comillas dobles en psql.)

### 17.2 Los ZIP del 21/09 capturaron el backlog, pero no prueban su recepción

| ZIP | hora | contenido relevante |
|---|---|---|
| `routlar1_2192026_854_sincdoc.ZIP` | 09:02 | `T_EVENTOS=3.391.421` |
| `routlar1_2192026_854_sincnata.ZIP` | 09:05 | `T_EVENTOS=3.391.421`, tablas de natalidad = **0** |
| `routlar1_2192026_854_sincmort.ZIP` | 09:07 | `T_EVENTOS=665.254`, `T_CERTMORT=136.210` |

Los tres son **exportaciones, no mecanismos de ejecución**. Secuencia: 09:02–09:05 capturan
3.391.421 eventos, y la cola se recrea a las **09:08:37** → consistente con una captura del
backlog, pero **no demuestra que el nivel central lo recibiera**. `sincmort` terminó con
`ORA-01408` no fatal.

> **Contexto del usuario (25/09/2026):** el nivel central **sí ha recibido los comprimidos de los
> martes**. La instrucción fue «correr la sincronización desde el menú»; eso se ejecutó el
> **lunes 21/09** y lo que falló fue **solo la sincronización de natalidad**, por no encontrar el
> orquestador. → **La carga del backlog no es el problema pendiente**; el pendiente es natalidad y
> el motor. Queda por confirmar si el central recibió además el sobre del lunes 21/09.


### 17.3 Natalidad: falta el paso de encolado, no el exportador

- No existe `routnata.sql`; la guía oficial indica que la sincronización se dispara desde el menú
  Windows de `SistemaTransferencia.exe`. `cr_repli_nata.sql` solo crea `TEMP.*` desde eventos
  **ya encolados** → el fallo fue el encolado previo.
- Alcance del encolado (calculado en vivo, solo lectura): `CERTNACIMIENTO` 429.577,
  `NAC_MADRE` 429.594, `NAC_RNACIDO` 429.583, `NAC_ANULADOS` 6.398 → **1.295.152 eventos**.
  Hay **320 certificados** 2010+ sin madre o sin recién nacido que el criterio original no envía
  (decisión funcional, no se tocó).
- Defectos de los scripts originales `plcna1/plnma1/plnrn1/plnan1`: sin guarda de duplicados,
  `V_I NUMBER(3)` sin inicializar (nunca hay commit → 1,3 M de filas en una transacción),
  `plcna1` incrementa `V_I` dos veces, y `EXCEPTION...GOTO M_MODIFICA` reintenta en bucle infinito.
- **Candidato no destructivo creado y validado: `migracion/encolar_natalidad_legacy.sql`**
  (modo seguro por defecto `V_EJECUTAR:=0`; dedup por `MINUS`; lote 5.000; sin `GOTO`).
  **NO ejecutado contra `SISMAI.EVENTOS_SINC`.** Validado solo contra tablas de prueba del usuario
  `RESPALDO`: dry-run 0 escrituras → 1ª corrida 29.683 → 2ª y 3ª corrida **0** (dedup probada),
  0 duplicados. Trampa medida: `NOT EXISTS` correlacionado sin índice = O(n·m) (>10 min);
  con `MINUS` el mismo conteo baja a **0,95 s**. Ritmo: ~480 filas/s → el lote completo ~**45 min**.

### 17.4 Respaldo verificado

`/home/informatica/Documentos/puente/sincronizado/respaldo_20260925/` — **10 archivos, 10/10
SHA-256 verificados** tras la copia: los 3 ZIP, `eventos_sinc_20260925.csv` (las 16.741 filas
actuales, volcado con `SPOOL` en solo lectura), el script candidato, la evidencia de validación,
el diagnóstico, los SQL, la guía oficial, el informe y el manifiesto. **No es un dump completo de
la BD**: cubre los artefactos de sincronización, no las 430 tablas del legado.

### 17.5 ⚠ Hallazgo de seguridad: cuentas de aplicación con rol DBA

`SISMAI` y `TEMP` tienen el **rol `DBA`** concedido (`dba_role_privs`, verificado 25/09). Son
cuentas de aplicación, no administrativas. Agravantes:
- `System.cfg` guarda la clave **en texto plano** con permisos `-rw-r--r--` (legible por
  cualquier usuario del servidor, incluido `respaldo`).
- Ese `System.cfg` es una **copia de abril de 2020** y su clave ya **no valida**
  (`ORA-01017`); la app real corre en el cliente Windows `DESKTOP-2UMA2G6` con su copia local.
  La clave vigente de `SISMAI` se desconoce (probablemente rotada sin actualizar el archivo).
- 5 intentos fallidos con la clave de 2020 **no bloqueaban** las cuentas (`SISMAI`/`TEMP` OPEN;
  `FAILED_LOGIN_ATTEMPTS` del profile, a revisar).
- **PENDIENTE DE AUTORIZACIÓN (no ejecutado):** `REVOKE DBA FROM SISMAI, TEMP` sustituyéndolo por
  los privileges mínimos que la app use; rotar las claves de `SISMAI`, `TEMP` y `oracle` (las
  tres pasaron en claro por la sesión); `chmod 600` en `System.cfg` o mover las credenciales al
  cliente Windows; restringir el acceso SSH de `respaldo` a `/home/salud`.
- **Cómo actuar como DBA en ese servidor:** solo la cuenta de SO **`oracle`** (uid 1002, único
  miembro del grupo `dba`) → `sqlplus / as sysdba`. `salud` y `respaldo` solo están en `users`,
  y `respaldo` no tiene `sudo` (el binario no existe). El SID por defecto de `lar1` es `lar1`
  (`@lar1` da `ORA-12154`, no hay alias TNS).

### 17.6 Pendientes de esta sesión (requieren autorización)

1. Confirmar si el nivel central recibió además el sobre del **lunes 21/09** (además de los de
   los martes, que según el usuario sí llegaron). Si no lo recibió, decidir si se recarga desde
   el respaldo **antes** de encolar natalidad.
2. Encolar los 1.295.152 eventos de natalidad (usuario de aplicación, ~45 min, ventana de
   mantenimiento, cola respaldada, **nunca** junto a `crear.sql`).
3. Índice único `(TABLA, ID)` sobre `EVENTOS_SINC` (DDL, evita duplicados silenciosos).
4. Revisión de privileges de `SISMAI`/`TEMP` y rotación de credenciales expuestas.
5. Importación de los `.dmp` a PostgreSQL: sigue **sin herramienta** (`oracledb` falla en modo
   Thin por cifrado obsoleto; no hay `imp`/`exp`/Instant Client). PostGIS + staging ya resueltos.

### 17.7 Plan para el lunes 28/09 — encolar natalidad y qué avala el martes 29/09

**Antes de encolar, verificar esto (es lo que decide si el martes funciona):**

- ⚠ **`repllar1.log` ausente desde el 08/09** (§16). Ese log es la bitácora de la fase que
  **copia la cola a `TEMP.T_*`**, y los envíos del 08/09, 16/09 y 22/09 traen 4 archivos en vez de
  5. **Si esa fase no corre, encolar el lunes no sirve de nada**: los 1.295.152 eventos quedan en
  `EVENTOS_SINC` y el martes no viajan. Hay que confirmar si `repllar1` (componente en
  `/home/salud/bin`, cron, o el paso equivalente de `SincFich/plcer1.sql`) se está ejecutando, y
  revisar el ZIP del **próximo martes anterior (22/09)** para ver si repone el quinto archivo.
- Verificar que el nivel central sigue esperando los **5 archivos** del sobre (los mismos que
  dejó de traer `repllar1.log`); el usuario pregunta si el nivel superior sigue bien: hoy
  **no está verificado**, y la evidencia de §16 apunta a que viene incompleto desde el 08/09.
- Encolar **antes** del corte del martes. Ideal: lunes.

**Ejecución del encolado (con el sistema en uso):**

- Se puede con los usuarios trabajando: son `INSERT` en una tabla **sin índices ni
  restricciones**, no bloquea a nadie.
- **Riesgo de rendimiento:** con solo 429.500 filas de prueba la base ya mostró esperas por
  `log buffer space`. Con 1,3 M puede degradar el servicio → hacerlo **en la tarde, fuera de las
  horas de carga**, con el `exp` diario de las 13:00 en mente (colisión de recursos).
- **Se puede abortar sin consecuencias graves:** confirma por lotes de 5.000 y deduplica por
  `MINUS`, así que relanzar continúa donde se quedó sin duplicar. Aun así, un corte deja natalidad
  **parcial** en la cola, que el martes enviaría incompleta.
- Secuencia: 1) guardar la salida del dry-run; 2) confirmar que el respaldo de la cola está
  intacto (`respaldo_20260925/eventos_sinc_20260925.csv`, 10/10 SHA-256); 3) ejecutar con el
  usuario de aplicación; 4) verificar que `TABLA+ID` no tiene duplicados y que el conteo final
  cuadró con lo anunciado.

**Qué espera el nivel central:** el sobre del **martes 29/09** llevará lo que esté en
`TEMP.T_*` ese día. El encolado del lunes es lo que hace que natalidad aparezca ahí — **solo si
`repllar1` corre**.

### 17.8 Respaldo total Oracle → PostgreSQL

- **Bloqueado por herramienta, no por datos.** `oracledb` falla en modo Thin (protocolos de
  cifrado obsoletos en Oracle 10g); no hay `imp`/`exp` ni Instant Client en el equipo. Sigue la
  regla de AGENTS.md: Thick con Instant Client antiguo, o pedirle al DBA que exporte.
- Ya está en PostgreSQL lo esencial: **nacimientos 438.577, defunciones 171.115** y el espejo de
  las 430 tablas legacy mapeadas. Falta **completar el espejo** de lo que no se importó.
- Camino más limpio si se quiere el total: el DBA corre `exp` por esquemas y se traen los `.dmp`
  (los de los ZIP son solo `TEMP.T_*`, no la base entera). Alternativa sin Oracle: que el DBA
  exporte CSV por tabla y usar el ETL ya construido.


### 17.9 Limpieza de la prueba (hecho)

- Sesión `sqlplus` huérfana en el servidor (SID 92, `SERIAL#` 36010) por un `INSERT` de prueba
  que sobrevivió al aborto del cliente: eliminada con `ALTER SYSTEM KILL SESSION` y
  `RESPALDO.TMP_ES` borrada. `EVENTOS_SINC` verificada intacta (16.741 filas).

### 17.10 Quién genera `repllar1.log` (26/09/2026) y guion de reconocimiento

**Qué es el archivo (analizado sobre `enviados/routlar1_482026_1526.ZIP`, el último sobre completo):**
`repllar1.log` es el *spool* de `sqlplus` de la **fase de replicación**: 83 `CREATE TABLE` + 86
`CREATE INDEX` (las `TEMP.T_*`) y, al final, los conteos por tabla que coinciden **exactamente** con
las «filas exportadas» de `routlar1.log` (`T_CERTMORT` 398, `T_CAUMMEDI` 769, `T_CERTNACI` 422,
`T_AUDITORIA` 9118). Es decir: **es el paso que arma `TEMP.T_*` desde `SISMAI.EVENTOS_SINC`**. El
sobre solo *recoge* los logs que existen, por eso desde el 08/09 vienen 4 archivos y los datos
viajan degradados (`T_CERTMORT` 398→159, `T_CAUMMEDI` 769→456 entre el 04/08 y el 08/09).

**Quién lo corre — no es el servidor Linux:**
- El cron de `srvsis` solo tiene el respaldo de las 13:00; `/home/salud/bin` está vacío y
  `SincFich/*` / `RoutLar1/*` están sin ejecutar (mtime 2020-04-04) → el motor no está instalado
  ni programado en el Linux.
- La guía oficial (y el fallo del 21/09) apunta al **cliente Windows de la sede**:
  `SistemaTransferencia.exe`, cuyo «menú → correr la sincronización» dispara los scripts
  `SincFich` (`plcer1.sql`, `cr_repli_*.sql`) y luego `RoutLar1` (exp de `TEMP.T_*` + ZIP de los
  5 archivos). Pistas de que el arranque es externo: `expbdsismai.bat` con `pscp -pw` y el share
  Samba `Salud` → `/home/salud/Aplicaciones` (readonly, user `salud`).

**¿Se puede correr a mano sin riesgo? No, no a ciegas:**
1. **No tenemos el script**: vive en el cliente Windows / en el share `Salud`. Hay que leerlo
   (`grep -nE "TRUNCATE|DELETE|DROP|spool"`) antes de tocar nada.
2. **El ciclo trunca la cola** (§5.1: exporta → envía al central → trunca). Si el `TRUNCATE` está
   dentro del paso `repl` y el central no ha confirmado el sobre del 21/09, se pierden las 16.741
   filas. No está verificado en qué paso está.
3. **El envío al central lo hace la app, no el script**: un `repl` manual llena `T_*` pero no
   entrega nada; y si luego corre la app, podría mandar un sobre duplicado o incompleto.
4. Rendimiento: con 429.500 filas de prueba ya hubo espera por *log buffer space*.

**Ruta segura (oficina, con autorización expresa):** (a) copiar el script en solo lectura y revisarlo;
(b) correr **solo los SELECT** de conteo; (c) si hay que producir `T_*`, con el truncate comentado y
la cola ya respaldada (`respaldo_20260925/eventos_sinc_20260925.csv`, 10/10 SHA-256); (d) mejor que
lo lance `SistemaTransferencia.exe`, que es lo que el central espera, y verificar que el ZIP traiga
los **5** archivos.

**Guion de reconocimiento listo (solo lectura, sin riesgo con el sistema en uso):**
- `migracion/recon_repllar1.sh` → wrapper SSH (usa `sshpass`; sin él imprime las órdenes manuales).
  Reporte en `auditoria/recon_repllar1_<AAAAMMDD>.txt` (ignorado por git: puede traer usuarios
  legacy y rastros de comandos con credenciales).
- `migracion/recon_repllar1_remoto.sh` → en `srvsis`: rutas del orquestador, cron/at/init, dónde y
  de qué fecha están los 5 logs del sobre, procesos, `.bash_history`, Samba, disco.
- `migracion/recon_repllar1.sql` → 9 secciones de solo lectura: huella de `repl` en `TEMP.T_*`
  (`LAST_DDL_TIME` y conteos por día), conteo real de cada `T_*`, ventana de `T_EVENTOS`, si el
  motor (objetos con `%SINC%`/`%REPLI%`/`%PLCER%`/`%TRANSF%`) existe y está `INVALID`, y quién
  tiene privilegios sobre `TEMP`.
- **Las tres respuestas a buscar:** (1) qué archivo menciona `repllar1` y quién lo lanza;
  (2) si `TEMP.T_*` no se recrean desde el 08/09 → `repl` no corre → encolar natalidad el lunes no
  serviría; (3) si el motor está inválido, nadie podrá correrlo ni queriendo.
- Validado el `.sql` contra el espejo `sis_oracle_legacy` como DBA y como usuario sin privilegios
  (corregidos 6 errores reales: `ALL_TABLES` no tiene `LAST_DDL_TIME`, `SYS_CONTEXT(...,'SERIAL')`
  no existe en 10g, `ALL_JOBS.JOB_NAME` y `ALL_TAB_PRIVS.TABLE_OWNER` inválidos → `TABLE_SCHEMA`).
  Espejo restaurado y contenedor detenido. **Pendiente de ejecutarlo en vivo en la oficina.**

### 17.11 Orden del lunes 28/09: qué corrige qué

**Los scripts por sí solos NO corrigen la situación: son diagnóstico (solo lectura).** Su valor es
quitar la incógnita de §17.7 **antes** de tocar la cola, para no encolar 1,3 M de eventos que no
van a viajar. La corrección en sí la hace el componente faltante (el `.exe` de Windows o el cron),
no estos archivos.

**Orden (regla: no pasar al paso 3 sin respuesta del paso 1):**

1. **Reconocimiento** — `./migracion/recon_repllar1.sh` (no cambia nada, se puede con el sistema en
   uso, incluso con usuarios capturando). Responde: ¿corre la fase `repl`?, ¿quién la lanza?,
   ¿el motor está inválido?
2. **Decidir según el resultado:**
   - `TEMP.T_*` recreadas en la última corrida → `repl` funciona y el problema es el **arranque**:
     restaurarlo (cron o `SistemaTransferencia.exe` del cliente Windows) → seguir al paso 3.
   - No se recrean **y** el motor está `INVALID` → el DBA recompila; sin eso no hay sincronización.
   - No se recrean **y** el script no está en el servidor → traerlo del share `Salud`, **leerlo**
     (`grep -nE "TRUNCATE|DELETE|DROP|spool"`) y decidir: correrlo tal cual con la cola respaldada,
     o escribir un equivalente controlado sin `TRUNCATE`.
   - El archivo que menciona `repllar1` **no existe en el Linux** → el motor vive solo en el PC de
     la sede: la sincronización se dispara **desde el cliente Windows**, no desde el servidor.
3. **Encolar natalidad** (1.295.152 eventos) solo con el paso 2 resuelto y la cola respaldada
   verificada (`respaldo_20260925/eventos_sinc_20260925.csv`, 10/10 SHA-256), en la tarde y fuera
   de las horas de carga.
4. **Verificar el sobre del 29/09:** 5 archivos, `repllar1.log` presente y `T_EVENTOS` con la
   natalidad. Si el nivel central lo rechaza o no lo recibe, **escalar al soporte SIS/Centura**:
   ningún componente local puede forzar la recepción del sobre.

**Expectativas realistas:** con los pasos 1 y 2 el martes 29/09 debería volver a salir un sobre
completo (5 archivos). Si el generador resulta ser el `.exe` de Windows y no está disponible en la
sede, el plan B es escribir un script propio que arme `TEMP.T_*` desde la cola — se puede, pero
**sin `TRUNCATE` y con revisión del DBA**; no antes.

---

### 17.12 Plan B: `replicar_controlado.sql` (26/09/2026) — listo, NO ejecutado

**Estado: el script existe y está probado; nunca se ha ejecutado contra `192.168.5.200`.** Es el
plan B de §17.11: reconstruir el contenido de `TEMP.T_*` desde `SISMAI.EVENTOS_SINC` porque la fase
original (`plcer1.sql` / `cr_repli_*.sql`) no está disponible y es justamente la que se perdió el
08/09/2026.

- `migracion/replicar_controlado.sql` — el bloque PL/SQL (un solo archivo, sin dependencias).
- `migracion/replicar_controlado_live.sh` — wrapper SSH. Es la **única puerta de entrada**: exige
  las tres condiciones y la frase `AUTORIZAR_PLAN_B_REPLICA_LARA`.

**Regla replicada** (la única verificada al 100 % contra el sobre del 04/08/2026,
`enviados/routlar1_482026_1526.ZIP`, y la línea base de §17.2): viaja la fila si su **último** evento
en la cola es `INSERT(1)` o `UPDATE(2)`; si el último es `DELETE(3)` no viaja. Se replica el **estado
consolidado actual** de la fila de origen, y el manifiesto se arma con la **cola completa** (no solo
la ventana de la semana). Comprobado en el sobre: las 5 filas de `T_CERTMORT` del 04/08 tienen
`ID 20-24`, inserted el 04/08 — días y semanas después del rango del sobre.

**Alcance real (23 de 83 tablas).** Cubre los 23 mapeos `TABLA → origen → T_*` de
`backend/registros/data/rutarala_spec.json`. **No** cubre las ~60 `T_*` restantes (las que llenaba
`copyhist`, p. ej. `T_AUDITORIA`, que en el 04/08 viajaron enteras y sin eventos), **no** las crea (el
DDL de `legancy/analisis/schema_routlar1.sql` está truncado: recrearlas sería inventar estructura) y
**no** trunca la cola. Por eso el sobre que arme este plan B **no es equivalente** al original: es
una recuperación parcial, y así hay que decirlo al reportar.

**Garantías del script:**
- No escribe nada en `SISMAI.*`: solo `SELECT` sobre las tablas de origen. La cola queda **intacta**
  (es el único soporte que queda de los 3,37 M del 27/08, con SHA-256 verificado).
- Sin DDL, sin `TRUNCATE`, sin envío al central (eso lo hace la aplicación).
- **Idempotente:** borra de `TEMP.T_*` solo los IDs que va a insertar y los reinserta; las filas de
  `TEMP` que no están en la cola **no se tocan**. Probado: con un ID previo en `T_CERTMORT` y una fila
  previa en `T_EVENTOS`, la reejecución los conservó y no duplicó nada.
- `COMMIT` por tabla: si se interrumpe, quedan las ya confirmadas y se relanza. Error en una tabla →
  `ROLLBACK` de esa tabla y sigue; el wrapper aborta si la salida trae `ERROR`.
- Modo seguro por defecto (`V_EJECUTAR := 0` = solo informe). El archivo del repositorio **siempre**
  queda en 0; la copia temporal es la única que va a 1.
- **El manifiesto `T_EVENTOS` es una copia de TODA la cola** de las 23 `TABLA` del mapeo (borra esas
  filas y reinserta todas), no solo de las claves que viajan. No es una decisión de diseño: es lo que
  hacía la fase original, que recreaba la tabla en cada corrida. Verificado contra el sobre del
  04/08/2026: sus 9.862 eventos incluyen los de los **34 IDs cuyo último evento es `DELETE(3)`**
  (57 de `RENGLONTELE`, 3 de `DOCUMENTO`) — 60 eventos que no viajan a ninguna `T_` pero cuya
  historia tiene que ver el nivel central. Por eso se quitó el parámetro `V_RELLENAR_T_EVENTOS`
  (antes en 0 = refresco parcial, que dejaba filas de corridas anteriores que volverían a viajar en
  el sobre; en 1 = recarga completa): hacer siempre lo segundo era lo correcto.

**Por qué una sola pasada analítica y no `NOT EXISTS`:** `EVENTOS_SINC` no tiene ningún índice
(§17.2), así que un `NOT EXISTS` correlacionado sobre `(TABLA, ID)` es cuadrático sobre 1,3 M de
eventos (mismo aviso que en `encolar_natalidad_legacy.sql`). El lote se resuelve con
`ROW_NUMBER() OVER (PARTITION BY ID ORDER BY FECHA DESC NULLS LAST, ROWID DESC)`.

**Salvedades que el DBA tiene que confirmar antes de ejecutar:**
1. Los 3 valores de `TABLA` sin mapeo que hay hoy en la cola —`REG_VACUNACION`,
   `PACIENTE_FICHA_EPI`, `PACIENTE_COND_ESPE` (16.741 filas)— **no se replican**. La sección [5] del
   informe propone candidatos por coincidencia de columnas, pero qué `T_` corresponde a qué `TABLA`
   es una decisión **funcional**: la tiene que dar el soporte SIS/Centura, no se deduce de la BD.
2. Si una tabla se salta por «exige NOT NULL sin origen», **no se fuerce**: significa que ese mapeo no
   es 1:1 y la lógica original hacía transformaciones, no copia.
3. `T_EVENTOS` se asume con las columnas `TABLA, ID, EVENTO, FECHA, STATUS, AMS`. **Verificado el
   26/09 contra la tabla real** (el dump del 04/08, en `IMPORT29` del espejo): son exactamente esas
   6, en el orden `TABLA, EVENTO, FECHA, ID, STATUS, AMS`, con `AMS VARCHAR2(12)` nullable. Queda por
   confirmar solo la estructura de `SISMAI.EVENTOS_SINC` en el servidor, que en el espejo es sintética.
4. El **costo**: sin índices en la cola, la primera pasada puede tardar. Correr primero el `informe` y
   medir; si la cola llega a 1,3 M (post-encolado de natalidad), repetir el cálculo en el servidor.

**Orden de ejecución (oficina/VPN):**

```bash
# 1) INFORME: cero escrituras, no pide autorización. Guardar la evidencia.
./migracion/replicar_controlado_live.sh informe
#    -> auditoria/replicar_controlado_informe_<AAAAMMDD_HHMMSS>.txt

# 2) ESCRITURA: solo con las 3 condiciones + la frase exacta.
#    Y con DBA: el usuario `respaldo` no tiene INSERT ANY TABLE (§17.5).
USUARIO=oracle CLAVE=<la de oracle> \
BACKUP_COLA_OK=SI BACKUP_TEMP_OK=SI CENTRAL_OK=SI \
  ./migracion/replicar_controlado_live.sh ejecutar
AUTORIZAR_PLAN_B_REPLICA_LARA
```

3. **Armar el sobre con la aplicación** (`RoutLar1` / `SistemaTransferencia.exe`): el script no envía
   nada. Verificar los 5 archivos con `repllar1.log` presente.
4. **Anular** si algo salió mal, sin tocar la cola, con la fecha `LOTE_INICIO` máxima que imprime la
   salida: `DELETE FROM TEMP.T_<TABLA> WHERE ID IN (...)` + `DELETE FROM TEMP.T_EVENTOS WHERE
   TABLA = '<TABLA>'` + `COMMIT`.

**Cómo se validó** (espejo `sis_oracle_legacy`, Oracle XE 11.2, nunca contra producción): esquema
sintético `SISMAI`/`TEMP` con `EVENTOS_SINC` de 13 eventos que cubren `INSERT`, `UPDATE`×2, `DELETE`
final, `DELETE` seguido de `INSERT` y empate de `FECHA`. Comprobado que (a) el dry-run no escribe nada,
(b) viajan los 3 IDs correctos y no el `DELETE` final, (c) la reejecución reemplaza y no duplica,
(d) una fila previa fuera de la cola sobrevive, (e) el mapeo no 1:1 se salta, (f) una desalineación de
esquema produce `ERROR` + `ROLLBACK` de esa tabla y el wrapper aborta, (g) la cola queda con las
mismas 13 filas. Además se corrigieron tres incompatibilidades de PL/SQL que-compilan solo en
versiones nuevas: el constructor de `record` en la colección (`PLS-00222`), `DBA_FREE_SPACE.USED_BYTES`
(no existe; es solo `BYTES`) y `COMMIT` poniendo `SQL%ROWCOUNT` a 0 (el conteo del `INSERT` se
captura antes). A partir de aquí la validación pasó de 13 eventos sintéticos al **paquete real
completo**: ver §17.13.

**Pendiente para cerrarlo:**
- [ ] Correr el `informe` en `192.168.5.200` y revisar las secciones [3] y [5] con el DBA.
- [ ] Confirmar con soporte SIS/Centura el mapeo de `REG_VACUNACION`, `PACIENTE_FICHA_EPI` y
      `PACIENTE_COND_ESPE`.
- [ ] Verificar la estructura real de `SISMAI.EVENTOS_SINC` y `TEMP.T_EVENTOS` (columna `AMS`).
- [ ] Respaldar `TEMP.T_*` (no está en `respaldo_20260925/`, que son los ZIP y el CSV de la cola).
- [ ] Solo con esas 4 cosas resueltas: pedir la autorización y ejecutar.

---

### 17.13 Simulación del paquete en el espejo: el plan B reproduce el envío del 04/08 (26/09/2026)

**Qué resuelve.** §17.12 validaba el plan B con 13 eventos sintéticos: demostraba que la lógica del
lote funciona, no que el sobre que arma sea el mismo que envió el legacy. Esta simulación lo corre
contra la **referencia real**: el paquete `enviados/routlar1_482026_1526.ZIP` (04/08/2026, 5 archivos)
que sí llegó a enviarse, cuyo `exp` está íntegro en el esquema `IMPORT29` del espejo
`legancy/BDSISMAI.DMP`. Se reconstruye el escenario y se compara **fila por fila** con `MINUS` en
ambos sentidos.

**Cómo correrla** (nunca toca `192.168.5.200`; todo en el espejo local):

```bash
./migracion/simulacion/ejecutar_simulacion.sh              # las 6 etapas
./migracion/simulacion/04_pruebas_negativas.sh             # solo las contrapruebas
```

| Archivo | Qué hace |
|---|---|
| `00_ddl_temp_04082026.sql` | El DDL real de la fase: 83 `CREATE TABLE` + 86 `CREATE INDEX` de `TEMP.T_*`, extraído del paquete. |
| `01_preparar_escenario.sql` | `SISMAI.EVENTOS_SINC ← IMPORT29.T_EVENTOS` (9.862 eventos) y las 23 fuentes `SISMAI.*` como proyección de su `T_*`. |
| `02_comparar.sql` | `MINUS` en ambos sentidos por tabla + veredicto `SIMULACION CORRECTA`. |
| `03_generar_paquete.sh` | `exp` real del usuario `TEMP` + los 5 archivos del ZIP, y comparación de conteos con el paquete real. |
| `04_pruebas_negativas.sh` | Contrapruebas A–E (ver abajo). |
| `ejecutar_simulacion.sh` | Orquestador: escenario → DDL → replicar → comparar → ZIP → idempotencia. |

**Resultado (26/09/2026, evidencia en `auditoria/simulacion_completa.txt`):**

- **23 de 23 tablas del mapeo idénticas** a la referencia: 9.531 filas, cero diferencias.
- **Manifiesto `T_EVENTOS` idéntico**: 9.862 eventos, 0 sobrantes, 0 faltantes.
- **Idempotente**: la segunda corrida borra 9.531 e inserta 9.531 y deja el mismo resultado.
- **Contrapruebas 12/12** (`auditoria/pruebas_negativas.txt`): A, un `DELETE(3)` al final del
  historial saca la fila de la `T_` y **se queda en el manifiesto**; B, un `INSERT(1)` de un ID que no
 Viajaba aparece en el manifiesto; C, quitar 2 columnas del origen deja la `T_` igual (copia menos,
  no más); D, una `TABLA` sin mapeo no entra y se reporta en `[5]`; E, dos corridas seguidas no cambian
  nada.

**Lo que la simulación cambió del script.** El manifiesto dejó de refrescarse solo para las claves
replicadas: ahora es **copia de toda la cola** de las 23 `TABLA` del mapeo. Lo decidió el paquete
real — sus 9.862 eventos incluyen 60 eventos de 34 IDs cuyo último evento es `DELETE(3)`, que no
viajan a ninguna `T_` pero cuya historia necesita ver el central. Se quitó `V_RELLENAR_T_EVENTOS`
(ver §17.12).

**Lo que la simulación NO demuestra** (say it when reporting):
1. `T_AUDITORIA` (9.118 filas en el real) y las otras ~60 `T_*` no se replican: es el alcance
   conocido del plan B, no un defecto de la simulación.
2. Los orígenes `SISMAI.*` del espejo son **proyecciones** de las `T_*`, no las tablas fuente reales:
   la proyección copia valores tal cual, así que la **transformación** real origen → `T_` no se
   prueba. Solo la lógica de lote, columnas, idempotencia y manifiesto.
3. `copyhistlar1.log` y `bloqlar1.log` del ZIP simulado son **STUB**: esas dos fases no están
   reconstruidas. El ZIP sirve para medir tamaño y estructura (260 K contra 273 K del `dmp` real),
   no para simular su contenido.
4. Corre contra Oracle XE 11.2, no contra 10.1.0.3.0. Es la misma versión mayor del PL/SQL soportado,
   pero el volumen es 9.862 eventos, no 1,3 M: el costo real está sin medir (ver salvedad 4 de §17.12).

---

*Registro creado el 12/09/2026.*

### 17.14 `generar_paquete_live.sh`: armar el sobre real (26/09/2026)

**Qué resuelve.** §17.13 probó el sobre en el espejo, pero contra producción el `exp` del usuario
`TEMP` sigue siendo un paso manual, y nada impedía armar un ZIP con 5 archivos y 2 de ellos falsos
sin avisar. Este guion hace las dos cosas: **preflight de solo lectura** y **armado con
confirmaciones**.

```bash
./migracion/generar_paquete_live.sh preflight        # solo lee, se puede con el sistema en uso
./migracion/generar_paquete_live.sh armar            # exp + ZIP; se niega a inventar los 2 logs
./migracion/generar_paquete_live.sh armar --con-stub  # incluye los 2 STUB, con doble confirmación
```

**El preflight BLOQUEA si:**

1. el manifiesto `TEMP.T_EVENTOS` está vacío o no se puede leer (sin manifiesto el sobre no sirve);
2. el usuario de `exp` no tiene `EXP_FULL_DATABASE` ni `SELECT ANY TABLE` (el `exp` de `owner=TEMP`
   no puede funcionar; por defecto `respaldo` no lo puede → hay que ir con `USUARIO=oracle`);
3. **hay filas en tablas `T_` que el plan B no controla** (~60). El `exp` se lleva *todo* `TEMP`, así
   que en el paquete del 04/08 iban todas en 0 y ahora se colarían sin que nadie las haya revisado;
   vaciarlas es operación del DBA con autorización, el plan B no las toca;
4. hay menos de 256 MB libres en el directorio del servidor;
5. no existe un log de `replicar_controlado_live.sh ejecutar` para usar de `repllar1.log` (avisa si
   es de ayer).

**Qué es real y qué no en el sobre armado:** `routlar1.dmp` y `routlar1.log` son el `exp` real de
`TEMP`; `repllar1.log` es la salida de la corrida del día; `copyhistlar1.log` y `bloqlar1.log` son
**STUB con marcador**. Falta el contenido de `T_AUDITORIA` (9.118 filas). El guion no envía nada,
no trunca la cola y no escribe en la base (un `exp` solo lee); pone los SHA-256 **fuera** del ZIP
(`SHA256SUMS.txt`) porque el sobre tiene que llevar exactamente 5 archivos, y verifica que sean 5
antes de terminar.

**Alcance de la validación:** `bash -n` y revisión del flujo; el `preflight` **no se ha ejecutado
contra `192.168.5.200`** porque no hay autorización para tocar el servidor. La primera corrida real
debe ser un `preflight`, que es inofensivo, y comparar sus conteos con los de la simulación.

**Bug encontrado y corregido al agregar la contraprueba F (§17.15):** el guardado de columnas
"que faltan" usaba `NVL(V_LIST, '')` esperando convertir el vacío en cadena, pero **en Oracle la
cadena vacía ES NULL**, así que devolvía NULL igual y la tabla con `NOT NULL` sin origen se replicaba
en lugar de saltarse. El contrato correcto es NULL = "no falta ninguna" y el comparador `IS NOT NULL`.
Lo detectó la contraprueba F, no la simulación del caso normal (§17.13 no quitaba columnas).

### 17.15 Contraprueba F: `NVL(lista,'')` no arregla nada (26/09/2026)

La simulación del caso normal (§17.13) no detectaba el fallo porque nunca quita columnas al origen.
La contraprueba F sí: borra del origen la columna `HESTABLECIMIENTO`, que en `TEMP.T_CERTMORT` es
`NOT NULL` sin equivalente en `SISMAI.CERTIFICADO`. El `INSERT` entonces omite esa columna y
`ORA-01400` — o sea, el lote se cae a mitad de la carga, no "salta la tabla".

**El bug.** `FALTAN_NOT_NULL`.armaba la lista con un loop (sustituyendo el `LISTAGG`, que no existe
en 10.1) y devolvía `NVL(V_LIST, '')`. En Oracle **la cadena vacía ES NULL**, así que
`NVL(NULL, '')` devuelve NULL: la función devolvía NULL tanto cuando faltaba una columna como cuando
no faltaba ninguna, y el `IF V_FALTAN IS NOT NULL AND V_FALTAN <> ''` del llamador nunca se cumplía.

**Cómo se rastreó** (el bloque completo se negaba a saltar la tabla, y no hab*a* error visible): tres
pasos con un `PL/SQL` de depuración sobre el mismo escenario — (1) la consulta directa de columnas
faltantes devolvía 1; (2) la función aislada devolvía `HESTABLECIMIENTO` correctamente; (3) un
`CASE WHEN V_FALTAN IS NULL` dentro de `PROCESAR` marco que para `CERTIFICADO` era NO y para
`CERTNACIMIENTO` SI, cuando el loop no había encontrado nada. Imposible con `NVL(...,'')` en el
código ⇒ el bug estaba en el "arreglo", no en el `IF`.

**Contrato final:** la función devuelve NULL = "no falta ninguna", la lista si falta alguna, y `'?'`
si hubo error al consultar el diccionario (esa tabla se salta y se reporta, que es lo seguro).
Llamador: `IF V_FALTAN IS NOT NULL THEN`. Idempotencia no afectada.

**Resultado de las contrapruebas: 14 correctas, 0 con falla** (`auditoria/pruebas_negativas.txt`),
con `T_CERTMORT` en 0 filas, las otras 22 tablas copian normal y el escenario base restaurado al final.

### 17.16 El central recibe todos los martes y no reclama (26/09/2026)

Dato del usuario: el nivel superior **ha recibido la información procesada y enviada todos los
martes y no se ha quejado**, y **no tiene soporte** — es una persona que a veces puede ayudar.

**Qué cambia en la evaluación de riesgo:**

- El riesgo de que el central rechace el sobre por los 2 logs STUB o el `T_AUDITORIA` vacío
  (§17.14) es **bajo**: nadie audita el contenido del sobre semanalmente.
- El riesgo real **no es el rechazo**, es el **silencio**: que el central acepte un sobre incompleto
  y eso no se detecte nunca. La defensa no es técnica, es de proceso: una vez al mes, o cuando se
  tenga una señal de falla, comparar contra el paquete de referencia y usar a esa persona del
  central como confirmación informal de recepción.
- Por lo tanto **el plan B + `generar_paquete_live.sh --con-stub` es viable como procedimiento
  semanal**, y el `exp` de las 13:00 + el legacy se pueden ir retirando en la práctica aunque no
  haya migración de la BD (§17.9) resuelta.
- Queda **sin resolver** la falta de soporte: si el central algún día cambia de interlocutor o
  empieza a validar, el sobre parcial deja de servir. Por eso el guion no envía nada y exige
  confirmación explícita, y por eso los dos STUB están marcados como tales: si alguien los lee, se
  sabe que no son los originales.

**Rutina semanal que queda (a confirmar):** lunes `preflight` + `replicar_controlado_live.sh ejecutar`
(sin el `exp` de las 13:00) → martes `generar_paquete_live.sh armar --con-stub` y entrega por el
canal de siempre, con un mensaje al contacto del central confirmando el número de eventos enviados.

### 17.17 Ventana del martes 29/09 después de las 13:00: extraer el Oracle a PostgreSQL

Contexto: el **martes 29/09 se envía la semana 38** y **después de las 13:00 nadie trabaja en el
sistema** (fin de jornada de captura). Esa ventana libre es la oportunidad para traer la base del
servidor en vivo y trabajar en casa sobre un entorno controlado. El usuario tiene la cuenta SO
**`oracle`** (grupo `dba`, `sqlplus / as sysdba`) — la única con DBA del servidor (§17).

**Objetivo de la mañana (no negociable, va antes que todo lo demás):** confirmar que el sobre de la
semana 38 salió con **5 archivos**. Si sale con 4, se aplica el plan B (§17.11, §17.14) y el resto
del día se dedica a eso. La extracción solo empieza con el sobre verificado.

#### Orden dentro de la ventana

| # | Fase | Tiempo | Peso en el servidor |
|---|---|---|---|
| 0 | Verificar que el respaldo de las 13:00 terminó bien | 5 min | nulo |
| 1 | **Subconjunto crítico** → PostgreSQL → verificar MM/MN | 20–30 min | bajo |
| 2 | Extracción total por esquemas (CSV) | 2–4 h | **alto** |
| 3 | Carga en PostgreSQL (`COPY`) + verificación | 30–45 min | nulo (es local) |

La fase 1 va primero a propósito: son 20 minutos y ya deja resoluble la pregunta de MM/MN. Si la
fase 2 se corta o falla, no se pierde el resultado que importa.

#### Fase 1 — el subconjunto que responde la pregunta de MM/MN (~1,2 M filas, no 6,4 M)

| Tabla | Filas aprox. | Para qué |
|---|---|---|
| `SISMAI.CERTIFICADO` (semanas 32–37) | ~1.200 | el hueco de MM/MN que falta en PostgreSQL |
| `SISMAI.RENGLON_CASOSMM` | 749 | **registro caso por caso de muerte materna** |
| `SISMAI.RENGLON_CASOSMI` | 9.993 | registro de mortalidad neonatal |
| `SISMAI.CAUSA_M` + `CAUSA_MMEDICO` | 543.595 | reclasificar MM/MN por causa |
| `SISMAI.ORGANIZACION`, `PERSONALSALUD`, `ORG_GEOGRAFICA` | ~166.000 | resolver establecimiento y profesional |

Se deja fuera a propósito **`RENGLONTELE` (2.663.432 filas, el 41% del volumen)** y las ~423 tablas
pequeñas. Saltar `RENGLONTELE` baja la carga de 6,4 M a ~1,2 M filas: **la cuarta parte del tiempo y
la décima parte del riesgo** sobre producción.

#### Reglas de la ventana (no negociables)

- **Solo lectura.** Todo `SELECT`/`SPOOL`. Ni un `INSERT`, ni un `TRUNCATE`, ni un `DROP`.
- **No tocar `SISMAI.EVENTOS_SINC`** (§17: ya fue dropeada y recreada el 21/09; se perdieron 3,37 M de
  eventos). Ninguna consulta que la bloquee, ninguna sesión que la modifique.
- **No ejecutar la fase `repl` ni `replicar_controlado_live.sh`.** Mañana se envía el sobre; no se
  cambia el estado de la cola el mismo día del envío.
- **Todo por `NOHUP`/`screen` y con bitácora de salida**, para poder recuperar el trabajo: si se
  corta la sesión, el
  proceso sigue y se puede recuperar sin relanzar desde cero.
- **Volcado de control primero**: antes de la fase 2, un `SELECT COUNT(*)` por tabla a CSV. Son
  430 consultas de un segundo y dan el contraste de filas para validar la carga después.
- **Si algo falla, se detiene y se anota.** No se reintenta a ciegas ni se "acomoda" con `UPDATE`.
- **SHA-256 de cada CSV** al terminar, para comparar contra el original si hay dudas.
- Las credenciales van por `legancy_conf/*.env` (ya en `.gitignore`, línea 16), **nunca** en el
  repositorio ni en la línea de comandos compartida.

#### Orden técnico de la extracción

`exp` **no sirve aquí**: un `.dmp` es binario de Oracle y **PostgreSQL no lo puede leer** (§17.8). La
ruta es **CSV por `sqlplus` + `COPY`**, que es la que ya existe en `migracion/extraer_datos_csv.sh`.
Los `.dmp` solo sirven como respaldo del DBA, no para el entorno de casa.

Por tabla: `ALTER SESSION` de NLS, `SPOOL` con `COL ... SEPARATOR ','` y el `SELECT`. Ojo con el
`encoding`: el origen es `WE8MSWIN1252` según AGENTS.md y los CSV deben salir en `AL32UTF8` o
`WE8MSWIN1252` para que `COPY` no los rechace en PostgreSQL (que es UTF-8).

#### Lo que sale de esta ventana

- Un `sis_salud_db_<fecha>.dump` nuevo, que **reemplaza** al del 24/09 (183 MB) y sirve de entorno
  de trabajo en casa.
- La respuesta definitiva de MM/MN 2026 y la corrección del **bug de mapeo de `RENGLON_CASOSMM`**
  (§17.18), cuyas columnas están desfasadas en el espejo actual.

#### Fase 2 en segundo plano, opcional

Si sobra tiempo después de la fase 3, se puede dejar la extracción de las 423 tablas pequeñas
corriendo con `NOHUP` para otro día. **No vale la pena meterlas mañana**: no aportan a MM/MN y
compiten con el mismo servidor.

### 17.18 MM/MN 2026: el registro de MM existe y estaba desencontrado (28/09/2026)

La responsable de MM/MN de la Dirección de Epidemiología Lara reporta para 2026, semanas 1 a 37:
**MM 17 + 1 violenta = 18** y **MN 228**. Contra eso, PostgreSQL da **7 MM** y **213 MN**. El
respaldo del §17.17 (traer el vivo) no es la causa: el dato del registro de MM **ya estaba en
PostgreSQL**, solo que en la tabla equivocada.

**El error de búsqueda:** la primera comprobación fue sobre `legacy."T_RCASOSMM"` y
`legacy."T_RCASOSMI"`, que están **vacías (0 y 6 filas)** — de ahí la conclusión equivocada de que
"el registro oficial de casos MMI está vacío y no hay fuente". La tabla buena es
**`sismai."RENGLON_CASOSMM"`, con 749 filas**, un registro **caso por caso** (no agregado por semana).

| Fuente | MM 2026 |
|---|---|
| Certificados de defunción (`HPRESENCIAEMBARAZO=1`) | 7 |
| **`sismai."RENGLON_CASOSMM"` (registro de investigación)** | **21** |
| Reportado por la responsable | 17 + 1 violenta = 18 |

> ⚠ **La primera fila estaba mal y la segunda es una vía distinta.** `HPRESENCIAEMBARAZO=1` no es
> "la muerte materna en 2026" sino solo el embarazo; el puerperio es el código 2. Con los dos,
> los certificados dan **16**, que es el dato correcto. Ver §17.20.

Los 21 casos van de 2026-02-03 a 2026-08-14, en las semanas 1 a 33. Los 18 reportados son de este
registro, no de los certificados: la campo `HPRESENCIAEMBARAZO` solo lo marca 7 veces en todo 2026.
( ALSO CORREGIDO en §17.20: el campo marca 17 veces en 2026, 16 de las cuales son muerte materna.)

**❌ NO era un bug de mapeo (corregido el 29/09/2026, ver §21):** aquí se afirmó que las
columnas de `RENGLON_CASOSMM` estaban desfasadas y que había que corregir `models_legacy.py`. **No
era eso.** `HCASOSMMI` es simplemente el **ID de la persona** (enlaza con `CASOS_MMI."ID"`: 748 de
749 filas casan) y por eso `SUM(HCASOSMMI)` da 658.439.440.845 — no es un conteo que se pueda sumar.
`PERIODOOCURRENCIA` viene `NULL` en las 749 porque **no es la fecha**: la fecha de la muerte está en
`CASOS_MMI."FECHAOCURRENCIA"`. **No hay nada que corregir en el mapeo**, y la comparación de
`ALL_TAB_COLUMNS` que se pensaba hacer al extraer el vivo no hace falta para esta tabla. Los valores
que sí son legibles en el renglón (establecimiento, CIE de causa, edad gestacional, forma de parto)
más los que trae `CASOS_MMI` (nombre, edad, sexo, fecha) dan el registro completo.

**El hueco de las semanas 32–37 sí es real y sí viene del origen.** Las defunciones en PostgreSQL
se desploman desde el 1 de agosto de 2026:

| Semanas | Defunciones/semana |
|---|---|
| 1–30 | ~205 (estable) |
| 31 | 127 |
| 32 | 8 |
| 33 | 8 |
| 34 | 2 |
| 35 | 3 |
| 36–37 | 0 |

Son ~780 defunciones de menos frente a la tendencia, y el ritmo de MN (6,2/semana) × 2 semanas ≈ 12
explica la diferencia de MN (213 → 228, que es lo que reporta la responsable). **Como el servidor en
vivo sí tiene hasta la semana 37, el faltante es de nuestro extracto y no de la captura** — por eso
el §17.17 lo resuelve.

**El retardo de 4 semanas no está en la elaboración del certificado.** Medido con
`FECHA_M − FECHAELABORACION` sobre las 6.246 de 2026: 81,6% el mismo día, 15,7% al día siguiente,
7,4% con más de un día (máximo 120). El retardo real es que **las muertes desde el 1 de agosto no se
están capturando**, no que los certificados lleguen tarde. La distribución de la Elaboración sirve,
entonces, para fecha de diagnóstico, no para modelar el retardo de llegada.

**No se puede reclasificar MM/MN por causa.** Solo **54 de 6.247** defunciones 2026 están codificadas
en PostgreSQL (0,9%), y en el origen el **97,5% de los certificados de 2026 tiene `HCAUSABASICA` NULL**.
Cualquier cifra de MM/MN que se intente sacar del CIE sale incompleta mientras no se codifique.

**Segundo bug, independiente del anterior y ya corregible en casa:** `ReporteComparativoView`
(`registros/views.py:621`) filtra por **año civil** (`fecha_evento__year=anio`) pero agrupa por
**semana ISO**. En la frontera de año eso descarta los certificados que llegan con retardo: **92
defunciones ocurridas en diciembre 2025 pertenecen a la semana 1 de 2026** y hoy no aparecen en el
reporte de 2026. La semana 1 de 2026 debe mostrar **241**, no 149. Es exactamente el caso que
describe la responsable ("llegan certificados de semanas anteriores hasta con 4 semanas de retardo y
deben agregarse a las semanas respectivas"), y el resto de semanas sí está bien porque el sistema
agrupa por la fecha del evento y no por la de ingreso.

### 17.19 ⚠ La semana epidemiológica no es ISO: 2025 tiene 53 y 2026 tiene 52 (28/09/2026)

Dato de la oficina: **2025 tuvo 53 semanas epidemiológica y 2026 tendrá 52**, y **la semana 53 de
2025 va del 28-12-2025 al 03-01-2026**. Es el dato que faltaba para cerrar el §17.18, y resulta que
**el código usa la convención equivocada**.

#### Por qué 2025 tiene 53 semanas y esa semana se mete a enero

- La semana epidemiológica venezolana es de **domingo a sábado** (7 días justos).
- El **año `Y` empieza en el domingo de la semana que contiene el 4 de enero de `Y`**, y acaba
  el sábado justo antes de ese domingo del año siguiente. El ancla es el **4 de enero, no el 1**:
  el 1 de enero cae a mitad de semana, y anclar en él daría un número de semanas equivocado.
- **2025:** el 4 de enero de 2025 fue sábado → la semana 1 arranca el **domingo 29-12-2024**.
  El año siguiente arranca el domingo 04-01-2026. Entre ambos hay 371 días = **53 semanas**.
- **2026:** el 4 de enero de 2026 fue domingo → la semana 1 arranca el **domingo 04-01-2026** y
  el 31-12-2026 cierra con **52 semanas** (la 52 es del 27-12-2026 al 02-01-2027).
- Por eso el **1, 2 y 3 de enero de 2026** (la semana que abre el 04) son la **semana 53 de 2025**:
  la semana no se parte al cambiar de año.

Lo que hace extraño a la "semana 53 de 2025" es simplemente que **una semana siempre dura 7 días y no
se parte al cambiar de año**. No es un error del calendario, es la definición.

> Nota: la regla se implementó como una cadena contigua — `inicio(Y) = domingo_de(4 de enero de Y)`
> y `fin(Y) = inicio(Y+1) − 7 días` — porque calcular el fin de cada año por separado
> (`domingo_de(31 de diciembre)`) **solapaba 2024 y 2025 en la semana del 29-12-2024** y esa fecha
> se etiquetaba dos veces (2024/53 y 2025/1). Con la cadena cada fecha pertenece a un único año
> (verificado sin solapes de 2023 a 2028).

#### El problema: el código usa ISO 8601, que da exactamente lo contrario

`vigilancia/services.py:6 semana_epidemiologica()` usa `fecha.isocalendar()`, y PostgreSQL
`EXTRACT(WEEK ...)` también es ISO. La ISO corre de **lunes a domingo**:

| Año | ISO (lo que hace el código) | Epidemiológico venezolano (lo que pide la oficina) |
|---|---|---|
| 2024 | 52 | — |
| 2025 | **52** | **53** |
| 2026 | **53** | **52** |
| 2027 | 52 | — |

**Están invertidos.** Verificado en PostgreSQL 18: `COUNT(DISTINCT EXTRACT(WEEK ...))` da 52 para
2025 y **53 para 2026**.

Además, ISO ubica las fechas de la frontera de otra manera:

| Fecha | ISO | Epidemiológico venezolano |
|---|---|---|
| 28-12-2025 (domingo) | semana **52** de 2025 | semana **53** de 2025 |
| 01-01-2026 (jueves) | semana **1** de 2026 | semana **53** de 2025 |
| 03-01-2026 (sábado) | semana **1** de 2026 | semana **53** de 2025 |
| 04-01-2026 (domingo) | semana **1** de 2026 | semana **1** de 2026 |

#### Impacto medido (con el código ya corregido)

Lo que cambia de verdad no es el número de la semana, sino **qué año se le asigna a cada fecha**.
Con el filtro civil (`fecha_evento__year`) estos registros se contaban en el año equivocado:

| Frontera | Registros | Van a | Antes contaban en |
|---|---|---|---|
| 29-12-2024 a 31-12-2024 | 76 defunciones / 120 nacimientos | 2025 (semana 1) | 2024 |
| 01-01-2026 a 03-01-2026 | 116 defunciones / 116 nacimientos | 2025 (semana 53) | 2026 |

Son **192 defunciones y 236 nacimientos** que el filtro civil colocaba en un año que no les
correspondía. Por eso el §17.18 medía 92 registros de diciembre 2025 "perdidos": no se perdían,
estaban mal clasificados.

Totales por año después del cambio (año epidemiológico, no civil):

| Año | Defunciones | Nacimientos | Semanas |
|---|---|---|---|
| 2025 | **11.084** | 17.128 | 53 |
| 2026 | **6.272** | 9.296 | 52 (datos solo hasta la semana 35) |

Serie 2026 de defunciones, semana a semana, con la convención venezolana:

| Semana | Rango | Defunciones | MN |
|---|---|---|---|
| 1 | 04-01 a 10-01 | 216 | 14 |
| 2 | 11-01 a 17-01 | 198 | 1 |
| … | … | ~180-250 | 3-14 |
| 29 | 20-07 a 26-07 | 198 | 6 |
| 30 | 27-07 a 01-08 | 167 | 8 |
| 31 | 02-08 a 08-08 | **37** | 3 |
| 32 | 09-08 a 15-08 | **39** | 7 |
| 33 | 16-08 a 22-08 | **42** | 8 |
| 34 | 23-08 a 29-08 | **25** | 3 |
| 35 | 30-08 a 05-09 | **2** | 0 |

**El desplome de la captura empieza en la semana 31 (del 2 al 8 de agosto)**, que es justo la semana
siguiente a la que cerró el sábado 01-08 y se envió el martes 04-08. Hasta la 30 el ritmo es normal
(~200/semana) y la MM más reciente es de junio; desde la 31 solo llega residuo. Detalle del análisis
en §17.21.

#### Qué se aplicó (28/09, en casa)

1. **`vigilancia/services.py`** — `semana_epidemiologica()`, `inicio/fin/rango_anio_epidemiologico()`
   y `semanas_en_anio()` reescritas con la cadena contigua del 4 de enero. Ya no se usa
   `isocalendar()` en ninguna parte.
2. **`registros/views.py`** — `_filtro_anio()` para tablero, comparativo y listados, en vez de
   `fecha_evento__year`; `_por_semana()` y `_neonatales_por_semana()` agrupan por fecha y etiquetan
   en Python (SQL no puede expresar domingo→sábado). Se eliminó `ExtractWeek` (era ISO).
3. **`exportar_rutalara.py`** — `--semana` pasó de ISO `AAAA-WNN` a **`AAAA-N`**
   (ej. `2026-31`) y valida que la semana exista en ese año (2026 no tiene 53).
4. **Pruebas** — 9 de `SemanaEpidemiologicaTests` (53/52, fronteras, no-solape, casos del legacy) y
   3 de `AnioEpidemiologicoTests` (regresión del bug de año civil). Suite: **91 pruebas OK**.

#### ✅ Confirmado con la oficina (28/09): el central usa la convención venezolana

**El nivel superior numera las semanas epidemiológicas, no ISO** (§17.24). Entonces este cambio es
una **corrección**, no una incompatibilidad: se puede enviar con la numeración venezolana. El plan
B de "no tocar hasta confirmar" queda sin objeto.

El `ConsolidadoSemanal` **no se reetiquetó**: los 70.975 registros importados toman `ANNO`/`PERIODO`
del propio legacy (`sismai."DOCUMENTO"`), que ya usa la convención venezolana (2025 = 1..53,
2026 = 1..37). Confirmado contra el legacy: el periodo 37 se consolidó el 21-22/09, sobre la semana
que cerró el sábado 19-09, que es la 37 y no la 38 ISO. **No hay nada que migrar**; si se hiciera,
se rompería el histórico.

Nada queda abierto de cara al central: la numeración es la venezolana, que es la que ya usan el
legacy y la oficina.

### 17.20 ✅ Corregida la muerte materna: el ETL solo leía un código de dos (28/09/2026, en casa)

Cerrada la diferencia "oficina 17+1 / PostgreSQL 7" del §17.18 sin tocar el Oracle. **La causa era
nuestro ETL, no el dato.**

#### El origen: el campo tiene cinco códigos y el ETL leía uno

`sismai.PRESENCIAEMBARAZO` es el catálogo del campo, y está en el espejo:

| Código | Significado | ¿MM? |
|---|---|---|
| 01 | AL MOMENTO DE LA MUERTE | **sí** |
| 02 | EN LOS ULTIMOS 12 MESES (puerperio) | **sí** |
| 03 | NO | no |
| 04 | IGNORADO | no |
| 05 | SIN INFORMACION | no |

`importar_legacy_registros.py` mapeaba `embarazo_o_puerperio = (embarazo == 1)`: **descartaba el
puerperio**. Con 1+2, los certificados de 2026 dan **16** y no 7. Que el número fuera 7 y no otra
cosa es lo que hizo pasar el bug desapercibido: 7 es un valor plausible para un año.

#### Segundo error, en el conteo: la MM no depende de la CIE

`views.py` contaba `embarazo_o_puerperio=True, codificacion_pendiente=False`, es decir **solo las
muertes maternas ya codificadas**. Como el **97,5% de los certificados de 2026 tiene `HCAUSABASICA`
NULL**, esa regla borraba casi todas: en 2024 el tablero mostraba **0** MM siendo que hay 21, y de las
16 de 2026 solo 2 tenían CIE. Que la causa esté o no codificada no cambia que la muerte fue materna;
lo que indica es si la muerta está en la lista de las que hay que codificar. **Regla aplicada: `mm`
cuenta todas, y el desglose con/sin CIE se informa aparte** (`mm_codificadas`, `mm_pendientes`).

#### Qué se cambió

- `importar_legacy_registros.py`: constante `CODIGOS_MM = {1, 2}` con el catálogo citado, y el mapeo
  usa `in CODIGOS_MM`.
- `registros/views.py`: el tablero y el comparativo cuentan la MM entera; se agrega `mm_codificadas`
  al tablero y se corrigen los rótulos ("Muertes maternas codificadas (MM)" → "Muertes maternas (MM)").
- `auditoria/exportar_auditoria_mm_mn.py`: el resumen imprime el total de MM, no solo las codificadas.
- `Tablero.jsx` / `Reportes.jsx`: rótulos.
- **Nuevo** `manage.py corregir_mm_legacy` (dry-run por defecto, `--ejecutar` aplica): el ETL es
  idempotente por `legacy_id` y no volvía a tocar las filas existentes, así que corregir el comando de
  importación **no reparaba lo ya cargado**; este comando sí, enlazando por `legacy_id` ↔
  `sismai."CERTIFICADO"."ID"`, y además **desmarca** las que el legacy tiene en 3/4/5 o NULL.
- Pruebas: `registros/tests.py::MuerteMaternaTests` (2 casos) — que el tablero y el comparativo
  cuenten la MM sin CIE. **79 pruebas backend** (antes 77), 13 frontend, `npm run build` OK.

#### Resultado y cuadre con la oficina

Ejecutado sobre las 173.533 defunciones del lote `LEGACY-CERTIFICADO`: **102 marcadas, 0
desmarcadas** (no había falsos positivos que limpiar), **191 MM** en todo el histórico. Idempotente.

| Año | Antes (tablero) | Ahora | Espejo directo | Oficina |
|---|---|---|---|---|
| 2024 | 0 | **21** | 21 | — |
| 2025 | 23 | **41** | 41 | — |
| 2026 | 7 | **16** | 16 | 17 + 1 violenta |

Los tres años cuadran exactamente con `sismai."CERTIFICADO"`, o sea que **nuestra cifra ya no tiene
bug de mapeo**: la de la oficina es 17 (+1 violenta) y la nuestra 16. Queda un residuo de 1, que es
justamente lo que hay que explicarle:

- **MN 2026:** la app da **221**, el espejo por `TIPOEDAD`/`EDAD` da **222** y la oficina **228**. La
  diferencia con 228 sigue siendo la del colapso de captura del 1 de agosto (~6,2 MN/semana × 2
  semanas ≈ 12), no un bug: los dos métodos locales coinciden entre sí.
- **El "+1 violenta" no es derivable de los certificados:** 15 de las 17 filled no tienen
  `HCAUSABASICA`, así que la causa externa (V00–Y99) no está. Sale de cruzar el registro de
  investigación `RENGLON_CASOSMM` (21 casos en 2026, el último el 14/08) contra los certificados, y
  ese cruce está **bloqueado por el bug de `HCASOSMMI`/`ID−2`**: en las 749 filas
  `HCASOSMMI = ID − 2` exactamente, o sea que es una **FK desalineada por el mapeo**, no un conteo
  (confirma lo del §17.18). El conteo correcto de esa tabla es `COUNT(*)`, y `HCASOSMMI` sirve para
  encontrar el certificado, cuando se corrija el mapeo.
- **La última MM capturada es del 11/08/2026** (y el último caso de investigación, del 14/08): la
  oficina tampoco tiene Mortality Materna de agosto en adelante en su propio sistema.

### 17.21 ✅ La captura se cortó el 01/08/2026: la semana 31 quedó a medias (28/09/2026)

Con la convención venezolana ya aplicada (§17.19), el desplome de natalidad y mortalidad tiene una
**fecha exacta de corte**. Antes, con la numeración ISO, parecía empezar en la semana 32.

#### La serie

| Semana | Rango (domingo→sábado) | Defunciones | Nacimientos |
|---|---|---|---|
| 28 | 13-07 a 19-07 | 197 | 241 |
| 29 | 20-07 a 26-07 | 198 | 288 |
| **30** | **27-07 a 01-08** | **167** | **165** |
| 31 | 02-08 a 08-08 | **37** | **18** |
| 32 | 09-08 a 15-08 | 39 | **0** |
| 33 | 16-08 a 22-08 | 42 | **0** |
| 34 | 23-08 a 29-08 | 25 | **0** |
| 35 | 30-08 a 05-09 | **2** | **0** |
| 36+ | — | 0 | 0 |

**El último día con captura completa es el sábado 01/08/2026** (135 defunciones y 143 nacimientos
en esa semana, con el pico del viernes 31/07). A partir del **domingo 02/08** la natalidad se cae a
18 y de la semana 32 en adelante **no llega ningún nacimiento**. La mortalidad no llega a cero porque
hay rezago: los últimos registros son del 31/08 (semana 35) y son pocos.

#### No es un centro: se quedaron callados todos a la vez

| Establecimiento | Def. antes 02/08 | Def. desde 02/08 | Nac. antes | Nac. desde |
|---|---|---|---|---|
| Hosp. Central Univ. Dr. Antonio María | 1.300 | 12 | 3.353 | 0 |
| Hosp. Dr. Pastor Orozco | 1.028 | 2 | 2.612 | 0 |
| Hosp. Dr. Luis Gómez López | 153 | 0 | — | — |
| Hosp. Dr. Baudilio Lara | 83 | 0 | 176 | 0 |
| Hosp. Esp. Ped. Agustín Zubillaga | 73 | 5 | — | — |
| Hosp. La Caruciña | — | — | 627 | 10 |
| Los 20+ establecimientos restantes | | 0 | | 0 |

**Ningún centro explains el corte**: los dos grandes (Central y Pastor Orozco, ~85% del volumen) y
todos los demás panduan simultaneous. Eso descarta un problema de una sala o de un hospital y
apunta a algo **central**: el proceso de sincronización o el envío del sobre.

#### La cola de eventos confirma la fecha

`sismai."EVENTOS"` (la cola del legacy) tiene eventos de `CERTIFICADO` y `CERTNACIMIENTO` solo hasta
el **04/08/2026**:

| Día | Eventos de certificado/nacimiento |
|---|---|
| 29/07 | 198 |
| 30/07 | 195 |
| 31/07 | 192 |
| **01/08** | (día del envío) |
| 03/08 | 207 |
| **04/08** | 134 |

Los últimos eventos son del **04/08**, que es el sobre de la semana 30 (cerrada el sábado 01/08):
la oficina **sí envió** esa semana. Lo que no hay es ningún evento posterior, ni una fila de
diagnóstico. La última MM capturada es del 11/08 y el último caso de investigación del 14/08
(§17.20), así que tampoco es que los centros dejaran de emitir: **dejaron de llegar al espejo**.

#### Conclusión

El corte es del **domingo 02/08/2026**, en la semana 31, después del envío correcto de la semana 30
del martes 04/08. Como afecta a todos los establecimientos a la vez y la cola no registra ni un
evento de diagnóstico posterior, la hipótesis más probable es una **interrupción del proceso de
sincronización** (o del envío) el 02/08, no un problema de captura en los centros.

**Confirmado por la oficina el 28/09:** los sobres **se emiten y se envían todos los martes**. Es
decir, los centros **sí siguieron capturando**: los datos de las semanas 31+ existen en el sistema y
no nos llegaron. **El hueco es recuperable** extrayéndolos del Oracle vivo (§17.24 y la fase 1 del
§17.17), y las cifras de agosto-septiembre que muestra el tablero son del extracto parcial, no las
de la oficina.

### 17.22 ❌ `HCASOSMMI` NO estaba desalineado: es una FK válida a `CASOS_MMI` (28/09/2026)

Corrige la hipótesis del §17.20. `HCASOSMMI` es **exactamente `ID − 2` en las 749 filas**, lo que
hacía pensar en un mapeo corrido. **No es así:** la desalineación es con la secuencia de la propia
tabla, y el campo es una llave foránea correcta.

| Prueba | Resultado |
|---|---|
| `RENGLON_CASOSMM.HCASOSMMI` → `sismai."CERTIFICADO"."ID"` | **0 de 749** |
| `RENGLON_CASOSMM.HCASOSMMI` → `sismai."CASOS_MMI"."ID"` | **748 de 749** |
| Renglones por caso (`HCASOSMMI` repetido) | ninguno: **1 renglón por caso**, 749 casos |
| El único huérfano | `ID_RENGLON 2912174605`, de **03/08/2018** (fuera de alcance) |

Es decir: `CASOS_MMI` es la **cabecera de la investigación** (nombre, sexo, edad, fecha de
ocurrencia) y `RENGLON_CASOSMM` es su **detalle obstétrico** (forma de parto, edad gestacional, control
prenatal, hijos). La relación es 1 a 1 y está bien. **El modelo `legacy/models_legacy.py` no necesita
corrección**; lo que hay que corregir es la conclusión del §17.20: el conteo de la tabla es
`COUNT(*)` (749) y `HCASOSMMI` sirve para encontrar la investigación, no el certificado.

#### Las 18 investigaciones de 2026 contra las 16 MM certificadas

Las 18 investigación de 2026 (por `FECHAOCURRENCIA`) contra los 16 certificados con
`HPRESENCIAEMBARAZO` IN (1,2):

| | Casos |
|---|---|
| MM certificadas (`HPRESENCIAEMBARAZO` 1 o 2) | **16** |
| Investigaciones de muerte materna en 2026 | **18** |
| MM **sin** investigación | 1 (27/01/2026) |
| Investigación **sin** MM certificada | **4** |

Sobre esas 4: son las fechas 07/04, 01/06, 04/06 y 07/07. En esas fechas **sí hay certificados de
fallecimiento de mujer** (10, 19, 19 y 8 respectivamente), pero **ninguno tiene el campo
`HPRESENCIAEMBARAZO` lleno**: están como `NULL`. O sea, las 4 muertes maternas que epidemiology sí
investigó **no se pueden ver en el tablero**, porque el certificado se emitió sin marcar
embarazo/puerperio. Es el mismo hueco de calidad de dato del §17.20, no un bug de conteo.

⚠ Nota sobre el sexo: los códigos **no son los mismos entre tablas**. En `CERTIFICADO`, `SEXO = 1` es
femenino; en `CASOS_MMI`, `HSEXO = 2` es femenino. Al cruzar por `SEXO` equivocadamente no aparece
ningún match, lo que reinforces la confusión. El cruce correcto de investigations con certificados
es por **fecha** (y `SEXO = 1` en el certificado), no por `HSEXO`.

**Conclusión de F:** no hay bug de mapeo que arreglar. La diferencia entre las 16 MM del tablero y
las 18 investigaciones (más la +1 violenta de la oficina) es **calidad del dato en origen**:
certificados maternos emitidos sin `HPRESENCIAEMBARAZO`. La acción correcta es pedir a la oficina
que complete ese campo (acción 4 del acta de conciliación), no tocar el código de mapeo.

### 17.23 La cola del sobre es una ventana móvil, no una semana (28/09/2026)

Al documentar el corte de captura (§17.21) se aclara una cosa del contrato de la cola que cambia
cómo se interpreta `T_EVENTOS`: **no es "la semana"**, es "todo lo que se movió desde el último envío".

#### Lo que muestra el sobre del 22/09

El `routlar1_2292026_1238.ZIP` (22/09/2026 12:38) trae `T_EVENTOS` con **9.496 filas**, de FECHA entre
el **16/09 13:01** y el **22/09 12:33**. Repartidas:

| Día | Eventos | Tablas distintas |
|---|---|---|
| 16/09 | 13 | 3 |
| 17/09 | 1.262 | 12 |
| 18/09 | 1.088 | 11 |
| 19/09 | 8 | 2 |
| 20/09 | 8 | 2 |
| 21/09 | 3.314 | 10 |
| 22/09 | 3.803 | 13 |

La cola **cruza dos martes** (15/09 y 22/09) y arranca el 16/09, que es el día siguiente al envío
anterior (`routlar1_1692026_1245.ZIP`, 16/09 12:45). O sea, arranca **16 minutos después del
sobre anterior**, no un lunes. Por tabla, lo que más viaja es `RENGLONTELE` (5.520),
`RENGLON_EPI15` (1.472), `DOCUMENTO` (501), `CAUSA_MMEDICO` (469) y los tres de natalidad
(`CERTNACIMIENTO`/`NAC_RNACIDO`/`NAC_MADRE`, 360 c/u) — más `CERTIFICADO` con 154.

#### Qué implica

1. **No se puede pedir "la semana 37" como ventana de reenvío.** Hay que pedir "desde el último
   envío", porque el sobre del 22/09 ya se llevó lo del 16-21/09 aunque la semana 37 Closing el
   19/09. Cualquier plan que pida "reenviar semanas 31 a 37" va a duplicar lo que ya se envió el
   17 y el 22, y `EVENTOS_SINC` no tiene clave única (§17.4) para que la deduplicación sea gratis.
2. **La etiqueta `SE-NN` del exportador es una conveniencia local**, no un campo del protocolo: el
   sobre real no nombra la semana, solo manda filas. El `PERIODO` viaja dentro de `DOCUMENTO`.
3. **Por eso el corte del 02/08 (§17.21) no se nota como "semana faltante" en la cola**: la cola
   seguiría enviando lo que haya, aunque sean pocos eventos. El 04/08 hay 134 eventos de
   certificado/nacimiento, y del 05/08 en adelante, ninguno. Los sobres del 15/09 y del 22/09
   existen, pero llegan vacíos de lo que importa.
4. **Al reintentar la sincronización (martes 29/09) hay que decidir la ventana antes de exportar**:
   `desde = último FECHA realmente enviado` (el 22/09 12:33 si se confirma ese sobre), no "lunes".

**Respuesta de la oficina (28/09): nadie conoce el criterio del TRUNCATE**, lo hace el sistema de
envío del legacy sin documentación. Por eso la ventana **no se puede calcular a priori**: se deriva
de lo observado (el corte es el último `FECHA` enviado, con ~16 min de margen) y se usa
`desde = último envío`. Ver §17.24.

### 17.24 ✅ Respuestas de la oficina (28/09/2026): el central usa semana epidemiológica

Las 4 preguntas abiertas quedan respondidas. Las dos primeras **desbloquean la extracción** y
corrigen el plan del §17.17.

**1. El central (nivel superior) numera las semanas epidemiológicas, no ISO.** Por lo tanto el cambio de §17.19 **no es una incompatibilidad de formato: es una corrección**, y el plan B de "no cambiar hasta confirmar" queda sin objeto. Se puede enviar con la numeración venezolana sin riesgo. Sigue siendo legítimo reenviar el histórico con la convención corregida, porque el legacy (`sismai."DOCUMENTO"."PERIODO"`) ya venía así y el central ya lo venía recibiendo.

**2. El corte del 02/08 es del envío semanal, no de la captura en los centros.** La oficina confirma que **los sobres se emiten y se envían todos los martes**. Eso cambia la interpretación del §17.21 en lo importante: **los datos de las semanas 31+ existen en el sistema del centro**, se emiten, y lo que falló es que no nos llegaran. Por lo tanto:

- El hueco **es recuperable**: la fase 1 del §17.17 los baja del Oracle vivo, en vez de resignarse a trabajar con el espejo truncado.
- No hace falta "pasar a nivel superior" a buscar los datos: están en el mismo servidor, en `SISMAI."CERTIFICADO"` y `SISMAI."NAC_RNACIDO"`.
- Las cifras de agosto-septiembre que hoy muestra el tablero no son definitivas: son las del extracto parcial, no las de la oficina.

**3. El desfase de 10 MN (218 vs 228) son faltantes.** Queda registrado como faltante del nivel Lara, **se revisa después y se escala a nivel superior** (acción 5 del acta). No bloquea nada más.

**4. Nadie conoce el criterio del TRUNCATE** de la cola: lo hace el sistema de envío del legacy, sin documentación. Por lo tanto **no se puede calcular la ventana a priori** y hay que derivarla de lo observado (§17.23): el corte observado es el del último envío (22/09 12:33), con 16 minutos de margen respecto al sobre anterior. Para la ventana del 29/09 se usa `desde = último FECHA realmente enviado` y se deja un margen de seguridad, aceptando que se repitan algunos eventos (que el central deduplica por `TABLA`/`ID`).

#### Script de la fase 1 (listo para el 29/09)

`migracion/extraer_mm_mn_roto.sh` (driver) + `migracion/extraer_mm_mn_roto.sql` (consultas).
Solo lectura: `SELECT` + `SPOOL`, nunca toca `EVENTOS_SINC`. Trae el periodo `>= 01/08/2026`
(semana 31, el día del solape sirve de control) de defunciones, nacimientos, los casos de muerte
materna y neonatal, y el catálogo de establecimientos. Genera un `manifiesto.txt` con el conteo de
filas por archivo y una bitácora. Ajustable con `DESDE=`, `SALIDA=`, `HOST=`.

Todo validado contra el espejo PostgreSQL: las 9 consultas ejecutan y las 89 columnas existen.
Dos errores se detectaron **antes** de tocar el servidor y se corrigieron:

- `CERTIFICADO."STATUS"` **no es NULL nunca** (es 1/0, 173.533/173.533), así que el filtro
  `STATUS IS NULL` devolvía **cero defunciones**: se eliminó.
- El filtro de nacimientos va por **`NAC_RNACIDO."FECHANACIMIENTO"`**, no por
  `CERTNACIMIENTO."FECHACERTIFICADO"`. En el espejo hay **1.522 certificados emitidos desde el
  01/08 que corresponden a nascimientos de junio y julio** (registro tardío): filtrar por el
  certificado traía datos que ya teníamos y perdía el periodo real. El importador usa la misma
  regla (`FECHANACIMIENTO` y, si falta, `FECHACERTIFICADO`). Los tardíos salen aparte en
  `nacimiento_tardio.csv` solo para conciliarlos.
- Los renglones de MM/MN se filtran por **`CASOS_MMI."FECHAOCURRENCIA"`** (la fecha de la muerte),
  no por `FECHAOPERACION` del renglón, que es la fecha en que se cargó la fila.

Sobre el espejo, la fase 1 rinde: 152 defunciones, 23 nacimientos de agosto, 1.499 registros
tardíos, 56 casos de investigación, 85 renglones de MN y 1 de MM. También se detectó que de los
29 recién nacidos de agosto **6 no tienen certificado** todavía, lo cual es normal (son recientes) y
queda anotado para el control de calidad de la carga.

### 17.25 ⚠ MN de las semanas 36 y 37, y el `repllar1.log` que falta (28/09/2026)

Dos datos de hoy que cambian el plan de la ventana del 29/09.

#### 1. La oficina cargó MN de las semanas 36 y 37 (28/09/2026)

Avisaron que **el lunes 28/09 cargaron muertes neonatales de las semanas 36 y 37** y que **mañana
(29/09) confirman la cantidad**. Qué se sabe y qué no:

- **No se conoce la cifra todavía.** No se escribe ningún número en el acta: hasta que la oficina
  lo confirme, poner uno sería inventarlo.
- **Cambia la base de comparación del desfase de 10 MN** (acción 3 del acta, 218 vs 228). Ese
  desfase se había medido contra un espejo congelado. Con MN de las semanas 36–37 recién cargados
  en el centro, **el número de control hay que rehacerlo**: la diferencia anterior puede ser
  completamente distinta. El 218/228 queda como registro histórico, no como conclusión vigente.
- **El rango de la extracción ya cubre esas semanas**: `DESDE=01/08/2026` (inicio del hueco) cubre
  la 31 en adelante, y las semanas 36 y 37 caen de sobra. No hay que ampliar nada por este motivo.
- **Ojo con las definiciones:** el MN del tablero y del acta sale de `Defuncion` (0–27 días entre
  `FECHA_M` y `FECHA_N`), no de `RENGLON_CASOSMI`. Si la cifra de la oficina viene de los renglones
  MMI, **no es comparable** con la nuestra y habría que pedir el criterio. Queda como pregunta para
  el 29/09 junto con la cantidad.

#### 2. El sobre semanal ya no trae 5 archivos desde el 08/09 (regresión)

`migracion/preflight_ventana.sh` compara el `routlar1_*.ZIP` más reciente con los 5 archivos que
debería traer. Resultado sobre `enviados/`:

| Sobre | Fecha | Archivos | Falta |
| --- | --- | --- | --- |
| `routlar1_242026_1552.ZIP` | 24/08/2026 | 5 | — |
| `routlar1_1732026_1532.ZIP` | 17/08/2026 | 5 | — |
| `routlar1_2652026_1648.ZIP` | 26/08/2026 | 5 | — |
| `routlar1_3062026_1551.ZIP` | 30/08/2026 | 5 | — |
| `routlar1_892026_1357.ZIP` | 08/09/2026 | **4** | `repllar1.log` |
| `routlar1_1692026_1245.ZIP` | 16/09/2026 | **4** | `repllar1.log` |

**`repllar1.log` desapareció del paquete a partir del 08/09/2026.** Es el log de replicación, no un
dato: `routlar1.dmp` sigue viniendo con contenido, así que **los sobres siguen llevando los
registros**. Lo que se perdió es la traza de replicación, que es justo lo que serviría para saber
qué se procesó y qué no.

Esto confirma el pendiente que ya estaba anotado en §17 («revisar la generación de los 5 archivos del
ZIP del martes»): el proceso que los produce (`RoutLar1`/scripts de `/home/salud/bin`) dejó de
escribir ese log. **A revisar en el servidor el 29/09**, junto con lo demás. No bloquea la
recuperación de MM/MN (que lee de `CERTIFICADO`/`NAC_RNACIDO`, no del sobre), pero sí debilita la
auditoría de los envíos semanales.

#### 3. Estado del código al 28/09

- `manage.py cargar_mm_mn_roto` listo y probado (20 pruebas): idempotente, no pisa trabajo humano,
  resuelve organización por nombre dentro del árbol Lara, y **aborta** si el catálogo de
  establecimientos no trae las raíces Lara en vez de adivinar.
- `migracion/preflight_ventana.sh` listo; sobre el estado actual da **FALLO** (correcto: hoy no hay
  respaldo ni es día de envío). Calcula `DESDE` desde lo último cargado (última defunción
  31/08/2026, último nacimiento 08/08/2026).
- El tablero ya avisa cuando la serie está incompleta (`cobertura` en `/api/registros/dashboard/`):
  hoy reporta **nacimientos 51 días atrasado** y **defunciones 28 días**, que son los números que
  justifican no publicar totales de agosto-septiembre como definitivos.

---

## 18. [COMPLETADO] Conciliación SIS-04/EPI-12 crudo vs SISV, 2009–2026 (28/09/2026)

App `conciliacion` (propia; no toca `vigilancia`) + `manage.py conciliar_eno`. Compara, por
**año + semana + organización + evento**, la transcripción legacy (`DOCUMENTO` → `RENGLONTELE` →
`CODIFICADOR`, filtrando árbol Lara y `TIPO=1`) contra lo que realmente guardó SISV.

**Resultado: `diferencia = 0` en los 18 años.** 530.827 celdas, 615.135 detalles por centro,
8.740.569 casos de enfermedad, todos cuadrados. **El ETL es fiel: no hay datos que recuperar.**

Lo que queda fuera está explicado y es por diseño, no pérdida:

| Qué | Filas | Casos | Por qué |
| --- | --- | --- | --- |
| Cuadra contra SISV | 482.635 | 8.740.569 | — |
| Pseudo-TOTAL excluido | 31.534 | 33.375.675 | no son enfermedades (78,9% del volumen) |
| 34 enfermedades sin equivalente ENO | 16.658 | 603.625 | no existe evento ENO que las reciba |
| **Cifra correcta, centro perdido** (fallback `LEGACY-LARA`) | 16.748 | 1.824.303 | 263 establecimientos legacy sin organización propia |

Avisos que evitan conclusiones equivocadas:

- **Pseudo-TOTAL no es enfermedad.** `1126717818` «TOTAL DE PACIENTES ATENDIDOS» (802.539 casos solo
  en 2026) se excluye; `1126717832` «TOTAL DE PACIENTES HOSPITALIZADOS» **sí** tiene equivalente ENO
  y se conserva. Tratarlos igual produce cifras absurdas.
- **Lo no conciliado de 2026 son 25.634 casos, el 98% código 041 «SÍNDROME VIRAL (B34)»**, no un
  fallo de carga. El histórico de esas 34 enfermedades son 375.913 casos de código 225
  (infecciones respiratorias, que la oficina dejó de llenar) y 220.273 de código 041.
- **Atribución de quién transcribió: parcial y no es una cuenta de persona.** `HISTDOC.INSTANCIA` es
  la **estación de trabajo** (`USUARIO` está vacío en las 58.596 filas), solo registra
  `EVENTO='Creado'` —no cada edición— y arranca el **05/08/2019**. Completa desde 2020, parcial en
  2019, ninguna antes; antes de esa fecha el campo queda vacío a propósito.

Decisión de diseño que conviene no deshacer: cuando varios establecimientos legacy caen en la misma
organización, el detalle deja `sisv_h/sisv_m` en `NULL` y marca `colision`, porque SISV guarda la
**suma** y repartirla entre centros sería inventar.

---

## 19. [COMPLETADO] Fase B — muertes ENO vs CERTIFICADO y el establecimiento perdido (28/09/2026)

**El renglón MORTALIDAD del ENO nunca se usó.** `RENGLONTELE."MUERTESHOM"/"MUERTESMUJ"`
suman **3.618 muertes en todo 2009–2026** frente a **173.533 certificados de defunción**:
el 2%. Por eso la conciliación de la fase A marcaría `MORTALIDAD` como `CUADRA` sobre
ceros. No es un defecto de la migración: las oficinas nunca transcribieron muertes al
EPI-12. La mortalidad real de SISV vive en `registros.Defuncion`.

**`CERTIFICADO` → `Defuncion` está completo: 173.533 = 173.533.** Pero la mitad estaba
inutilizable por falta de centro, y la causa era un bug real del importador:

- `importar_legacy_registros._defunciones` leía solo `CERTIFICADO."HESTABLECIMIENTO_OCUR"`.
- Ese campo viene **nulo en 87.203 de los 173.533 certificados**, mientras
  `"HESTABLECIMIENTO"` **siempre está** (en 87.203 de 87.203; cero casos con ambos nulos).
- Resultado: 87.203 muertes importadas sin nombre de establecimiento y, por tanto, con
  `organizacion_id IS NULL` — el 50,3% del histórico de defunciones, invisible para
  cualquier usuario con alcance de centro.

Corregido en dos pasos:

1. `importar_legacy_registros` ahora usa `_OCUR` **y, si es nulo, `HESTABLECIMIENTO`**
   (misma precedencia que ya usaba `cargar_mm_mn_roto`). Evita que se repita.
2. `manage.py recuperar_establecimiento_defuncion [--ejecutar]` rellena el nombre en lo ya
   importado. Un solo `UPDATE ... FROM` en transacción, **solo sobre campos vacíos**:
   nunca pisa un establecimiento ya escrito. Idempotente.

Aplicado sobre la BD: **87.203 defunciones recuperadas** y, con
`asignar_organizacion_legacy --ejecutar`, **87.240** asignadas a su centro (se crearon 4
organizaciones y se reutilizaron 711). Quedan **70 defunciones sin centro**, de 39
establecimientos que no están en el árbol Lara («DES PORTUGUESA», hospitales de otros
estados): es correcto que no se inventen centros.

Efecto colateral útil: el mismo comando asignó **14.460 fichas de vigilancia** que también
estaban huérfanas. Las 8.703 que siguen sin centro son fichas individuales sin
establecimiento (se agrupan por residencia), lo cual es lo esperado.

Con esto la mortalidad por año queda atribuida al 100% en 2009–2026 (de 4 centros en 2009
a 100–140 por año). 6 pruebas nuevas; suite completa **137 OK**.

---

## 20. [COMPLETADO] Fase C — MM/MN por semana, y dos caídas de captura que nadie había visto (28/09/2026)

Al contrastar el MN de SISV (`Defuncion`, 0–27 días entre `fecha_nacimiento` y `fecha_evento`)
contra el registro materno-infantil de la oficina (`sismai."CASOS_MMI"`, 10.737 casos 2009-2026,
con `EDAD` en horas/días/meses/años y enlace `HDOCUMENTO` → `DOCUMENTO` → centro + semana):

**El MN de SISV sigue bien al registro de la oficina** en los años con captura normal
(2015-2026 difieren en el orden del 5-15%). Eso valida la definición de 0 a 27 días que ya
usa el tablero. Los neonatos de `CASOS_MMI` son las filas en horas (1.912) y días ≤27 (5.251).

**Pero hay dos caídas de captura de meses que ninguna pantalla detecta:**

| Serie | Normal | Colapsada | Recuperada |
| --- | --- | --- | --- |
| Defunciones | ~1.000/mes | **2019-06 → 2021-07** (11-90/mes) | 2021-08 |
| Nacimientos | ~900/mes | **2019-10 → 2021-11** (5-45/mes) | 2021-12 |

En las 21 meses de 2019-06 a 2021-02 hay **3.083 certificados frente a 22.779** en los 21
meses previos: faltan ~19.700. Las defunciones de 2019 (5.291) y 2020 (427) no son un
cambio epidemiológico, es que el sistema dejó de capturar.

**Y la información sí se registró en otro lado:** el registro MMI de la oficina tiene **455
casos en 2019 y 334 en 2020**, con 264 y 165 neonatos, mientras el sistema de certificados
tenía 167 y 5. O sea: durante la caída se registró la mortalidad materno-infantil en un
sitio y no en el otro. Es la misma lógica del hueco MM/MN de agosto-septiembre 2026 (§16), dos
años antes, y nadie lo había detectado.

Por qué el tablero no lo avisa: `_cobertura` marca meses **vacíos**, no meses **degradados**.
Comprobado: entre 2009-01 y 2026-08 **no hay ni un solo mes con cero filas** en nacimientos,
defunciones ni fichas, así que `meses_sin_datos` no se dispara nunca y el banner solo funciona
por `atraso_dias` (días sin registrar). Es un control de "voy al día", no de "este período está
completo". Detectar una caída exige umbrales, y un umbral mal puesto inventa huecos falsos; por
eso **no se cambió nada sin decidir** (ya resuelto, ver §20.2).

Para responder si esos certificados existen en el Oracle de origen (que es lo que decide si la
pérdida es recuperable o definitiva) está `migracion/diagnostico_hueco_2019_2021.sh`: solo
lectura, conteo mensual de `CERTIFICADO.FECHA_M` y `NAC_RNACIDO.FECHANACIMIENTO` en 2018-2022,
local o por ssh (`HOST=192.168.5.200`, `SIMULAR=1` para ver qué haría sin correr). **No se ha
podido ejecutar**: `192.168.5.200` no responde desde la red de trabajo actual. En el espejo los
números del colapso son los mismos en `sismai."CERTIFICADO"` que en `registros_defuncion`
(51/36/83/34...), o sea que el importador es fiel: si falta, falta en el origen.

> ⚠ **Superado por §21 (CERRADO 29/09/2026):** la definición quedó resuelta sin preguntar a la
> oficina — la muerte materna son las filas que enlazan con `RENGLON_CASOSMM`, y el indicador del
> tablero ya sale de ahí. Lo que sigue es el registro de la duda original, a modo de historial.

**MM sigue bloqueado por una definición, no por un bug:** `CASOS_MMI` no distingue la muerte
materna de la infantil. En el grupo de edad «años» hay 708 personas de 12-50 años con
`HSEXO=2`, lo que sugiere que **aquí 2 = F**, al revés que en `RENGLONTELE` (donde 1 = F y
2 = M, verificado con nombres). Con las dos convenciones mezcladas, cualquier cifra de MM
salida de ahí sería una suposición. Hace falta que la oficina diga qué filas de `CASOS_MMI`
son maternas.

### 20.1 Conciliación neonatal semanal (cerrado) — `manage.py conciliar_neonatal`

El MN quedó conciliado de verdad, por semana y centro: modelo `conciliacion.ConciliacionNeonatal`
(migración `0003`) y comando homónimo, con `--desde/--anio/--ejecutar/--csv/--todo-pais/--alerta`.
Dry-run por defecto, CSV con BOM, 9 pruebas nuevas; suite completa **146 OK**.

| Año | Legacy | SISV | Dif. | % |
| --- | --- | --- | --- | --- |
| 2018 | 452 | 516 | -64 | -12 % |
| 2019 | 262 | 171 | **+91** | **+53 %** |
| 2020 | 172 | 11 | **+161** | **+1464 %** |
| 2021 | 242 | 412 | -170 | -41 % |
| 2022 | 564 | 627 | -63 | -10 % |
| 2023 | 793 | 776 | +17 | **+2 %** |
| 2024 | 583 | 580 | +3 | **+1 %** |
| 2025 | 384 | 389 | -5 | **-1 %** |
| 2026 | 234 | 218 | +16 | **+7 %** |

Dos sistemas independientes (el registro MMI de la oficina y los certificados de SISV) **coinciden
casi exacto en 2023-2026**. Eso valida a la vez la definición de 0-27 días del tablero y el
importador. 2009-2018 sale -10 % a -30 % (SISV por encima): el formulario MMI se rellenaba menos
que el certificado, no al revés. Solo 2019-2020 se invierte, y es la caída de captura.

Dos trampas del legacy que hubo que esquivar:

- **`DOCUMENTO."PERIODO"` no es una semana**, es un número de formulario del centro: en 2019 el
  periodo 29 va del 2 de enero al 12 de septiembre, y hay **20.446 pares de periodos solapados**.
  La semana se calcula **en los dos lados desde la fecha real del evento** con
  `vigilancia.services.semana_epidemiologica`.
- **`DOCUMENTO."TIPO"` = 23** en los 10.754 documentos de `CASOS_MMI`, no 1 (1 es el ENO de
  mortalidad, `RENGLONTELE`). Filtrar por 1 deja el lado legacy vacío **en silencio**: la primera
  corrida dio 0 sin avisar. Hay una prueba que fija el 23.

⚠ El lado SISV solo cuenta defunciones **con fecha de nacimiento** (104 sin ella en 2026): es un
mínimo, y las que no la tienen pueden ser neonatos que se quedan fuera.

### 20.2 Detección de meses degradados (HECHO 02/10/2026)

Lo que el §20 dejó pendiente («no se cambió nada sin decidir») ya está hecho. `ConfiguracionGeneral`
ganó tres campos (migración `registros.0007`): `detectar_meses_degradados` (bool, por defecto
`True`), `factor_mes_degradado` (float, `0.40`) y `min_meses_historia` (entero, `12`), expuestos
por `GET/PUT /api/registros/configuracion/` (escribe quien `puede_configurar`) y persistidos en la
BD; no hay UI de configuración.

`DashboardView._meses_degradados(series, cfg, rango)` recorre los meses terminados de cada serie
(en alcance) y marca un mes cuando su total cae por debajo de `factor × mediana` de los últimos
`min_meses_historia` meses **normales** (los no marcados). La base se ancla así al último nivel
sano: con una mediana móvil corriente, a los 12 meses de caída la referencia ya estaría tan baja
como la caída y dejaría de avisar. Es conservador: exige 12 meses normales antes de marcar,
ignora el mes en curso (a mitad de mes siempre está a medias) y se puede desactivar. El rango
solo filtra lo **reportado**, no la base: mirando 2026 no avisa de la caída 2019-2021; mirando
2019/2020/2021 sí. `_cobertura` lo entrega como `meses_degradados` y `completo` pasa a ser falso
si hay alguno; `AvisoCobertura` (Tablero.jsx) lo muestra bajo «Meses muy por debajo de lo
habitual».

Verificado contra la BD real: con `factor` 0,40 y 12 meses de historia, 2020 marca **14 meses de
nacimientos** (dic 2019–ene 2021) y **13 de defunciones** (dic 2019–dic 2020), justo las caídas
descritas arriba; 2026 marca **1** en cada serie (agosto de 2026, el corte del 02/08). 5 pruebas
nuevas (`MesesDegradadosTableroTests`), suite **227 OK**.

---

## 21. [CERRADO 29/09/2026] La muerte materna: el registro de investigación manda sobre el certificado

**No hubo que preguntar nada a la oficina.** La pista de §21.1 funcionó tal cual y además corrigió
el indicador del tablero, que estaba mal desde siempre. Resumen de lo verificado y aplicado:

- `sismai."RENGLON_CASOSMM"` tiene **749 filas** y `sismai."RENGLON_CASOSMI"` **9.993**; `CASOS_MMI`
  tiene 10.742. `HCASOSMMI` **es una llave válida a `CASOS_MMI."ID"`**: 748 de las 749 filas de MM
  enlazan y traen `FECHAOCURRENCIA`. El grano es (persona, causa), pero en la práctica hay **748
  personas distintas en 748 renglones**, así que en MM contar renglones sí es contar muertes.
- **El "bug de mapeo" de §17.18 no existía.** `HCASOSMMI` no está desfasado: es el ID de la persona
  (997186319 y compañía), y por eso `SUM(HCASOSMMI)` da 658.439.440.845. `PERIODOOCURRENCIA` viene
  `NULL` en las 749 porque **no es la fecha**: la fecha de la muerte está en
  `CASOS_MMI."FECHAOCURRENCIA"`. No hay que corregir `models_legacy.py` ni el orden de columnas.
- **El MM sí es atribuible a un centro**, igual que el MN: sale por `CASOS_MMI."HDOCUMENTO"` →
  `DOCUMENTO."HORIGEN"`, y se reparte en **19 establecimientos**, todos del árbol Lara (502 en el
  central, 118 en `DES LARA`, 81 en Pastor Oropezá IVSS...). No hizo falta el agregado sin
  organización para nada.
- `DOCUMENTO."TIPO"` es **23** en los formularios MMI, no 1, igual que en la conciliación neonatal.

### 21.1 El hallazgo: el indicador de MM del tablero estaba subcontando

El tablero contaba MM como `Defuncion.embarazo_o_puerperio`, que viene de
`CERTIFICADO.HPRESENCIAEMBARAZO IN (1, 2)`. **Ese campo es un aviso opcional del certificador, no un
registro**: el certificado de defunción se diligencia en el hospital y describe a la mujer que
murió; el embarazo o puerperio es un dato adicional que el certificador marca **si se le ocurre**.
Lo hace en una fracción de los casos:

| Año | MM en el registro de investigación | MM en el certificado | Marcado |
| --- | --- | --- | --- |
| 2016 | 65 | 1 | 2 % |
| 2017 | 78 | 3 | 4 % |
| 2019 | 40 | 0 | 0 % |
| 2022 | 70 | 4 | 6 % |
| 2023 | 65 | 12 | 18 % |
| 2025 | 39 | 23 | 59 % |
| **2026** | **18** | **7** | **39 %** |
| Total 2009–2026 | 748 | 89 | 11,9 % |

> La columna «MM en el certificado» está tomada del estado **previo** a `corregir_mm_legacy`
> (§17.20), cuando el `embarazo_o_puerperio` del certificado solo marcaba el código 1
> (89 total / 7 en 2026). Con la corrección 1+2 el certificado marca **191** en el histórico y
> **16 en 2026** — que es lo que el espejo directo de `sismai."CERTIFICADO"` da. La tabla ilustra el
> subconteo original, no la cifra vigente.

**El registro da 18 para 2026, que es exactamente los 17 + 1 violenta que reportó la responsable de
Lara.** Con el indicador anterior el tablero decía 7.

La prueba de que no es un problema de captura sino de diligenciamiento: en 10 de las fechas de MM de
2026 hay defunciones femeninas en PostgreSQL ese mismo día, con el campo sin marcar. La muerte se
capturó; lo que no se llenó fue el aviso.

### 21.2 Lo que se aplicó

- **El tablero** (`registros/views.py::_mortalidad_materno_infantil`) cuenta MM desde
  `RENGLON_CASOSMM`+`CASOS_MMI` y expone `mm_certificadas` / `mm_codificadas` / `mm_pendientes` al
  lado, con `mm_fuente` para saber de dónde salió el número. `/reportes` usa la misma fuente.
- **Recorta por alcance** como el MN, porque el registro trae establecimiento. Con alcance de centro
  y **cero MM atribuidas a ese centro** se cae al certificado en vez de mostrar 0: un 0 ahí
  significaría "este centro no tuvo muertes maternas", que es justo lo que no se sabe. En el mirror
  de desarrollo todos los establecimientos caen al agregado porque `Organizacion` solo tiene las 6
  demo; con `asignar_organizacion_legacy` aplicado resuelve.
- **`manage.py conciliar_mm`** (gemelo de `conciliar_neonatal`, grano año/semana/organización): 567
  filas con la BD corregida (HPRESENCIAEMBARAZO 1+2, §17.20), 748 del registro contra **191
  certificados**, **88 semanas CUADRA, 31 DIFERENCIA, 406 solo en el registro y 42 solo en el
  certificado**. (Las cifras de la primera versión — 460 filas, 89 certificados, 33/36/382/9 — eran
  del estado previo a `corregir_mm_legacy`, cuando el certificado solo marcaba el código 1.) La
  diferencia **es** el hallazgo y el comando la reporta como tal en vez de esconderla.
- Modelo `conciliacion.ConciliacionMaterna`, migración `0004`, 8 pruebas nuevas; las de MM del
  tablero fijan el caso real (18 del registro contra 1 certificado) y que un registro vacío **no** es
  un cero. Suite: **156 pruebas** (antes 146).

### 21.3 Las 42 semanas «solo en el certificado»: ninguna fuente es completa

Al revés de lo temido, hay **42** semanas (post-corrección 1+2) con muerte materna **en el
certificado y no en el registro de investigación**, y no son ruido: las causas son *síndrome HELLP*,
*otras inercias uterinas*, *choque hipovolémico* y *trabajo de parto prematuro espontáneo*, más **una
violenta** (*agresión con disparo*, 2012), que es el «+1» que la responsable separó del resto. (Con
el certificado en su estado previo — solo código 1, 89 filas — eran 9 semanas; §21.2.) O sea: el
registro de investigación tampoco capturó todas. **El indicador es el del registro (es el que la
oficina usa y reporta) y el certificado se reporta aparte**, no se suman.

### 21.4 Las preguntas de §21.3 que ya no hacen falta

1. ~~¿Qué filas de `CASOS_MMI` son muerte materna?~~ **Resuelto**: las que enlazan con
   `RENGLON_CASOSMM`. No hace falta que la oficina defina nada.
2. ~~¿Qué significa `HSEXO` en `CASOS_MMI`?~~ **Resuelto por los datos**: las 18 MM de 2026 tienen
   `HSEXO=2` con edades de 16 a 38, o sea **2 = F** en esta tabla, al revés que `RENGLONTELE`
   (1 = F). Confirmado por 748 casos coherentes, no por 3 ejemplos.
3. ~~¿`CASOS_MMI` es acumulado o notificación por envío?~~ **No hace falta**: `RENGLON_CASOSMM` es
   una investigación por muerte, con una fila por persona, y su propia fecha.

Lo que **queda abierto** y sí conviene preguntar en algún momento, pero ya no bloquea nada:
por qué 10.111 de 10.742 filas de `CASOS_MMI` no tienen `CEDULA` y por qué hay cédulas repetidas
entre personas distintas; y qué son las 703 filas sin `UNIDAD_EDAD`. Sin identidad confiable no se
puede cruzar `CASOS_MMI` con `CERTIFICADO` uno a uno, pero **para contar MM no hace falta**: el
conteo no requiere cruzar identidades.

### 21.5 Lo que se descartó

La idea de reclasificar MM/MN **por causa CIE** (§20) sigue descartada y ahora se sabe por qué además:
en 2026 el 97,5 % de los certificados tiene `HCAUSABASICA` nula y solo 54 de 6.247 defunciones están
codificadas. El registro de investigación tampoco salva esto: su `HCAUSA_CIE10` viene sin catálogo
resuelto. La MM no se puede sacar del CIE mientras la codificación siga así.

---

## 22. [EJECUTADO 02/10/2026 — paso 1 cerrado y verificado] Respaldo total del Oracle y, aunque la sincronización sigue rota

> **El 02/10, en la oficina, el paso 1 se ejecutó y se verificó** (§22.7). Sigue pendiente lo demás: recompilar los 16 objetos (§22.3), que salgan 5 archivos (§22.4) y reevaluar (§22.5).

**Lo que pidió el usuario el 30/09:** respaldar la base de producción, corregir lo que impide que la
sincronización produzca los 5 archivos, y reevaluar los hallazgos después de que corra. **Alcance de esta
sección: dejar anotado el plan. Nada de lo de abajo se ha ejecutado todavía** (salvo los dos scripts
nuevos, que están escritos pero sin validar).

### 22.1 Lo que se encontró (30/09, solo lectura)

El paquete de la semana **`routlar1_2992026_137.ZIP` (29/09) trae 4 archivos, no 5**: `bloqlar1.log`,
`copyhistlar1.log`, `routlar1.log`, `routlar1.dmp`. Falta el quinto, que es el de replicación
(`repllar1.log` / `repllar1_mort.log` / `replla1_nata.log`).

Dos cosas que **no** son culpa del paquete:

- **`T_CERTNACI` no existe.** En `TEMP` hay 82 tablas, todas creadas el 29/09 a las 13:07, y sí están
  `T_CERTMORT`, `T_MADRNACI`, `T_RNACNACI` y `T_RNACANUL` — o sea que **el `CREATE` de natalidad corrió a
  medias**: la primera tabla falló y las demás se crearon igual.
- **`SISMAI.EVENTOS_SINC` está congelada.** 16.741 filas, **todas del 21/09 09:08** (la fecha del DROP+
  recreada), y solo de `PACIENTE_COND_ESPE`, `PACIENTE_FICHA_EPI` y `REG_VACUNACION`. **Ni un solo evento
  de `CERTIFICADO` ni de `CERTNACIMIENTO`.** Mientras no se encole, la sincronización no tiene materia
  prima aunque el paquete salga bien.

Además hay **16 objetos inválidos** (1 función `FIDPADRE`, 4 procedimientos `SPDOC`/`SPREGDSP`/
`SPREGEPI`/`SPREGTEL`, 11 vistas), siendo `NATALIDAD` laDependent de `T_CERTNACI`. Que estos objetos
inválidos **causen** la cola vacía es **una hipótesis razonable, no una causa probada**: el orden es
`CREATE T_CERTNACI` → vistas → **encolar** → `cr_repli_nata.sql`, y si todo el bloque falló en la primera
tabla, los eventos nunca llegaron a encolarse.

### 22.2 Pendiente 1 — Respaldo (lo primero, antes de tocar nada)

**Regla: ningún DDL en producción hasta que exista un respaldo verificado.**

- `migracion/respaldo_total.sh` (nuevo) — `exp` por esquemas `SISMAI TEMP HISTORICO INBDLAR1`.
  **Corregido el 30/09 (en casa):**
  1. **Credencial de base.** `exp` pide usuario/contraseña de Oracle, y la clave que abre el SSH del SO
     pero en la base da `ORA-01017` (probado el 30/09: `EXP-00056` → `ORA-01017` → `EXP-00030` →
     `EXP-00000`). Ahora el script **aborta sin `CLAVE_ORACLE`** (leída de `legancy_conf/credenciales.env`
     o del entorno, nunca en duro) y usa **`USUARIO_DB`** (configurable; por defecto el mismo del SO),
     porque la cuenta que exporta en la base puede ser distinta del usuario SSH (p. ej. `respaldo`).
     Sigue haciendo falta que el usuario dé la clave. Las claves de `SISMAI`/`TEMP`/`HISTORICO` están en
     `SaludCor/ActualizaS/System.cfg` del share pero **ofuscadas**, y no es seguro descifrar credenciales
     de producción para armar un respaldo: **el usuario debe dar una clave válida o autorizar crear un
     usuario de export.**
  2. `INDEXES=Y`/`CONSTRAINTS=Y`/`GRANTS=Y` → el `.dmp` ya es un respaldo **íntegro**.
  3. La contraseña ya **no queda en un parfile legible**: el parfile se escribe con `chmod 600` dentro
     del servidor y se **borra al terminar** cada esquema.
  4. Los esquemas corren **secuencialmente** (una exp espera a la anterior antes de arrancar), no los 4
     a la vez (el UNDO es de 1 GB, §17.7). Quitado el `FULL=Y` que hacía que `exp` ignorara `OWNER` y
     exportara la base completa 4 veces.
- `migracion/espejo_csv.sh` (nuevo) — respaldo por CSV con `sqlplus / as sysdba`, que **no necesita clave
  de base** y que PostgreSQL **sí** puede leer (un `.dmp` es binario de Oracle y no se puede importar,
  §17.8). **Lo que ya quedó verificado el 30/09** (simulación + prueba real, no solo escrito):
  - El conteo de control sale con **525 tablas** de los 4 esquemas y la estructura trae
    **exactamente 525 `CREATE TABLE`**: el contraste es el criterio de éxito, no "salió sin error".
  - Extracción real de `SISMAI.ACTIVIDAD`: **6.542 líneas de 13 campos**, con acentos correctos
    (`Niños y Adolescentes Abandonados`). Un renglón por fila, que es lo que exige el `COPY`.
  - `TEMPS.T_USUARIOS`: 5 filas, 21 campos.
  - La clave **ya no está en el repo**: se lee de `legancy_conf/credenciales.env` (ignorado por git) o
    de la variable `CLAVE`; sin ella el script se detiene con mensaje claro.
  **Lo que falta:** correrlo de verdad (2-4 h) y cargar a PostgreSQL. Los ajustes de sqlplus que lo
  hacen funcionar están comentados en el script porque no son evidentes: `SET WRAP OFF`/`TAB OFF` (sin
  ellos una fila larga se parte en varias y el `COPY` no cuadra columnas), `SET TRIMSPOOL ON`,
  `SET COLSEP ','` y `SET NUMWIDTH 20`. La base es **`WE8ISO8859P1`**, no `WE8MSWIN1252` como dice
  `AGENTS.md`; por eso `NLS_LANG` va en el entorno del proceso (en 10.1 `ALTER SESSION SET NLS_LANG` no
  existe) y hay que forzar `AMERICAN_AMERICA.AL32UTF8`. El DDL se saca con `GET_DDL` en un `SELECT`
  pelado porque el buffer de `DBMS_OUTPUT` es acumulativo y está capado a 32 KB: por PL/SQL abortaba en
  la tercera tabla.
- Destino: `/home/oracle` (59 GB libres). **Los dumps/CSV no van al repositorio** (datos sensibles) y
  deben quedar con permisos restringidos.

### 22.3 Pendiente 2 — Recompilar los 16 objetos (solo tras verificar el respaldo)

**Escrito el 30/09 (en casa):** `migracion/recompilar_16_objetos.sql` (lanzable con `sqlplus / as sysdba`
o con `migracion/recompilar_16_live.sh`, que hace el `ssh`/`sshpass` y pide confirmación), con la lista
exacta del §22.1 y **sin importar el `crear.sql` del share**. No se ha ejecutado: **cambia objetos del
sistema en producción, la autorización del usuario es explícita y solo cubre estos 16.** Comportamiento:

- Primero comprueba que existe `TEMP.T_CERTNACI` y **aborta antes de tocar nada** si no está: como
  `NATALIDAD` depende de ella, recompilarla sin la tabla la dejaría igual de inválida y no habría
  servido (la vista H_DEPEN, en cambio, no se toca por omisión de tabla: está en la lista y se
  recompila normal).
- Recompila **solo** los 16 (función `FIDPADRE`, procedimientos `SPDOC`/`SPREGDSP`/`SPREGEPI`/`SPREGTEL`
  y las 11 vistas). Un `ALTER ... COMPILE` que falle **no aborta el bloque**: se anota `SQLERRM` y se
  sigue con el resto.
- Al final cuenta inválidos **antes y después** con `ALL_OBJECTS` (en el esquema `SISMAI`) y muestra
  `ALL_ERRORS` de lo que siga roto: número, no impresión.
- Si `T_CERTNACI` no existe porque su `CREATE` falló, hay que crearla antes (el DDL del share
  `crear.sql` **no se usa**: borra `EVENTOS_SINC`).

### 22.4 Pendiente 3 — Que salgan 5 archivos

- `migracion/preflight_ventana.sh` ya se ajustó para aceptar los tres nombres posibles del log y para
  **exigir** `T_CERTNACI`/`T_CERTMORT`, así que hoy detectaría el paquete de 4. **Pero validar ≠ generar:**
  el quinto archivo lo produce el cliente Windows, y **no hay acceso a esa máquina**.
- Los scripts del share (`SincFich`, `cr_repli_*`, `bloqueob.sql`) son de ~2020 y **no incluyen el
  orquestador semanal actual**; tampoco hay log de replicación del 29/09 que diga por qué no se creó
  `T_CERTNACI`. Hay que ubiquitous el cliente (`SistemaTransferencia.exe`) o su `.bat` Weekly.
- **Nunca** correr `crear.sql` (hace DROP+CREATE de `SISMAI.EVENTOS_SINC`) ni `bloqueob.sql` (mata
  sesiones) para «resolver» esto.

### 22.5 Pendiente 4 — Reevaluar los hallazgos

Solo tiene sentido **después** de que la sincronización corra y traiga eventos. Entonces se repite el
diagnóstico (`migracion/diagnostico_certnaci.sql`, salida de referencia en
`auditoria/diagnostico_certnaci_20260930.txt`) para comprobar: (a) que la cola `EVENTOS_SINC` volvió a
crecer con eventos de `CERTIFICADO`/`CERTNACIMIENTO`, (b) que el ZIP trae 5 archivos, (c) que
`T_CERTNACI` existe y (d) cuántos objetos siguen inválidos. Hasta entonces, **la concordancia
EN/ISO de §17 y las conciliaciones de §18–21 no se tocan**: describen el histórico ya cargado.

### 22.6 Lo que se necesita del usuario para el 01/10

1. **Clave de una cuenta Oracle con permisos de lectura** (o permiso para crear una de export) y la
   **cuenta de base** (`USUARIO_DB`, puede ser distinta del SSH). Sin esto el `.dmp` clásico no sale; la
   vía CSV con `sysdba` funciona igual y es la que ya está encaminada. El `respaldo_total.sh` aborta con
   mensaje claro si falten `CLAVE`/`CLAVE_ORACLE`, y `SIMULAR=1` muestra lo que haría.
2. **Autorización explícita** para el `ALTER … COMPILE` de los 16 objetos (ya la dio el 30/09, pero
   conviene recordarla al ejecutar). Correr solo tras **verificar el respaldo** (que los 4 `.dmp` pesen
   y el `.log` diga «terminado correctamente»).
3. **Acceso al cliente Windows** que arma el paquete, o el `.bat` Weekly actual, para cerrar el punto del
   quinto archivo.

#### Checklist del 01/10 (orden de ejecución)

| # | Paso | Verificación de éxito |
| --- | --- | --- |
| 1 | `migracion/preflight_ventana.sh` (el respaldo de hoy >13:00 ya existe) | 5 salidas verdes, `DESDE` calculado |
| 2 | `SIMULAR=1 ./migracion/respaldo_total.sh` | Imprime los 4 comandos `exp`, no ejecuta |
| 3 | `./migracion/respaldo_total.sh` con `CLAVE`+`CLAVE_ORACLE` (`--` SECUENCIAL) | 4 `.dmp` + 4 `.log` en `respaldo_<fecha>_<hora>`; cada log con «terminado correctamente»; SHA-256 en pantalla |
| 4 | Respaldar también por CSV con `migracion/espejo_csv.sh` (2-4 h, se puede dejar corriendo) | Conteo de control 525 tablas = 525 `CREATE TABLE`, filas por tabla en los CSV |
| 5 | `manage.py cargar_mm_mn_roto --directorio salida_mm_mn_<fecha>` (dry-run) | Sin duplicados por `LEG-CERT-{id}`/`LEG-RN-{id}`; organizaciones resueltas en el árbol Lara |
| 6 | Ídem con `--ejecutar` | Conteo de registros nuevos; 0 pisados de CIE revisado |
| 7 | ¿Existe `TEMP.T_CERTNACI`? (comprobar con el diagnóstico) | «sí» → recompilar; «no» → pedir el DDL que falta o crearla según `cr_repli_nata.sql` |
| 8 | `migracion/recompilar_16_live.sh` (tras autorización reiterada) | «Inválidos: antes N → después 0» (o lista explícita de lo que queda + `ALL_ERRORS`) |
| 9 | Volver a mirar la sincronización (el cliente Windows / `.bat` Weekly) | el ZIP de la semana siguiente trae **5** archivos |
| 10 | `migracion/diagnostico_certnaci.sql` de nuevo (salida a `auditoria/`) | `EVENTOS_SINC` creciendo con `CERTIFICADO`/`CERTNACIMIENTO`, ZIP de 5, `T_CERTNACI` presente |
| 11 | Reevaluar §22.1-§22.4 con lo observado y actualizar esta sección | Conclusiones por escrito |

> Regla dorada del día: **ningún DDL** (ni `ALTER COMPILE` ni `CREATE T_CERTNACI`) hasta que el
> respaldo del paso 3 esté verificado. El script `respaldo_total.sh` ya no exporta `FULL=Y` ni en
> paralelo: una exp por esquema, la siguiente arranca cuando la anterior termina.

_Anotado el 30/09/2026 y actualizado esa misma tarde (scripts de respaldo y recompilación corregidos y
listos; el despliegue sigue pendiente de ejecución). Al ejecutar mañana, actualizar esta sección con el
resultado real y mover lo que quede a §22.5._

---

### 22.7 [HECHO 02/10/2026] El respaldo salió, se verificó con `imp`, y no hizo falta ninguna clave nueva

Ejecutado desde la oficina contra `192.168.5.200`. **Copia local en `/home/program/respaldos_sismai/`**
(permisos `600`, con `SHA256SUMS.txt`; los hashes coinciden 4/4 con los del servidor).

| Esquema | `.dmp` | Objetos que lee `imp SHOW=Y` |
| --- | --- | --- |
| SISMAI | 1.023 MB | 350 |
| HISTORICO | 91 MB | 10 |
| INBDLAR1 | 2,9 MB | 83 |
| TEMP | 16 KB | **0** |

- **TEMP sale vacío** porque `respaldo` no ve ese esquema. No es un `.dmp` roto: es que la cuenta no
  tiene permiso. Para respaldar TEMP hace falta otra cuenta.
- **La verificación que sí importa es `imp ... SHOW=Y FROMUSER=<esquema>`**: que el `.dmp` pese y el
  log diga «terminado» no prueba nada, porque un export cortado también pesa. `imp` recorre el archivo
  entero sin escribir nada y avisa si está truncado. Sin `FROMUSER` responde `IMP-00031`, y el `USERID`
  va en la línea de comandos porque si no, en segundo plano, cae a pedir el usuario por stdin.
- `respaldo_total.sh` quedó **fusionado** entre lo escrito desde casa (secuencial por esquema, parfile
  con `chmod 600` que se borra al final, `GRANTS`/`INDEXES`/`CONSTRAINTS=Y`) y lo corregido en la
  oficina. Tres cosas que solo se learn en la oficina: la cuenta por defecto es `respaldo` (`oracle`
  no tiene clave conocida), el destino va en `$HOME` (a `respaldo` no le escribe `/home/oracle`), y
  **la espera del export no puede ser por PID** porque `exp` hace fork: el proceso que devuelve
  `echo $!` muere mientras el hijo sigue escribiendo, y eso se midió como un `.dmp` de 351 MB de los
  1,02 GB finales. Ahora se espera la línea de fin del log, y el éxito se acepta en inglés y en
  español porque sale según `NLS_LANG` (buscar solo «terminado correctamente» marcó `[REVISAR]` un
  export que sí había terminado).
- **`espejo_csv.sh`** quedó adaptado a `respaldo` y validado (443 tablas, 443 `CREATE TABLE`), pero
  **sin extraer datos**: es la vía para PostgreSQL, no un respaldo.

**El quinto archivo tiene dueño:** el cliente Windows `192.168.5.133` tiene el cliente Oracle y
Centuria y ejecuta `SistemaTransferencia.exe`, que vive en el share del servidor
(`/home/salud/Aplicaciones/SISMAI/`). Desde el equipo de desarrollo responde SMB 139/445 y RPC 135,
pero **RDP 3389 está cerrado**: hace falta habilitarlo o ir a esa máquina.

### 22.8 ✅ El colapso de captura 2019-2021 es real en el ORIGEN: la pérdida es definitiva

`migracion/diagnostico_hueco_2019_2021.sh` **ejecutado contra `192.168.5.200`** el 02/10/2026, solo
lectura. Salida de referencia: `auditoria/diagnostico_hueco_2019_2021_20261002.txt`.

La pregunta era binaria — ¿los certificados están en el origen y no se extrajeron, o nunca se
capturaron? — y la respuesta es la mala: **el origen tampoco los tiene.**

| Serie | Normal | Colapso | Normal de nuevo |
| --- | --- | --- | --- |
| Defunciones | ~1.000/mes | **2019-06 → 2020-12** (11-95/mes) | 2021-01 (1.249) |
| Nacimientos | ~2.800/mes | **2019-09 → 2021-12** (5-398/mes) | **no se recuperó** |

**Contrastado mes a mes contra el espejo PostgreSQL: cuadran.** 48 meses de defunciones, diferencias
de 1 a 3 registros (2018-06: origen 1.165 vs espejo 1.162), que son los certificados con `FECHA_M`
nula que el filtro de mes no cuenta en uno de los dos lados. **El importador es fiel: no hay bug que
corregir y no hay nada que reextraer.**

**Corrige una afirmación anterior:** se decía que la natalidad «se recuperaba» en 2021-12. **No se
recuperó**: 2021-12 son **45 nacimientos**, el mes más bajo de toda la serie, después de 29 meses por
debajo de 400. Al publicar hay que decirlo así: entre 2019-09 y 2021-12 la serie de nacimientos no
es una caída, es un vacío de dos años y medio.

**Y el alcance del problema:** en el origen hay certificados hasta el **20/09/2026** y nacimientos
hasta el **11/09/2026**. O sea que el origen **sí sigue capturando**; lo que falta es que esos datos
lleguen a PostgreSQL, que es el problema de §22.4, no una pérdida histórica.

#### La conexión a `sqlplus` en ese servidor, y cuatro bugs del script

Solo funciona **Easy Connect con el servicio `bdlar1`**:
`sqlplus -s respaldo/respaldo@//localhost:1521/bdlar1`. Las otras tres fallan: usuario/clave a
secas → `ORA-12162`; `@lar1` → `ORA-12154` (no hay alias TNS); `@//host:1521/lar1` → `ORA-12514`,
porque **`lar1` es el SID y el servicio se llama `bdlar1`** (sale del `SID_LIST_LISTENER` del
`listener.ora`; el listener está sano y `lar1` está READY). Los scripts ya usan esa cadena.

Los otros tres fallos eran del script, no del servidor: `ORACLE_HOME` no viajaba al remoto (sin él
`sqlplus` da *Error 6 initializing SQL* / *sp1<lang>.msb not found*, que parece de permisos y es
otra cosa); el `ENV_ORACLE` iba sin `;` y bash intentaba exportar el comando entero; y **el resumen
salía vacío con los 48 meses ahí cargados**, porque el awk usaba `-F'|'` y sqlplus en `-S` alinea
los campos con tabulaciones (`MESES\t\t2018-01 \t\t    1172`). Con `[ \t]+` funciona. Ese
último es el peor tipo de fallo —aparenta que no hay datos cuando sí los hay— y era el único que
quedaba sin detectar, porque el script «terminaba bien».

### 22.9 [PENDIENTE] La información de 2019-2021 que el nivel central habría cargado en otro formato

> Anotado el 02/10/2026 a partir de lo que informa la oficina. **Matiza §22.8**, que dio la caída por
> pérdida definitiva *en el origen SISMAI*: puede existir una fuente paralela del nivel central.

Contexto aportado por el usuario:

- **El respaldo del 02/10/2026 está al día e incluye la semana epidemiológica 38 completa y parte de
  la 39.**
- En **2019-2020** (pandemia; el hueco llega hasta 2021) **el estado no usó el sistema**. El **nivel
  central cargó esa información** y, al parecer, **la pasó en otro formato** para que se pudiera
  ubicar la información del estado.

Qué queda por averiguar (no se ha hecho nada todavía):

1. **Ubicar** esos datos del nivel central (¿dónde están? ¿planillas, Excel, otro sistema, otro
   dump?).
2. **Revisar su estructura** y decidir si se pueden **incorporar a la base de datos sin perder**
   la información ya cargada (nacimientos/defunciones del periodo y las conciliaciones §18–§21).
3. Determinar el **alcance**: ¿son **solo certificados de defunción**, **solo nacimientos**, o
   ambos? ¿traen CIE, fechas y establecimiento suficientes para el ETL?
4. Si se incorporan, **reconciliar** contra el origen y documentar el alta como una fuente nueva
   (no como corrección del legacy).

Regla: **no cargar nada de esta fuente** hasta tener el archivo y su estructura a la vista; y si se
carga, hacerlo **aditivo** (nunca borrar ni pisar lo ya importado), igual que
`cargar_mm_mn_roto`.

## 23. [HECHO 02/10/2026] Los certificados oficiales: EV-14, EV-25 y el registro semanal MM/MN

El usuario aportó 8 capturas de los formularios reales (`capturas/certificado_nacimiento.jpg`,
`certificado_defuncion.jpg`, `pantalla1_mm.jpg` … `pantalla6_mm.jpg`; los números de certificado están
tachados por seguridad). La tarea era ajustar las pantallas ya diseñadas a los campos que pide cada
certificado. Este entorno **no puede ver imágenes**, así que se transcribieron con **RapidOCR**
(`rapidocr_onnxruntime` instalado en `.venv`; tesseract no está en el sistema). El OCR del certificado
impreso sale muy sucio ("Cerificado de Nacimiento EV25", "causaeas"), pero el de las **pantallas del
sistema** es bueno, y son las que mandan: los rótulos de sección se leen sin ambigüedad.

### 23.1 Lo que dice cada captura

| Captura | Documento | Contenido reconocido |
| --- | --- | --- |
| `certificado_nacimiento.jpg` | Certificado de Nacimiento EV-25 (impreso) | 1. Lugar de nacimiento, 2. Fecha de nacimiento, 3. Tipo de parto (único/gemelar), sección de la madre al nacer, dirección habitual de la madre, "distribución gratuita original madre o padre" |
| `certificado_defuncion.jpg` | Certificado de Defunción EV-14 (impreso, 82 campos) | Registro civil; identificación del fallecido (1-9); 30/39 edad; 31.a-c y 40.a-e gestas / última gesta / contribuyó a la muerte / puerperio / embarazada; 32/41 estado conyugal; 35/45 y 36/46 ocupación y residencia; 42 lee y escribe; 48.a-c cirugía (sí, fecha, descripción); 49 manera de morir; 50 fecha y hora del hecho violento; 53 descripción del hecho; 57 diagnóstico confirmado por; 60 correo; 61/65 médico y cargo; 68 destino del cadáver; 70-80 registro civil, acta, folio, gaceta, resolución; 81-82 firma y sello |
| `pantalla1_mm.jpg`, `pantalla2_mm.jpg` | **Certificado de Defunción — Modelo Nuevo** (el que se llena en pantalla) | Cabecera: consecutivo, año, partida, nº de certificado, NOMSIS, fecha de elaboración. Secciones **I** Identificación del fallecido (apellido, nombre, sexo, cédula, fecha y hora de muerte, edad, lugar de nacimiento, etnia, asistencia médica, sitio y lugar de ocurrencia, dirección, código comunidad, ubicación geográfica; nacionalidad V/E/P; datos de la partida de nacimiento: tomo, folio, libro, acta), **II** menores de un año / muerte fetal y datos de la madre, **III-IV** 1 año o más / muerte en mujeres en edad fértil, **V** muerte violenta, **VI** certificación médica (causa descrita por el médico, causa aplicando las reglas, causa primera parte, segunda parte — "separados por punto y coma" —, causa básica, antecedentes CIE-10, otros estados patológicos, "registrar cada causa en filas diferentes", diagnóstico confirmado por autopsia/examen del cadáver/examen de laboratorio/historia clínica/interrogatorio, médico firmante), **VII** responsable de la certificación |
| `pantalla3_mm.jpg` | **Certificado de Nacimiento — Modelo Nuevo** | Sección I datos del nacimiento (nombre, sexo **Masculino/Femenino/Hermafrodita**, fecha y hora, semana de gestación, peso, talla, nro de historia clínica), II datos de la madre, III datos del padre, IV registro civil, constancia de nacimiento, responsable de la certificación (nombre, cargo, director del establecimiento) |
| `pantalla4_mm.jpg` … `pantalla6_mm.jpg` | **Registro Semanal de la Mortalidad Materna y Mortalidad Infantil (Anexo del Telegrama)** | Código del establecimiento que reporta, año-periodo, semana, fecha, número, frecuencia semanal; nº de partos, nacidos vivos, nacidos muertos, abortos; **detalle de mortalidad materna** (tipo de identificación, cédula, edad, apellidos, nombres, fecha, residencia en Venezuela/fuera del país, ocurrencia); **mortalidad infantil y 1-4 años** (apellidos, nombres, fecha, sexo, edad, unidad, peso, control prenatal nº de consultas, edad gestacional, código de residencia, residencia, ocurrencia); informe/observaciones |

> Ojo con algo que cambia la lectura del tablero: el formulario nuevo **no** tiene un checkbox
> "defunción materna" suelto como el legacy. Lo que tiene es el bloque de la madre (secciones II/III-IV:
> nº de gestas, fecha de la última gesta, "contribuyó a la muerte", "en puerperio de", "estaba
> embarazada"). El campo `embarazo_o_puerperio` se conserva por compatibilidad y por el indicador de
> §21, pero **la forma de diligenciarlo en el EV-14 es esa**, no una marca suelta.

### 23.2 HECHO: el certificado de defunción ahora sigue el EV-14

Antes el formulario solo pedía 5 campos obligatorios y tres casillas; el EV-14 tiene 82. Se amplió
`registros.Defuncion` (migración `0005_defuncion_ev14`) con **50 campos nuevos**, todos opcionales, y el
frontend se reorganizó por secciones oficiales:

| Sección | Campos agregados |
| --- | --- |
| **I — Identificación** | `nacionalidad`, `segundo_apellido`, `segundo_nombre`, `edad_ignorada`, `lugar_nacimiento`, `nacimiento_exterior`, `estado_civil`, `profesion`, `ocupacion_lugar_trabajo`, `sabe_leer_escribir`, `residencia_habitual`, `asistencia_medica` |
| **II — Menor de un año / muerte fetal / madre** | `es_muerte_fetal`, `peso_nacer_gramos`, `edad_gestacional_semanas`, `tipo_embarazo`, `tipo_parto`, `asistencia_parto`, `madre_apellidos`, `madre_nombres`, `madre_cedula`, `madre_numero_gestas`, `madre_fecha_ultima_gesta`, `madre_embarazada`, `madre_puerperio` |
| **V — Muerte violenta** | `manera_de_morir`, `fecha_hecho_violento`, `hora_hecho_violento`, `descripcion_hecho_violento` |
| **VI — Certificación médica** | `causa_antecedentes`, `otros_estados_patologicos`, `diagnostico_examen_cadaver`, `diagnostico_examen_laboratorio`, `diagnostico_historia_clinica`, `diagnostico_interrogatorio_familiar`, `cirugia`, `fecha_ultima_cirugia`, `descripcion_cirugia`, `intervalo_enf_muerte`, `correo_contacto`, `matricula_mpps` |
| **VII — Registro civil** | `registro_civil_nombre`, `folio_defuncion`, `numero_acta_defuncion`, `fecha_registro`, `declarante_nombres`, `declarante_cedula`, `registrador_civil_nombres`, `registrador_civil_cedula`, `gaceta`, `resolucion` |

Decisiones que conviene no perder:

- **Nada se volvió obligatorio.** Los 50 campos son `null`/`blank`, así que los certificados ya cargados y
  los que produce el ETL siguen siendo válidos; el certificado mínimo sigue creándose (prueba
  `test_los_certificados_existentes_no_cambian`).
- **El territorio y el centro no se duplican en la sección I**: siguen viniendo del `SelectTerritorial` y
  del `CentroSelector` del bloque 1, que ya respetan el alcance del usuario.
- `embarazo_o_puerperio` **no se toca**. Es el campo que lee el tablero (§21) y el que usa
  `conciliar_mm`; el bloque de la madre es información de respaldo, no un reemplazo. La prueba
  `test_seccion_ii_muerte_fetal_y_datos_de_la_madre` fija que las dos cosas conviven.
- Las causas se manejan como **una línea por causa**, como dice el formulario nuevo ("registrar cada causa
  en filas diferentes"): `causa_directa` (línea a), `causa_antecedentes` (b, c, d) y
  `otros_estados_patologicos`, con la causa básica ya en el CIE de `SeccionCIE`.

Pruebas: `registros/tests.py::DefuncionEV14Tests` (7) — una por sección, una de que el mínimo no se rompió
y una de que una elección inválida se rechaza. **Suite completa 163 OK** (156 → 163), frontend 13 OK,
`npm run build` OK.

### 23.3 HECHO (02/10/2026): el certificado de nacimiento ahora sigue el EV-25

`CargaNacimientos.jsx` cubría tipo de parto, pesos, gemelar y padres, pero le faltaban los campos que
el certificado pide. Se amplió `registros.Nacimiento` (migración `0006_nacimiento_ev25`) con **24 campos
nuevos**, todos opcionales, y el frontend se reorganizó por secciones del EV-25:

| Sección | Campos agregados |
| --- | --- |
| **Cabecera** | `fecha_emision`, `numero_planilla`, `tipo_numero_certificado` (Completo / Histórico) |
| **I — Datos del nacimiento** | `nino_nombres`, `nino_apellidos`, `numero_historia_clinica` |
| **II — Madre** | `madre_nacionalidad`, `madre_pasaporte`, `madre_residencia`, `madre_residencia_pais`, `madre_residencia_direccion`, `madre_residencia_parroquia` (FK), `madre_residencia_comunidad` (FK) |
| **III — Padre** | `padre_nacionalidad`, `padre_pasaporte`, `padre_residencia`, `padre_residencia_pais`, `padre_residencia_direccion`, `padre_residencia_parroquia` (FK), `padre_residencia_comunidad` (FK) |
| **Responsable** | `certificador_nombres`, `certificador_cedula`, `certificador_matricula_mpps`, `director_establecimiento` |

Decisiones que conviene no perder:

- **Sexo `Hermafrodita`.** El modelo usaba `I = Indeterminado`; el certificado lo llama Hermafrodita. Se
  **cambió solo la etiqueta** (`I` → "Hermafrodita") y se añadió `N` = "Sin información" (el certificado
  tiene cuatro opciones: Sin Información / Masculino / Femenino / Hermafrodita, y M/F/I no alcanzaban).
  El **código `I` no se tocó**: hay 115 nacimientos con `I` de 438.477 (M 225.544, F 212.918) y el
  histórico no se reinterpreta. `Tablero.jsx` rotula `I` y `N` con el mismo texto.
- **Nada se volvió obligatorio**, igual que en §23.2: el certificado mínimo se sigue creando
  (`test_certificado_minimo_sigue_creandose`).
- **La residencia habitual se ancla al territorio del EV-25**, no al del establecimiento. Los cuatro FKs
  se validan en `Nacimiento.clean()` y en `NacimientoSerializer.validate()` (nivel PARROQUIA / COMUNIDAD);
  el serializer devuelve `madre_residencia_territorio` / `padre_residencia_territorio` con los cuatro
  niveles para que `SelectTerritorial` precargue la cascada (`destino` + `comunidadComoLista`).
- **El ETL no se toca.** `importar_legacy_registros` leía `NAC_RNACIDO."NOMBRES"` y
  `NAC_MADRE."HRESIDENCIA"` pero no había dónde guardarlos; los sigue ignorando.
- **Backfill (`manage.py completar_nacimiento_legacy`):** recupera lo que el ETL descartó. Rellena
  `nino_nombres` desde `NAC_RNACIDO."NOMBRES"` (438.518 recuperables) y `madre_residencia_parroquia`
  desde `NAC_MADRE."HRESIDENCIA"` → `ORG_GEOGRAFICA` → parroquia del árbol (416.706 recuperables; el
  nombre legacy no siempre coincide con el INE, por eso no son todas). Es un `UPDATE` por bloque,
  **solo campos vacíos**, idempotente y dry-run por defecto (`--ejecutar` aplica, `--solo nombres|residencia`
  limita). El nombre del padre ya lo importaba el ETL, así que no se toca.

Pruebas: `registros/tests.py::NacimientoEV25Tests` (6: mínimo intacto, cabecera/RN, sexo I/N, residencia
madre por parroquia, padre por comunidad, nivel inválido → 400) y
`registros/tests_completar_nacimiento.py` (6). **Suite backend 193 OK** (181 → 193), frontend 13 OK,
`npm run build` OK.

### 23.4 HECHO (02/10/2026): el Registro Semanal de Mortalidad Materna e Infantil, como reporte generado

El anexo del telegrama **no** es el consolidado semanal de ENO (`vigilancia.ConsolidadoSemanal`,
EPI-12/EPI-14) ni el EPI-15 de morbilidad (`Epi15.jsx`). Es otro formulario, con otro grano: **un registro
por establecimiento y por semana**, con conteos agregados y detalle caso por caso.

**No se construyó como formulario de captura sino como reporte generado** desde
`registros.Nacimiento`/`registros.Defuncion` y el registro de investigación de MM, que es lo que el usuario
necesita y además concilia. Se verificó antes qué casillas salen de la BD local y cuáles no:

| Casilla del anexo | Origen en SISV | ¿Se genera? |
| --- | --- | --- |
| Nacidos vivos | `Nacimiento.nacido_vivo=True` del centro y la semana | Sí |
| Nacidos muertos | `Nacimiento.nacido_vivo=False` | Sí |
| No. de partos | — | **No**: el certificado es por recién nacido, no por parto (un gemelar son dos filas); no se inventa |
| Abortos | — | **No**: SISV no captura abortos; no se inventa |
| Mortalidad materna | `sismai."RENGLON_CASOSMM"` → `CASOS_MMI` (respaldo: `Defuncion.embarazo_o_puerperio`) | Sí |
| Mortalidad infantil y 1-4 años | `Defuncion` con `fecha_nacimiento` (0-27 d = neonatal, <1 año = infantil, 1-4 años) | Sí |

Del detalle del anexo se genera el materno completo (identificación, cédula, edad, fecha, residencia y
ocurrencia). Del infantil se generan nombres, sexo, edad, fecha, residencia y ocurrencia; **peso, control
prenatal y edad gestacional no se generan** porque no están en `Defuncion` (quedan para cuando se capturen).

Implementación:

- `vigilancia/services.py::rango_semana(anio, semana)` → `(domingo, sábado)` de la semana epidemiológica.
- `registros/services.py::muerte_materna_detalle(desde, hasta, organizaciones)` → un caso de MM por
  persona (`DISTINCT ON c."ID"`, la misma dedupe que el conteo), con residencia por `ORG_GEOGRAFICA`.
- Endpoint `GET /api/registros/reportes/semanal-mmi/?anio=&semana=[&formato=csv]`: por centro dentro del
  alcance (`_organizaciones_del_alcance`), nacidos vivos/muertos, MM (`mm_fuente` =
  `REGISTRO_INVESTIGACION`/`CERTIFICADO`, más `mm_certificadas` para conciliar), MN, infantil <1 año,
  1-4 años y los dos detalles. Con `formato=csv` descarga un CSV con BOM de tres secciones
  (RESUMEN / MATERNA / INFANTIL). Con alcance de centro, su centro aparece en ceros aunque no tenga
  actividad.
- Frontend: sección **«Registro semanal de mortalidad materna e infantil»** en `/reportes`
  (`Reportes.jsx`) con año/semana, tabla por centro, detalles plegables y exportación CSV.
- Pruebas: `registros/tests.py::ReporteSemanalMMITests` (7) — resumen por centro, caída al certificado
  sin legacy, MM del registro de investigación, alcance de centro, centro sin datos, CSV y validación.

**Nota de alcance:** siguen existiendo fuentes distintas de MM/MN (§20, §21 y el consolidado ENO). Este
anexo no agrega un número nuevo que compita: es una vista semanal por establecimiento de las mismas
fuentes del tablero, y la marca `*` en el frontend avisa cuándo el MM de ese centro salió del certificado
porque el registro de investigación no estaba disponible.

---

## 24. [HECHO 02/10/2026] Despacho de certificados y registradores civiles: el legacy no los tiene, hay que construirlos

### 24.1 Pedido del usuario (1)

Módulo para controlar el **despacho de certificados de nacimiento y defunción**:

- Registrar **fecha de entrega**, **centro médico**, **serie desde–hasta** de los certificados entregados y
  la **cantidad** por centro.
- Registrar el **responsable que recibe**.
- **Reporte 1**: certificados de nacimiento y de defunción **por separado**, con nº de certificado,
  nombre, apellido y fecha, **por centro médico**.
- **Reporte 2**: los **entregados que aún no han sido retornados ni justificados**, con estatus:
  - **Sin asignar** (entregado, todavía sin usar),
  - **Dañado** (con acta de justificación: número y fecha),
  - **En tránsito** (nombre, apellido y fecha en que salió del centro).
- **Cruzar** contra la BD (Nacimientos/Defunciones ya cargados) para saber qué certificados están en uso.
- Revisar el **legacy** para reconstruir serie/cantidad por centro y mes/año si fuera posible.
- Mantener todo actualizado para que los reportes no mientan.

### 24.2 Pedido del usuario (2): registradores civiles [HECHO 02/10/2026]

> **Pedido original (01/10/2026):** llevar control de los **registradores civiles**. Por cada registro
> civil / centro hay que saber **quién está a cargo y desde qué fecha**, y al cambiar **dar de baja al
> anterior con fecha** e **ingresar el nuevo responsable con su fecha de toma de posesión**. El objetivo
> es responder «¿quién firmaba en esta fecha?» de forma **retroactiva**. Debe modelarse como **historial
> con vigencias** (desde/hasta), no como un campo suelto en la organización; un `Foreign` al usuario no
> alcanza porque el registrador civil **no tiene por qué ser usuario del sistema**.

**Implementado** como app propia `backend/registradores/` (no se metió en `despacho` porque el dominio
—quién firma— es distinto al de los talonarios —qué serie se entregó—, aunque se comparte el permiso):

| Modelo | Rol |
| --- | --- |
| `RegistroCivil` | La oficina (`nombre` único), `organizacion` opcional (centro), `estado`/`municipio`/`parroquia`, `activo`. |
| `RegistradorCivil` | La persona: `nacionalidad` (V/E/P/I/O), `cedula`, `nombres`, `apellidos`, contacto, `activo`. Único por `(nacionalidad, cedula)`. **No** es `auth.User`. |
| `DesignacionRegistrador` | La vigencia: FK a registro civil y registrador, `cargo` (TITULAR/SUPLENTE/ENCARGADO), `desde`, `hasta` (**nulo = vigente**), `fecha_toma_posesion`, `acta_nombramiento`. |

- **«¿Quién firmaba?» retroactivo:** `registradores/services.py::vigentes_en(registro_civil, fecha)` =
  `desde <= fecha` y (`hasta` nulo o `>= fecha`). Endpoint `GET /api/registradores/quien-firmaba/?registro_civil=&fecha=`.
- **Se permite el solape** (titular y suplente a la vez) a propósito, por eso no hay restricción de
  no-solape; la consulta devuelve **todos** los vigentes ordenados por cargo.
- **Endpoints** `/api/registradores/`: `registros-civiles/` y `/<id>/`, `registradores/` y `/<id>/`,
  `designaciones/` y `/<id>/` (filtros `registro_civil`, `registrador`, `cargo`, `vigente=1`),
  `quien-firmaba/`. Escribe quien `puede_despachar` (Jefe de Unidad / Director / superusuario); leer,
  cualquier autenticado. El alcance replica el del despacho (CENTRO ve su centro, REGIONAL su estado).
- **Borrado protegido:** no se elimina un registro civil ni un registrador con designaciones
  (`on_delete=PROTECT` → 400 con mensaje claro); se desactiva o se cierra la vigencia.
- **Frontend** `/registradores` (`Registradores.jsx`): tres formularios + tablas (registros civiles,
  registradores, historial de designaciones) y un bloque «¿Quién firmaba en una fecha?».
- **Pruebas** `registradores/tests.py` (22).

**Catálogo sembrado desde el legacy (02/10/2026):** `sismai.CERTIFICADO` guarda
`NOMREGISTRADOR`/`CIREGISTRADOR`/`NACREGISTRADOR` por certificado de defunción (**167.447 de 173.533**,
9.603 nombres distintos con muchas variantes de la misma cédula). Comando
`manage.py sembrar_registradores_legacy [--ejecutar] [--limite N]` (dry-run por defecto, idempotente):
agrupa por `(nacionalidad, cédula)`, elige el nombre más frecuente como canónico (a igualdad, el más
largo) y divide `nombres`/`apellidos` asumiendo que el legacy escribe **apellidos primero**.
- **Ejecutado: 3.857 registradores** (3.845 V + 12 E) a partir de 167.447 filas y 12.713 variantes.
  Se descartaron **11.184 certificados con nombre pero sin cédula** (no se pueden deduplicar); 0 con
  nombre inválido.
- **No crea `RegistroCivil` ni `DesignacionRegistrador`**: el legacy no modela la oficina ni la vigencia.
  Esas se cargan a mano.
- La división de nombres es **heurística** (el orden del legacy varía: `"ESPINOZA NELIDA"` domina a
  `"NELIDA ESPINOZA"`); el catálogo se corrige desde `/registradores`. `apellidos` quedó opcional
  (migración `0002`) para los pocos nombres de un solo token.


### 24.3 Hallazgo: el legacy no guarda el despacho (verificado en la BD local)

El usuario sospechaba que la entrega se podía reconstruir del legacy. **No se puede**, y quedó verificado
consultando el PostgreSQL local (`sis_salud_db`, la copia del Oracle 10g):

| Tabla legacy | Qué habría guardado | Estado real |
| --- | --- | --- |
| `sismai.NUMERO_BD` | rango de números por establecimiento (`NATA_IDS`, `MORT_IDS`, `IDESTABLE`) | **0 filas** |
| `sismai.HISTORICO_IDS` | consecutivo y nº de planilla (`CONSECUTIVO`, `NROPLANILLA_NUMEROMSDS`, `ANNO`, `BD`) | **0 filas** |
| `sismai.CERTIFICADO` | el certificado cargado, con `HESTABLECIMIENTO`, `ANNOCERTIFICADO`, `NUMEROMSDS` | 173.533 filas (datos, no entrega) |

Lo que sí tiene `sismai.CERTIFICADO`:

- `HESTABLECIMIENTO` = el centro, pero **no es fiable como centro real**: 173.500 de 173.533 certificados
  están bajo `67754` (el nivel central/regional). El centro verdadero se recupera por
  `DOCUMENTO.HORIGEN` (es el mismo problema del establecimiento perdido, §17 y §19).
- `ANNOCERTIFICADO` = año; `FECHA_M`/`FECHAELABORACION` = fechas. Sirven para agrupar **por mes/año**.
- `NUMEROMSDS` = número **casi único** (173.471 distintos de 173.533) pero es un **contador global**: en el
  centro 67754 va de 0 a **9.913.094.228**. **No se reinicia por centro ni por año**, así que **no define
  una serie por establecimiento**.
- `CERTIFICADO` y `NUMEROPARTIDA` = número de libro, pero **inservibles**: `CERTIFICADO` viene vacío en
  18.785 filas y en `0` en 1.124, con duplicados por todas partes.
- `CONSECUTIVO` (`000013-1031089`) = prefijo del **modelo de formulario** (161.728 comparten `000013`) +
  consecutivo; el prefijo **no es el centro**.

**Conclusión:** la entrega de talonarios (qué serie salió de la oficina, a qué centro, en qué fecha y a
quién) **nunca vivió en el SISMAI**; se llevó en papel. El sistema nuevo tiene que **capturarla desde
cero**. Lo único reconstruible del legacy es el **consumo** (certificados efectivamente llenados) por
centro y mes/año, que es justamente uno de los reportes pedidos y que en el sistema nuevo sale directo de
`registros.Nacimiento`/`registros.Defuncion`.

### 24.4 Lógica de cruce propuesta

- **Talonario entregado** (lo que se registra a mano): serie desde–hasta + cantidad + centro + fecha +
  responsable.
- **Consumo** (automático): contar los `Nacimiento`/`Defuncion` cuyo nº de certificado esté dentro de una
  serie entregada a ese centro. El actual `registro_numero` es texto libre (`DEF-YYYY-XXXXXX`); para el
  cruce hace falta que la serie y el `registro_numero` hablen el mismo idioma (número puro, o serie con
  prefijo). **Es la decisión de diseño más importante y hay que tomarla con el usuario.**
- **No retornado / sin justificar** = entregado − consumido − dañado − devuelto.

### 24.5 Implementación (01/10/2026): app `despacho`

Se construyó la app `backend/despacho/` (`Talonario`, `NovedadCertificado`; migración `0001_initial`).

- **Rol nuevo `JEFE_UNIDAD` («Jefe de Unidad»)** en `seguridad.Perfil` (migración `seguridad.0004_alter_perfil_rol`)
  y permiso `puede_despachar` en `seguridad/services.py::permisos_de` = superusuario o rol `JEFE_UNIDAD`/`DIRECTOR`.
  Crear/editar/eliminar talonarios y novedades exige `puede_despachar`; leer y reportes, cualquier autenticado.
- **`Talonario`**: tipo (NACIMIENTO/DEFUNCION), centro (FK `Organizacion`), `fecha_entrega`, `serie_desde`/`serie_hasta`,
  `cantidad` calculada en `save()`, `responsable_recibe`/`responsable_entrega`, `observaciones`, `creado_por`/`creado_en`.
  Restricciones: serie única por `(centro, tipo, desde, hasta)` y `serie_hasta >= serie_desde`.
- **`NovedadCertificado`** (excepción, no una fila por certificado): `DANADO` / `EN_TRANSITO` / `DEVUELTO`, con
  justificación (nº y fecha de acta) y datos del tránsito (nombres, apellidos, fecha de salida). Único por
  `(talonario, numero)`.
- **Cruce (`despacho/services.py`)**: se extrae el **sufijo numérico** del `registro_numero` (decisión del usuario:
  «el Nº incluye el consecutivo de la serie») y se compara contra la serie del talonario, dentro del subárbol del
  centro (`organizaciones_descendientes`). Un `registro_numero` sin dígitos finales se **ignora** (no cuenta ni como
  usado ni como faltante). Faltante = rango − usados − dañados − devueltos − en tránsito.
- **Endpoints** (`/api/despacho/`): `talonarios/` (GET/POST), `talonarios/<id>/` (GET/PATCH/DELETE),
  `talonarios/<id>/certificados/` (detalle certificado por certificado + resumen), `novedades/` (GET/POST),
  `novedades/<id>/` (PATCH/DELETE), `reportes/certificados/` (reporte 1, por centro y tipo; CSV) y
  `reportes/pendientes/` (reporte 2, no retornados/justificados; CSV). Todos respetan `alcance_registros`.
- **Nota (resuelta el 02/10/2026 con el EV-25, §23.3):** en nacimientos el reporte 1 usa el **nombre del
  recién nacido** (`nino_nombres`/`nino_apellidos`) y lo rotula `persona: "Recién nacido"`; si el registro
  no lo trae (los importados antes del EV-25 y aún sin backfill) cae al de la madre y lo rotula
  `persona: "Madre"`. El CSV del reporte 1 ahora lleva una columna **Persona** para que no se confundan.
- **Frontend** `/despacho` (`Despacho.jsx`): formulario de talonario (con `CentroSelector`), tabla con resumen
  (usados / sin asignar / dañados / en tránsito / devueltos), panel de detalle certificado por certificado con
  alta/baja de novedades, y los dos reportes con exportación CSV.
- **Pruebas**: `despacho/tests.py` (18) — permisos, cantidad calculada, serie inválida/duplicada, cruce
  (usado/faltante/otro centro/descendiente/sin dígitos), novedades (fuera de serie/duplicada), alcance
  (centro/regional) y reportes (JSON y CSV con BOM). Suite backend: **181 OK** (eran 163); frontend 13 OK;
  `npm run build` OK.

**Pendiente de este módulo:** el §24.1 pedía «revisar el legacy para reconstruir serie/cantidad por
centro y mes/año»; ya se verificó que **no es posible** (§24.3, tablas vacías), así que ese punto queda
cerrado como no viable. Los registradores civiles (§24.2) ya están **con su catálogo sembrado desde el
legacy** (3.857 personas), igual que el registro semanal MM/MN (§23.4) y el certificado de nacimiento
EV-25 (§23.3). Queda como paso manual cargar registros civiles y designaciones (el legacy no los tiene).

## 25. [HECHO 02/10/2026] Refresco offline del espejo legacy en PostgreSQL desde los `.dmp`

> El Oracle de la oficina (`192.168.5.200`) **no responde desde la red de casa** (§22 notas), así que el
> espejo `sismai`/`inbdlar1`/`historico` de `sis_salud_db` se actualizó **desde los respaldos** del
> 02/10/2026, sin tocar producción. El pipeline original (`/tmp/opencode/legacy`) se había perdido; se
> **reconstruyó** y quedó versionado en `migracion/`.

**Ruta offline (la que se usó):** `.dmp` (`exp` clásico) → Oracle local en Docker → CSV → PostgreSQL.

| Paso | Herramienta |
| --- | --- |
| Oracle local | contenedor `sis_oracle_legacy` (`gvenzl/oracle-xe:11.2.0.2`, host 1529→1521) |
| Cargar `.dmp` | `imp` clásico con `parfile` (`INDEXES=N CONSTRAINTS=N GRANTS=N IGNORE=Y`) |
| Exportar a CSV | `SYSTEM.SISV_EXPORTAR_CSV` (PL/SQL, `;`, comillas dobles, NULL vacío) |
| Cargar en PG | `COPY ... (FORMAT csv, DELIMITER ';', HEADER true, QUOTE '\"', NULL '')` |

**Scripts versionados (reconstruidos):**
- `migracion/actualizar_espejo_pg.sh` — orquesta los 8 pasos (contenedor → `imp` → export → `COPY` →
  verificación de conteos Oracle vs PG). Invocar con `newgrp docker -c "bash migracion/actualizar_espejo_pg.sh"`.
- `migracion/espejo_generar.py` — lee la lista de tablas del espejo PG y genera los `imp_*.par`, el
  driver de exportación y los `counts_*.sql`.
- `migracion/sisv_exportar_csv.sql` — procedimiento PL/SQL genérico de exportación.
- `migracion/cargar_espejo_pg.py` — `TRUNCATE` + `COPY` por tabla (idempotente, dry-run por defecto).
- `migracion/espejo_crear_usuarios.sql` — tablespaces `DATOS`/`DATOS2`/`INDICE` y usuarios del espejo.
- (La vía directa contra el Oracle vivo sigue siendo `migracion/espejo_csv.sh`, §22.7; solo sirve con
  la oficina accesible.)

**Resultado (verificado tabla por tabla):** 348 tablas = **sismai 256 + inbdlar1 83 + historico 9**,
conteo Oracle vs PostgreSQL **0 diferencias** (348/348). Fechas frescas:
`sismai."CERTIFICADO"` 173.976 (máx `FECHA_M` **2026-09-20**), `sismai."NAC_RNACIDO"` 439.332
(máx **2026-09-11**), `sismai."CERTNACIMIENTO"` 439.596 (máx **2026-10-02 12:25**),
`sismai."RENGLONTELE"` 2.674.452.

**El esquema `legacy` (82 tablas `T_*`) NO se refrescó:** no viene en `respaldos_sismai` (se originó en
`routlar1.dmp`, que no está en este respaldo). Queda intacto.

**Trampas aprendidas:**
- `/tmp` es **tmpfs de 3,8 GB**: los ~760 MB de CSV más copias la llenan. El staging por defecto es
  `/var/tmp/espejo` (disco raíz).
- `python-oracledb` en modo thin **no conecta a 11.2** (`DPY-3010`); la exportación se hace con PL/SQL.
- El procedimiento con buffer **`CLOB` era ~50× más lento** (concatena por celda); con `VARCHAR2(32767)`
  las 348 tablas salen en ~3,5 min. Solo hay 2 columnas `LONG` (`ACTIVIDAD.DESCRIPCION`,
  `ESTABLECIMIENTO.DESCRIPCION`), que caben en el buffer.
- La sesión fuerza `NLS_NUMERIC_CHARACTERS='.,'`; el `LONG` puede traer saltos de línea (van entre
  comillas y `COPY` los maneja).

**Siguiente paso (HECHO 02/10/2026):** correr los ETL de la app (`importar_legacy_registros`,
`importar_legacy_vigilancia`) para llevar las semanas nuevas del espejo a `registros`/`vigilancia`.
Ejecutado y verificado: ver §26.

## 26. [HECHO 02/10/2026] ETL de la app sobre el espejo refrescado, calidad de datos y reporte MM/MN

> Cerrado el paso que §25 dejaba abierto. El espejo ya estaba al día; aquí se llevan las semanas nuevas
> a `registros`/`vigilancia` y se deja constancia del control de calidad y del reporte semanal.

**Lo que se corrió (contra `sis_salud_db`, que contiene espejo y tablas de la app):**

- `manage.py importar_legacy_registros` (incremental por `legacy_id`, **sin** `--borrar`):
  nacimientos **438.577 → 439.282** (+705, máx `2026-09-11`), defunciones **173.533 → 173.976**
  (+443, máx `2026-09-20`). No duplica porque salta los `legacy_id` ya presentes.
- `manage.py importar_legacy_vigilancia --borrar`: recarga limpia de los lotes legacy.
  Fichas **LEGACY-MMI 10.756** + **LEGACY-VIOLENTA 12.409 = 23.165** (+2 MMI); `ConsolidadoSemanal`
  **73.515**, `FilaConsolidado` **508.121**, `FilaEpi15` **556.327**.
  `--borrar` solo elimina consolidados `legacy_tabla=RENGLONTELE/EPI-15` y fichas de lote MMI/VIOLENTA:
  no toca consolidados hechos por usuarios.
- `manage.py asignar_organizacion_legacy --ejecutar`: **+686** nacimientos, **+443** defunciones,
  **+14.462** fichas. Quedan sin organización 19 nacimientos (domicilio), 70 defunciones y las fichas
  violentas sin establecimiento (fuera del árbol Lara), igual que antes. La recarga de vigilancia
  resetea `organizacion` de **todas** las fichas, por eso hay que reasignar después.

**Por qué `--borrar` en vigilancia:** los cargadores de fichas MMI/violenta no deduplican y
`codigo_notificacion`/`registro_numero` son `UNIQUE`; sin borrar, la recarga falla por colisión. (Los
consolidados EPI-12/EPI-15 sí son incrementales, pero `--borrar` actúa sobre los cuatro a la vez.)

**Calidad de datos (verificada por SQL):**
- Sin caracteres de control, U+FFFD ni mojibake en `sismai.CERTIFICADO/NAC_RNACIDO/CERTNACIMIENTO/
  CASOS_MMI/ESTABLECIMIENTO` ni en `registros_nacimiento/defuncion/fichavigilancia`.
- Sin duplicados: todos los `ID` del espejo y `registro_numero`/`codigo_notificacion`/`legacy_id` de
  la app son únicos (`CERTIFICADO.CERTIFICADO` con 5.907 valores en 155.183 filas es un código, no el nº).

**Reporte Año/Semana** (semana epidemiológica domingo-sábado) en
`auditoria/REPORTE_ESPEJO_2026.md` (directorio ignorado por git):
- 2026: **MM_reg 18**, MM_cert 16, **MN_reg 233** (año epi) / 236 (calendario), MN_cert 232,
  nacimientos **9.988** por `FECHANACIMIENTO` frente a 12.914 por `FECHACERTIFICADO`, cert. defunción
  6.689, cert. nacimiento 12.914.
- Contraste con la oficina: **MM 18 coincide**; **MN ~258 no se reproduce** (brecha ~22-25 por el corte
  de captura del ~02/08, visible en la caída de `NAC_RNACIDO` y `MN_reg` desde la semana 31). El
  certificado de nacimiento sigue contando (certificados tardíos) mientras `NAC_RNACIDO` se atrasa.

**Test corregido:** `legacy.tests.test_usuarios_y_estatus_de_yasminmorb` fijaba `ESTATUS=2`, pero el
respaldo del 02/10 trae **1** (el usuario cambió de estado en producción). Ahora valida que exista y que
`ESTATUS ∈ {1,2}`, sin fijar el dato vivo. Suite: **227 OK**.

**Backfills (HECHO 02/10/2026):** `completar_nacimiento_legacy --ejecutar` rellenó **705** nombres de
recién nacido y **653** residencias maternas (parroquia) de los nacimientos nuevos; quedaron 439.223
nacimientos con `nino_nombres` y 417.358 con parroquia de residencia. `corregir_mm_legacy --ejecutar`:
1 marcada + 1 desmarcada; **MM totales del lote 191** (16 en 2026), consistente con la definición 1+2
del certificado.

## 27. [HECHO 05/10/2026] Recuperación del hueco MM/MN de agosto–septiembre de 2026

> Cierra el paso 2 y 3 de "Recuperación del hueco MM/MN" (§22). La captura se cortó el
> 02/08/2026: el centro siguió generando los sobres semanales, así que los datos **sí estaban
> en el Oracle** y faltaban en PostgreSQL. Recuperados, atribuidos a su centro y conciliados.

### 27.1 Preflight: se siguió adelante con 4 desviaciones

`migracion/preflight_ventana.sh` (solo lectura) reportó 4 fallos, todos evaluados:

| Preflight | Veredicto |
| --- | --- |
| No hay dump del 05/10 | No bloquea: la extracción es `SELECT`+`SPOOL` y **no había `exp`/`expdp` corriendo** (leer la base a medio respaldar es el error clásico, y no lo había). El respaldo del 02/10 está verificado (§27.5). |
| El ZIP trae 4 archivos, no 5 | No aplica: se extrajo del Oracle, no del sobre. El quinto archivo (`repllar1*.log`) es el orquestador del cliente Windows (§22.7). |
| `TEMP.T_CERTNACI` no existe | No bloquea el MM/MN (afecta a la vista `NATALIDAD`, no a los certificados). Sí bloquea el item 2 (§27.6). |
| No es martes | Irrelevante: el día de la semana solo importa para predecir el próximo sobre, no para leer datos ya presentes. |

Se conservó `DESDE=01/08/2026` (inicio del hueco) en vez del recomendado 20/08, para que la
carga sea reproducible y comparable con la caída de agosto.

### 27.2 Extracción (solo lectura) — `salida_mm_mn_20261005_1528`

`migracion/extraer_mm_mn_roto.sh` + `.sql` (ambos corregidos: credenciales desde
`legancy_conf/credenciales.env`, `ORACLE_HOME=/opt/oracle`, servicio `//localhost:1521/bdlar1`,
`DEFINE` con comillas preservadas, `HORAMUERTE` como `VARCHAR2` —trae `HHMMSS` y no es fecha—,
fuera `ESTABLECIMIENTO.DESCRIPCION` que es `LONG` y rompía el CSV, `WHENEVER SQLERROR EXIT`
para no dejar archivos truncados, y manifiesto con descartadas).

**12 CSV, 0 filas descartadas:** `muerte` 616, `nacimiento` 500, `nac_madre` 500,
`nac_rnacido` 500, `casosmmi` 67, `renglon_casosmi` 66, `renglon_casosmm` 1,
`establecimiento` 21.148, `cie10_legacy` 16.664, `org_geografica` 58.960,
`nacimiento_tardio` 1.811, `causa_m` **0**.

- `causa_m` sale vacía y **no es un fallo del script**: el último certificado con causa enlazada
  es de **2023-03-19** (§20.1). De las 616 defunciones, solo 3 traen `HCAUSABASICA`.
- Fechas máximas en el origen: defunción **2026-09-20**, nacimiento **2026-09-16**, MMI **2026-10-03**.

### 27.3 Carga en PostgreSQL — 594 defunciones y 477 nacimientos

`manage.py cargar_mm_mn_roto --directorio salida_mm_mn_20261005_1528 --ejecutar`

| | Nuevos | Actualizados | Pendientes de codificación |
| --- | --- | --- | --- |
| Defunciones | **594** | 22 | **594** |
| Nacimientos | **477** | 23 | — |

Del lote: **1 muerte materna** y **37 neonatales**. Segunda corrida en dry-run: 616 defunciones y
500 nacimientos `sin_cambio` → **idempotente**.

**Las 594 quedan con `codificacion_pendiente=True`** (cambio deliberado del cargador): en el
certificado sin causa no hay nada que codificar, y marcarlas como «ya revisadas» las sacaría de la
bandeja sin que nadie las viera. Con eso la cola de codificación quedó en **49.755**.

Semana a semana, el hueco se cerró (defunciones / nacimientos, semana domingo–sábado):

| Semana | 27/07 | 03/08 | 10/08 | 17/08 | 24/08 | 31/08 | 07/09 | 14/09 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Antes | 9 | 8 | 2 | 3 | 0 | 0 | 0 | 0 |
| Ahora | 162 | 147 | 148 | 151 | 98 | 26 | 6 | 5 |

### 27.4 La atribución por centro se había perdido (y por qué)

Al verificar los efectos secundarios apareció que **86.258 defunciones y 438.573 nacimientos tenían
`establecimiento` pero `organizacion = NULL`**: eran invisibles para cualquier usuario con alcance
de centro, y la columna «Centro» salía vacía.

**Causa raíz:** §25/§26 refrescaron el espejo y re-ejecutaron `importar_legacy_registros`. Ese
comando **nunca asigna `organizacion`** (solo carga datos), así que cualquier recarga con `--borrar`
borra la atribución y hay que reasignar después. §26 lo documentó para las fichas de vigilancia,
no para nacimientos/defunciones.

```bash
./.venv/bin/python backend/manage.py asignar_organizacion_legacy            # 438.554 + 86.203 por asignar
./.venv/bin/python backend/manage.py asignar_organizacion_legacy --ejecutar # 438.554 nac + 86.203 def
```

**Orgs creadas=0, reutilizadas=596**: los 991 centros `LEGCSV-*` que creó el cargador cuelgan del
regional Lara, así que la atribución los reutilizó por nombre normalizado y **no duplicó** centros.

**Pendiente de negocio:** los centros del legacy (`LEGCSV-*`) son organizaciones **distintas** de
las 6 demo (`LARA-HCB` = Hospital Central de Barquisimeto). Un usuario `CENTRO` con perfil sobre
una demo ve 2 registros, no el histórico; con perfil sobre un centro real sí lo ve. Fusionar
«HOSP. CENTRAL UNIV. DR. ANTONIO MARIA PINEDA» con «Hospital Central de Barquisimeto» es una
decisión de negocio (alias), no un ETL.

### 27.5 Conciliación (paso 3)

`manage.py conciliar_neonatal --anio 2026` (dry-run, no escribe):

```
Filas: 86 · legacy 231 · SISV 236 · diferencia -5   (-2,1 %)
  CUADRA=53 · DIFERENCIA=22 · SOLO_CRUDO=5 · SOLO_SISV=6
```

El registro de investigación (legacy) y `registros.Defuncion` coinciden en el **97,9 %** tras la
recuperación: los 29 neonatales de las semanas 31–35 ya salen de los sobres.

`manage.py conciliar_mm --anio 2026`: **registro 18 / certificados 7**. El registro coincide con
lo que reporta la oficina (18) y confirma §21: el certificado marca el embarazo en el 38,9 %.

**Restore point verificado** (condición previa a cualquier escritura en Oracle):
`/home/respaldo/respaldo_20261002_1408` — 4 `.dmp` (SISMAI 1.072.316.416 B), los 4 logs con
«terminated successfully», `imp SHOW=Y` lee 350 objetos de SISMAI, SHA-256 en
`/home/program/respaldos_sismai/SHA256SUMS.txt`.

### 27.6 Item 2 — recompilar los 16 objetos: **[HECHO 09/10/2026]**

> **Resuelto el 09/10/2026.** El usuario facilitó la clave del usuario de SO `oracle`
> (grupo `dba`), que entra por SSH y `sqlplus / as sysdba`. Se ejecutó el SQL corregido y
> **los 16 objetos quedaron `VALID`; SISMAI tiene 0 inválidos** (detalle y bug del script en
> §27.11). Se conserva el texto original de abajo como contexto.

Los 16 `INVALID` de SISMAI siguen ahí. Para recompilarlos hace falta `/ as sysdba`, y:

- `oracle` (uid 1002, grupo `dba`) no acepta nuestra llave: `Permission denied (publickey,keyboard-interactive)`,
  `/home/oracle/.ssh` no es accesible y no hay clave conocida.
- `respaldo` **sí entra**, pero sus únicos privilegios son `ALTER ANY INDEX`, `RESTRICTED SESSION`
  y `UNLIMITED TABLESPACE`: no puede recompilar objetos ajenos. Tampoco ve `ALL_ERRORS` de SISMAI,
  así que el diagnóstico por objeto solo lo puede hacer el DBA.

**Dejado listo** (`migracion/recompilar_16_live.sh` reescrito: no hardcodea claves, valida el
respaldo por logs antes de escribir, y por defecto **no escribe**):

```bash
./migracion/recompilar_16_live.sh --preparar     # verifica respaldo + sube el SQL  (ya corrido)
```

El SQL ya está en el servidor (`/home/respaldo/recompilar_16_objetos.sql`). En la **consola**,
como `oracle`:

```bash
su - oracle
export ORACLE_HOME=/opt/oracle ORACLE_SID=lar1 NLS_LANG=SPANISH_SPAIN.AL32UTF8
cp /home/respaldo/recompilar_16_objetos.sql /tmp/
/opt/oracle/bin/sqlplus -s / as sysdba @/tmp/recompilar_16_objetos.sql | tee ~/recompilar_16_$(date +%Y%m%d_%H%M).log
```

El veredicto es la sección `[5]` del log (**0 inválidos** = éxito). Corrección al alcance: el SQL
**no aborta** si falta `TEMP.T_CERTNACI`; avisa en `[1]`, recompila los otros 15 y deja `NATALIDAD`
inválida por dependencia — que es justo lo que hay que ver antes de ir a crear esa tabla.

### 27.7 Lo que sigue abierto

1. **El origen se quedó sin datos desde el 20/09**: aunque se recuperó agosto, en el Oracle **no
   hay ni una defunción posterior al 20/09/2026** (ni nacimientos después del 16/09). El anexo del
   martes sigue llegando pero con fecha de-certified vieja, o la captura del centro se detuvo: hay
   que confirmarlo con la oficina antes de prometer el mes cerrado.
2. ~~**`TEMP.T_CERTNACI`**: sin ella `NATALIDAD` no recompila.~~ **Descartado el 09/10/2026**:
   `NATALIDAD` **no** usa `TEMP.T_CERTNACI` (depende de `SISMAI.CERTNACIMIENTO`, `NAC_MADRE`,
   `NAC_RNACIDO`, `ESTABLECIMIENTO` y `SISMAI.V_ORG_GEOGRAFICA`) y compiló `VALID` sin esa tabla.
   La hipótesis de §22.1/§27.3 era falsa. Sigue sin existir `TEMP.T_CERTNACI`, pero ya no bloquea
   nada de lo nuestro.
3. ~~**Item 2**: ejecutar el comando de §27.6 con acceso a la consola, o dar acceso (llave/clave) a
   una cuenta con DBA para poder correrlo remoto.~~ **HECHO 09/10/2026** (§27.11).
4. **Alias de centros** legacy↔demo (§27.4), si se quiere que los usuarios demo vean el histórico.

### 27.8 `lara_2019_2020.xlsx`: solo mortalidad, **NO cargado**

Análisis delegado (el archivo está en la raíz y **no** se importó a la BD):

- 2 hojas de datos (**2019**: 11.810 filas, **2020**: 10.337) + `Diccionario` (EV-14 de 2012).
  220 columnas; fila 1 título, fila 2 encabezados, fila 3 en adelante.
- Es **persona por persona**, no agregado, y **no cubre 2021**.
- **Sin diagnóstico**: 418 casos en 2020 frente a 2 en 2019. El patrón (concentrado oct–dic 2020,
  componente respiratorio `J189`+`J960`) es **compatible con COVID, pero no lo demuestra**: hace
  falta la confirmación molecular o el código de la prueba en la fuente.
- **No trae establecimiento utilizable** (el campo viene vacío; solo localidad/municipio), así que
  **no se puede atribuir por centro** sin un cruce con el padrón.
- Contraste con SISV: 5.291 defunciones de 2019 y 427 de 2020, o sea que el archivo complementaría
  huecos. **No verificado** contra la BD antes de cualquier carga.

**Recomendación:** no cargarlo a ciegas. Antes: (a) confirmar con la oficina si trae el código de
COVID/neumonía, (b) decidir la fuente de verdad para 2019-2020 (¿el archivo pisa al certificado?),
(c) como no trae establecimiento, emparejar el centro por localidad solo para construir un *mapa* de
atribución, nunca como dato original.

### 27.9 Refresco del espejo, resincronización y verificación de semanas 39-40 (06/10/2026)

**Delimitador del espejo: `\x01` (SOH), no coma.** Con coma, cualquier texto con coma embebida
parte el registro. El bug que costó entender: dentro de `sxs "..."`, el heredoc remoto del
generador tenía que ir `<<'GEN'` (entrecomillado); con `<<GEN` el shell remoto rehace la expansión
de `COLSEP_VAL` y **se come el byte `\x01`**, dejando `SET COLSEP` vacío → separador por defecto
(espacios). Con `HEADING OFF` no hay cabeceras, así que se carga con `--formato text
--sin-encabezado` (no hay línea que borrar). `HEADER` es solo de `FORMAT csv` en PostgreSQL.

**Espejo 100 % sincronizado con el origen** (12/12 tablas, contraconteo exacto), incluidas las 4 de
apoyo que estaban desfasadas (`CAUSA_M` +27, `CIE10` +37, `NAC_MADRE` +723, `ORG_GEOGRAFICA` +21):

```bash
./migracion/espejo_csv.sh                      # en el servidor, COLSEP_VAL=$'\x01'
./.venv/bin/python migracion/cargar_espejo_pg.py --directorio /var/tmp/espejo_20261006 \
    --esquema sismai --formato text --sin-encabezado --recortar-campos \
    --delimitador $'\x01' --ejecutar           # 11 tablas, 59 s
```

| Tabla | Origen | Espejo | | Tabla | Origen | Espejo |
|---|---:|---:|---|---|---:|---:|
| CERTIFICADO | 174.095 | 174.095 | | CAUSA_M | 211.285 | 211.285 |
| CERTNACIMIENTO | 439.790 | 439.790 | | CIE10 | 16.664 | 16.664 |
| NAC_RNACIDO | 439.476 | 439.476 | | ORG_GEOGRAFICA | 58.960 | 58.960 |
| NAC_MADRE | 439.809 | 439.809 | | ESTABLECIMIENTO | 21.148 | 21.148 |
| DOCUMENTO | 140.309 | 140.309 | | CASOS_MMI | 10.762 | 10.762 |
| RENGLON_CASOSMI | 10.011 | 10.011 | | RENGLON_CASOSMM | 749 | 749 |

**El origen sigue recibiendo certificados retroactivos**: de las filas que faltaban, 57 defunciones
y 41 nacimientos tienen `FECHAOPERACION = 06/10/2026`, y 305 nacimientos entraron en una tanda del
17-23/09 con fecha de nacimiento repartida por todo el año (por eso el ETL del hueco, que solo
miraba agosto en adelante, no los vio). **El espejo hay que refrescarlo periódicamente**, no una
vez: los certificados se cargan tarde con fecha vieja.

**Resincronización (2 registros perdidos en importaciones anteriores):**

| Comando | Resultado |
|---|---|
| `importar_legacy_registros` | **403 nacimientos + 110 defunciones** creados (84 quedaron `codificacion_pendiente`) |
| `recuperar_establecimiento_defuncion --ejecutar` | **87.111** defunciones recuperadas desde `CERTIFICADO` |
| `asignar_organizacion_legacy --ejecutar` | 403 + 110 + **87.096** asignados; 0 orgs creadas, 596 reutilizadas |

Tras esto SISV vuelve al estado documentado en §17: **70 defunciones y 19 nacimientos sin
organización** (establecimientos fuera del árbol Lara, a propósito) y **1 defunción sin
establecimiento**. Los 87.111 recuperados apuntan a `HESTABLECIMIENTO = 67754` = **DES LARA**
(en el árbol): el origen trae `HESTABLECIMIENTO_OCUR` nulo en 87.420 certificados y
`HESTABLECIMIENTO` **nunca** nulo (0 de 174.095), así que el fallback del importador es correcto y
lo que faltaba era el *backfill* de lo ya importado.

**`limpiar_legacy_no_lara` NO se ejecutó** (decisión del usuario, 06/10): preferimos no borrar.
El dry-run proponía 2.277 defunciones (56 por establecimiento fuera del árbol + 2.221 **sin
establecimiento** con residencia Yaracuy 483 / Portuguesa 406 / Zulia 156 / …). Ojo: el **orden**
cambia el resultado — si se recupera el establecimiento primero, esas 2.221 dejan de cumplir el
criterio «sin establecimiento y residencia ≠ Lara» y se conservan; solo se caerían 71.

**Verificación de semanas epidemiológicas (domingo–sábado; semana 1 de 2026 = dom 04/01/2026,
NO ISO — `vigilancia.services.semana_epidemiologica`):**

| Sem. | Rango | Def. espejo | Def. SISV | Nac. espejo | Nac. SISV | MM | MN |
|---|---|---:|---:|---:|---:|---:|---:|
| 36 | 06–12/09 | 7 | 7 | 18 | 16 | 0 | 4 |
| 37 | 13–19/09 | 4 | 4 | 1 | 1 | 0 | 3 |
| 38 | 20–26/09 | 1 | 1 | 0 | 0 | 0 | 0 |
| **39** | 27/09–03/10 | **0** | **0** | **0** | **0** | **0** | **0** |
| **40** | 04–10/10 | **0** | **0** | **0** | **0** | **0** | **0** |

**Las semanas 39 y 40 están vacías en los dos sistemas** y coinciden: no hay nada que conciliar.
Lo confirmado en §27.7.1 se mantiene — el origen no tiene defunciones después del 20/09 ni
nacimientos después del 16/09, aunque **sí** sigue llegando documentación con fecha vieja.

**Totales oficiales — MM cuadra, MN no y es de definición:**

| Fuente | MM 2026 | MN 2026 |
|---|---:|---:|
| **Oficina** | **18** | **235** |
| SISV tablero (año **epidemiológico** 2026 = 04/01/26–02/01/27) | **18** ✓ | **233** |
| SISV año **calendario** 2026 | 7 (certificados) | **236** |
| Legado `CASOS_MMI` (área Lara), epi / calendario | — | 236 / 239 |

- **MM = 18 ✓ exacto**: sale de `RENGLON_CASOSMM`→`CASOS_MMI` (registro de investigación), que es
  lo que reporta la oficina. El certificado (`embarazo_o_puerperio`) solo marca 7.
- **MN no calza con ninguna ventana**: el tablero da **233** (año epidemiológico, la definición que
  usa `_filtro_anio`) y el año calendario **236**; la oficina dice **235** y el legado da 236 (epi)
  o 239 (calendario). Las 3 muertes del 01–03/01/2026 caen en la semana 53 de 2025 y por eso
  separan 233 de 236. **Hay que preguntar a la oficina con qué ventana cuentan** antes de dar un
  número por bueno; ninguna de las cuatro combinaciones da 235.
- Sin duplicados, sin `es_muerte_fetal`, sin fechas invertidas en los 236; el lado legacy tiene
  **+3** sobre SISV en *ambas* ventanas (7 SOLO_CRUDO / 3 SOLO_SISV por celda en
  `conciliar_neonatal --anio 2026`).

**Estado de la suite:** 227 tests OK (`DJANGO_DB_ENGINE=sqlite manage.py test` desde `backend/`).

### 27.10 Purga de la data demo de PostgreSQL (08/10/2026)

Se borró todo lo que había sembrado `sembrar_demo`. Estado **antes** → **después**:

| Qué | Antes | Después |
|---|---:|---:|
| Nacimientos (`lote LOTE-*`) | 439.479 | **439.476** (−3) |
| Defunciones (`lote LOTE-*`) | 174.097 | **174.095** (−2) |
| Fichas de vigilancia | 2 | **0** |
| Consolidados semanales (+112 filas hijas) | 1 | **0** |
| Organizaciones | 997 | **995** |
| Usuarios | 7 | **1** (`admin`) |

Lo que se borró: los 8 registros de `mock_data.py` (3 nacimientos + 2 defunciones + 2 fichas con
códigos `FV-2026-00345`/`FV-2001-00012` + 1 consolidado sin `legacy_tabla`), las 2 organizaciones
centro demo (**`LARA-HCB`** y **`LARA-CAB`**, sin hijos y sin ningún registro real) y los usuarios
`laraepid`, `hbcentral`, `codificadora`, `epi`, `dir` y `tester_legacy`.

**Lo que NO se borró, y por qué:**

- **`MPPS` → `LARA-GOB` → `LARA-EPI`** parecen demo (las creó `sembrar_demo`), pero **`LARA-EPI`
  es la raíz de los 993 centros reales** que creó `asignar_organizacion_legacy`. Borrarlas
  orphanaría todo el árbol de atribución. No son demo: son la estructura jerárquica real
  (ministerio→gobernación→regional→centros). Si algún día hay que rehacerlas, hay que
  **reparentar los 993 centros** antes, no después.
- **`LEGACY-LARA`**: es el fallback «Legacy regional (histórico)» para los 263 establecimientos
  legacy sin centro propio (§17.21). Tampoco es demo.
- **`admin`**: es el único superusuario y la única forma de entrar a `/admin` y a la API. Se
  conserva siempre; la clave de demo es `Sisv.2026!` y **hay que cambiarla en producción**.

Consecuencias prácticas: ya no se puede probar el alcance multicentro (no hay usuarios con rol
ni con organización), y `/vigilancia` empieza vacío. Para restaurarlos:
`./.venv/bin/python backend/manage.py sembrar_demo` (idempotente, `--sin-usuarios` omite usuarios).

Tras la purga, SISV quedó con **exactamente los 174.095 certificados de defunción del origen**
(`sismai."CERTIFICADO"`) y los **70 defunciones / 19 nacimientos sin organización** documentados en
§17 (establecimientos fuera del árbol Lara, a propósito). Suite: **227 tests OK**.

### 27.11 [HECHO 09/10/2026] Recompilación de los 16 objetos Oracle: `SISMAI` con 0 inválidos

Con la clave del usuario de SO **`oracle`** (grupo `dba`, guardada en
`legancy_conf/credenciales.env` como `SISV_SSH_USUARIO_DBA`/`SISV_SSH_CLAVE_DBA`) se entra por SSH
al servidor y `sqlplus / as sysdba` responde (antes era `ORA-01031`). **Resultado: los 16 objetos
pasaron de `INVALID` a `VALID` y `ALL_OBJECTS` no deja ningún inválido en `SISMAI`.**

**Dos cosas que estaban mal en el plan original de §27.6:**

1. **El SQL tenía un bug de PL/SQL.** Declaraba un `RECORD` y lo instanciaba con
   `t_objeto('VIEW','X')`; **PL/SQL no admite constructores de `RECORD`** y en Oracle 10g eso da
   `PLS-00320: la declaración de tipo de esta expresión está incompleta o tiene un formato
   incorrecto` (el `ALTER` nunca llegaba a ejecutarse). Corregido en
   `migracion/recompilar_16_objetos.sql`: la lista es ahora una tabla asociativa de `VARCHAR2`
   con formato `'TIPO|NOMBRE'` separado en runtime. No hubo que tocar nada del servidor.
2. **El orden de compilación importa.** Los 4 procedimientos (`SPDOC`, `SPREGDSP`, `SPREGEPI`,
   `SPREGTEL`) referencian la función `FIDPADRE`, que estaba en la **posición 16** — o sea, se
   compilaba *después* que ellos. Por eso en la primera pasada quedaron `INVALID` **sin error de
   sintaxis** (`DBA_ERRORS`/`ALL_ERRORS` salían vacíos: es invalidez *por dependencia*, no error
   de código). Con las vistas y `FIDPADRE` ya válidos, **una segunda pasada** sobre los 4 los
   cerró. (`FIDDOC` y `FNUMDOC`, las otras dos funciones referenciadas, ya estaban válidas.)

**Verificación final:**

| Objeto | Antes | Después |
|---|---|---|
| 11 vistas (`C_INFORMES`, `C_INFORMES1`, `NATALIDAD`, `V_REGISTROCIRUGIA`, `V_FICHAEPI13`, `C_ESTABLECIMIENTO`, `V_ESTABLE_DIREC`, `V_ORG_SANITARIA`, `V_PACIENTEVACUNACION`, `V_PACIENTECIRUGIA`, `H_DEPEN`) | INVALID | **VALID** |
| `FUNCTION FIDPADRE` | INVALID | **VALID** |
| `PROCEDURE SPDOC`, `SPREGDSP`, `SPREGEPI`, `SPREGTEL` | INVALID | **VALID** |
| `COUNT(*) INVALID` en `SISMAI` | 16 | **0** |

**`TEMP.T_CERTNACI` no era el problema.** `NATALIDAD` compiló `VALID` sin ella porque **no la
usa** (depende de `SISMAI.CERTNACIMIENTO`/`NAC_MADRE`/`NAC_RNACIDO`/`ESTABLECIMIENTO` y de
`SISMAI.V_ORG_GEOGRAFICA`). La hipótesis de §22.1/§27.3 queda descartada; ya no hace falta pedir
ese DDL.

**No se tocó** nada más: ni `EVENTOS_SINC`, ni el esquema `TEMP`, ni objetos fuera de los 16
(alcance §22.3). Resto de inválidos en la base (fuera de alcance, preexistentes y de `SYS`):
12 `PACKAGE BODY` y 34 `VIEW` de `SYS`, y 2 `VIEW` de `SYSTEM` — ajenos a SISMAI.

Log del servidor: `/tmp/recompilar_16_20261009_0954.log` (primera pasada) y salida de la segunda
pasada capturada en la sesión de OpenCode del 09/10/2026.
