"""Genera el mapa de modelos del sistema legacy SISMAI.

Contra las tablas/vistas migradas en los esquemas `sismai`, `legacy`,
`inbdlar1` y `historico` de la BD PostgreSQL (origen: Oracle 10g), escribe:

* ``backend/legacy/models_legacy.py``: un modelo ``managed=False`` por tabla
  (equivalente a lo que produciría ``inspectdb`` pero con el nombre de tabla
  calificado por esquema: ``db_table = '"sismai"."ESTABLECIMIENTO"'``).
* ``legancy/analisis/PRIORIDADES_LEGACY.md``: inventario priorizado de las
  tablas (thierarchy de prioridades P1/P2/P3) para el plan de integración.

Los modelos son de SOLO LECTURA (``managed=False``); no crean migraciones ni
alteran ninguna tabla. Las clases duplicadas entre esquemas (p. ej. la tabla
``T_USUARIOS`` en ``legacy`` e ``inbdlar1``) se distinguen con un prefijo del
esquema en el nombre de la clase.
"""

import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection

ESQUEMAS = ("sismai", "legacy", "inbdlar1", "historico")

BASE_DIR = Path(__file__).resolve().parents[4]
MODELOS_OUT = BASE_DIR / "backend" / "legacy" / "models_legacy.py"
REPORTE_OUT = BASE_DIR / "legancy" / "analisis" / "PRIORIDADES_LEGACY.md"

PALABRAS_RESERVADAS = {
    "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "finally", "for", "from",
    "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or",
    "pass", "raise", "return", "try", "while", "with", "yield",
    "True", "False", "None",
}

# Prioridad 1 (dominio / negocio): tablas que sustentan el mapa de centros,
# usuarios, territorio, catálogos clínicos CIE legacy y las fuentes de vigilancia
# cuya integración a los modelos nuevos (registros/vigilancia) está por decidir.
TIER1 = {
    ("sismai", "ESTABLECIMIENTO"): "Catálogo maestro de establecimientos (a integrar a seguridad.Organizacion)",
    ("sismai", "ESTABLECIMIENTO_MAESTRA"): "Maestra de establecimientos",
    ("sismai", "DEPENDENCIA_ADM"): "Dependencia administrativa (campo HDEPENDENCIA_ADM)",
    ("sismai", "NIVEL"): "Nivel de atención (campo HNIVEL)",
    ("sismai", "USUARIOS"): "Usuarios SISMAI (LOGIN, ESTATUS, perfil, jerarquía)",
    ("sismai", "USUARIO_ESTAB"): "Vinculación usuario - establecimiento",
    ("sismai", "PERSONALMEDICO"): "Personal médico firmante",
    ("sismai", "PERSONALSALUD"): "Personal de salud",
    ("sismai", "ORG_GEOGRAFICA"): "División político territorial (Estado-Municipio-Parroquia-Comunidad)",
    ("sismai", "LOCALIDADESTAB"): "Vinculación establecimiento - localidad",
    ("sismai", "CIE10"): "Catálogo CIE-10 legacy (códigos con punto)",
    ("sismai", "VALIDARCIE10"): "Validación CIE-10 legacy (sin punto)",
    ("sismai", "CODIF_CIE10"): "Mapeo CODIFICADOR - CIE-10",
    ("sismai", "CATEGORIA_CIE10"): "Niveles de categoría CIE-10 (Cap/Grupo/Cat/Subcat)",
    ("sismai", "SEXO"): "Catálogo de sexo (legacy: 1=Femenino, 2=Masculino)",
    ("sismai", "EDADES"): "Catálogo de edades",
    ("sismai", "CASOS_MMI"): "Fichas de vigilancia individuales materno-infantil (integración pendiente)",
    ("sismai", "RENGLON_CASOSMI"): "Causas de CASOS_MMI con CIE-10",
    ("sismai", "M_VIOLENTA"): "Violencia (accidente/homicidio/suicidio) ligada a CERTIFICADO",
    ("sismai", "RENGLONTELE"): "Consolidado semanal RENGLONTELE (morbilidad, EPI-12)",
    ("sismai", "RENGLON_EPI15"): "Consolidado EPI-15",
    ("sismai", "RENGLON_DSP04"): "Consolidado DSP-04",
    ("sismai", "INFORME_EPI"): "Informe EPI agregado (CASOSP/S/X) - fuente de ConsolidadoSemanal",
    ("sismai", "CAMBIOS"): "Bitácora de cambios (TABLA/EVENTO/FECHA/ID/STATUS/AMS)",
    ("legacy", "T_ESTABLE"): "Establecimientos (lista nivel central)",
    ("legacy", "T_USUARIOS"): "Usuarios (lista nivel central)",
    ("legacy", "T_ORGGEOG"): "Organización geográfica (nivel central)",
    ("legacy", "T_PERSMEDI"): "Personal médico (nivel central)",
    ("inbdlar1", "T_USUARIOS"): "Usuarios efectivos región Lara",
    ("inbdlar1", "T_ESTABLE"): "Establecimientos efectivos región Lara",
    ("inbdlar1", "T_ORGGEOG"): "Geografía efectiva región Lara",
    ("historico", "EVENTOS"): "Log de eventos procesados (STATUS != 0)",
}

