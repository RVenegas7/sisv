"""Auditoría de calidad del número físico del certificado y los nombres (§35).

Informe **de solo lectura** sobre lo que la propia BD refleja del legacy: el número físico
del certificado (``numero_certificado`` en defunción, ``numero_planilla`` en nacimiento)
y los nombres de las personas. Detecta:

- **duplicados** por número real (el legacy reutilizaba el número físico),
- **números mal formados** (no numéricos) y **números que son la fecha del evento**,
- **nombres con dígitos incrustados** (tecleo/OCR sin validación).

Dos identificadores que no hay que confundir:

- ``registro_numero`` = ``LEG-CERT-{ID}`` / ``LEG-RN-{ID}`` → la **clave interna** de Oracle
  (no sirve para buscar el papel).
- ``numero_certificado`` / ``numero_planilla`` = ``CERTIFICADO."NUMEROMSDS"`` /
  ``CERTNACIMIENTO."NROPLANILLA"`` → el **número impreso**, el que el personal busca en el
  físico y en el sistema. Por eso **todos** los CSV lo muestran (§35, 15/10/2026).

La cédula que acompaña a cada certificado sale de la persona del hecho: ``fallecido_cedula``
(defunción) y ``madre_cedula`` (nacimiento). ⚠ En nacimientos **no** se usa
``CERTNACIMIENTO."CEDULA"``/``"NOMBRES"``: esa columna trae los datos del **personal que
llenó** el certificado (médicos/registradores; la misma cédula aparece cientos de veces), no
de la madre. La madre vive en ``NAC_MADRE``.

El duplicado se informa por número y se **distingue por cédula**: el mismo número con la misma
cédula es un registro repetido; el mismo número con cédulas distintas es un número reutilizado
en personas diferentes.

No corrige nada: describe, para decidir. ``--csv`` escribe los detalles en una carpeta.
"""

import csv
import os

from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from registros.calidad import numero_es_fecha
from registros.models import Defuncion, Nacimiento

MODULOS = {
    "defunciones": {
        "modelo": Defuncion,
        "campo_numero": "numero_certificado",
        "campo_cedula": "fallecido_cedula",
        # Persona del certificado: el fallecido.
        "grupos_persona": (("fallecido_nombres", "fallecido_apellidos"),),
        "campos_nombre": ("fallecido_nombres", "fallecido_apellidos", "madre_nombres"),
    },
    "nacimientos": {
        "modelo": Nacimiento,
        "campo_numero": "numero_planilla",
        "campo_cedula": "madre_cedula",
        # Persona del certificado: el recién nacido; si el legacy no lo trae, la madre.
        "grupos_persona": (
            ("nino_nombres", "nino_apellidos"),
            ("madre_nombres", "madre_apellidos"),
        ),
        "campos_nombre": ("nino_nombres", "nino_apellidos", "madre_nombres", "padre_nombres"),
    },
}


def _texto(valor):
    return (valor or "").strip()


def _persona(registro, cfg):
    """Nombre de la persona del certificado (recién nacido, y si no, la madre)."""
    for grupo in cfg["grupos_persona"]:
        partes = [_texto(getattr(registro, c)) for c in grupo]
        partes = [p for p in partes if p]
        if partes:
            return " ".join(partes)
    return ""


def _cedula(registro, cfg):
    return _texto(getattr(registro, cfg["campo_cedula"], ""))


def _centro(registro):
    return registro.organizacion.nombre if registro.organizacion_id else ""


def _escribir_csv(ruta, cabecera, filas):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabecera)
        escritor.writerows(filas)


