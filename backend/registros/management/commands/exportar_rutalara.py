import datetime as dt
import io
import json
import os
import re
import zipfile

import psycopg

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

SPEC_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "rutarala_spec.json")

EXPORT_TABLE_RE = re.compile(r"exporting table\s+([A-Za-z0-9_\.]+)")
EXPORTED_ROWS_RE = re.compile(r"(\d+)\s+rows? exported")


def _semana_iso(iso: str) -> tuple[dt.date, dt.date]:
    try:
        anio, semana = (int(x) for x in iso.split("-")[1:])
    except (ValueError, IndexError):
        raise CommandError("Formato de --semana inválido: use AAAA-WNN (ej. 2026-W32).")
    inicio = dt.date.fromisocalendar(anio, semana, 1)
    return inicio, inicio + dt.timedelta(days=6)


def _extraer_conteos_referencia(ruta_zip: str) -> dict[str, int]:
    """Extrae {T_TABLA: filas} leyendo routlar1.log de un ZIP de referencia (envío real)."""
    nombre = os.path.basename(ruta_zip).lower()
    with zipfile.ZipFile(ruta_zip) as z:
        # rutlar1.log / routlar1.log (NLS variante) el que exista
        candidatos = [n for n in z.namelist() if "routlar1.log" in n.lower() or "rutlar1.log" in n.lower()]
        if not candidatos:
            raise CommandError(f"No se encontró routlar1.log dentro de {ruta_zip}.")
        log = z.read(candidatos[0]).decode("latin-1", errors="replace")
    conteos: dict[str, int] = {}
    tabla_actual = None
    for linea in log.splitlines():
        m = EXPORT_TABLE_RE.search(linea.rstrip())
        if m:
            tabla_actual = m.group(1).rsplit(".", 1)[-1]
            continue
        if tabla_actual:
            mf = EXPORTED_ROWS_RE.search(linea.rstrip())
            if mf:
                conteos[tabla_actual] = int(mf.group(1))
                tabla_actual = None
    if not conteos:
        raise CommandError(f"No se pudieron parsear conteos de {nombre}.")
    return conteos


