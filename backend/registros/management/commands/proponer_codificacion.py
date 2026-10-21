"""Propone la codificación CIE en lote y la deja ESPERANDO CONFIRMACIÓN humana.

Para qué sirve
--------------
El motor de `registros.sugerencia` calcula la propuesta en el momento, cuando el
codificador abre un certificado por su número (ver `ConsultaCertificadoView`). En una
base con ~174.000 defunciones eso significa que ningún certificado tiene propuesta
hasta que alguien lo abre: al 20/10/2026 había **0 de 174.095** con sugerencia.

Este comando adelanta ese trabajo para todos a la vez, sin cambiar el flujo: escribe
`sugerencia_codigo`/`sugerencia_titulo`/`sugerencia_origen`/`sugerencia_json`/
`sugerencia_en` y **nada más**.

Lo que este comando NO hace (a propósito)
-----------------------------------------
- **No confirma**: no toca `codificado_en` ni `codificado_por`. La confirmación es
  humana y sigue siendo una por una, como pide `codificador.md` (las reglas de
  selección de causa básica de la OMS no se automatizan).
- **No cambia `cie10`/`cie11`** ni `codificacion_pendiente`: la propuesta es un aviso
  para el codificador, no una codificación.
- Se puede volver a correr: es idempotente por registro (sin `--rehacer` no reescribe lo
  que ya tenía la misma propuesta).

Por qué el modo por defecto solo propone las fuentes fiables
------------------------------------------------------------
Medido sobre la base del 20/10/2026 (300 certificados): 283 (94 %) resolvían por
**cross-walk exacto** (`fuente` `CROSSWALK` o `CIE10-LEGACY`, ambas con score 999), que
es la traducción fiable CIE-10 → CIE-11 del código histórico. El 6 % restante **cae al
texto** y ahí hay errores clínicos graves comprobados:

    E43.X «Desnutrición proteicocalórica severa»  -> XS7N «Angustia severa»
    E86.X «Depleción del volumen»                 -> XM99E9 «Volumen catártico»
    W74.0 «Ahogamiento mortal en vivienda»        -> NF08.1 «Ahogamiento no mortal»

Esos diagnósticos no tienen mapeo en el cross-walk de la OMS y el motor elige por
coincidencia de palabras. Por eso el defecto es **solo proponer lo que viene del código
del certificado** y dejar el resto sin propuesta, para que se codifique a mano. Con
`--todo` se incluye también lo propuesto por texto (queda marcado como `CATALOGO` para
que el codificador lo revise con lupa).

Uso
---
    manage.py proponer_codificacion                  # dry-run, solo fuentes fiables
    manage.py proponer_codificacion --ejecutar
    manage.py proponer_codificacion --modelo defunciones|fichas|todas
    manage.py proponer_codificacion --limite 50
    manage.py proponer_codificacion --todo --ejecutar     # incluye lo propuesto por texto
    manage.py proponer_codificacion --rehacer --ejecutar  # recalcula lo ya propuesto
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from registros.models import Defuncion, FichaVigilancia
from registros.sugerencia import sugerir

# Solo estos campos se escriben: la propuesta no es una codificación confirmada.
CAMPOS_SUGERENCIA = [
    "sugerencia_codigo", "sugerencia_titulo", "sugerencia_origen",
    "sugerencia_json", "sugerencia_en",
]

MODELOS = {
    "defunciones": (Defuncion, "defunción", "defunciones"),
    "fichas": (FichaVigilancia, "ficha", "fichas"),
}

# Fuentes fiables del motor: ambas vienen del código legacy con score 999, no de
# coincidencia de texto. `CROSSWALK` = CIE-10 → CIE-11 por el cross-walk de la OMS;
# `CIE10-LEGACY` = el evento es anterior al corte CIE-11 y se propone el propio código
# CIE-10 del certificado (ver `sugerencia._desde_crosswalk`).
FUENTES_FIABLES = ("CROSSWALK", "CIE10-LEGACY")


class Command(BaseCommand):
    help = ("Propone la codificación CIE en lote y la deja pendiente de confirmación humana "
            "(no confirma: solo llena sugerencia_*).")

    def add_arguments(self, parser):
        parser.add_argument(
            "--modelo", default="defunciones", choices=["defunciones", "fichas", "todas"],
            help="Qué registros proponer (def. defunciones).",
        )
        parser.add_argument(
            "--ejecutar", action="store_true",
            help="Aplica los cambios. Sin esto solo informa (dry-run).",
        )
        parser.add_argument(
            "--todo", action="store_true",
            help=("Incluye también las propuestas hechas por coincidencia de texto "
                  "(fuente CATALOGO), que pueden ser clínicamente erróneas. Por defecto "
                  "solo se proponen las del cross-walk exacto."),
        )
        parser.add_argument(
            "--rehacer", action="store_true",
            help="Recalcula también los registros que ya tienen sugerencia.",
        )
        parser.add_argument(
            "--limite", type=int, default=0,
            help="Procesa como máximo N registros (0 = todos). Útil para probar.",
        )

    def handle(self, *args, **opts):
        modelos = list(MODELOS) if opts["modelo"] == "todas" else [opts["modelo"]]
        ejecutar = opts["ejecutar"]
        todo = opts["todo"]
        limite = opts["limite"]

        if not ejecutar:
            self.stdout.write(self.style.WARNING("DRY-RUN: nada se guarda.\n"))

        total_global = {"vistos": 0, "propuestos": 0, "omitidos_texto": 0,
                        "sin_propuesta": 0, "ya": 0}
        for nombre in modelos:
            self._modelo(nombre, ejecutar=ejecutar, todo=todo, limite=limite,
                         rehacer=opts["rehacer"], total=total_global)

        self.stdout.write("")
        self.stdout.write(
            f"Vistos: {total_global['vistos']} · propuestos: {total_global['propuestos']} · "
            f"omitidos por ser texto: {total_global['omitidos_texto']} · "
            f"sin propuesta: {total_global['sin_propuesta']} · ya tenían: {total_global['ya']}"
        )
        if not ejecutar:
            self.stdout.write(self.style.WARNING("Vuelve a correrlo con --ejecutar para aplicar."))
        else:
            self.stdout.write(self.style.SUCCESS(
                "Propuestas guardadas. Siguen PENDIENTES DE CONFIRMACIÓN: "
                "ninguna quedó codificada (codificado_en sin tocar)."
            ))

    def _modelo(self, nombre, *, ejecutar, todo, limite, rehacer, total):
        modelo, etiqueta, plural = MODELOS[nombre]

        # Candidatos: los que tienen algo de donde inferir un código. Un registro sin
        # causa ni código legacy no puede proponer nada (el motor devolvería null), así
        # que se excluye en la consulta. Con `--todo` también entran los que solo tienen
        # texto libre, porque ahí el motor propone por coincidencia (arriesgado).
        if nombre == "fichas":
            if todo:
                qs = modelo.objects.filter(Q(nombre_evento__gt="") | Q(sintomas__gt=""))
            else:
                # Las fichas no tienen código legacy: sin `--todo` no hay fuente fiable.
                qs = modelo.objects.none()
        elif todo:
            qs = modelo.objects.filter(Q(cie10_legacy__gt="") | Q(causa_primera_parte__gt=""))
        else:
            qs = modelo.objects.exclude(cie10_legacy="")
        if not rehacer:
            qs = qs.filter(Q(sugerencia_en__isnull=True) | Q(sugerencia_codigo=""))
        qs = qs.order_by("id")
        if limite:
            qs = qs[:limite]

        self.stdout.write(f"\n=== {plural} ===")
        contador = {"vistos": 0, "propuestos": 0, "omitidos_texto": 0,
                    "sin_propuesta": 0, "ya": 0}
        pendientes = []
        for registro in qs.iterator(chunk_size=500):
            contador["vistos"] += 1
            resultado = sugerir(registro)
            basica = resultado.get("causa_basica") or {}
            if not basica:
                contador["sin_propuesta"] += 1
                continue
            if basica.get("fuente") not in FUENTES_FIABLES and not todo:
                contador["omitidos_texto"] += 1
                continue

            # Si el código propuesto no cambió y NO se pidió rehacer, no se toca: sería
            # reescribir lo mismo. Con `--rehacer` sí se refresca la ficha completa,
            # porque la metainformación puede haber cambiado (p. ej. el `origen` de una
            # propuesta antigua que decía CATALOGO y en realidad salió del código legacy).
            if not rehacer and registro.sugerencia_codigo and registro.sugerencia_codigo == basica.get("codigo"):
                contador["ya"] += 1
                continue

            if not ejecutar:
                contador["propuestos"] += 1
                if contador["propuestos"] <= 5:
                    self.stdout.write(
                        f"  {registro.registro_numero} | {registro.cie10_legacy} -> "
                        f"{basica['codigo']} ({basica['fuente']})"
                    )
                continue

            registro.sugerencia_codigo = basica.get("codigo", "") or ""
            registro.sugerencia_titulo = (basica.get("titulo", "") or "")[:500]
            registro.sugerencia_origen = resultado.get("origen", "CATALOGO")
            registro.sugerencia_json = resultado
            registro.sugerencia_en = timezone.now()
            pendientes.append(registro)
            contador["propuestos"] += 1

            if len(pendientes) >= 1000:
                modelo.objects.bulk_update(pendientes, CAMPOS_SUGERENCIA)
                pendientes = []

        if pendientes:
            modelo.objects.bulk_update(pendientes, CAMPOS_SUGERENCIA)

        for clave in total:
            total[clave] += contador[clave]

        self.stdout.write(
            f"  vistos: {contador['vistos']} · propuestos: {contador['propuestos']} · "
            f"omitidos por texto: {contador['omitidos_texto']} · "
            f"sin propuesta: {contador['sin_propuesta']} · ya tenían: {contador['ya']}"
        )
