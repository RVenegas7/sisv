"""Siembra el catálogo de registradores civiles con los del legacy SISMAI.

El legacy guarda **quién firmaba** cada certificado, pero **nunca** modeló el
registro civil ni la vigencia. Este comando aprovecha esas columnas para crear el
catálogo de personas (``RegistradorCivil``), agrupando por cédula y eligiendo el
nombre más frecuente como canónico. Dos orígenes:

- ``--origen defunciones`` (defecto): ``sismai.CERTIFICADO``
  (``NOMREGISTRADOR``, ``CIREGISTRADOR``, ``NACREGISTRADOR``), el registrador que
  firmó el certificado de defunción.
- ``--origen nacimientos``: ``sismai.CERTNACIMIENTO``
  (``JEFECIVIL``, ``JEFECIVILCI``) con la fecha de registro civil
  (``FECHAREGCIVIL``), que se anota como periodo **observado** de firmas
  (``firmo_desde``/``firmo_hasta``): no es una designación.

Lo que **no** hace, a propósito: no inventa ``RegistroCivil`` ni
``DesignacionRegistrador``, porque el legacy no tiene esos datos (no hay ninguna
columna con la oficina). Esas se cargan a mano desde ``/registradores``.

Sin ``--ejecutar`` solo informa (dry-run). Es idempotente: omite las cédulas que
ya existan en el catálogo (compara solo la cédula, porque el legacy de
nacimientos no distingue la nacionalidad). Requiere la base con el espejo del
legacy; en una base sin él (p. ej. SQLite de pruebas) avisa y termina.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError

from registradores.models import RegistradorCivil
from registradores.services import consolidar_registradores

ORIGENES = {
    "defunciones": {
        "modelo": "Certificado",
        "tabla": "sismai.CERTIFICADO",
        "campo": "NOMREGISTRADOR",
        "unidad": "certificados",
    },
    "nacimientos": {
        "modelo": "Certnacimiento",
        "tabla": "sismai.CERTNACIMIENTO",
        "campo": "JEFECIVIL",
        "unidad": "actas",
    },
}


class Command(BaseCommand):
    help = ("Crea RegistradorCivil desde el legacy (agrupa por cédula; no crea "
            "registros civiles ni designaciones).")

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true",
                            help="Aplica los cambios (sin esto solo informa).")
        parser.add_argument("--origen", choices=sorted(ORIGENES), default="defunciones",
                            help="De dónde se leen los registradores (def. defunciones = "
                                 "CERTIFICADO; nacimientos = CERTNACIMIENTO.JEFECIVIL).")
        parser.add_argument("--limite", type=int, default=None,
                            help="Lee solo las primeras N filas del legacy (muestreo).")

    def handle(self, *args, **options):
        origen = options["origen"]
        info = ORIGENES[origen]
        filas = self._leer_filas(options["limite"], origen)
        if filas is None:
            self.stderr.write(self.style.ERROR(
                f"El esquema legacy ({info['tabla']}) no está disponible en esta "
                "base; apunte a la BD con el espejo del legacy."
            ))
            return

        personas, descartados = consolidar_registradores(filas)
        cedulas = set(RegistradorCivil.objects.values_list("cedula", flat=True))
        nuevos = [p for p in personas if p["cedula"] not in cedulas]
        ya_en_catalogo = len(personas) - len(nuevos)

        self.stdout.write(
            f"Origen: {origen} ({info['tabla']}.{info['campo']})."
        )
        self.stdout.write(
            f"Filas leídas con registrador: {len(filas):,} · "
            f"cédulas distintas: {len(personas):,} "
            f"({sum(p['variantes'] for p in personas):,} variantes de nombre)."
        )
        self.stdout.write(
            f"Descartadas sin cédula: {descartados['sin_cedula']:,} · "
            f"con cédula inválida (<5 dígitos): {descartados['cedula_corta']:,} · "
            f"sin nombre válido: {descartados['sin_nombre']:,}."
        )
        self.stdout.write(
            f"Ya en el catálogo: {ya_en_catalogo:,} · por crear: {len(nuevos):,}."
        )

        if nuevos:
            self.stdout.write("Muestra de altas:")
            for p in nuevos[:10]:
                periodo = ""
                if p["firmo_desde"]:
                    fin = p["firmo_hasta"].isoformat() if p["firmo_hasta"] else "?"
                    periodo = f", firmó entre {p['firmo_desde'].isoformat()} y {fin}"
                self.stdout.write(
                    f"  {p['nacionalidad']}-{p['cedula']}  {p['nombres']} {p['apellidos']} "
                    f"({p['certificados']:,} {info['unidad']}, {p['variantes']} variantes"
                    f"{periodo})"
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
                firmo_desde=p["firmo_desde"],
                firmo_hasta=p["firmo_hasta"],
                observaciones=self._observaciones(info, p),
            )
            for p in nuevos
        ]
        with transaction.atomic():
            RegistradorCivil.objects.bulk_create(objetos, batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"Creados {len(objetos):,} registradores civiles. "
            "No se crearon registros civiles ni designaciones (el legacy no los tiene): "
            "cárguelos a mano desde /registradores."
        ))

    @staticmethod
    def _observaciones(info, p):
        texto = (
            f"Alta automática desde legacy SISMAI ({info['tabla']}.{info['campo']}): "
            f"{p['certificados']} {info['unidad']}, {p['variantes']} variantes de nombre."
        )
        if p["firmo_desde"]:
            fin = p["firmo_hasta"].isoformat() if p["firmo_hasta"] else "?"
            texto += (
                f" Firmó entre {p['firmo_desde'].isoformat()} y {fin} "
                "(periodo observado en el legacy, no es una designación)."
            )
        return texto

    def _leer_filas(self, limite, origen):
        """Devuelve filas del legacy ([(nac, cédula, nombre[, fecha])]), o None."""
        if origen == "nacimientos":
            from legacy.models_legacy import Certnacimiento

            qs = (
                Certnacimiento.objects
                .exclude(jefecivil__isnull=True)
                .exclude(jefecivil="")
                .values_list("jefecivilci", "jefecivil", "fecharegcivil")
            )
        else:
            from legacy.models_legacy import Certificado

            qs = (
                Certificado.objects
                .exclude(nomregistrador__isnull=True)
                .exclude(nomregistrador="")
                .values_list("nacregistrador", "ciregistrador", "nomregistrador")
            )

        try:
            filas = list(qs[:limite] if limite else qs.iterator(chunk_size=5000))
        except (OperationalError, ProgrammingError):
            return None
        if origen == "nacimientos":
            # El legacy de nacimientos no guarda la nacionalidad del jefe civil.
            return [(None, ci, nombre, fecha) for ci, nombre, fecha in filas]
        return filas
