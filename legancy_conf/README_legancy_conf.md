# legancy_conf/ — Configuración del sistema legacy (SIS/LAR1)

Carpeta para **credenciales y configuración de conexión** al Oracle 10g del servidor
legacy (openSUSE 11.4, accesible por SSH con el usuario de sistema `oracle`).

> **IMPORTANTE:** aquí solo van **plantillas** versionables. Los archivos con datos
> reales se copian/renombran y **nunca** deben subirse al repositorio
> (ver `.gitignore` raíz: `legancy_conf/*.env` y `legancy_conf/tnsnames.ora`).

## Contenido

| Archivo | Propósito |
|---|---|
| `credenciales.env.ejemplo` | Plantilla de credenciales/variables. Copiar a `credenciales.env` y completar. |
| `tnsnames.ora.ejemplo` | Plantilla de descriptor TNS para registrar el servicio. Copiar a `tnsnames.ora` si el cliente Oracle lo requiere. |
| `conectar_legacy.sh` | Script de referencia: carga `credenciales.env` y prueba la conexión con `sqlplus`. |
| `README_legancy_conf.md` | Este documento. |

## Cómo usar

1. Copiar plantillas y rellenar los valores reales (IP/host, SID, credenciales):

   ```bash
   cp legancy_conf/credenciales.env.ejemplo legancy_conf/credenciales.env
   cp legancy_conf/tnsnames.ora.ejemplo legancy_conf/tnsnames.ora   # solo si hace falta
   ```

2. Acceso al servidor legacy y verificación de entorno:

   ```bash
   ssh oracle@<host>   # dentro del servidor
   # si no hay credenciales.env, usar sh/migracion/verificar_env_oracle.sh
   ```

   Los scripts `migracion/` (`extraer_estructura.sql`, `extraer_datos_csv.sh`) están pensados
   para ejecutarse **dentro del servidor**, como usuario `oracle`.

## Reglas al conectar al Oracle 10g (recordatorio)

- Verificar **siempre** `ORACLE_HOME`, `ORACLE_SID` y `NLS_LANG` antes de invocar `sqlplus`.
- Confirmar el juego de caracteres en cada exportación: `WE8MSWIN1252` (frecuente) frente a
  `AL32UTF8`; revisar encodings antes de importar a PostgreSQL.
- No usar sintaxis moderna de openSUSE/SLES: 11.4 solo trae repositorios y comandos
  tradicionales.
- Priorizar herramientas de consola (`sqlplus`, `exp`); `oracledb` modo Thin **falla** por
  cifrado obsoleto (usar modo Thick con Instant Client antiguo solo si es imprescindible).
- La variable `EXCLUIR` de `extraer_datos_csv.sh` ya filtra las colas de replicación
  (`EVENTOS_SINC`, `EVENTOS_DBLINK`, `EVENTOS_RESP`) en re-dumps.

*Creado el 19/09/2026.*