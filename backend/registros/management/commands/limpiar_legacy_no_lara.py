"""Elimina registros que no pertenecen estrictamente al estado Lara.

Criterio (acordado con el usuario el 2026-09-24):
  - Nacimientos: solo se conservan los cuyo establecimiento pertenece al árbol de
    establecimientos del estado Lara (DES LARA / DPS LARA en sismai.ESTABLECIMIENTO).
  - Defunciones: igual por establecimiento; las defunciones sin establecimiento
    (domicilio) solo se conservan si la residencia es ``Lara``.
  - Data de demostración (lotes ``LOTE-*`` y fichas demo) se elimina; los usuarios
    y organizaciones demo se conservan.

Ejecutar: ``manage.py limpiar_legacy_no_lara --ejecutar`` (por defecto solo informa).
"""
import re
import unicodedata

from django.db import connection, transaction
from django.db.models import Q
from django.core.management.base import BaseCommand

from registros.models import Defuncion, FichaVigilancia, Nacimiento
from vigilancia.models import ConsolidadoSemanal

RAICES_LARA = [67754.0, 3441583108.0]  # DES LARA + DPS LARA

FICHAS_DEMO = ["FV-2026-00345", "FV-2001-00012"]


def normalizar(nombre):
    nombre = re.sub(r"\([^)]*\)", "", nombre or "")
    nombre = "".join(c for c in unicodedata.normalize("NFD", nombre) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", nombre.lower()).strip()


class Command(BaseCommand):
    help = "Elimina registros fuera del estado Lara y data de demostración (dry-run por defecto)."

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Aplica la eliminación (sin esto solo informa).")

    def _establecimientos_fuera(self, modelo):
        return [
            e
            for e in modelo.objects.exclude(establecimiento="").values_list("establecimiento", flat=True).distinct()
            if normalizar(e) not in self.arbol_norm
        ]

    def _qs_a_eliminar(self, modelo):
        """1) Establecimiento no vacío fuera del árbol Lara.
        2) Sin establecimiento (domicilio) con residencia distinta de Lara."""
        ids = self._establecimientos_fuera(modelo)
        conds = []
        if ids:
            conds.append(Q(establecimiento__in=ids))
        conds.append(Q(establecimiento="") & ~Q(estado="Lara"))
        if len(conds) == 1:
            return modelo.objects.filter(conds[0])
        return modelo.objects.filter(conds[0] | conds[1])

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
        self.arbol_norm = {normalizar(nombres[i]) for i in arbol if nombres[i]}
        self.stdout.write(f"Árbol Lara: {len(arbol)} establecimientos, {len(self.arbol_norm)} nombres únicos.")

        objetivos = []
        for modelo, nombre in ((Nacimiento, "Nacimientos"), (Defuncion, "Defunciones"), (FichaVigilancia, "Fichas")):
            objetivos.append((f"{nombre}: fuera de Lara (establecimiento/residencia)", self._qs_a_eliminar(modelo).count()))
            objetivos.append((f"{nombre}: data demo (lote LOTE-*)", modelo.objects.filter(lote_id__startswith="LOTE-").count()))
        objetivos.append(("Fichas demo (códigos)", FichaVigilancia.objects.filter(codigo_notificacion__in=FICHAS_DEMO).count()))
        objetivos.append(("Consolidados sin origen legacy", ConsolidadoSemanal.objects.filter(legacy_tabla="").count()))

        self.stdout.write("Resumen de la limpieza propuesta:")
        for rotulo, n in objetivos:
            self.stdout.write(f"  {rotulo}: {n}")

        if not ejecutar:
            self.stdout.write(self.style.WARNING("Dry-run: no se borró nada. Use --ejecutar para aplicar."))
            return

        with transaction.atomic():
            for modelo in (Nacimiento, Defuncion, FichaVigilancia):
                self._qs_a_eliminar(modelo).delete()
                modelo.objects.filter(lote_id__startswith="LOTE-").delete()
            FichaVigilancia.objects.filter(codigo_notificacion__in=FICHAS_DEMO).delete()
            ConsolidadoSemanal.objects.filter(legacy_tabla="").delete()
        self.stdout.write(self.style.SUCCESS("Limpieza aplicada."))