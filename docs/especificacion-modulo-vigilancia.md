# Especificación funcional — Módulo de Vigilancia Epidemiológica (SISV)

- **Fecha:** 12/09/2026
- **Estado:** **VALIDADO** por el guardián del dominio (12/09/2026). Autorizado a pasar a implementación backend + catálogo ENO + frontend.
- **Fuente normativa de referencia:** OMS/RSPI y MPPS (documentos originales guardados en `docs/normativa/`).

## 1. Base normativa

### 1.1 Internacional
- **Reglamento Sanitario Internacional (RSPI) 2005:** marco para la notificación inmediata de eventos agudos y de potencial emergencia de salud pública internacional (PHEIC). Define capacidades básicas (core capacities) de detección y notificación en el nivel local.
- **OMS / Clasificaciones CIE:** los eventos se identifican con **CIE-10** (histórico) y **CIE-11** (vigente). Coincide con el modelo `RegistroConCIE` ya implementado (versión por fecha).
- **Definiciones de caso de OMS/PAHO** por evento (dengue, sarampión, etc.): etiquetan la clasificación (sospechoso/probable/confirmado/descartado) de la notificación individual.

### 1.2 Venezuela (MPPS – Dirección General de Epidemiología)
- Constitución (art. 83) y **Ley Orgánica de Salud** (G.O. 36.579, 11/11/1998): la salud es derecho fundamental y la vigilancia epidemiológica es competencia del MPPS.
- **Sistema de Información Epidemiológico Nacional (SIE)** del MPPS: notificación de Enfermedades y Eventos de Notificación Obligatoria (**ENO**).
- Lista **ENO/eventos actualizada por el MPPS** (codificada en CIE-11): **114 ENO/eventos** según el propio formulario EPI-12 → se preservará la numeración oficial (orden 1..100 del formulario).
- **Formatos SIE oficiales** (descargados 12/09/2026 de mpps.gob.ve, PDF + texto en `docs/normativa/`):
  - **SIS-04 / EPI-12** — *Consolidado Semanal de Enfermedades y Eventos de Notificación Obligatoria — Morbilidad*.
  - **SIS-04 / EPI-14** — *Consolidado Semanal … — Mortalidad*.
  - Complementarios (mencionados en la página de formatos): SIS-02/EPI-10 y EPI-13 (registro de pacientes atendidos), SIS-03/EPI-11 (tabulador diario de morbilidad), EPI-04/EPI-15 (morbilidad registrada, SIS-2026).
  - **Manual de Normas SIVIGILA** (vigilancia de muerte materna, infantil y de 1-4 años, **SIS-05**): define la notificación **inmediata** (fichas individuales MM-1/MM-2, MI-1/MI-2) y la **semanal obligatoria** (EPI-14), con flujo local → municipal → regional → nacional y notificación negativa.

### 1.3 Conclusión normativa (3 subsistemas del módulo)
1. **Notificación individual** (fichas/registros de caso con CIE) → ya existe `FichaVigilancia`, necesita vincularse al catálogo ENO y a la semana epidemiológica.
2. **Consolidado semanal agregado** con eventos ENO por código, grupos de edad y sexo, con muertes → **NO existe**; es lo que muestra la captura (`Registro Semanal de SIS 04-EP`).
3. **Situaciones especiales / alertas / epidemias** (brotes, rumores, desastres, eventos químicos/radionucleares/alimentarios) → **NO existe**.

## 2. La captura de referencia (`capturas/Pantalla Vigilancia.jpg`)

`Registro Semanal de SIS 04-EP..` **= consolidado semanal SIS-04 (EPI-12/EPI-14)**. Elementos:

- **Cabecera:** Período reportado (año + semana), fecha, código del establecimiento, código CIE manual; tab Entidad/Municipio/Establecimiento (MPPS Lara).
- **Tabla principal:** `Código | Enfermedad | Edad | Casos (Hombre|Mujer) | Muertes`.
- **Nota del formulario (OCR):** *«Seleccione Edad "Ignorada" y coloque el valor en la columna "Casos Hombre" para ciertos eventos; (009) Etapa de brotes; Rumores de brotes»*. → **Regla de negocio obligatoria:** cuando la edad es desconocida, el conteo se anota en la columna **Hombres** (no hay columna «passthrough»), al menos para eventos de brotes/rumores. **Confirmado por el guardián del dominio (12/09/2026):** la «edad ignorada» ocurre cuando **no se logró captar la edad de la persona** (típico en muertes —catástrofes— o por fallas en la captura de la información); es la causa y por eso el conteo se registra en la columna Hombres del grupo «Edad ignorada».
- Diferencias entre EPI-12 y EPI-14 (del formulario oficial):
  - EPI-12 (morbilidad): ~99 filas, incluye filas «ETA Nº de Brotes», «Casos Asociados a Brotes», «Rumor de Epizootias», «Total Pacientes Atendidos», «Total Hospitalizados».
  - EPI-14 (mortalidad): filas de mortalidad por cada evento (todas con código CIE-11) + secciones materno-infantil; el Manual SIVIGILA indica anotar `*` al evento y adjuntar la ficha SIVIGILA MM-1/MI-1 para muertes maternas e <5 años.