class Command(BaseCommand):
    help = (
        "Genera el sobre semanal de rutas (esquema TEMP.T_*) desde la BD local replicando el contrato "
        "del ruteo Oracle: viaja el ESTADO CONSOLIDADO ACTUAL de toda fila cuyo último evento en "
        "EVENTOS_SINC dentro de la ventana es INSERT(1) o UPDATE(2). Las filas con último evento "
        "DELETE(3) no viajan. Fuente de eventos: sismai.EVENTOS (espejo). "
        "Salida: ZIP con CSV por tabla T_*, T_EVENTOS.csv y resumen de conteos estilo repllar1.log. "
        "Referencia del contrato: enviados/routlar1_482026_1526.ZIP (SE-32, 04/08/2026) y legancy/analisis/schema_routlar1.sql."
    )

    def add_arguments(self, parser):
        parser.add_argument("--semana", help="Semana ISO AAAA-WNN (ej. 2026-W32).")
        parser.add_argument("--desde", help="Inicio ventana YYYY-MM-DD (inclusive).")
        parser.add_argument("--hasta", help="Fin ventana YYYY-MM-DD (exclusivo).")
        parser.add_argument("--eventos", default="sismai.EVENTOS", help="Tabla origen de eventos (sismai.EVENTOS).")
        parser.add_argument("--salida", default="enviados", help="Directorio de salida del ZIP.")
        parser.add_argument("--comparar", help="ZIP de referencia (envío real) cuyo routlar1.log validar.")
        parser.add_argument(
            "--solo-eventos", action="store_true",
            help="Solo emite T_EVENTOS.csv (sin materializar el resto de las tablas T_*).",
        )

    def handle(self, *args, **opts):
        if (opts["desde"] or opts["hasta"]) and opts["semana"]:
            raise CommandError("Indique --semana O --desde/--hasta, no ambos.")
        if opts["semana"]:
            desde, hasta = _semana_iso(opts["semana"])
            hasta = hasta + dt.timedelta(days=1)
            etiqueta = opts["semana"]
        elif opts["desde"] and opts["hasta"]:
            desde = dt.date.fromisoformat(opts["desde"])
            hasta = dt.date.fromisoformat(opts["hasta"])
            etiqueta = f"{desde}->{hasta}"
        elif opts["desde"] or opts["hasta"]:
            raise CommandError("--desde y --hasta deben indicarse juntos.")
        else:
            desde = hasta = None
            etiqueta = "full"
        if desde and hasta <= desde:
            raise CommandError("--hasta debe ser posterior a --desde.")

        with open(SPEC_JSON, encoding="utf-8") as f:
            spec = json.load(f)
        mapeo = spec["mapeo"]
        columnas = spec["columnas"]

        db = settings.DATABASES["default"]
        conn = psycopg.connect(
            host=db.get("HOST", "127.0.0.1"),
            port=db.get("PORT", 5432),
            dbname=db.get("NAME"),
            user=db.get("USER"),
            password=db.get("PASSWORD"),
        )

        schema, tabla = opts["eventos"].split(".")
        if opts["desde"] or opts["semana"]:
            sql_ev = (
                f'SELECT "FECHA", "TABLA", "EVENTO", "ID" FROM {schema}."{tabla}" '
                f'WHERE "FECHA" >= %s AND "FECHA" < %s ORDER BY "TABLA", "ID", "FECHA" DESC'
            )
            params = (desde, hasta)
            self.stdout.write(f"Leyendo cola de eventos {opts['eventos']} [{desde} → {hasta}) …")
        else:
            sql_ev = (
                f'SELECT "FECHA", "TABLA", "EVENTO", "ID" FROM {schema}."{tabla}" '
                f'ORDER BY "TABLA", "ID", "FECHA" DESC'
            )
            params = ()
            self.stdout.write(f"Leyendo cola de eventos completa {opts['eventos']} …")
        ultimo_evento = {}
        fechas = {}
        eventos_completos = []
        with conn.cursor() as cur:
            cur.execute(sql_ev, params)
            for fecha, t, e, i in cur:
                eventos_completos.append((t, e, fecha, int(i)))
                key = (t, int(i))
                if key not in ultimo_evento:
                    ultimo_evento[key] = e
                    fechas[key] = fecha
        self.stdout.write(f"  eventos leídos:  {len(eventos_completos)} eventos / {len(ultimo_evento)} filas candidatas")

        viajan = {(t, i): e for (t, i), e in ultimo_evento.items() if e in ("1", "2")}
        self.stdout.write(f"  filas que viajan (último evento INSERT/UPDATE): {len(viajan)}")

        por_tabla = {}
        for (t, i) in viajan:
            por_tabla.setdefault(t, []).append(i)
        for t, lista in por_tabla.items():
            por_tabla[t] = sorted(set(lista))

        os.makedirs(opts["salida"], exist_ok=True)
        nombre_zip = f"generado_{dt.date.today():%Y%m%d}_{etiqueta.replace('-', '')}.zip"
        ruta_zip = os.path.join(opts["salida"], nombre_zip)
        conteos = {}
        with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as z:
            tev_filas = sorted(
                ((t, e, fecha.isoformat(sep=" "), i) for t, e, fecha, i in eventos_completos),
                key=lambda r: (r[0], r[2], r[3]),
            )
            z.writestr("T_EVENTOS.csv", "\n".join(f"{t}|{e}|{f}|{i}" for t, e, f, i in tev_filas) + "\n")
            conteos["T_EVENTOS"] = len(tev_filas)

            if not opts["solo_eventos"]:
                for destino, cols in sorted(columnas.items()):
                    if destino == "T_EVENTOS":
                        continue
                    fuente = None
                    for tabla_evento, (src, dst) in mapeo.items():
                        if dst == destino:
                            fuente = (tabla_evento, src)
                            break
                    if fuente is None or not cols:
                        conteos[destino] = 0
                        cabecera = "|".join(cols) + "\n" if cols else "\n"
                        z.writestr(f"{destino}.csv", cabecera)
                        continue
                    tabla_evento, src = fuente
                    ids = por_tabla.get(tabla_evento, [])
                    if not ids:
                        conteos[destino] = 0
                        z.writestr(f"{destino}.csv", "|".join(cols) + "\n")
                        continue
                    cols_sql = ", ".join(f'"{c}"' for c in cols)
                    sql = (
                        f'SELECT {cols_sql} FROM sismai."{src}" '
                        f'WHERE "ID" = ANY(%s::double precision[]) ORDER BY "ID"'
                    )
                    lineas = []
                    with conn.cursor() as cur:
                        cur.execute(sql, (ids,))
                        for row in cur:
                            partes = []
                            for v in row:
                                if v is None:
                                    partes.append("")
                                elif isinstance(v, dt.datetime):
                                    partes.append(v.strftime("%Y-%m-%d %H:%M:%S"))
                                elif isinstance(v, dt.date):
                                    partes.append(v.isoformat())
                                elif isinstance(v, float) and v.is_integer():
                                    partes.append(str(int(v)))
                                else:
                                    partes.append(str(v))
                            lineas.append("|".join(partes))
                    conteos[destino] = len(lineas)
                    self.stdout.write(f"  {destino}: {len(lineas)} filas desde {src}")
                    z.writestr(f"{destino}.csv", "|".join(cols) + "\n" + "\n".join(lineas) + "\n")

        resumen = "\n".join(
            f"{t}: {conteos.get(t, 0)} filas" for t in sorted(columnas) if t != "T_EVENTOS"
        )
        ruta_conteos = os.path.join(opts["salida"], nombre_zip.replace(".zip", "_conteos.txt"))
        with open(ruta_conteos, "w", encoding="utf-8") as f:
            f.write(resumen + "\n")

        self.stdout.write(self.style.SUCCESS(f"Generado {ruta_zip} ({len(viajan)} filas viajeras)."))
        self.stdout.write(self.style.NOTICE(f"Conteos por tabla: {ruta_conteos}"))

        if opts["comparar"]:
            ref = _extraer_conteos_referencia(opts["comparar"])
            dims = set(ref) | set(conteos)
            diffs = []
            ok = True
            for t in sorted(dims):
                r = ref.get(t, 0)
                g = conteos.get(t, 0)
                estado = "OK" if r == g else "DIF"
                if estado == "DIF":
                    ok = False
                    diffs.append(t)
                self.stdout.write(f"  [{estado}] {t}: referencia {r} / generado {g}")
            self.stdout.write("")
            self.stdout.write(
                self.style.ERROR("COMPARACIÓN CON DIFERENCIAS: " + ", ".join(diffs))
                if diffs
                else self.style.SUCCESS("COMPARACIÓN EXACTA CONTRA EL ENVÍO REAL")
            )
        conn.close()