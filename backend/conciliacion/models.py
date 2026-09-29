from django.db import models
from django.utils import timezone

TIPO_CHOICES = [
    ("MORBILIDAD", "Morbilidad"),
    ("MORTALIDAD", "Mortalidad"),
]

ESTADO_CHOICES = [
    ("CUADRA", "Cuadra"),
    ("DIFERENCIA", "Diferencia"),
    ("SOLO_CRUDO", "Solo en el crudo"),
    ("SOLO_SISV", "Solo en SISV"),
    ("EXCLUIDO_EN_ETL", "Excluido por diseño del ETL"),
]

RESOLUCION_CHOICES = [
    ("CONCILIADO", "Conciliado"),
    ("CENTRO_SIN_ORG", "Centro sin organización"),
    ("CENTRO_SIN_ORG_Y_EVENTO_SIN_EQUIVALENTE", "Centro sin organización y evento sin equivalente"),
    ("EVENTO_SIN_EQUIVALENTE", "Evento sin equivalente ENO"),
    ("PSEUDO_TOTAL_EXCLUIDO", "Fila de total excluida por diseño"),
    ("SIN_FUENTE_EN_CRUDO", "Sin fuente en el crudo"),
]


class ConciliacionENO(models.Model):
    """Diferencia entre lo transcrito en el legacy y lo que SISV consolidó.

    El grano es **(año, semana, tipo, organización, enfermedad legacy)**, que es
    exactamente el grano de `ConsolidadoSemanal` + `FilaConsolidado`. Así el lado
    `sisv_*` es exacto y la diferencia es interpretable sin repartir nada.

    El detalle por centro vive en `ConciliacionENOCentro`: la conciliación agrupa
    porque **el ETL consolida por organización**, no por establecimiento, y cuando
    varios establecimientos legacy caen en la misma organización sus casos se suman
    en una sola fila. Por eso la fila lleva `cantidad_centros` y `colision`.
    """

    anio = models.SmallIntegerField("Año", db_index=True)
    semana = models.SmallIntegerField("Semana epidemiológica", db_index=True)
    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES)

    organizacion = models.ForeignKey(
        "seguridad.Organizacion",
        on_delete=models.CASCADE,
        related_name="conciliaciones_eno",
        verbose_name="Organización",
    )
    evento = models.ForeignKey(
        "vigilancia.EventoENO",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conciliaciones_eno",
        verbose_name="Evento ENO",
        help_text="Vacío si la enfermedad legacy no tiene equivalente en el catálogo ENO.",
    )

    legado_enfermedad_id = models.BigIntegerField("ID enfermedad legacy", db_index=True)
    legado_enfermedad_codigo = models.CharField("Código legacy", max_length=30, blank=True)
    legado_enfermedad_nombre = models.CharField("Enfermedad legacy", max_length=300, blank=True)
    es_pseudo_total = models.BooleanField(
        "Es fila de total",
        default=False,
        help_text="Filas 'TOTAL DE PACIENTES...' del catálogo legacy: no son enfermedades.",
    )

    cantidad_centros = models.PositiveIntegerField("Centros legacy", default=1)
    colision = models.BooleanField(
        "Varios centros en la misma organización",
        default=False,
        help_text="Más de un establecimiento legacy consolidó en esta misma organización.",
    )

    crudo_h = models.IntegerField("Casos crudos hombres", default=0)
    crudo_m = models.IntegerField("Casos crudos mujeres", default=0)
    sisv_h = models.IntegerField("Casos SISV hombres", default=0)
    sisv_m = models.IntegerField("Casos SISV mujeres", default=0)
    diferencia_h = models.IntegerField("Diferencia hombres", default=0)
    diferencia_m = models.IntegerField("Diferencia mujeres", default=0)

    estado = models.CharField("Estado", max_length=16, choices=ESTADO_CHOICES, db_index=True)
    resolucion = models.CharField("Resolución", max_length=45, choices=RESOLUCION_CHOICES)
    calculado_en = models.DateTimeField("Calculado en", default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Conciliación ENO"
        verbose_name_plural = "Conciliaciones ENO"
        unique_together = ("anio", "semana", "tipo", "organizacion", "legado_enfermedad_id")
        ordering = ("anio", "semana", "tipo", "organizacion_id", "legado_enfermedad_id")
        indexes = [models.Index(fields=["anio", "semana", "estado"])]

    def __str__(self):
        return f"{self.anio} S{self.semana:02d} {self.tipo} {self.organizacion_id} [{self.legado_enfermedad_id}]"


class ConciliacionENOCentro(models.Model):
    """Detalle por establecimiento legacy: qué reportó cada centro y dónde acabó.

    Es el grano que pide la oficina (**centro + evento**). `sisv_h`/`sisv_m` se
    rellenan solo cuando la organización hospeda **un único** establecimiento legacy:
    si comparten organización, SISV guarda la suma de varios y no se puede repartir
    sin inventar, así que quedan en `NULL` y se marca `colision`.
    """

    conciliacion = models.ForeignKey(
        ConciliacionENO,
        on_delete=models.CASCADE,
        related_name="centros",
        verbose_name="Conciliación",
    )
    legado_establecimiento_id = models.BigIntegerField("ID establecimiento legacy", db_index=True)
    legado_establecimiento_nombre = models.CharField(
        "Establecimiento legacy", max_length=200, blank=True
    )
    legado_documento = models.BigIntegerField(
        "ID documento legacy",
        null=True,
        blank=True,
        db_index=True,
        help_text="Es único por centro+semana+tipo: identifica laHoja semanal que reportó el centro.",
    )
    transcrito_por = models.CharField(
        "Transcrito por",
        max_length=30,
        blank=True,
        help_text="INSTANCIA de HISTDOC: estación de trabajo, no cuenta verificada de persona. "
                  "Vacío antes de agosto de 2019, cuando aún no se llevaba ese rastro.",
    )
    crudo_h = models.IntegerField("Casos hombres", default=0)
    crudo_m = models.IntegerField("Casos mujeres", default=0)
    sisv_h = models.IntegerField("Casos SISV hombres", null=True, blank=True)
    sisv_m = models.IntegerField("Casos SISV mujeres", null=True, blank=True)
    colision = models.BooleanField("Organización compartida", default=False)

    class Meta:
        verbose_name = "Conciliación ENO por centro"
        verbose_name_plural = "Conciliaciones ENO por centro"
        unique_together = (
            "conciliacion",
            "legado_establecimiento_id",
        )
        ordering = ("conciliacion__anio", "conciliacion__semana", "legado_establecimiento_id")

    def __str__(self):
        return f"{self.legado_establecimiento_id} {self.legado_establecimiento_nombre[:40]}"
