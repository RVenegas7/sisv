"""Siembra el catálogo de registradores civiles con los del legacy SISMAI.

El legacy guarda el registrador que firmó cada certificado de defunción en
``sismai.CERTIFICADO`` (``NOMREGISTRADOR``, ``CIREGISTRADOR``, ``NACREGISTRADOR``),
pero **nunca** modeló el registro civil ni la vigencia. Este comando aprovecha
esas columnas para crear el catálogo de personas (``RegistradorCivil``), agrupando
por cédula y eligiendo el nombre más frecuente como canónico.

Lo que **no** hace, a propósito: no inventa ``RegistroCivil`` ni
``DesignacionRegistrador``, porque el legacy no tiene esos datos. Esas se cargan
a mano desde ``/registradores``.

Sin ``--ejecutar`` solo informa (dry-run). Es idempotente: omite los
``(nacionalidad, cédula)`` que ya existan en el catálogo. Requiere la base con el
espejo del legacy; en una base sin él (p. ej. SQLite de pruebas) avisa y termina.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError

from registradores.models import RegistradorCivil
from registradores.services import consolidar_registradores


class Command(BaseCommand):
    help = ("Crea RegistradorCivil desde sismai.CERTIFICADO (agrupa por cédula; "
            "no crea registros civiles ni designaciones).")

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true",
                            help="Aplica los cambios (sin esto solo informa).")
        parser.add_argument("--limite", type=int, default=None,
                            help="Lee solo las primeras N filas del legacy (muestreo).")

    def handle(self, *args, **options):
        filas = self._leer_filas(options["limite"])
        if filas is None:
            self.stderr.write(self.style.ERROR(
                "El esquema legacy (sismai.CERTIFICADO) no está disponible en esta "
                "base; apunte a la BD con el espejo del legacy."
            ))
            return

        personas, descartados = consolidar_registradores(filas)
        existentes = set(RegistradorCivil.objects.values_list("nacionalidad", "cedula"))
        ya_en_catalogo = [(p["nacionalidad"], p["cedula"]) for p in personas
                          if (p["nacionalidad"], p["cedula"]) in existentes]
        nuevos = [p for p in personas
                  if (p["nacionalidad"], p["cedula"]) not in existentes]

        self.stdout.write(
            f"Filas leídas con registrador: {len(filas):,} · "
            f"cédulas distintas: {len(personas):,} "
            f"({sum(p['variantes'] for p in personas):,} variantes de nombre)."
        )
        self.stdout.write(
            f"Descartadas sin cédula: {descartados['sin_cedula']:,} · "
            f"sin nombre válido: {descartados['sin_nombre']:,}."
        )
        self.stdout.write(
            f"Ya en el catálogo: {len(ya_en_catalogo):,} · por crear: {len(nuevos):,}."
        )

        if nuevos:
            self.stdout.write("Muestra de altas:")
            for p in nuevos[:10]:
                self.stdout.write(
                    f"  {p['nacionalidad']}-{p['cedula']}  {p['nombres']} {p['apellidos']} "
                    f"({p['certificados']:,} certificados, {p['variantes']} variantes)"
                )

        if not nuevos:
            self.stdout.write(self.style.SUCCESS("Nada que crear; el catálogo está al día."))
            return
        if not options["ejecutar"]:
            self.stdout.write(self.style.WARNING(
                "Dry-run: no se modificó nada. Use --ejecutar para aplicar."))
            return

        objetos = [
            RegistradorCivil(
                nacionalidad=p["nacionalidad"],
                cedula=p["cedula"],
                nombres=p["nombres"],
                apellidos=p["apellidos"],
                activo=True,
                observaciones=(
                    "Alta automática desde legacy SISMAI (CERTIFICADO): "
                    f"{p['certificados']} certificados, {p['variantes']} variantes de nombre."
                ),
            )
            for p in nuevos
        ]
        with transaction.atomic():
            RegistradorCivil.objects.bulk_create(objetos, batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"Creados {len(objetos):,} registradores civiles."
        ))

    def _leer_filas(self, limite):
        """Devuelve [(nac, cédula, nombre)] del legacy, o None si no está disponible."""
        from legacy.models_legacy import Certificado

        qs = (
            Certificado.objects
            .exclude(nomregistrador__isnull=True)
            .exclude(nomregistrador="")
            .values_list("nacregistrador", "ciregistrador", "nomregistrador")
        )
        if limite:
            qs = qs[:limite]
        try:
            return list(qs.iterator(chunk_size=5000))
        except (OperationalError, ProgrammingError):
            return None