class Command(BaseCommand):
    help = "Informe de duplicados, números mal formados y nombres raros (§35)."

    def add_arguments(self, parser):
        parser.add_argument("--modulo", choices=[*MODULOS, "todos"], default="todos")
        parser.add_argument("--csv", dest="carpeta",
                            help="Carpeta destino de los CSV del detalle.")
        parser.add_argument("--limite", type=int, default=20,
                            help="Filas de muestra por categoría en la consola (0 = todas).")

    def handle(self, *args, **options):
        modulos = MODULOS if options["modulo"] == "todos" else {
            options["modulo"]: MODULOS[options["modulo"]]}
        limite = options["limite"] or None
        if options["carpeta"]:
            os.makedirs(options["carpeta"], exist_ok=True)

        for nombre, cfg in modulos.items():
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n=== {nombre} ==="))
            self._un_modulo(nombre, cfg, options.get("carpeta"), limite)

    def _un_modulo(self, nombre, cfg, carpeta, limite):
        modelo = cfg["modelo"]
        campo = cfg["campo_numero"]
        campo_cedula = cfg["campo_cedula"]
        campos_nombre = cfg["campos_nombre"]
        total = modelo.objects.count()
        self.stdout.write(f"Registros: {total:,}")

        # --- 1. Duplicados por número real -------------------------------------
        duplicados = list(
            modelo.objects.exclude(**{campo: ""})
            .values(campo)
            .annotate(n=Count("id"))
            .filter(n__gt=1)
            .order_by("-n", campo)
        )
        filas_excedentes = sum(d["n"] - 1 for d in duplicados)
        self.stdout.write(
            f"Duplicados: {len(duplicados):,} números repetidos "
            f"({filas_excedentes:,} filas de más)."
        )
        filas_dup = []
        mismo = distinto = sin_cedula = 0
        for d in duplicados:
            registros = list(
                modelo.objects.filter(**{campo: d[campo]})
                .only("id", "registro_numero", "fecha_evento", "organizacion", campo, campo_cedula,
                      *(c for g in cfg["grupos_persona"] for c in g))
            )
            cedulas = {_cedula(r, cfg) for r in registros}
            cedulas.discard("")
            if not cedulas:
                sin_cedula += 1
            elif len(cedulas) == 1:
                mismo += 1
            else:
                distinto += 1
            for r in registros:
                filas_dup.append([
                    _texto(getattr(r, campo)), d["n"], r.id, r.registro_numero or "",
                    _cedula(r, cfg), _persona(r, cfg),
                    str(r.fecha_evento or ""), _centro(r),
                ])
        if duplicados:
            self.stdout.write(
                f"  · {mismo:,} con la misma cédula (registro repetido) · "
                f"{distinto:,} con cédulas distintas (número reutilizado) · "
                f"{sin_cedula:,} sin cédula."
            )
            for d in duplicados[:limite]:
                self.stdout.write(f"  · {d[campo]} × {d['n']}")
        if carpeta:
            _escribir_csv(
                os.path.join(carpeta, f"dup_{nombre}.csv"),
                ["Numero", "Veces", "ID", "Registro", "Cedula", "Persona", "Fecha", "Centro"],
                filas_dup,
            )

        # --- 2. Números mal formados ------------------------------------------
        malos = list(
            modelo.objects.exclude(**{campo: ""})
            .exclude(**{f"{campo}__regex": r"^\d+$"})
            .only("id", "registro_numero", "fecha_evento", campo, campo_cedula, "organizacion")
        )
        como_fecha = [r for r in malos if numero_es_fecha(
            getattr(r, campo), r.fecha_evento)]
        self.stdout.write(
            f"Números no numéricos: {len(malos):,} "
            f"(de ellos, {len(como_fecha)} son la fecha del evento)."
        )
        for r in malos[:limite]:
            self.stdout.write(f"  · id={r.id} nº={getattr(r, campo)!r}")
        if carpeta:
            _escribir_csv(
                os.path.join(carpeta, f"numeros_raros_{nombre}.csv"),
                ["Numero", "PareceFecha", "ID", "Registro", "Cedula", "Fecha", "Centro"],
                [[_texto(getattr(r, campo)),
                  "si" if numero_es_fecha(getattr(r, campo), r.fecha_evento) else "",
                  r.id, r.registro_numero or "", _cedula(r, cfg),
                  str(r.fecha_evento or ""), _centro(r)]
                 for r in malos],
            )

        # --- 3. Nombres con dígitos incrustados --------------------------------
        cond = Q()
        for c in campos_nombre:
            cond |= Q(**{f"{c}__regex": r"\d"})
        raros = list(
            modelo.objects.filter(cond).only(
                "id", "registro_numero", "fecha_evento", "organizacion",
                campo, campo_cedula, *campos_nombre)
        )
        self.stdout.write(f"Nombres con dígitos: {len(raros):,} registros.")
        for r in raros[:limite]:
            detalle = " | ".join(f"{c}={getattr(r, c)!r}" for c in campos_nombre
                                 if any(ch.isdigit() for ch in getattr(r, c) or ""))
            self.stdout.write(f"  · nº={_texto(getattr(r, campo)) or '(sin número)'} id={r.id} {detalle}")
        if carpeta:
            _escribir_csv(
                os.path.join(carpeta, f"nombres_raros_{nombre}.csv"),
                ["Numero", "ID", "Registro", "Cedula", "Fecha", "Centro", *campos_nombre],
                [[_texto(getattr(r, campo)), r.id, r.registro_numero or "", _cedula(r, cfg),
                  str(r.fecha_evento or ""), _centro(r),
                  *(_texto(getattr(r, c)) for c in campos_nombre)] for r in raros],
            )