# Prioridad 2 (operativo/registro).
PREFIJOS_TIER2 = ("NAC_", "CAUSA", "RENGLON_", "M_", "T_")
NOMBRES_TIER2 = {
    "CERTNACIMIENTO", "CERTIFICADO", "DOCUMENTO", "DOCUMENTOCONS",
    "ACTIVIDAD", "T_AUDITORIA", "AUDITORIA", "EVENTOS",
}

NOTAS = {
    ("historico", "EVENTOS"): "Único log real (se descartaron EVENTOS_SINC/DBLINK/RESP).",
    ("sismai", "RENGLONTELE"): "No usar las colas EVENTOS_SINC/DBLINK (riesgo de doble conteo).",
    ("sismai", "ESTABLECIMIENTO"): "STATUS: A=activo, I=inactivo, B=bloqueado.",
    ("sismai", "USUARIOS"): "ESTATUS: 2=activo/normal, 1=deshabilitado, NULL sin estado.",
}


def nombre_python(columna):
    nombre = columna.lower().replace(" ", "_")
    if nombre in PALABRAS_RESERVADAS or nombre[:1].isdigit() or nombre.startswith("_"):
        nombre = "f_" + nombre
    return nombre


def tipo_modelo(tipo_pg):
    """Traduce format_type() de PostgreSQL a (nombre de models.Field, kwargs)."""
    t = (tipo_pg or "").strip().lower()
    if t in ("smallint", "integer", "bigint", "oid", "xid", "regclass"):
        return {"smallint": "models.SmallIntegerField",
                "integer": "models.IntegerField",
                "bigint": "models.BigIntegerField",
                "oid": "models.BigIntegerField",
                "xid": "models.BigIntegerField",
                "regclass": "models.BigIntegerField"}[t], {}
    if t.startswith("numeric") or t.startswith("decimal"):
        m = re.match(r"(?:numeric|decimal)\((\d+)\s*,\s*(\d+)\)", t)
        if m:
            p, s = int(m.group(1)), int(m.group(2))
            if s == 0 and p <= 9:
                return "models.IntegerField", {}
            if s == 0 and 9 < p <= 18:
                return "models.BigIntegerField", {}
            if p <= 1000:
                return "models.DecimalField", {"max_digits": p, "decimal_places": s}
        return "models.FloatField", {}
    if t in ("real", "double precision"):
        return "models.FloatField", {}
    if t.startswith(("character varying", "varchar", "character", "char")):
        m = re.match(r"(?:character varying|varchar|bpchar|character|char)\((\d+)\)", t)
        if m and int(m.group(1)) <= 4000:
            return "models.CharField", {"max_length": int(m.group(1))}
        return "models.TextField", {}
    if t == "text":
        return "models.TextField", {}
    if t.startswith("timestamp"):
        return "models.DateTimeField", {}
    if t == "date":
        return "models.DateField", {}
    if t.startswith("time"):
        return "models.TimeField", {}
    if t.startswith("interval"):
        return "models.DurationField", {}
    if t == "boolean":
        return "models.BooleanField", {}
    if t in ("json", "jsonb"):
        return "models.JSONField", {}
    if t == "bytea":
        return "models.BinaryField", {}
    if t == "uuid":
        return "models.UUIDField", {}
    return "models.TextField", {}


def solucionar_nombre_clase(nombre_tabla, schema, usados):
    base = "".join(w.capitalize() for w in re.split(r"[^A-Za-z0-9]+", nombre_tabla.lower()))
    candidato = base
    if usados.get(base.lower()):
        prefijo = "".join(w.capitalize() for w in re.split(r"[^A-Za-z0-9]+", schema.lower()))
        candidato = prefijo + base
    while candidato.lower() in usados:
        candidato += "_"
    usados[base.lower()] = True
    usados[candidato.lower()] = True
    return candidato


