# AGENTS.md — SISV (Sistema Integral de Salud)

Idioma de trabajo: **responder siempre en español**.

## Stack del proyecto

- **Backend:** Django REST Framework (operativo, ver sección Backend).
- **Frontend:** React + Vite, consumo de API con Axios (operativo).
- **BD destino:** PostgreSQL **18.6** (última versión estable, publicada 2026-08-13) vía Docker.
- **BD origen:** Oracle 10g en servidor openSUSE 11.4 (acceso por SSH con usuario de sistema `oracle`, privilegios DBA implícitos).
- Migración MariaDB 10.11 → PostgreSQL 18.6 **completada** (jun 2026): MariaDB quedó fuera de uso.

## Base de datos local (PostgreSQL 18.6 vía Docker) - EN ACTIVO

- Contenedor `sis_postgres_dev` (imagen `postgres:18.6-alpine`, puerto `5436:5432`) corriendo con
  `--restart always` y volumen persistente `sis_postgres_data`. Levantado con `docker run` porque en
  este equipo **el plugin `docker compose` no existe** (`docker compose` da error).
- BD `sis_salud_db`, usuario `sis_user` / `sis_password` (sin superusuario `postgres` en el default).
- **PostgreSQL 18 cambió el punto de montaje oficial:** el volumen va en `/var/lib/postgresql`
  (antes `/var/lib/postgresql/data`); el `PGDATA` real de la imagen es `/var/lib/postgresql/18/docker`.
- El puerto `5436` es de SISV porque el `5432` lo ocupa `tryton-postgres`; otros contenedores usan
  `5433` (`farmacia_pg`), `5434` (`banco-sangre-db`) y `5435` (`rrhh_postgres`).
- Verificar: `docker exec sis_postgres_dev psql -U sis_user -d sis_salud_db -c "SELECT version()"`.
- **IMPORTANTE en sesiones de OpenCode:** el usuario `rafael` ya está en el grupo `docker`, pero el
  shell persistente hereda grupos antiguos → ejecutar comandos docker con `newgrp docker -c "..."`
  (o usar `sudo`). Cualquier proceso `docker run`/`pull` que tarde >120s cuelga la sesión.
- El contenedor `sis_mariadb_dev` (imagen `mariadb:10.11`, puerto `3306`) quedó **detenido**; su
  volumen `mariadb_data` se conserva por si se requiere un rollback. El MariaDB del sistema
  (`/usr/sbin/mariadbd`) sigue **deshabilitado** (`systemctl disable`).
- Proxmox 9.2 (producción futura): se correrá PostgreSQL nativo, sin Docker; se exporta con `pg_dump`.
- El `docker-compose.yml` se mantiene como documentación/despliegue alternativo en otros equipos.

## Backend (Django REST) y Frontend (React + Vite)

- Virtualenv en `.venv/`. Instalar: `./.venv/bin/pip install -r backend/requirements.txt`.
- Base de datos de Django: **PostgreSQL 18.6 por defecto ya operativa** (driver `psycopg` v3);
  `DJANGO_DB_ENGINE=sqlite` para pruebas aisladas sin contenedor.
- Migraciones existentes aplicadas en PostgreSQL (catalogos + registros).
- Arrancar backend: `./.venv/bin/python backend/manage.py runserver 127.0.0.1:8000`.
- Arrancar frontend: `npm run dev` dentro de `frontend/` (proxy `/api` → puerto 8000; puerto 5173).
- Mover el servidor en segundo plano dentro de una llamada a Bash de OpenCode **cuelga la sesión
  de hasta 120s**: verificar endpoints con el cliente de pruebas de Django
  (`manage.py shell -c "from django.test import Client; ..."`), no con `curl` a un proceso `&`.
- **Acceso desde la red local (casa/oficina):** `./iniciar_lan.sh` levanta Django en `0.0.0.0:8000`
  y Vite con `--host 0.0.0.0` (puerto 5173); cualquier dispositivo de la red entra por `http://<IP>:5173`
  (todo el tráfico `/api` pasa por el proxy de Vite, misma-origen). `settings.py` detecta automáticamente
  la IP local y la añade a `CSRF_TRUSTED_ORIGINS`/`CORS_ALLOWED_ORIGINS` (por eso el login funciona desde
  el celular); también se puede fijar con env `DJANGO_CSRF_TRUSTED_ORIGINS`. Vite tiene `server.host: true`
  en `vite.config.js`. En oficina la IP fija es `192.168.5.202`; en casa es DHCP. La BD vive en el contenedor
  `sis_postgres_dev` (puerto 5436), no se necesita exponerla en la red.

### Estructura de apps (backend/)

- `catalogos`: modelos `CIE10`, `CIE11` (jerárquico self-referential: capítulo→bloque→categoría→subgrupo),
  `MapeoCIE` (cross-walk). Serializers + vistas con datos reales en BD.
- `registros`: `Nacimiento`, `Defuncion`, `FichaVigilancia` heredan `RegistroConCIE`.
- `seguridad`: `Organizacion` (jerárquica: ministerio→gobernación→regional→centro) y `Perfil` con rol.
  Endpoints `/api/seguridad/` (organizaciones, roles). Cada `RegistroConCIE` enlaza `organizacion`.
- **Autenticación y alcance (multicentro):** login por sesión Django en `/api/auth/` (login/logout/me/csrf).
  El frontend exige iniciar sesión (página `Login.jsx`); usa cookie de sesión + token CSRF (`setCsrf` en
  `api/axios.js`). El alcance se define en `seguridad/services.py::alcance_registros`:
  - `MINISTERIO`/`GOBERNACIÓN`/sin org → ve todo; puede elegir centro de destino en la carga.
  - `REGIONAL` (ej. Dirección de Epidemiología del Estado Lara) → ve **todos los centros de su estado**
    (filtra por `estado`), y en la carga elige el centro destino de cada certificado (`CentroSelector.jsx`).
  - `CENTRO` → solo su centro; la carga se fuerza a él (ignora lo enviado).
  - Sin org / superusuario → ve todo; en la carga puede elegir cualquier organización (todas se muestran
    en el selector de `Vigilancia.jsx`). El POST sin `organizacion` devuelve 400 claro: «Debe indicar la
    organización/establecimiento destino».
  - En listas, cada registro devuelve `organizacion_nombre`; hay columna «Centro» en las tablas.
  - Dashboard y reportes también respetan el alcance.
  - Permisos finos por acción en `seguridad/services.py::permisos_de` y enforce en los endpoints:
    **crear/editar** → TRANSCRIPTOR, CODIFICADOR, **VIGILANCIA**, DIRECTOR y superusuario; **eliminar y
    configurar** → solo DIRECTOR y superusuario; **EPIDEMIÓLOGO** y **SECRETARIA** son solo lectura.
    El frontend deshabilita el formulario (bloqueo con `fieldset disabled`) y oculta los botones según
    `usuario.permisos`.
  - **Usuarios demo (clave `Sisv.2026!`, cambiar en producción):** `admin` (superusuario, acceso total),
    `laraepid` (transcriptor direcc. regional Lara), `codificadora` (codificadora regional, no elimina),
    `hbcentral` (transcriptor Hospital Central de Barquisimeto), `epi` (epidemiólogo, solo lectura),
    `dir` (director regional). Organizaciones demo bajo MPPS→Gobernación Lara→
    Dirección Epidemiología Lara→ Hospital Central de Barquisimeto / Ambulatorio Cabudare.
    Crear más desde `/admin` (Django) asignando `Perfil` (rol + organización).
