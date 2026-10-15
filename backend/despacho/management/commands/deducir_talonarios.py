"""Deduce los talonarios (rango de serie) a partir de los certificados de la BD.

El SISMAI legacy no guardó nunca la entrega de talonarios, así que la serie que
recibió cada centro se **infiere** de los certificados que sí están cargados
(ver ``despacho.services.series_deducidas``). Este comando recorre la BD, propone
una serie por centro y —solo con ``--ejecutar``— crea los ``Talonario``:

- ``serie_desde``/``serie_hasta`` = mínimo y máximo número impreso de la corrida;
- ``fecha_entrega`` = fecha del certificado usado más antiguo de la corrida (es
  una cota superior de la entrega real: el talonario se entregó antes de usarse);
- ``responsable_recibe`` = ``--responsable-recibe`` (por defecto «Por confirmar»),
  porque el legacy no registra a quién se le entregó;
- ``observaciones`` deja constancia de que es una deducción automática.

Con ``--redondeo N`` el rango se estira hacia el corte de decena más cercano
(las asignaciones van de «múltiplo de 10 + 1» a «múltiplo de 10»), hasta ``N``
números y sin pisar un número que ya sepamos usado por otro centro: así el rango
se acerca a la serie realmente entregada y no al trozo que el centro agotó.

**Es una inferencia**, no un dato del sistema antiguo: sin ``--ejecutar`` solo
informa (dry-run) y no toca nada. Omite las series que ya tienen un talonario que
cubre el rango, para poder reejecutarlo sin duplicar.
"""

from django.core.management.base import BaseCommand

from despacho.models import Talonario
from despacho.services import MODELO_POR_TIPO, series_deducidas
from seguridad.models import Organizacion


class Command(BaseCommand):
    help = (
        "Deduce por centro el rango de serie de los talonarios desde los "
        "certificados cargados. Dry-run por defecto; --ejecutar crea los talonarios."
    )

    def add_arguments(self, parser):
        parser.add_argument("--ejecutar", action="store_true", help="Crea los talonarios deducidos.")
        parser.add_argument("--tipo", choices=["NACIMIENTO", "DEFUNCION", "todos"], default="todos")
        parser.add_argument("--centro", type=int, default=None, help="Limita a un centro (id).")
        parser.add_argument("--anio", type=int, default=None, help="Limita al año del evento.")
        parser.add_argument("--tolerancia", type=int, default=10,
                            help="Hueco máximo entre números consecutivos de una misma serie (def. 10).")
        parser.add_argument("--min-usados", type=int, default=3,
                            help="Mínimo de certificados usados por serie (def. 3).")
        parser.add_argument("--densidad", type=float, default=0.5,
                            help="Densidad mínima usados/extensión (def. 0.5; 0 = sin filtro).")
        parser.add_argument("--redondeo", type=int, default=0,
                            help="Estira cada extremo hacia el corte de decena más cercano, "
                                 "hasta N números, sin pisar números usados (0 = apagado, def. 0).")
        parser.add_argument("--responsable-recibe", default="Por confirmar",
                            help="Responsable que recibe (el legacy no lo guardó).")
        parser.add_argument("--responsable-entrega", default="", help="Responsable que entrega.")

    def handle(self, *args, **opts):
        tipos = list(MODELO_POR_TIPO) if opts["tipo"] == "todos" else [opts["tipo"]]
        organizaciones = None
        if opts["centro"]:
            organizaciones = {opts["centro"]}
            if not Organizacion.objects.filter(pk=opts["centro"]).exists():
                self.stderr.write(self.style.ERROR(f"No existe la organización {opts['centro']}."))
                return

        creados = 0
        for tipo in tipos:
            modelo = MODELO_POR_TIPO[tipo]
            # Los talonarios ya registrados se cargan una vez: consultar `exists()`
            # por candidato eran ~12.000 consultas (~30 s).
            existentes = {}
            qs_tal = Talonario.objects.filter(tipo=tipo)
            if organizaciones is not None:
                qs_tal = qs_tal.filter(centro_id__in=organizaciones)
            for centro_id, desde, hasta in qs_tal.values_list("centro_id", "serie_desde", "serie_hasta"):
                existentes.setdefault(centro_id, []).append((desde, hasta))
            candidatas = series_deducidas(
                modelo,
                tolerancia=opts["tolerancia"],
                min_usados=opts["min_usados"],
                densidad_minima=opts["densidad"],
                organizaciones=organizaciones,
                anio=opts["anio"],
                margen_redondeo=max(0, min(9, opts["redondeo"])),
            )
            self.stdout.write(f"{tipo}: {len(candidatas)} series candidatas.")
            for c in candidatas:
                cubierta = any(
                    d <= c["serie_desde"] and h >= c["serie_hasta"]
                    for d, h in existentes.get(c["centro_id"], [])
                )
                if cubierta:
                    continue
                sufijo = ""
                if c["redondeado"]:
                    sufijo = (f" [redondeado; observado "
                              f"{c['serie_desde_observada']}-{c['serie_hasta_observada']}"
                              f", densidad obs. {c['densidad_observada']}]")
                self.stdout.write(
                    f"  {c['centro']}: {c['serie_desde']}-{c['serie_hasta']} "
                    f"({c['usados']} usados, densidad {c['densidad']}, "
                    f"{c['fecha_desde']}..{c['fecha_hasta']}){sufijo}"
                )
                if not opts["ejecutar"]:
                    continue
                Talonario.objects.create(
                    tipo=tipo,
                    centro_id=c["centro_id"],
                    fecha_entrega=c["fecha_desde"],
                    serie_desde=c["serie_desde"],
                    serie_hasta=c["serie_hasta"],
                    responsable_recibe=opts["responsable_recibe"],
                    responsable_entrega=opts["responsable_entrega"],
                    observaciones=(
                        f"Deducido de la BD: {c['usados']} certificados usados entre "
                        f"{c['fecha_desde']} y {c['fecha_hasta']}."
                    ),
                )
                creados += 1

        if opts["ejecutar"]:
            self.stdout.write(self.style.SUCCESS(f"Talonarios creados: {creados}."))
        else:
            self.stdout.write("Dry-run: no se creó nada. Use --ejecutar para aplicar.")
