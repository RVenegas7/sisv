from django.core.management.base import BaseCommand
from django.db.models import Q

from catalogos.models import CIE11, MapeoCIE
from vigilancia.models import EventoENO


def _tokens(codigos):
    """Divide el campo separado por comas y /, devolviendo tokens sin duplicados."""
    if not codigos:
        return []
    vistos = set()
    salida = []
    for parte in codigos.replace("/", ",").split(","):
        tok = parte.strip()
        if not tok:
            continue
        if tok in vistos:
            continue
        vistos.add(tok)
        salida.append(tok)
    return salida


def _expandir_rango(token):
    """Devuelve códigos CIE-11 del catálogo dentro de un rango 'X-Y'."""
    inicio, fin = token.split("-", 1)
    qs = CIE11.objects.filter(codigo__range=(inicio, fin)).values_list("codigo", flat=True)
    return list(qs)


def _cie10_de(token):
    """Mapa un token CIE-11 (código o rango) a sus códigos CIE-10 vía cross-walk."""
    if "-" in token:
        codigos11 = _expandir_rango(token)
    else:
        codigos11 = [token] if CIE11.objects.filter(codigo=token).exists() else []
    if not codigos11:
        return []
    mapeos = MapeoCIE.objects.filter(
        Q(cie11__codigo__in=codigos11)
    ).select_related("cie10", "cie11")
    salida = sorted({m.cie10.codigo for m in mapeos})
    return salida


class Command(BaseCommand):
    help = (
        "Enriquece EventoENO con equivalentes CIE-10 derivadas del cross-walk. "
        "Conserva los códigos CIE-10 explícitos del formulario y agrega los del mapeo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limite-caracteres",
            type=int,
            default=200,
            help="Máximo de caracteres para codigos_cie10 (default 200, tamaño del campo).",
        )

    def handle(self, *args, **options):
        limite = options["limite_caracteres"]
        eventos = EventoENO.objects.exclude(codigos_cie11="")
        total = eventos.count()
        actualizados = 0
        sin_mapeo = 0
        for e in eventos:
            tokens = _tokens(e.codigos_cie11)
            nuevo_c11 = ", ".join(tokens)
            cie10 = list(_tokens(e.codigos_cie10))
            for tok in tokens:
                for cod in _cie10_de(tok):
                    if cod not in cie10:
                        cie10.append(cod)
            nuevo_c10 = ", ".join(cie10)
            if not nuevo_c10:
                sin_mapeo += 1
            if len(nuevo_c10) > limite:
                nuevo_c10 = nuevo_c10[: limite - 1].rstrip(", ") + "…"
            if nuevo_c11 != e.codigos_cie11 or nuevo_c10 != e.codigos_cie10:
                e.codigos_cie11 = nuevo_c11
                e.codigos_cie10 = nuevo_c10
                e.save(update_fields=["codigos_cie11", "codigos_cie10"])
                actualizados += 1
        con_c10 = EventoENO.objects.exclude(codigos_cie10="").count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Eventos ENO analizados: {total} · actualizados: {actualizados} · "
                f"con CIE-10: {con_c10} · sin mapeo CIE-10: {sin_mapeo}"
            )
        )