- `territorio`: división política `DivisionTerritorial` (self-referential, niveles ESTADO→MUNICIPIO→PARROQUIA→COMUNIDAD).
  **ASIC**: modelo `ASIC` (área de salud integral comunitaria) con `parroquia` sede (FK), dirección, responsable,
  teléfono, email y `establecimientos_adscritos` (consultorios/CDI/CRI/ambulatorios de su red). Endpoints
  `/api/territorio/asic/` (GET filtrable por estado/municipio/parroquia/q + POST) y `/api/territorio/asic/<id>/`
  (GET/PATCH/DELETE); crear/editar/eliminar requiere `puede_configurar` (DIRECTOR/superusuario). La org
  (centro de salud) se vincula con `Organizacion.asic` y expone `parroquia`; cada centro queda asociado a
  **ASIC + parroquia + municipio + estado** (derivado del ASIC). **Comunidades (24/09/2026):** M2M
  `ASIC.comunidades` → `DivisionTerritorial` nivel COMUNIDAD (`asics_territoriales`); el serializador
  expone `comunidades`/`comunidad_count`, y POST/PATCH de `/api/territorio/asic/` aceptan `comunidades`
  (ids o CSV) validando nivel COMUNIDAD. Frontend **`/asic`** (`Asic.jsx`): formulario + cascada
  estado→municipio→parroquia + checkboxes de comunidades + tabla.
  **Fuente oficial del territorio completo (hasta comunidades):** API de la APN `apisegen.apn.gob.ve`
  (División Político Territorial y de Población, Sede/IGVSB+INE, proyección 2023). Requiere
  **token de desarrollador**: registrarse en `https://apisegen.apn.gob.ve/registroUsuario/`, luego
  `POST /api/v1/login` (usuario/clave form-urlencoded) devuelve `token`; los GET (`listadoEntidad`,
  `listadoMunicipio?codEntidad=`, `listadoParroquia?...`, `listadoComunidad?...`) reciben `token` por query.
  Swagger en `https://apisegen.apn.gob.ve/api/v1/api-doc/`. Comando:
  `./.venv/bin/python backend/manage.py descargar_territorio_apn --usuario <dev> --clave <clave>` (o env
  `APN_USUARIO`/`APN_CLAVE`); siembra ESTADO→MUNICIPIO→PARROQUIA→COMUNIDAD con códigos INE; `--borrar`
  vacía, `--sin-comunidades` omite el nivel fino. **Cargado completo el 23/09/2026** con credenciales de
  desarrollador de `venegas` (no commitearlas): la API entrega solo **24 entidades** (Dependencias Federales
  no existe) → en BD **24 estados / 335 municipios / 1.125 parroquias / 74.631 comunidades** (el 25/1.138
  de `marydn/venezuela-sql` es referencia teórica). Códigos INE parciales por nivel (estado 2 + municipio 2 +
  parroquia 2 + comunidad 11 díg.); las 28 comunidades "faltantes" son duplicados del INE deduplicados por la
  restricción única `(nivel, nombre, padre)`. Filas instaladas en `territorio/data/estados.py` y
  `territorio_banco_sangre.csv` (este último incompleto, sin comunidades; ya sustituido por la descarga APN).
- **BD territorio aparte para otras aplicaciones:** creada `territorio_apn` en `sis_postgres_dev` (5436),
  propietario `sis_user`, con entidades normalizadas `estados`(2)/`municipios`(4)/`parroquias`(6)/
  `comunidades`(17) y vista `division_geografica` (state→comunidad). La puebla
  `./.venv/bin/python backend/manage.py exportar_territorio_pg` (idempotente, TRUNCATE+insert desde
  `DivisionTerritorial`; parámetros por CLI o env `APN_PG_*`). Acceso local: `docker exec sis_postgres_dev
  psql -U sis_user -d territorio_apn`.
- `vigilancia`: **Consolidado Semanal de ENO (SIS-04/EPI-12 y EPI-14)**. Modelos: `EventoENO` (catálogo 123 eventos
  `en_epi12`/`en_epi14` con orden oficial), `ConsolidadoSemanal` (anio/semana/tipo MORBILIDAD|MORTALIDAD, estado
  BORRADOR|ENVIADO|CERRADO, origen PROPIO|CONSOLIDADO_SUPERIOR; unique por org+año+semana+tipo), `FilaConsolidado`
  (13 grupos etarios × 2 sexos; **regla «edad ignorada» → columna Hombres**, M siempre 0), `SituacionEspecial`,
  `AlertaEpidemia`. Endpoints `/api/vigilancia/`: `eventos-eno` (GET, filtros grupo/en_epi12/en_epi14/q),
  `consolidados/` (GET lista + POST crea y siembra filas del catálogo), `consolidados/<id>/` (GET/PATCH/DELETE,
  reemplazo total de filas/situaciones/alertas), `consolidados/exportar/` (CSV con BOM, respeta alcance y filtros).
  Permisos: crear/editar TRANSCRIPTOR/CODIFICADOR/DIRECTOR; eliminar DIRECTOR/superusuario; EPIDEMIÓLOGO lectura
  (igual que `permisos_de`). Frontend: `/vigilancia` (matriz editable 13×2, pestañas situaciones/alertas, estados,
  exportar CSV); `/vigilancia/fichas` conserva la carga individual heredada. El org en POST se fuerza desde
  `organizacion_por_defecto` (CENTRO) o del payload (niveles superiores eligen centro destino); utilidades en
  `vigilancia/services.py` (`semana_epidemiologica`, `organizaciones_descendientes`, `sembrar_filas`).
