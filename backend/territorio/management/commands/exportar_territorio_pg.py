import os

import psycopg

from django.core.management.base import BaseCommand, CommandError

from territorio.models import DivisionTerritorial

NIVELES = ["ESTADO", "MUNICIPIO", "PARROQUIA", "COMUNIDAD"]


class Command(BaseCommand):
    help = (
        "Exporta la división territorial (estado→municipio→parroquia→comunidad) de la BD de Django "
        "a una base PostgreSQL externa (por defecto territorio_apn) con esquema normalizado y "
        "códigos INE completos por concatenación. Conversa tablas y reinserta todo (idempotente)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--host", default=os.getenv("APN_PG_HOST", "127.0.0.1"))
        parser.add_argument("--port", default=int(os.getenv("APN_PG_PORT", "5436")))
        parser.add_argument("--dbname", default=os.getenv("APN_PG_DBNAME", "territorio_apn"))
        parser.add_argument("--usuario", default=os.getenv("APN_PG_USER", "sis_user"))
        parser.add_argument("--clave", default=os.getenv("APN_PG_PASSWORD", "sis_password"))

    def handle(self, *args, **opts):
        destino = {
            "host": opts["host"],
            "port": int(opts["port"]),
            "dbname": opts["dbname"],
            "user": opts["usuario"],
            "password": opts["clave"],
        }
        self.stdout.write(f"Conectando a {destino['host']}:{destino['port']}/{destino['dbname']} …")

        estados = list(DivisionTerritorial.objects.filter(nivel="ESTADO"))
        if not estados:
            raise CommandError("No hay datos de ESTADO en la BD de origen.")

        municipios = list(DivisionTerritorial.objects.filter(nivel="MUNICIPIO"))
        parroquias = list(DivisionTerritorial.objects.filter(nivel="PARROQUIA"))
        comunidades = list(DivisionTerritorial.objects.filter(nivel="COMUNIDAD"))

        from collections import defaultdict

        hijos = defaultdict(list)
        for o in municipios + parroquias + comunidades:
            hijos[o.padre_id].append(o)

        def _codigo(o, ancho=None):
            cod = (o.codigo or "").strip()
            return cod.zfill(ancho) if ancho else cod

        filas = {"estados": [], "municipios": [], "parroquias": [], "comunidades": []}
        for e in estados:
            c = _codigo(e, 2)
            filas["estados"].append((c, e.nombre))
            for m in hijos.get(e.id, []):
                c_m = c + _codigo(m, 2)
                filas["municipios"].append((c_m, m.nombre, c))
                for p in hijos.get(m.id, []):
                    c_p = c_m + _codigo(p, 2)
                    filas["parroquias"].append((c_p, p.nombre, c_m))
                    for com in hijos.get(p.id, []):
                        filas["comunidades"].append((c_p + _codigo(com), com.nombre, c_p))

        try:
            conn = psycopg.connect(**destino)
        except psycopg.OperationalError as e:
            raise CommandError(f"No se pudo conectar a la base destino: {e}")

        with conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE comunidades, parroquias, municipios, estados")
                ejecutar = {
                    "estados": ("INSERT INTO estados (codigo, nombre) VALUES (%s, %s)", filas["estados"]),
                    "municipios": ("INSERT INTO municipios (codigo, nombre, estado_codigo) VALUES (%s, %s, %s)", filas["municipios"]),
                    "parroquias": ("INSERT INTO parroquias (codigo, nombre, municipio_codigo) VALUES (%s, %s, %s)", filas["parroquias"]),
                    "comunidades": ("INSERT INTO comunidades (codigo, nombre, parroquia_codigo) VALUES (%s, %s, %s)", filas["comunidades"]),
                }
                for tabla, (sql, datos) in ejecutar.items():
                    cur.executemany(sql, datos)
                    self.stdout.write(self.style.SUCCESS(f"  {tabla}: {len(datos)} filas"))
        conn.close()
        self.stdout.write(self.style.SUCCESS("Exportación completada."))
        self.stdout.write(
            "Vista para reportes: SELECT * FROM division_geografica; (órdenes: estado, municipio, parroquia, comunidad)"
        )