- **Secciones inferiores (ambos formularios):**
  - *Situaciones Especiales:* tipo de evento (químico, radionuclear, en animales, desastre natural, alimentario, infeccioso, indeterminado), comunidad, casos, muertes, descripción.
  - *Situaciones de Alerta* y *Situaciones de Epidemia:* enfermedad, casos, muertes, marcadores (grave, inusitado, nacional), fecha de inicio/fin, unidad geográfica y unidad sanitaria.

## 3. Estado actual del sistema (brecha)

| Capacidad normativa | Estado hoy |
|---|---|
| Notificación individual con CIE (fecha) | Existe (`FichaVigilancia` + `SeccionCIE`) |
| Vínculo de la ficha al evento ENO oficial | No (usa `nombre_evento` libre) |
| Semana epidemiológica en registros | No |
| Consolidado semanal agregado (EPI-12/14) | No |
| Catálogo de eventos ENO (nº de orden + CIE-11) | No |
| Regla de «edad ignorada → columna Hombres» | No |
| Situaciones especiales / alertas / epidemias | No |
| Alcance multicentro (Lara/regional), permisos por rol | Sí (se reutiliza) |
| Reportes/exportación CSV | Existe (se amplía al nuevo módulo) |

## 4. Diseño propuesto

### 4.1 Catálogo `EventoENO` (app `vigilancia`)
Modelo con los campos:
- `orden_epi12` (int, nº del formulario EPI-12), `orden_epi14` (int, nul label), `codigo_evento` (str, ej. `ETA_BROTES`),
- `nombre` (str, texto exacto del formulario, ej. «ETA Nº de Brotes»),
- `codigos_cie11` (str, códigos oficiales separados; ej. `1D20-1D21-1D22` para Dengue), `codigos_cie10` (str, cuando exista mapeo),
- `en_epi12` / `en_epi14` (bool), `notificacion` (`INMEDIATA`/`SEMANAL`), `grupo` (transmisibles/IRA/IRS/ITS/creónicas/no transmisibles/materno infantil), `activo`.
- **Sembrado:** comando `cargar_eventos_eno` que carga la lista real extraída de los EPI-12/14 (`docs/normativa/EPI-12_texto.txt`, `EPI-14_texto.txt`): **114 ENO/eventos** = 101 filas del cuerpo del EPI-12 (órdenes 1-22, 25-54, 55-101; el orden salta 23-24, sin filas) + **13 del anexo «enfermedades micóticas»** (órdenes 102-114). El numerador oficial 1..114 se preserva tal cual.

### 4.2 `ConsolidadoSemanal` (cabecera)
- `organizacion` (FK `seguridad.Organizacion` — respeta alcance), `anio` (int), `semana` (int 1..53), `tipo` (`MORBILIDAD`/`MORTALIDAD`),
- `estado` (`BORRADOR`/`ENVIADO`/`CERRADO`), `creado_por`, `enviado_en`,
- **restricción única:** `(organizacion, anio, semana, tipo)` — un consolidado por semana por tipo y establecimiento.
- semana ISO derivada de `fecha_evento` (utilidad `semana_epidemiologica(date) → (anio, semana)`).

### 4.2.b Consolidación por nivel superior (decisión del guardián, 12/09/2026)

- El consolidado puede crearse en **cualquier nivel** de la jerarquía de organizaciones (CENTRO, municipio, REGIONAL). Respetará el alcance de `seguridad` (un centro solo ve/crea su propio consolidado; un regional ve y crea en su ámbito).
- Al crear un `ConsolidadoSemanal` en una organización **con organizaciones hijas** (municipio/regional), las filas se **precargan con la suma** de las filas de los consolidados de las organizaciones hijas para el mismo (anio, semana, tipo) que se encuentren en estado `ENVIADO`/`CERRADO`/`BORRADOR` (incluye a su vez la suma de sus propios hijos, recursivamente). El usuario puede **editar/ratificar** los valores antes de enviar.
- Campo `origen` (str): `PROPIO` para el consolidado tecleado del establecimiento, o `CONSOLIDADO_SUPERIOR` para el que se generó sumando hijos — informativo; ambos son editables al precargar.
- El proceso de consolidación **no borra ni modifica** los consolidados de los niveles inferiores (son fuentes que se suman).

### 4.3 `FilaConsolidado` (detalle, matriz 1:1 con el formulario)
- `consolidado` (FK), `evento` (FK `EventoENO`),
- conteos por **grupo × sexo**: 13 grupos (`<1`, `1-4`, `5-6`, `7-9`, `10-11`, `12-14`, `15-19`, `20-24`, `25-44`, `45-59`, `60-64`, `65+`, `edad_ignorada`) × 2 (`h`, `m`) → 26 columnas enteras (default 0),
- totales calculados (no persistidos) `total_hombres`, `total_mujeres`, `total`.