- Las tablas de hechos **persisten en PostgreSQL** (ya no son mock): nacimientos/defunciones/fichas con CRUD
  (GET/POST/PUT/PATCH/DELETE) vía ORM, scoping por alcance y validación CIE por fecha; `/dashboard/` y
  `/reportes/` leen de la BD; `/reportes/exportar/` descarga CSV (UTF-8 BOM para Excel) respetando alcance
  y filtros (módulo/desde/hasta/estado). `ConfiguracionGeneral` en `registros` (GET/PUT `/configuracion/`).
  Los serializers decoran cada registro con `organizacion`, `organizacion_id`, `organizacion_nombre` y
  `organizacion_nivel`; PATCH parcial valida CIE solo si se tocan campos CIE.
  **`Reporte comparativo anual (24/09/2026):`** `/registros/reportes/comparativo/?anio1=&anio2=`
  (`ReporteComparativoView`) por semana epidemiológica (ISO 1–53) con series nacimientos, muertes,
  muertes_maternas (M, `embarazo_o_puerperio=True`) y mmi (fichas `LEGACY-MMI`/`LEGACY-VIOLENTA`),
  respetando alcance; en `/reportes` se renderiza con `GraficoLineas` (SVG propio, anio1 sólido/anio2
  punteado, sin dependencias).
  - **Certificado de defunción = EV-14 oficial (01/10/2026, migración `0005_defuncion_ev14`):**
    `Defuncion` tiene **50 campos más**, todos opcionales (`null`/`blank`) para no romper los certificados
    ya cargados ni el ETL, organizados por las secciones del EV-14: **I** identificación
    (`nacionalidad`, `segundo_apellido`/`segundo_nombre`, `edad_ignorada`, `lugar_nacimiento`,
    `nacimiento_exterior`, `estado_civil`, `profesion`, `ocupacion_lugar_trabajo`,
    `sabe_leer_escribir`, `residencia_habitual`, `asistencia_medica`), **II** menor de un año / muerte
    fetal / madre (`es_muerte_fetal`, `peso_nacer_gramos`, `edad_gestacional_semanas`, `tipo_embarazo`,
    `tipo_parto`, `asistencia_parto`, `madre_*` incluido `madre_numero_gestas`,
    `madre_fecha_ultima_gesta`, `madre_embarazada`, `madre_puerperio`), **V** muerte violenta
    (`manera_de_morir`, `fecha_/hora_hecho_violento`, `descripcion_hecho_violento`), **VI** certificación
    médica (`causa_antecedentes`, `otros_estados_patologicos`, `intervalo_enf_muerte`, los 4
    `diagnostico_*` de «confirmado por», `cirugia`/`fecha_ultima_cirugia`/`descripcion_cirugia`,
    `correo_contacto`, `matricula_mpps`) y **VII** registro civil (`registro_civil_nombre`,
    `numero_acta_defuncion`, `folio_defuncion`, `fecha_registro`, `declarante_*`, `registrador_civil_*`,
    `gaceta`, `resolucion`). `/defunciones` (`CargaDefunciones.jsx`) se reorganizó con esos rótulos.
    Reglas: **nada nuevo es obligatorio** (el certificado mínimo se sigue creando) y **`embarazo_o_puerperio`
    no se toca** (es lo que leen el tablero y `conciliar_mm`; el bloque de la madre es respaldo, no
    reemplazo). Pruebas en `registros/tests.py::DefuncionEV14Tests`. Análisis de las capturas del usuario y
    el registro semanal MM/MN ya hecho en `PENDIENTES.md` §23.
    Las capturas están en `capturas/`; para leerlas **hay que pasar por OCR** (`rapidocr_onnxruntime` en
    `.venv`, tesseract no está instalado), porque este entorno no ve imágenes.
  - **Certificado de nacimiento = EV-25 oficial (02/10/2026, migración `0006_nacimiento_ev25`):**
    `Nacimiento` tiene **24 campos más**, todos opcionales: **I** del recién nacido (`nino_nombres`,
    `nino_apellidos`, `numero_historia_clinica`), **II** madre y **III** padre (nacionalidad
    `V/E/P/I/O`, `*_pasaporte`, `*_residencia` `V/E/I`, `*_residencia_pais`,
    `*_residencia_direccion`, `*_residencia_parroquia`/`*_residencia_comunidad` como FKs al
    `territorio.DivisionTerritorial`), **IV** registro civil ya existente, **Responsable**
    (`certificador_nombres`/`_cedula`/`_matricula_mpps`, `director_establecimiento`) y cabecera
    (`fecha_emision`, `numero_planilla`, `tipo_numero_certificado` COMPLETO|HISTORICO). El **sexo**
    cambió de etiqueta: `I` ahora se rotula **«Hermafrodita»** (el código no se toca) y se añadió
    `N` = «Sin información»; solo 115 filas históricas tienen `I`. `clean()` y el serializer validan
    que los FKs de residencia sean PARROQUIA/COMUNIDAD, y el serializer expone
    `madre_residencia_territorio`/`padre_residencia_territorio` (4 niveles) para que
    `SelectTerritorial` (props `destino`/`comunidadComoLista`) precargue la cascada. `/nacimientos`
    (`CargaNacimientos.jsx`) se reorganizó por secciones. Reglas: **nada nuevo es obligatorio** y el
    ETL no se toca. Pruebas en `registros/tests.py::NacimientoEV25Tests`;
    **backfill** `manage.py completar_nacimiento_legacy` (dry-run; `--ejecutar`; `--solo nombres|residencia`)
    recupera de `NAC_RNACIDO."NOMBRES"` (438.518) y `NAC_MADRE."HRESIDENCIA"` (416.706, por nombre
    dentro del árbol), **solo campos vacíos** e idempotente; pruebas en
    `registros/tests_completar_nacimiento.py`.
  - **Registro semanal MM/MN (02/10/2026, §23.4):** el anexo del telegrama es un **reporte generado**, no
    un formulario de captura. Endpoint `GET /api/registros/reportes/semanal-mmi/?anio=&semana=[&formato=csv]`
    (`ReporteSemanalMMIView`) por establecimiento y semana: nacidos vivos/muertos desde
    `Nacimiento.nacido_vivo`, MM (`registros/services.py::muerte_materna_detalle`, `mm_fuente`
    `REGISTRO_INVESTIGACION`/`CERTIFICADO` más `mm_certificadas`), MN (0-27 d), infantil <1 año y 1-4 años
    desde `Defuncion` + `fecha_nacimiento`. **`partos` y `abortos` no se generan** (el certificado es por
    recién nacido, no por parto; SISV no captura abortos). CSV con BOM de tres secciones
    RESUMEN/MATERNA/INFANTIL. Helper `vigilancia.services.rango_semana`. Frontend: sección en `/reportes`
    (`Reportes.jsx`). Pruebas `registros/tests.py::ReporteSemanalMMITests` (7).
- **Limpiar legacy fuera de Lara / demo (24/09/2026):** `manage.py limpiar_legacy_no_lara` (criterio
  **centro Lara + domicilio Lara**, economía del árbol DES LARA=67754/DPS LARA=3441583108; dry-run por
  defecto, `--ejecutar` aplica). Ejecutado: **Nacimientos 438.577, Defunciones 171.115, Fichas 0,
  Consolidados 0**. Bandeja de codificación: endpoint de defunciones acepta `?pendientes=1`
  (`codificacion_pendiente=True`); el checkbox «Solo pendientes de codificación» en `/defunciones`
  (CargaDefunciones.jsx) lista las **49.162** defunciones que esperan CIE.
- **El establecimiento de la mitad de las defunciones estaba perdido (28/09/2026, corregido):**
  `importar_legacy_registros` leía solo `CERTIFICADO."HESTABLECIMIENTO_OCUR"`, que viene **nulo en
  87.203 de 173.533 certificados**, mientras `"HESTABLECIMIENTO"` **siempre** está. Esas muertes se
  importaron sin nombre y por tanto con `organizacion_id IS NULL` (el 50,3% del histórico),
  invisibles para cualquier usuario con alcance de centro. El importador ya usa `_OCUR` **o, si es
  nulo, `HESTABLECIMIENTO`**; para lo ya importado está `manage.py
  recuperar_establecimiento_defuncion [--ejecutar]` (un solo `UPDATE ... FROM`, **solo campos
  vacíos**, idempotente). Aplicado: 87.203 recuperadas + 87.240 asignadas con
  `asignar_organizacion_legacy --ejecutar` (que además asignó 14.460 fichas huérfanas). Quedan
  **70** defunciones de 39 establecimientos fuera del árbol Lara, sin centro a propósito.
  **El renglón MORTALIDAD del ENO nunca se usó:** `RENGLONTELE` suma 3.618 muertes en 18 años
  contra 173.533 certificados; la mortalidad real vive en `registros.Defuncion`, no en ENO.
