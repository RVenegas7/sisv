"""Asigna la Organización (centro) a los registros legacy según su establecimiento.

Reutiliza el árbol de establecimientos del estado Lara (sismai.ESTABLECIMIENTO,
raíces DES LARA=67754 / DPS LARA=3441583108) igual que ``limpiar_legacy_no_lara``:

  1. Crea/reutiliza una ``Organizacion`` nivel CENTRO (hija de la Dirección de
     Epidemiología del Estado Lara) por cada nombre distinto de establecimiento
     presente en los registros que pertenezca al árbol Lara.
  2. Asigna ``organizacion_id`` a los registros (Nacimiento/Defuncion/Ficha) cuyo
     ``establecimiento`` resuelva; los de domicilio (sin establecimiento) se dejan
     sin organización (su agrupación usa el estado de residencia).

Idempotente: si la orga ya existe (por nombre normalizado) se reutiliza y los
registros ya asignados no se tocan. La asignación usa una única ``UPDATE ...
FROM (VALUES ...)`` por modelo.

Ejecutar: ``manage.py asignar_organizacion_legacy`` (informa; --ejecutar aplica).
"""
import re
import unicodedata

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from registros.models import Defuncion, FichaVigilancia, Nacimiento
from seguridad.models import Organizacion

RAICES_LARA = [67754.0, 3441583108.0]  # DES LARA + DPS LARA


def normalizar(nombre):
    nombre = re.sub(r"\([^)]*\)", "", nombre or "")
    nombre = "".join(c for c in unicodedata.normalize("NFD", nombre) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", nombre.lower()).strip()


class Command(BaseCommand):
    help = "Asigna la Organización (centro) a los registros legacy según su establecimiento (Lara)."

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Aplica la asignación (sin esto solo informa).")

    def handle(self, *args, **options):
        ejecutar = options["ejecutar"]

        with connection.cursor() as cur:
            cur.execute('SELECT "ID", "PADRE", "NOMBRE" FROM sismai."ESTABLECIMIENTO";')
            filas = cur.fetchall()
        padres = {float(i): float(p) for i, p, _ in filas if p}
        nombres = {float(i): (n or "").strip() for i, _, n in filas}

        arbol = set(RAICES_LARA)
        cambio = True
        while cambio:
            cambio = False
            for i, p in padres.items():
                if p in arbol and i not in arbol:
                    arbol.add(i)
                    cambio = True
        arbol_norm = {normalizar(nombres[i]) for i in arbol if nombres[i]}
        self.stdout.write(f"Árbol Lara: {len(arbol)} establecimientos, {len(arbol_norm)} nombres únicos.")

        padre = (
            Organizacion.objects.filter(nivel="REGIONAL", estado="Lara")
            .exclude(codigo="LEGACY-LARA")
            .order_by("id")
            .first()
        )
        if padre is None:
            self.stdout.write(self.style.ERROR("No existe la Dirección de Epidemiología del Estado Lara."))
            return

        modelos = (
            (Nacimiento, "Nacimientos"),
            (Defuncion, "Defunciones"),
            (FichaVigilancia, "Fichas de vigilancia"),
        )

        numeros = {}
        for modelo, rotulo in modelos:
            por_est = {}
            for e in modelo.objects.exclude(establecimiento="").values_list("establecimiento", flat=True).distinct():
                e = (e or "").strip()
                if e:
                    por_est[e] = normalizar(e) in arbol_norm
            n_asignables = sum(1 for v in por_est.values() if v)
            n_registros = sum(
                modelo.objects.filter(establecimiento=e, organizacion_id__isnull=True).count()
                for e, ok in por_est.items()
                if ok
            )
            numeros[(modelo, rotulo)] = por_est
            self.stdout.write(
                f"  {rotulo}: {n_asignables} establecimientos Lara, {n_registros} registros por asignar, "
                f"{len(por_est) - n_asignables} sin mapa."
            )

        if not ejecutar:
            n_orgs = Organizacion.objects.filter(padre=padre).count()
            self.stdout.write(
                self.style.WARNING(f"Dry-run: parent={padre.nombre} · orgs hijas existentes={n_orgs}")
            )
            self.stdout.write(self.style.WARNING("No se asignó nada. Use --ejecutar para aplicar."))
            return

        existentes_por_nombre = {normalizar(o.nombre): o for o in Organizacion.objects.filter(padre=padre)}
        creadas = reutilizadas = 0

        def _org_para(nombre_establecimiento, indice):
            nonlocal creadas, reutilizadas
            org = existentes_por_nombre.get(normalizar(nombre_establecimiento))
            if org is not None:
                reutilizadas += 1
                return org
            org = Organizacion.objects.create(
                nombre=nombre_establecimiento.strip()[:150],
                codigo=f"LEG-CENTRO-{indice:03d}",
                nivel="CENTRO",
                estado="Lara",
                municipio="",
                padre=padre,
                activo=True,
            )
            existentes_por_nombre[normalizar(nombre_establecimiento)] = org
            creadas += 1
            return org

        asignados = {}
        with transaction.atomic():
            indice = 0
            for (modelo, rotulo), por_est in numeros.items():
                mapa = {}
                for e, ok in por_est.items():
                    if ok:
                        indice += 1
                        mapa[e] = _org_para(e, indice).pk
                if not mapa:
                    asignados[rotulo] = 0
                    continue
                params = [v for e, oid in mapa.items() for v in (e, oid)]
                placeholders = ", ".join("(%s, %s)" for _ in mapa)
                with connection.cursor() as cur:
                    cur.execute(
                        f'UPDATE {modelo._meta.db_table} SET organizacion_id = v.oid '
                        f"FROM (VALUES {placeholders}) AS v(est, oid) "
                        "WHERE " + modelo._meta.db_table + ".establecimiento = v.est "
                        "AND " + modelo._meta.db_table + ".organizacion_id IS NULL",
                        params,
                    )
                    asignados[rotulo] = cur.rowcount
                self.stdout.write(f"  {rotulo}: {asignados[rotulo]} registros asignados.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Asignación aplicada. Orgas creadas={creadas}, reutilizadas={reutilizadas}. Registros={asignados}."
            )
        )