### 4.4 `SituacionEspecial` y `AlertaEpidemia`
- `SituacionEspecial`: `consolidado` FK, `tipo_evento` (químico/radionuclear/animal/desastre/alimentario/infeccioso/indeterminado), `comunidad`, `casos`, `muertes`, `descripcion`.
- `AlertaEpidemia`: `consolidado` FK, `clase` (`ALERTA`/`EPIDEMIA`), `evento` FK, `casos`, `muertes`, `grave` (bool), `inusitado` (bool), `impacto_nacional` (bool), `fecha_inicio`, `fecha_fin`, `unidad_geografica`, `unidad_sanitaria`.

### 4.5 Mejora mínima a `FichaVigilancia` (fase 2)
- `evento_eno` FK (opcional) y `semana` derivada. Sin cambios destructivos; se conserva `nombre_evento`.

## 5. Reglas de negocio

1. **CIE por fecha:** se hereda de `RegistroConCIE.clean` (CIE-10 histórico / CIE-11 actual según `fecha_corte_cie11`). El formulario EPI-12/14 actual usa CIE-11.
2. **Edad ignorada → columna Hombres** (regla del formulario; validar alcance con el guardián del dominio).
3. **Unicidad semanal** por (org, año, semana, tipo); la misma semana no se puede re-abrir una vez `CERRADO`.
4. **Notificación negativa:** el EPI-12/14 exige enviar el formulario aunque no haya casos (filas en 0). El sistema debe permitir marcar «enviado con 0 casos».
5. **Totales:** siempre recalcular del detalle; nunca editar a mano.
6. **Muertes <5 años y maternas:** remite al Manual SIVIGILA (ficha individual + `*` en EPI-14) — enlazar la fila EPI-14 con la ficha MM-1/MI-1 cuando exista en la BD.
7. **Alcance multicentro y permisos:** aplicar `seguridad/services.py::alcance_registros`/`permisos_de` igual que el resto de registros (transcriptor/coficadora/director editan; epidemiólogo lee).
8. **Consolidación por nivel superior:** el consolidado de un municipio/región se precarga con la suma de los consolidados de sus organizaciones hijas (misma semana/tipo) y es **editable/ratificable** antes del envío; nunca altera las fuentes. La restricción de unicidad semanal aplica también al consolidado superior.

## 6. API y frontend

- **Backend (app `vigilancia`):**
  - `GET/POST /api/vigilancia/consolidados/`, `GET/PUT/PATCH/DELETE /api/vigilancia/consolidados/<id>/`,
  - `GET /api/vigilancia/eventos-eno/?grupo=&en_epi12=` (catálogo),
  - sub-recursos de filas y situaciones; exportación CSV respetando alcance (patrón de `/reportes/exportar/`).
  - `manage.py cargar_eventos_eno` (catálogo) y extensión de `sembrar_demo` con un consolidado demo.
- **Frontend:** página `Vigilancia.jsx` reutilizando patrones (JSON: `CargaFichasVigilancia.jsx`):
  - selector año/semana/tipo + cabecera (entidad/municipio/establecimiento),
  - tabla matriz eventos × grupos × H/M con edición por celda, filas precargadas del catálogo ENO,
  - pestañas/secciones: Informe (matriz), Situaciones Especiales, Alertas/Epidemias (coinciden con la captura),
  - bloqueo por permisos (`fieldset disabled`) igual que las fichas.

## 7. Entregables de esta iteración

- [x] Normativa obtenida y archivada (EPI-12, EPI-14, Manual SIVIGILA → `docs/normativa/`).
- [x] Este documento (spec).
- [x] **Validación del guardián del dominio (12/09/2026):**
  - 1) **Grupos etarios exactos:** los 13 grupos propuestos coinciden literalmente con la cabecera de los formularios EPI-12 y EPI-14 (`<1`, `1-4`, `5-6`, `7-9`, `10-11`, `12-14`, `15-19`, `20-24`, `25-44`, `45-59`, `60-64`, `65+`, `Edad Ignorada`).
  - 2) **Regla «edad ignorada» → columna Hombres:** confirmada (nota oficial del formulario + confirmación del guardián).
  - 3) **Consolidación municipal/regional:** **decisión:** consolidado editable por nivel superior — el municipio/región precarga la suma de sus establecimientos y la ratifica/edita (ver §4.2.b y regla 8), conforme al flujo SIVIGILA local→municipal→regional→nacional.
- [ ] Implementación backend (app `vigilancia`) + comando catálogo ENO + frontend (`Vigilancia.jsx`) + consolidado demo en `sembrar_demo`.

## 8. Fuentes

- MPPS — Formatos SIE 2026 (mpps.gob.ve/formatos-sie/): SIS-04/EPI-12, SIS-04/EPI-14.
- MPPS — Manual de Normas SIVIGILA (2026), vigilancia muerte materna e infantil (SIS-05).
- Captura de referencia: `capturas/Pantalla Vigilancia.jpg` + `capturas/OCR_Pantalla_Vigilancia.txt`.
- Documentos descargados: `docs/normativa/`.