- **Muerte materna (corregido el 29/09/2026):** el indicador MM **ya no** sale de
  `Defuncion.embarazo_o_puerperio`. Ese campo es un aviso opcional del certificador
  (`CERTIFICADO.HPRESENCIAEMBARAZO` en 1=embarazo o 2=puerperio) y lo diligencia en solo el **11,9 %
  de las muertes maternas**: 748 en el registro de investigación contra **89 marcadas con solo el
  código 1. Con la corrección 1+2 (§17.20) el certificado marca 191**, 2009-2026. Salva que MM no
  dependa de la CIE, pero **subcuenta**, y por eso el tablero daba 7 en 2026 donde la responsable de
  Lara reporta 17 + 1 violenta.
  - **El indicador sale de `sismai."RENGLON_CASOSMM"` enlazado a `sismai."CASOS_MMI"`
    (`HCASOSMMI` → `CASOS_MMI."ID"`, 748 de 749 enlazan)**, que es el registro de investigación
    caso por caso: **18 en 2026**, exactamente lo que reporta la oficina. La fecha de la muerte está
    en `CASOS_MMI."FECHAOCURRENCIA"`, **no** en `PERIODOOCURRENCIA` (viene `NULL` en las 749), y
    `HCASOSMMI` es el **ID de la persona, no un contador** (por eso `SUM` da 658.439.440.845). No
    hay bug de mapeo: era la lectura equivocada (§21).
  - El MM **sí es atribuible a un centro** por `CASOS_MMI."HDOCUMENTO"` → `DOCUMENTO."HORIGEN"`
    (19 establecimientos, todos del árbol Lara), así que respeta el alcance como el MN. Con alcance
    acotado y **cero MM atribuidas** se cae al certificado en vez de mostrar 0, porque un 0 ahí
    significaría «este centro no tuvo muertes maternas», que es justo lo que no se sabe.
  - El conteo de certificados no se pierde: el tablero expone `mm_certificadas`, `mm_codificadas`,
    `mm_pendientes` y `mm_fuente`, y el frontend avisa de la diferencia. `manage.py
    conciliar_mm [--anio N] [--ejecutar] [--csv ruta]` (grano año/semana/organización, modelo
    `ConciliacionMaterna`): **567 filas con la BD corregida (1+2)**, 88 CUADRA / 31 DIFERENCIA /
    406 solo en el registro / **42 solo en el certificado** — ninguna de las dos fuentes es completa.
    (Las cifras 460/33/36/382/9 de la versión anterior eran del estado previo a `corregir_mm_legacy`,
    cuando el certificado solo marcaba el código 1 = 89.) El indicador es el del registro.
  - MN = defunción de 0 a 27 días de vida, con fecha de nacimiento conocida. **MN no se toca:** ya
    cuadraba (213 = 213 en 2026 con `conciliar_neonatal`).
  - `manage.py corregir_mm_legacy` sigue existiendo para el campo del certificado.
- `conciliacion`: **auditoría SIS-04/EPI-12 crudo legacy vs SISV** (28/09/2026). App propia, no
  altera `vigilancia`. Modelos `ConciliacionENO` (año, semana, tipo, organización, enfermedad legacy,
  crudo/SISV/diferencia, `estado`, `resolucion`) y `ConciliacionENOCentro` (detalle por establecimiento
  legacy + `legado_documento` + `transcrito_por`). Comando `manage.py conciliar_eno --desde 2009
  [--anio N] [--ejecutar] [--csv ruta] [--todo-pais] [--limite N]`.
  - **Resultado del histórico completo 2009–2026: `diferencia = 0` en los 18 años.** 530.827 filas,
    615.135 detalles, 8.740.569 casos de enfermedad en 270 organizaciones, todos cuadrados contra el
    crudo. El ETL **`importar_legacy_vigilancia` es fiel**: no hay pérdida de datos que corregir.
  - Lo que sí queda fuera, y **por diseño** (no son pérdidas): 31.534 filas **pseudo-TOTAL**
    (33.375.675 casos) que el ETL nunca exportó; y 16.658 filas de **34 enfermedades sin
    equivalente ENO** (603.625 casos, legacy 1126717818 «TOTAL DE PACIENTES ATENDIDOS» y
    1126717832 «TOTAL DE PACIENTES HOSPITALIZADOS»). En 2026 el 98% de lo no conciliado es
    código 041 «SÍNDROME VIRAL (B34)».
  - **Pseudo-TOTAL ≠ enfermedad.** `es_pseudo_total()` detecta nombres que empiezan por TOTAL;
    `1126717832` SÍ tiene equivalente (`ENO_total_pacientes_hospitalizados_por_todas`) y se
    conserva, `1126717818` no y se excluye. Confundir ambos explica cifras absurdas.
  - 16.748 filas / 1.824.303 casos cuadran contra el fallback `LEGACY-LARA` («Legacy regional
    (histórico)»): 263 establecimientos legacy sin organización propia. **Cifra correcta, centro
    perdido**; el detalle por centro los conserva con `colision=si`.
  - **Atribución de transcripción:** `HISTDOC.INSTANCIA` es la **estación de trabajo**, no una
    cuenta verificada (`USUARIO` está vacío en las 58.596 filas). Solo registra `EVENTO='Creado'`
    y arranca el **05/08/2019**: hay atribución completa desde 2020, parcial en 2019 y **ninguna
    antes**. Antes de 2019-08 el campo queda vacío a propósito, no inventado.
  - El `--csv` respeta `--anio`/`--desde` y escribe además `<ruta>_centros.csv` con el detalle y la
    estación (hay prueba que lo fija: un CSV de 2026 no puede traer filas de 2009).
  - **Conciliación neonatal (fase C, `manage.py conciliar_neonatal`, 28/09/2026):** modelo
    `conciliacion.ConciliacionNeonatal` (migración `0003`), grano **(año, semana, organización)**.
    Lado legacy = `sismai."CASOS_MMI"` (registro materno-infantil, 10.754 casos 2009-2026): los
    neonatos son edad en **horas** (≤648) o en **días ≤27**, y el centro sale de
    `HDOCUMENTO` → `DOCUMENTO.HORIGEN` → nombre normalizado. Lado SISV = `registros.Defuncion` con
    fecha de nacimiento conocida y 0-27 días. Dry-run por defecto, `--csv` con BOM, 9 pruebas.
    - ⚠ **`DOCUMENTO."PERIODO"` NO es una semana**: es un número de formulario del centro y sus
      rangos se solapan (en 2019 el periodo 29 va del 2 de enero al 12 de septiembre; 20.446 pares
      solapados). La semana se calcula **en cada lado desde la fecha real** con
      `vigilancia.services.semana_epidemiologica`.
    - ⚠ **`DOCUMENTO."TIPO"` = 23** en los 10.754 documentos MMI, no 1 (1 = ENO de mortalidad,
      `RENGLONTELE`). Filtrar por 1 deja el legacy vacío en silencio.
    - **Resultado:** los dos sistemas coinciden casi exacto en 2023-2026 (2023 +2 %, 2024 +1 %,
      2025 -1 %, 2026 +7 %): valida la definición de 0-27 días del tablero y el importador.
      2009-2018 sale -10 % a -30 % (el formulario MMI se rellenaba menos que el certificado). Solo
      2019-2020 se invierte (+53 % y +1464 %) por la caída de captura (§20).
    - El lado SISV solo cuenta defunciones **con fecha de nacimiento**: es un mínimo.
    - **No concilia MM** (eso es `conciliar_mm`, 29/09/2026): `CASOS_MMI` mezcla materna, infantil y
      otras sin marcarlas, y usa `HSEXO` con la convención **inversa** a `RENGLONTELE` (aquí 2 = F,
      allá 2 = M).
  - **Conciliación materna (`manage.py conciliar_mm`, 29/09/2026):** modelo
    `conciliacion.ConciliacionMaterna` (migración `0004`), grano **(año, semana, organización)**.
    Lado legacy = `sismai."RENGLON_CASOSMM"` enlazado a `CASOS_MMI` por `HCASOSMMI`
    (748 de 749 enlazan; `count(DISTINCT "HCASOSMMI")` porque el grano es (persona, causa)).
    Lado SISV = `registros.Defuncion` con `embarazo_o_puerperio`. Dry-run por defecto, `--csv` con
    BOM, 8 pruebas. **Aquí los dos lados no son la misma definición y la diferencia es el
    resultado:** el certificado marca el embarazo en el 11,9 % de las muertes del registro.
    - **Resultado 2009-2026:** 748 del registro contra **191 certificados** (post-`corregir_mm_legacy`,
      1+2; con solo el código 1 eran 89); 88 CUADRA / 31 DIFERENCIA /
      406 solo en el registro / **42 solo en el certificado** (entre ellas una violenta, 2012).
      Ninguna fuente es completa; el indicador es el del registro.
    - Los certificados **sin organización no se filtran**: van al agregado. Filtrarlos por
      `organizacion_id IS NOT NULL` los borraría en silencio y daría un falso "el certificado no
      registró ninguna muerte materna".
    - `DOCUMENTO."TIPO"` = 23 aquí también, por el mismo motivo que en la conciliación neonatal.

