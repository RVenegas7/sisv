# CHECKPOINT 20/10/2026 — Simulación de envíos semanales (routlar1) desde SISV

> Punto de guarda. Objetivo: **probar que SISV reproduce el contrato del sobre de ruteo**
> (`routlar1_*.ZIP`) que la oficina envía al central, usando los dos sobres YA enviados
> (14/10 y 20/10/2026) como patrón de verdad.

## Estado: COMPLETADO — documentado en PENDIENTES.md §38 y AGENTS.md

La validación **pasó**: SISV reproduce el contrato del sobre (regla de selección, estructura de
columnas y contenido). Lo único que falta para cerrar del todo es **refrescar el espejo** (§32) y
comprobar que los **conteos** cuadran a cero.

## Resumen de lo que se hizo

| Eje | Resultado |
| --- | --- |
| **Regla de selección** (IDs viajeros) | **EQUIVALENTE**: 22/22 tablas event-driven, **0 diferencias de IDs** en ambos sobres. Viaja el estado consolidado de cada fila cuyo **último evento en la ventana es INSERT(1)/UPDATE(2)**; DELETE(3) no viaja. El `T_EVENTOS` del `.dmp` es el manifiesto exacto. |
| **Estructura de columnas** | **81/82 exactas** (nombre+orden). Solo falta `T_CERTNACI` (el sobre real no la trae, §34). |
| **Contenido campo a campo** | ENV14: 31 filas comparables; ENV20: 16 filas. En ambos **0 discrepancias de lógica** (42 y 20 diferencias de campo, respectivamente): frescura del espejo (filas tocadas tras el 02/10) o artefactos de formato (fechas `DATE` con/sin hora). |
| **Conteos por tabla** | DIF explicadas: espejo congelado al 02/10 vs ventanas 06/10→20/10. |

### Correcciones aplicadas a código/datos

- **`backend/registros/data/rutarala_spec.json`**: columnas que faltaban vs el sobre real
  (`T_CERTMORT` +`VALSEXO`,`VALCAUSABASICA`; `T_RCASOSMM` +`NUM_PARTOS`,`HIJOS_NACVIVOS`,
  `HIJOS_NACMUERTOS`,`HIJOS_NACABORTOS`; `T_SEGDIABE` +`EVALUACION2` y orden `USUARIO`/`FLUORO`).
- **`backend/registros/management/commands/exportar_rutalara.py`**: el parser de `--comparar`
  ahora entiende el log de `exp` en **español** además del inglés.
- Suite backend: **308 OK**; `manage.py check` sin problemas.

### Herramientas nuevas (reutilizables, en `migracion/simulacion/`)

- `preparar_entorno_validacion.sh <ZIP> <ESQUEMA>` — importa el `.dmp` del sobre real en un
  esquema `ENVxx` del Oracle local y deja `ids_/cols_/manifiesto_` en `/tmp/opencode/`.
- `validar_sobre.py <ENV14|ENV20>` — valida regla de selección + columnas.
- `extraer_contenido_iso.py <ENV>` / `comparar_contenido.py <ENV> <zip>` — contenido campo a campo.

## Pendiente único

Repetir la comparación **tras el refresco del espejo (§32/§37)**: ahí los conteos deben quedar en
**0 diferencias** y quedaría probada la sustitución completa del `exp` del legado.

## Entorno dejado

- Contenedor `sis_oracle_legacy` mencionado en el checkpoint anterior: **detenido** (los esquemas
  ENV14/ENV20 persisten en el volumen). Arrancar con `newgrp docker -c "docker start sis_oracle_legacy"`.
- Manifiestos en PostgreSQL: `simulacion.eventos_env14` (10.801) y `simulacion.eventos_env20` (8.446).
- `/tmp/opencode/` puede vaciarse al reiniciar; se regenera con `preparar_entorno_validacion.sh`.
