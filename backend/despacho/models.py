"""Despacho de talonarios de certificados de nacimiento y defunción.

El SISMAI legacy **no guardó nunca la entrega** de talonarios (las tablas
`sismai.NUMERO_BD` y `sismai.HISTORICO_IDS`, que habrían tenido las series
`NATA_IDS`/`MORT_IDS` y el consecutivo, están vacías). Por eso este control se
construye desde cero en SISV: cada `Talonario` es una entrega física de una serie
continua a un centro, y el uso de esos certificados se deduce cruzando la serie
contra `registros.Nacimiento`/`registros.Defuncion`.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Talonario(models.Model):
    TIPO_NACIMIENTO = "NACIMIENTO"
    TIPO_DEFUNCION = "DEFUNCION"
    TIPO_CHOICES = [
        (TIPO_NACIMIENTO, "Nacimiento"),
        (TIPO_DEFUNCION, "Defunción"),
    ]

    tipo = models.CharField("Tipo de certificado", max_length=12, choices=TIPO_CHOICES)
    centro = models.ForeignKey(
        "seguridad.Organizacion",
        on_delete=models.PROTECT,
        related_name="talonarios",
        verbose_name="Centro médico",
    )
    fecha_entrega = models.DateField("Fecha de entrega")
    serie_desde = models.PositiveIntegerField("Serie desde")
    serie_hasta = models.PositiveIntegerField("Serie hasta")
    cantidad = models.PositiveIntegerField("Cantidad entregada", editable=False, default=0)
    responsable_recibe = models.CharField("Responsable que recibe", max_length=200)
    responsable_entrega = models.CharField("Responsable que entrega", max_length=200, blank=True, default="")
    observaciones = models.TextField("Observaciones", blank=True, default="")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Registrado por",
    )
    creado_en = models.DateTimeField("Registrado en", auto_now_add=True)

    class Meta:
        verbose_name = "Talonario despachado"
        verbose_name_plural = "Talonarios despachados"
        ordering = ["-fecha_entrega", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["centro", "tipo", "serie_desde", "serie_hasta"],
                name="talonario_unico_por_serie",
            ),
            models.CheckConstraint(
                condition=models.Q(serie_hasta__gte=models.F("serie_desde")),
                name="talonario_serie_valida",
            ),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.serie_desde}-{self.serie_hasta} ({self.centro})"

    def clean(self):
        if self.serie_desde and self.serie_hasta and self.serie_hasta < self.serie_desde:
            raise ValidationError({"serie_hasta": "La serie hasta no puede ser menor que la serie desde."})

    def save(self, *args, **kwargs):
        if self.serie_desde and self.serie_hasta and self.serie_hasta >= self.serie_desde:
            self.cantidad = self.serie_hasta - self.serie_desde + 1
        super().save(*args, **kwargs)


class NovedadCertificado(models.Model):
    """Excepción sobre un certificado de la serie (no es una fila por certificado).

    El estado normal es «sin asignar» (entregado y todavía sin usar); solo se
    registran aquí los casos que rompen la serie: dañado, en tránsito o devuelto.
    El uso (certificado cargado) se deduce automáticamente contra la BD.
    """

    ESTADO_DANADO = "DANADO"
    ESTADO_EN_TRANSITO = "EN_TRANSITO"
    ESTADO_DEVUELTO = "DEVUELTO"
    ESTADO_CHOICES = [
        (ESTADO_DANADO, "Dañado"),
        (ESTADO_EN_TRANSITO, "En tránsito"),
        (ESTADO_DEVUELTO, "Devuelto"),
    ]

    talonario = models.ForeignKey(
        Talonario,
        on_delete=models.CASCADE,
        related_name="novedades",
        verbose_name="Talonario",
    )
    numero = models.PositiveIntegerField("Número del certificado")
    estado = models.CharField("Estatus", max_length=15, choices=ESTADO_CHOICES)

    justificacion_numero = models.CharField("Nº de acta de justificación", max_length=50, blank=True, default="")
    justificacion_fecha = models.DateField("Fecha del acta de justificación", null=True, blank=True)

    transitado_nombres = models.CharField("Nombres (en tránsito)", max_length=150, blank=True, default="")
    transitado_apellidos = models.CharField("Apellidos (en tránsito)", max_length=150, blank=True, default="")
    fecha_salio_centro = models.DateField("Fecha en que salió del centro", null=True, blank=True)

    observaciones = models.TextField("Observaciones", blank=True, default="")

    class Meta:
        verbose_name = "Novedad de certificado"
        verbose_name_plural = "Novedades de certificados"
        ordering = ["talonario", "numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["talonario", "numero"],
                name="novedad_unica_por_certificado",
            ),
        ]

    def __str__(self):
        return f"{self.talonario_id}: #{self.numero} {self.get_estado_display()}"