- `despacho`: **control de entrega de talonarios de certificados de nacimiento y defunción** (01/10/2026).
  El legacy **no guardó nunca el despacho** (`sismai.NUMERO_BD` y `sismai.HISTORICO_IDS` están vacías), así
  que se captura desde cero. Modelos: `Talonario` (tipo NACIMIENTO|DEFUNCION, centro, fecha_entrega,
  serie_desde/serie_hasta, `cantidad` calculada, responsables, observaciones) y `NovedadCertificado`
  (excepción por certificado: DANADO|EN_TRANSITO|DEVUELTO con justificación y datos del tránsito; unique por
  talonario+numero). El **uso** se deduce cruzando el **sufijo numérico** de `registro_numero`
  (`DEF-2026-000003`→3) contra la serie, dentro del subárbol del centro
  (`organizaciones_descendientes`); un `registro_numero` sin dígitos finales se ignora. `faltante` =
  rango − usados − dañados − devueltos − en tránsito. Endpoints `/api/despacho/`: `talonarios/` (GET/POST),
  `talonarios/<id>/` (GET/PATCH/DELETE), `talonarios/<id>/certificados/` (por certificado + resumen),
  `novedades/` y `novedades/<id>/`, `reportes/certificados/` (nº, nombres, apellidos, fecha, centro; CSV) y
  `reportes/pendientes/` (entregados no retornados/justificados; CSV), respetando `alcance_registros`.
  **Rol nuevo `JEFE_UNIDAD` («Jefe de Unidad»)** en `seguridad.Perfil` y permiso `puede_despachar` en
  `permisos_de` (superusuario / JEFE_UNIDAD / DIRECTOR) para crear/editar/eliminar; leer y reportes, cualquier
  autenticado. Frontend `/despacho` (`Despacho.jsx`). **Nota:** el reporte 1 de nacimientos usa el nombre
  del **recién nacido** (`nino_nombres`/`nino_apellidos`, rotulado `persona: "Recién nacido"`) y cae al de
  la **madre** (`persona: "Madre"`) cuando el registro no lo trae (importados antes del EV-25 sin backfill);
  el CSV lleva columna **Persona**. Pruebas: `despacho/tests.py` (18). El certificado de nacimiento ya
  se amplió al EV-25 (§23.3).

- `registradores`: **control de registradores civiles con historial de vigencias** (02/10/2026, §24.2).
  App propia porque el dominio (quién firma) no es el de los talonarios. Modelos: `RegistroCivil`
  (oficina, `organizacion` opcional, `activo`), `RegistradorCivil` (persona: nacionalidad V/E/P/I/O,
  cédula, nombres, contacto; **no** es `auth.User`; único por `(nacionalidad, cedula)`) y
  `DesignacionRegistrador` (vigencia: registro civil + registrador, cargo TITULAR|SUPLENTE|ENCARGADO,
  `desde`, `hasta` nulo = vigente, toma de posesión, acta). **«¿Quién firmaba?» retroactivo**:
  `services.py::vigentes_en(registro_civil, fecha)`, endpoint
  `GET /api/registradores/quien-firmaba/?registro_civil=&fecha=`. **El solape se permite** (titular y
  suplente a la vez), por eso la consulta devuelve todos los vigentes. Endpoints `/api/registradores/`:
  `registros-civiles/` y `/<id>/`, `registradores/` y `/<id>/`, `designaciones/` y `/<id>/` (filtros
  `registro_civil`, `registrador`, `cargo`, `vigente=1`). Escribe quien `puede_despachar`; leer, cualquier
  autenticado; alcance igual al despacho. **Borrado protegido** (`PROTECT` → 400) con designaciones.
  Frontend `/registradores` (`Registradores.jsx`). Pruebas `registradores/tests.py` (22). **Catálogo
  sembrado del legacy** con `manage.py sembrar_registradores_legacy [--ejecutar] [--limite N]` (dry-run,
  idempotente): lee `sismai.CERTIFICADO.NOMREGISTRADOR`/`CIREGISTRADOR`/`NACREGISTRADOR` (167.447 filas,
  12.713 variantes), agrupa por `(nacionalidad, cédula)`, elige el nombre más frecuente y ejecutado creó
  **3.857 registradores** (3.845 V + 12 E; 11.184 sin cédula descartados). **No** crea registros civiles
  ni designaciones (el legacy no los modela); la división nombres/apellidos es heurística (asume apellidos
  primero) y `apellidos` quedó opcional (migración `0002`).

- `legacy`: **mapa de modelos del legado SISMAI** (no altera el flujo). App con `models_legacy.py`
  **generado** (modelos `managed=False`, solo lectura) para las **430 tablas/vistas** de
  `sismai`/`inbdlar1`/`legacy`/`historico`, y el inventario priorizado
  `legancy/analisis/PRIORIDADES_LEGACY.md` (P1 dominio=32, P2 operativo=185, P3=213). Regenerar con
  `manage.py mapear_legacy`; pruebas `legacy/tests.py` (correr con `DJANGO_DB_ENGINE=sqlite`). Detalle
  en PENDIENTES.md §8. Modelos de ejemplo: `legacy.models_legacy.Establecimiento` (centros, fuente de
  `seguridad.Organizacion`), `Usuarios` (ESTATUS: 2=activo, 1=deshabilitado), `OrgGeografica`, `CasosMmi`.