class Command(BaseCommand):
    help = "Genera backend/legacy/models_legacy.py y el inventario priorizado del legacy."

    def handle(self, *args, **options):
        self.inventario = self._inventario()
        self.columnas = {k: self._columnas(*k) for k in ((s, t) for s, t, *_ in self.inventario)}
        self.primary = {k: self._primary(*k) for k in self.columnas}
        self.fks = {k: self._fk(*k) for k in self.columnas}
        self._presencia = {}
        for s, t, *_ in self.inventario:
            self._presencia[t] = self._presencia.get(t, 0) + 1
        self._generar_modelos()
        self._generar_reporte()
        self.stdout.write(self.style.SUCCESS(
            f"modelos_legacy.py y PRIORIDADES_LEGACY.md generados "
            f"({len(self.inventario)} tablas/vistas)"
        ))

    def _inventario(self):
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT n.nspname, c.relname, c.relkind,
                       c.reltuples::bigint AS filas,
                       (SELECT count(*) FROM pg_attribute a
                         WHERE a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped) AS ncol
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = ANY(%s)
                  AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
                  AND NOT c.relname LIKE 'pg_%%'
                ORDER BY n.nspname, c.relname
                """,
                [list(ESQUEMAS)],
            )
            return cur.fetchall()

    def _columnas(self, schema, nombre):
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS ftype,
                       (NOT a.attnotnull) AS nullable, a.attidentity,
                       col_description(c.oid, a.attnum) AS comentario
                FROM pg_attribute a
                JOIN pg_class c ON c.oid = a.attrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = %s AND c.relname = %s
                  AND a.attnum > 0 AND NOT a.attisdropped
                ORDER BY a.attnum
                """,
                [schema, nombre],
            )
            return cur.fetchall()

    def _primary(self, schema, nombre):
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT a.attname
                FROM pg_index i
                JOIN pg_class c ON c.oid = i.indrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(i.indkey)
                WHERE n.nspname = %s AND c.relname = %s AND i.indisprimary
                ORDER BY array_position(i.indkey, a.attnum)
                """,
                [schema, nombre],
            )
            return [r[0] for r in cur.fetchall()]

    def _fk(self, schema, nombre):
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT con.conname, con.confrelid::regclass::text
                FROM pg_constraint con
                JOIN pg_class c ON c.oid = con.conrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = %s AND c.relname = %s AND con.contype = 'f'
                ORDER BY con.conname
                """,
                [schema, nombre],
            )
            return cur.fetchall()

    def _tier(self, schema, nombre):
        if (schema, nombre) in TIER1:
            return 1
        if schema in ("legacy", "historico"):
            if schema == "historico" and nombre.startswith("ERRORES"):
                return 3
            return 2
        if schema == "inbdlar1":
            return 2 if nombre.startswith("T_") else 3
        if any(nombre.startswith(p) for p in PREFIJOS_TIER2) or nombre in NOMBRES_TIER2:
            return 2
        return 3

    def _generar_modelos(self):
        usados = {}
        clases = []
        indice = []
        for schema, nombre, relkind, filas, ncol in self.inventario:
            nombre_clase = solucionar_nombre_clase(nombre, schema, usados)
            pk_cols = self.primary[(schema, nombre)]
            columnas = self.columnas[(schema, nombre)]
            pk_nominal = None
            pk_real = len(pk_cols) == 1
            if len(pk_cols) == 0:
                pk_nominal = columnas[0][0]
            elif len(pk_cols) > 1:
                pk_nominal = pk_cols[0]
            lineas = [f"class {nombre_clase}(models.Model):"]
            for col, tipo_pg, nullable, identidad, comentario in columnas:
                campo = nombre_python(col)
                kwargs = {"blank": True, "null": True}
                if (pk_real and pk_cols[0] == col) or (pk_nominal == col):
                    kwargs["primary_key"] = True
                if campo != col:
                    kwargs["db_column"] = col
                field, opciones = tipo_modelo(tipo_pg)
                kwargs.update(opciones)
                cuerpo = f"    {campo} = {field}({', '.join(f'{k}={v!r}' for k, v in kwargs.items())})"
                if comentario:
                    cuerpo += f"  # {comentario}"
                lineas.append(cuerpo)
            if pk_real:
                pass
            elif len(pk_cols) == 0:
                lineas.append("    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).")
            else:
                lineas.append("    # PK compuesta en el legacy: la primera columna es PK nominal (solo lectura).")
            lineas.extend([
                "",
                "    class Meta:",
                '        app_label = "legacy"',
                "        managed = False",
                f'        db_table = "\\"{schema}\\".\\"{nombre}\\""',
                "",
            ])
            clases.append("\n".join(lineas))
            indice.append(nombre_clase)
        contenido = [
            "# -*- coding: utf-8 -*-",
            "# GENERADO AUTOMÁTICAMENTE por `manage.py mapear_legacy` (no editar a mano).",
            "#",
            "# Mapa de modelos del sistema legacy SISMAI (Oracle 10g → PostgreSQL).",
            "# Modelos de SOLO LECTURA (managed=False): no crean migraciones ni alteran",
            '# tablas. db_table va calificado por esquema (ej. "sismai"."ESTABLECIMIENTO").',
            "# Esquemas documentados: sismai / legacy / inbdlar1 / historico.",
            "from django.db import models",
            "",
            "",
            "\n\n".join(clases),
            "",
            "__all__ = [",
        ]
        for nombre_clase in indice:
            contenido.append(f'    "{nombre_clase}",')
        contenido.append("]")
        contenido.append("")
        MODELOS_OUT.write_text("\n".join(contenido), encoding="utf-8")

    def _generar_reporte(self):
        tipo_txt = {"r": "tabla", "p": "tabla part.", "v": "vista", "m": "vista mat.", "f": "tabla ext."}
        lineas = [
            "# Inventario priorizado del sistema legacy SISMAI",
            "",
            "**Generado por** `manage.py mapear_legacy`. Modelo de referencia: "
            "`backend/legacy/models_legacy.py` (un modelo `managed=False` por tabla/vista, solo lectura).",
            "Esquemas migrados: `sismai`, `inbdlar1`, `legacy`, `historico` (origen: Oracle 10g).",
            "",
            "## Criterios de prioridad",
            "",
            "- **P1 — Dominio/negocio:** catálogos de centro, usuarios, jerarquía, territorio, CIE legacy y"
            "  las fuentes de vigilancia cuya integración a `registros`/`vigilancia` está por decidir.",
            "- **P2 — Operativo/registro:** tablas de hechos (nacimientos/defunciones), espejos centrales/efectivos"
            "  (`T_*`) y logs de actividad.",
            "- **P3 — Catálogos de soporte / configuración / colas:** resto.",
            "",
            "## Resumen",
            "",
            "| Tier | Tablas |",
            "|---|---|",
        ]
        por_tier = {}
        for s, n, rk, filas, nc in self.inventario:
            por_tier[self._tier(s, n)] = por_tier.get(self._tier(s, n), 0) + 1
        for tier in (1, 2, 3):
            lineas.append(f"| P{tier} | {por_tier.get(tier, 0)} |")
        lineas.extend([
            "",
            "## Inventario (filas aproximadas, ordenado por prioridad y tamaño)",
            "",
            "| Tier | Esquema | Tabla | Tipo | Filas (aprox) | Col | PK | FKs | Nota |",
            "|---|---|---|---|---|---|---|---|---|",
        ])

        def clave(item):
            s, nombre, rk, filas, nc = item
            return (self._tier(s, nombre), -(filas or 0), s, nombre)

        for s, nombre, rk, filas, nc in sorted(self.inventario, key=clave):
            tier = self._tier(s, nombre)
            pk = len(self.primary[(s, nombre)])
            fks = len(self.fks[(s, nombre)])
            nota = TIER1.get((s, nombre)) or NOTAS.get((s, nombre)) or ""
            filas_txt = f"{filas or 0:,}".replace(",", ".")
            lineas.append(
                f"| P{tier} | `{s}` | `{nombre}` | {tipo_txt.get(rk, rk)} | {filas_txt} "
                f"| {nc} | {pk} | {fks} | {nota} |"
            )
        lineas.extend([
            "",
            "## Tablas P1 (dominio) con conteo exacto",
            "",
            "| Esquema | Tabla | Filas exactas |",
            "|---|---|---|",
        ])
        for s, nombre in sorted(TIER1):
            if (s, nombre) not in self.columnas:
                continue
            with connection.cursor() as cur:
                cur.execute(f'SELECT count(*) FROM {s}."{nombre.replace(chr(34), "")}"')
                total = cur.fetchone()[0]
            lineas.append(f"| `{s}` | `{nombre}` | {total:,}".replace(",", "."))
        REPORTE_OUT.write_text("\n".join(lineas), encoding="utf-8")