- Datos de demostración: sembrar con `./.venv/bin/python backend/manage.py sembrar_demo [--borrar]`
  (crea/fija de forma idempotente las **organizaciones y usuarios demo** documentados arriba, carga
  `mock_data.py` y asigna la org demo LARA-HCB con su estado/municipio; usar `--sin-usuarios` para
  omitir usuarios/org). Los endpoints que antes eran simulados en memoria ahora consultan la BD real.
- **Servidor SISMAI en producción (`192.168.5.200`, Oracle 10.1.0.3.0, SID `lar1`, base `bdlar1`) —
  diagnóstico 25/09/2026, detalle en PENDIENTES.md §17. NO modificar sin autorización expresa:**
  - Acceso de solo lectura: `ssh respaldo@192.168.5.200` + `export ORACLE_HOME=/opt/oracle
    ORACLE_SID=lar1` + `sqlplus -s respaldo/respaldo` (sin alias TNS: `@lar1` da `ORA-12154`).
    La **única** cuenta con DBA es la de SO **`oracle`** (grupo `dba`) vía `sqlplus / as sysdba`,
    pero **no tiene clave conocida** (por llave pública da *Permission denied*): todo lo del
    02/10/2026 se hizo con `respaldo`, que también sirve para `exp`/`imp` (`USERID=respaldo/respaldo`).
    **`legancy_conf/credenciales.env`** (ignorado por git) tiene host, usuarios y `NLS_LANG`; los
    scripts de `migracion/` lo leen solos. Ojo: **`NLS_LANG` sin definir hace fallar `sqlplus`** con
    *Error 6 initializing SQL* / *sp1\<lang\>.msb not found*, que parece de permisos y no lo es
    (la base es `WE8ISO8859P1`, hay que forzar `AL32UTF8`).
    `respaldo` lee 443 de las 525 tablas (SISMAI 350 / INBDLAR1 83 / HISTORICO 10) y **no ve TEMP**.
  - **Conexión a `sqlplus` en ese servidor: solo funciona Easy Connect con el SERVICIO `bdlar1`**:
    `sqlplus -s respaldo/respaldo@//localhost:1521/bdlar1`. Las otras tres fallan (02/10):
    usuario/clave a secas → `ORA-12162`; `@lar1` → `ORA-12154` (no hay alias TNS);
    `@//host:1521/lar1` → `ORA-12514`, porque **`lar1` es el SID y el servicio se llama `bdlar1`**
    (sale del `SID_LIST_LISTENER` de `/opt/oracle/network/admin/listener.ora`; el listener escucha
    en 1521 y `lar1` está READY). Los scripts de `migracion/` ya usan esa cadena.
  - **El colapso de captura 2019-2021 es real en el origen (02/10/2026, §22.8):** defunciones
    ~1.000/mes → 11-95 entre 2019-06 y 2020-12; nacimientos ~2.800/mes → 5-398 entre 2019-09 y
    2021-12 **y sin recuperarse**. PostgreSQL cuadra mes a mes con el Oracle: **no hay nada que
    reextraer**, el importador es fiel.
  - **Cliente Windows `192.168.5.133`** (verificado 02/10/2026, PENDIENTES.md §22.7): tiene el
    cliente Oracle y Centuria, y **ejecuta `SistemaTransferencia.exe`**, que vive en el share del
    servidor (`/home/salud/Aplicaciones/SISMAI/`). Desde el equipo de desarrollo responde SMB
    139/445 y RPC 135; **RDP 3389 cerrado**. Es el que produce el quinto archivo del sobre
    (`repllar1*.log`), y por eso **no hay ningún cron en el Linux que lo genere**.
  - **Respaldo verificado (02/10/2026, §23):** `migracion/respaldo_total.sh` produjo los 4 `.dmp`
    (SISMAI 1.023 MB / HISTORICO 91 MB / INBDLAR1 2,9 MB / TEMP 16 KB) con `imp SHOW=Y FROMUSER=`
    confirmando que se leen. El parfile lleva `OWNER=` **sin** `FULL=Y` (son excluyentes:
    `EXP-00026`), y la espera del export se hace por la **línea de fin del log**, no por PID
    (`exp` fork-ea y `kill -0` miente).
  - **`SISMAI.EVENTOS_SINC` fue DROP+recreada el 21/09 09:08:37** (`SincFich/crear.sql`) y tiene
    **16.741 filas**; el backlog de 3,37 M **ya no existe en la cola viva** (solo en los ZIP del
    21/09, que confirman que lo capturaron pero no prueban su recepción central). PostgreSQL no lo tiene
    (`sismai."EVENTOS"`=0, `legacy."T_EVENTOS"`=7.802). En PG el esquema es legacy con mayúsculas:
    **siempre comillas dobles** (`legacy."T_EVENTOS"`).
  - `EVENTOS_SINC` **no tiene restricciones ni índices** → sin clave `(TABLA,ID)` cualquier
    reejecución duplica en silencio.
  - Natalidad: falta el **encolado**, no el exportador (`cr_repli_nata.sql` solo arma `TEMP.*` desde
    eventos ya encolados). Los `pl*` originales son defectuosos (sin dedup, `V_I` sin inicializar);
    usar `migracion/encolar_natalidad_legacy.sql` (1.295.152 eventos, ~45 min, modo seguro por
    defecto, **nunca** junto a `crear.sql`).
  - Respaldo verificado de la sincronización (10 archivos, 10/10 SHA-256) en
    `/home/informatica/Documentos/puente/sincronizado/respaldo_20260925/`. **No es dump completo**
    de la BD. Copias nuevas al share: `smbclient -N //127.0.0.1/CompartidoInformatica` (escribir
    directo como `program` en `/home/informatica/...` está denegado).
  - ⚠ **Seguridad:** `SISMAI` y `TEMP` tienen el **rol `DBA`** siendo cuentas de aplicación, y
    `System.cfg` tiene la clave en texto plano con permisos `-rw-r--r--`. El `REVOKE` y la rotación
    de claves están **pendientes de autorización del usuario** (no ejecutados).

### Scripts de migración (migracion/)

- `verificar_env_oracle.sh` (correr como usuario `oracle`): comprueba `ORACLE_HOME`, `ORACLE_SID`,
  `NLS_LANG` y `sqlplus`.
- `extraer_estructura.sql`: `DBMS_METADATA.GET_DDL` + inventario de tablas, columnas (tipos para el
  mapeo NUMBER→INT/DECIMAL, VARCHAR2→VARCHAR, DATE→DATETIME), PK/FK y secuencias.
- `extraer_datos_csv.sh`: exporta cada tabla a CSV (separador `;`). Validar encoding
  (WE8MSWIN1252 vs AL32UTF8) antes de importar a PostgreSQL.

### Recuperación del hueco MM/MN (ventana del martes 29/09/2026)

La captura se cortó el 02/08/2026; el centro siguió generando los sobres semanales, así que los
datos **existen en el sistema del centro** y no llegaron a PostgreSQL. Recuperarlos es un proceso
de tres pasos, y el orden importa: no se carga antes de extraer, ni se concilia antes de cargar.

| Paso | Qué | Cómo |
| --- | --- | --- |
| 0 | Pre-vuelo | `migracion/preflight_ventana.sh` |
| 1 | Bajar del Oracle 10g | `migracion/extraer_mm_mn_roto.sh` + `.sql` |
| 2 | Cargar en PostgreSQL | `manage.py cargar_mm_mn_roto` |
| 3 | Conciliar | `/reportes` + acta en `auditoria/` (ignorada por git) |

- **`migracion/preflight_ventana.sh`** — corre en la máquina de trabajo, sin red: comprueba que no
  haya un `exp`/`expdp` corriendo (leer la base a medio respaldar es el error clásico), que exista
  un dump de hoy posterior a las 13:00, que el `routlar1_*.ZIP` más reciente traiga sus 5 archivos,
  y calcula el `DESDE` recomendado desde lo último cargado. Sale con código 1 si hay fallos.
  Variables: `DIR_RESPALDO`, `DIR_SOBRES`, `HORA_RESPALDO`, `SOLAPES`, `DESDE`, `RESPALDO=0`.
- **`migracion/extraer_mm_mn_roto.sh`** — **solo lectura** (`SELECT` + `SPOOL`); no toca
  `SISMAI.EVENTOS_SINC` ni la cola. Escribe 12 CSV con `;` en `salida_mm_mn_<fecha>/`:
  `muerte`, `causa_m`, `nacimiento`, `nacimiento_tardio`, `nac_madre`, `nac_rnacido`, `casosmmi`,
  `renglon_casosmm`, `renglon_casosmi`, `establecimiento`, `cie10_legacy`, `org_geografica`.
  - El encabezado de cada CSV lo pone el propio SQL (`SELECT 'ID;FECHA_M;...' FROM DUAL`), así que
    el orden de columnas no está escrito a mano en el cargador: se lee por nombre y, si falta una
    columna, aborta diciendo cuál.
  - Modo local (en el servidor, `/ as sysdba`) o remoto (`HOST=192.168.5.200`, sube el SQL, ejecuta
    allá y trae los CSV por `tar`; necesita `sshpass` o `expect`). `DESDE=01/08/2026` por defecto
    (inicio del hueco), `SIMULAR=1` para ver qué haría sin ejecutar.
  - `WHENEVER SQLERROR EXIT`: si una consulta falla, el script borra los CSV parciales en vez de
    dejar un archivo truncado que el manifiesto daría por bueno.
  - **El manifiesto cuenta líneas físicas, así que cada total incluye su fila de encabezado.**
- **`manage.py cargar_mm_mn_roto --directorio <dir> [--ejecutar] [--limite N]`** — mete los CSV en
  `registros`. Sin `--ejecutar` solo informa (dry-run).
  - **Idempotente** por `registro_numero` (`LEG-CERT-{id}` / `LEG-RN-{id}`): se puede correr las
    veces que haga falta, no duplica.
  - **No pisa trabajo humano:** el CIE-10/CIE-11 revisado y `codificacion_pendiente=False` se
    conservan, y **un valor vacío nunca borra uno que ya había** (si `CAUSA_M` viene vacío, no
    borra la causa que alguien ya cargó a mano).
  - La organización se resuelve **por nombre de establecimiento** dentro del árbol Lara
    (raíces 67754 / 3441583108), igual que `asignar_organizacion_legacy`. Si el catálogo no trae
    las raíces **aborta**: adivinar crearía organizaciones de todo el país bajo Lara.
    Las que falten se crean con código `LEGCSV-nnnn` (para no chocar con la serie `LEG-CENTRO-001`
    que siembra `asignar_organizacion_legacy`).
  - `--limite` aplica a los **datos**, nunca a los catálogos: truncar el catálogo de establecimientos
    daría una resolución de organizaciones falsa.
  - **No se cargan** `nacimiento_tardio`, `casosmmi`, `renglon_casosmm` ni `renglon_casosmi`: no
    hay modelo en `registros`, quedan como evidencia para el acta.
  - El **MN del tablero y del acta sale de `Defuncion`** (0–27 días entre `FECHA_M` y `FECHA_N`),
    **no** de `renglon_casosmi`. Las cifras de la oficina pueden no ser comparables.

**Definiciones que hay que respetar al conciliar:**

- **MM**: `CERTIFICADO.HPRESENCIAEMBARAZO IN (1, 2)`. El 1 = al momento de la muerte, el 2 = últimos
  12 meses. **No** es un rango de fechas ni un código de causa.
- **MN**: defunción de 0 a 27 días de vida (inclusive). A los 28 días ya no es neonatal.
- `CERTIFICADO.STATUS` es **0/1, nunca `NULL`**: filtrar por `STATUS IS NULL` no devuelve nada.
- El filtro de nacimientos es por `NAC_RNACIDO.FECHANACIMIENTO`, **no** por
  `CERTNACIMIENTO.FECHACERTIFICADO` (los certificados tardíos van aparte y aboundan: 1.499 desde
  agosto frente a 23 con nacimiento en el periodo).
- **Año epidemiológico** domingo–sábado: 2025 tiene **53** semanas y 2026 **52**; el filtro por año
  es un rango de fechas, no `fecha_evento__year` (`registros/views.py::_filtro_anio`).
  `exportar_rutalara --semana` acepta `AAAA-N`.
- El central usa sus propias semanas epidemiológicas; el número de semana **no coincide** con el ISO.

**Aviso de datos incompletos:** el tablero muestra un banner cuando la serie tiene un hueco
(`registros/views.py::DashboardView._cobertura` → `cobertura.meses_sin_datos` y `cobertura.atraso_dias`).
El mes en curso nunca se marca: a mitad de mes siempre está a medias y avisar sería mentir.
⚠ **`meses_sin_datos` es código muerto en la práctica**: entre 2009-01 y 2026-08 no hay ni un mes
con cero filas en nacimientos, defunciones ni fichas, así que solo se dispara por el otro lado. El
banner también avisa por `atraso_dias` (días sin registrar). **Desde el 02/10/2026 (§20.2) detecta
además meses *degradados*:** `_meses_degradados` marca un mes terminado si queda por debajo de
`factor_mes_degradado` (0,40) × la mediana de los últimos `min_meses_historia` (12) meses
*normales*, anclando la base al último nivel sano (una mediana móvil corriente se arrastraría con
la caída). Exige 12 meses normales, ignora el mes en curso, se puede desactivar y solo reporta el
año que se mira (mirando 2026 no avisa de la caída 2019-2021). Los 3 parámetros viven en
`ConfiguracionGeneral` (`/api/registros/configuracion/`). El banner lo muestra en
`cobertura.meses_degradados` (`AvisoCobertura`). Para saber si esos certificados existen en el
origen Oracle está `migracion/diagnostico_hueco_2019_2021.sh` (solo lectura, conteo mensual 2018-2022).

## Migración Oracle 10g → PostgreSQL (crítico)

- `oracledb` en modo **Thin falla** por protocolos de cifrado obsoletos. Priorizar herramientas nativas de consola: `sqlplus`/`exp`. Usar modo Thick con Instant Client antiguo solo si es estrictamente necesario.
- No usar sintaxis moderna de openSUSE/SLES: 11.4 usa repositorios obsoletos y comandos tradicionales.
- Al conectar: verificar `ORACLE_HOME` y `ORACLE_SID` antes de invocar `sqlplus`.
- Plan de extracción: DDL con `DBMS_METADATA.GET_DDL` primero (estructura sin datos), luego datos en CSV/SQL estándar.
- Cuidar encodings al exportar: probablemente `WE8MSWIN1252` o `AL32UTF8`.
- Mapeo de tipos: `NUMBER`→`INTEGER`/`DECIMAL`, `VARCHAR2`→`VARCHAR`, `DATE`→`TIMESTAMP`/`DATE`.
- No hay código fuente del sistema antiguo; todo se deduce de la BD.

## Arquitectura requerida de catálogos clínicos (CIE-10 / CIE-11)

El sistema heredado solo soportaba CIE-10 (4 dígitos). Intentaron registrar CIE-11 pero rompió integridad. El nuevo sistema debe:

- Modelo `CIE10`: estructura alfanumérica tradicional de 4 dígitos.
- Modelo `CIE11`: jerarquía self-referential (ForeignKey a sí mismo) para capítulos → bloques → categorías → subgrupos.
- Modelo de cross-walking: tabla de equivalencias CIE-10 ↔ CIE-11 (y viceversa) para reportes históricos unificados.
- Tablas de hechos (Defunciones, Fichas de Vigilancia): selección dinámica del catálogo según fecha del evento o bandera de versión (CIE-10 para el pasado, CIE-11 para el presente). La data histórica CIE-10 debe preservarse intacta según el año del registro.
- Frontend: smart search/autocomplete por texto o código, árbol/cascada de subgrupos CIE-11, y validación en tiempo real de subgrupos obligatorios antes de enviar a la API.

## Fuente oficial de catálogos (OMS/WHO) — CIE-11 y CIE-10 cargados

- CIE-10: **cargado en español** (13/09/2026). La fuente oficial OMS (CDN `icdcdn.who.int`, formato
  «Plain text tabular», zip `backend/catalogos/data/icd10_2019_meta.zip`) **solo publica inglés** (los
  `…es…`/`spa` devuelven 404) y ya **no ofrece `DBCIE.db`**. La traducción española oficial (OPS/OMS, Vol. 1)
  no existe en formato machine-readable; se usó el dataset jerarquizado español de `verasativa/CIE-10`
  (scrape de la página oficial OMS `icd.who.int/browse10/2019/es` + catálogo Chile MINSAL/DEIS), guardado en
  `backend/catalogos/data/cie10_es_oms_icdcodeinfo.csv`: **14.208 códigos** (21 capítulos, 2.034 de 3 dígitos +
  12.174 de 4 dígitos), normalizados a formato OMS con punto (`A000`→`A00.0`). Cobertura 12.026/12.221 del
  catálogo OMS 2019 (98,4%; faltan subcategorías nuevas como `A09.0/A09.9`, `A97`, `B18.00` — no estaban en el
  scrape; el capítulo 22 U00-U99 queda fuera). Comandos: `manage.py importar_cie --cie10-es <csv>` (español),
  `manage.py importar_cie --cie10-oms <zip|dir>` (inglés OMS plain text; [0]=nivel, [5]=código, [7]=sin punto,
  [8]=título), `manage.py importar_cie --cie10 <DBCIE.db>` (sqlite).
- CIE-11: **cargado desde el contenedor `servicio-cie11`** (imagen oficial `whoicd/icd-api`, release `2026-01`,
  idioma `es`, levantado en `localhost:8080`). 37.211 registros en `catalogos_cie11` (28 capítulos, 1.360 bloques,
  19.884 categorías, 15.939 subgrupos). Comando: `manage.py importar_cie11_oms` (recorre la API local; requiere el
  contenedor activo; los nodos de agrupación sin código clínico usan el ID interno de WHO).
  **Nota ICD-API local:** las URLs devueltas apuntan a `http://id.who.int` (redirigirían al exterior); el comando
  las reescribe a `localhost:8080`, y la API exige headers `API-Version: v2`, `Accept-Language: es` y `Accept: */*`
  (sin `Accept` devuelve 412).
- CIE-10 ↔ CIE-11 (cross-walk): **importado** (13/09/2026), `catalogos_mapeocie` con **11.879 equivalencias**
  (5.008 EXA / 773 PAR / 6.098 INE) desde el **`mapping.zip` oficial de la OMS** (release 2025-01,
  `icdcdn.who.int/static/releasefiles/2025-01/mapping.zip`). Comando: `manage.py importar_mapeos <zip> --solo-categorias`.
  Los tipos se derivan por round-trip: EXA si `c10→c11` y `c11→c10` coinciden, PAR si hay postcoordinación `&…` o
  destinos múltiples, INE en el resto. Endpoint `/api/catalogos/mapeos/?cie10=<codigo>`.

## Convenciones y estado

- Repositorio **git iniciado** (19/09/2026): remoto `git@github.com:RVenegas7/sisv.git`, rama `main`
  (origin configurado). La llave SSH es `~/.ssh/oficina` (misma que entra al servidor de la oficina;
  está en el agente, y **no** existe `~/.ssh/sisv_github`). `git push origin main` basta.
  Antes de commitear revisar `.gitignore` (dumps legacy, `legancy_conf/*.env`, `salida_mm_mn_*/`,
  `lara_2019_2020.xlsx`, etc.).
- Código base Django/React ya creado: backend con serializers + vistas de datos reales y frontend con los
  formularios de carga de Nacimientos, Defunciones y Fichas de Vigilancia, más el buscador CIE
  reutilizable (smart search + árbol/cascada). Los reportes (`/reportes`) y el módulo de vigilancia
  (`/vigilancia`) están implementados.
- Componentes frontend clave: `CIESearch` (autocomplete + cascada CIE-11 + subgrupos obligatorios),
  `SeccionCIE` (selector de versión por fecha + buscador), `src/utils/cie.js` (`validarCIE`).
- Extracción del servidor heredado se ejecuta como usuario `oracle` en openSUSE.
- **Pruebas automatizadas (24/09/2026):** backend con `DJANGO_DB_ENGINE=sqlite manage.py test`
  (**correr desde `backend/`** — desde la raíz descubre 0 tests),
  (**227 pruebas a 06/10/2026** (verificado): 115 de `backend/tests_sisv.py` + 18 de `backend/despacho/tests.py`
  + 22 de `backend/registradores/tests.py`
  + 33 de `conciliacion` (16 ENO +
  9 neonatal + 8 materna) + 27 de `registros/tests.py` (2 EV-14, 7 de las secciones del
  certificado EV-14, 6 del EV-25, 7 del reporte semanal MM/MN y 5 de meses degradados) + 6 de `registros/tests_recuperar_establecimiento.py`
  + 6 de `registros/tests_completar_nacimiento.py`; requiere
  `__init__.py` en las
  apps — registros, seguridad, territorio y catalogos eran namespace packages y por eso el
  descubrimiento fallaba);
  frontend con `npm test` (Vitest, 13 pruebas en `src/utils/cie.test.js` y `src/api/sisv.test.js`).
  Verificación manual: `manage.py check` y `npm run build`.
- **Seguridad (23/09/2026):** la API exige sesión por defecto (`IsAuthenticated` global; públicos solo
  `/api/auth/login|logout|me|csrf` y `/api/`). Rate limiting del login en `seguridad/throttle.py`
  (5 intentos/5 min → 429 con bloqueo 15 min). Dependencias auditadas sin vulnerabilidades
  (pip-audit + npm audit). Detalle en PENDIENTES.md §9 y §12.