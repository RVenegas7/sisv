from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

GRUPOS_ETARIOS = [
    ("menor_1", "< 1 año"),
    ("de_1_4", "1 a 4 años"),
    ("de_5_6", "5 a 6 años"),
    ("de_7_9", "7 a 9 años"),
    ("de_10_11", "10 a 11 años"),
    ("de_12_14", "12 a 14 años"),
    ("de_15_19", "15 a 19 años"),
    ("de_20_24", "20 a 24 años"),
    ("de_25_44", "25 a 44 años"),
    ("de_45_59", "45 a 59 años"),
    ("de_60_64", "60 a 64 años"),
    ("de_65", "65 años y más"),
    ("edad_ignorada", "Edad ignorada"),
]

SEXOS = [("h", "Hombres"), ("m", "Mujeres")]

GRUPO_LABEL = dict(GRUPOS_ETARIOS)

# Columnas H/M por grupo (<1H, <1M, 1-4H, 1-4M, …).
CAMPOS_COLUMNA = [(g, s) for g, _ in GRUPOS_ETARIOS for s, _ in SEXOS]


def columna(grupo, sexo):
    return f"{grupo}_{sexo}"


class EventoENO(models.Model):
    """Catálogo de Enfermedades y Eventos de Notificación Obligatoria del MPPS.

    Se preserva la numeración oficial del formulario (orden 1..114 del EPI-12
    y 1..107 del EPI-14, incluyendo el anexo de enfermedades micóticas).
    """

    GRUPO_CHOICES = [
        ("TRANSMISIBLES", "Transmisibles"),
        ("IRA", "Infecciones respiratorias agudas"),
        ("IRS", "Infecciones respiratorias / síndromes"),
        ("ITS", "Infecciones de transmisión sexual"),
        ("CARGAS", "Cargas / crónicas no transmisibles"),
        ("MATERNO_INFANTIL", "Materno infantil"),
        ("MICOTICAS", "Enfermedades micóticas"),
        ("OTRO", "Otro"),
    ]
    NOTIFICACION_INMEDIATA = "INMEDIATA"
    NOTIFICACION_SEMANAL = "SEMANAL"
    NOTIFICACION_CHOICES = [
        (NOTIFICACION_INMEDIATA, "Inmediata"),
        (NOTIFICACION_SEMANAL, "Semanal"),
    ]

    codigo_evento = models.CharField("Código interno", max_length=60, unique=True)
    nombre = models.CharField("Enfermedad / Evento", max_length=300)
    orden_epi12 = models.PositiveSmallIntegerField("Orden EPI-12", null=True, blank=True)
    orden_epi14 = models.PositiveSmallIntegerField("Orden EPI-14", null=True, blank=True)
    en_epi12 = models.BooleanField("En EPI-12 (morbilidad)", default=False)
    en_epi14 = models.BooleanField("En EPI-14 (mortalidad)", default=False)
    codigos_cie11 = models.CharField("Códigos CIE-11", max_length=200, blank=True)
    codigos_cie10 = models.CharField("Códigos CIE-10 (si hay mapeo)", max_length=200, blank=True)
    notificacion = models.CharField(
        "Tipo de notificación", max_length=10, choices=NOTIFICACION_CHOICES, default=NOTIFICACION_SEMANAL
    )
    grupo = models.CharField("Grupo", max_length=20, choices=GRUPO_CHOICES, default="OTRO")
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Evento ENO"
        verbose_name_plural = "Eventos ENO (notificación obligatoria)"
        ordering = ["orden_epi12", "orden_epi14", "nombre"]

    def __str__(self):
        return f"({self.orden_epi12 or self.orden_epi14 or '—'}) {self.nombre}"


class ConsolidadoSemanal(models.Model):
    TIPO_MORBILIDAD = "MORBILIDAD"
    TIPO_MORTALIDAD = "MORTALIDAD"
    TIPO_CHOICES = [
        (TIPO_MORBILIDAD, "Morbilidad (EPI-12)"),
        (TIPO_MORTALIDAD, "Mortalidad (EPI-14)"),
    ]
    ESTADO_BORRADOR = "BORRADOR"
    ESTADO_ENVIADO = "ENVIADO"
    ESTADO_CERRADO = "CERRADO"
    ESTADO_CHOICES = [
        (ESTADO_BORRADOR, "Borrador"),
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_CERRADO, "Cerrado"),
    ]
    ORIGEN_PROPIO = "PROPIO"
    ORIGEN_CONSOLIDADO = "CONSOLIDADO_SUPERIOR"
    ORIGEN_CHOICES = [
        (ORIGEN_PROPIO, "Propio del establecimiento"),
        (ORIGEN_CONSOLIDADO, "Suma de organizaciones dependientes"),
    ]

    organizacion = models.ForeignKey(
        "seguridad.Organizacion",
        on_delete=models.PROTECT,
        related_name="consolidados_semanales",
        verbose_name="Organización / establecimiento",
    )
    anio = models.PositiveSmallIntegerField("Año")
    semana = models.PositiveSmallIntegerField("Semana epidemiológica (1-53)")
    tipo = models.CharField("Tipo de consolidado", max_length=10, choices=TIPO_CHOICES)
    estado = models.CharField("Estado", max_length=10, choices=ESTADO_CHOICES, default=ESTADO_BORRADOR)
    origen = models.CharField("Origen", max_length=22, choices=ORIGEN_CHOICES, default=ORIGEN_PROPIO)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="consolidados_semanales",
        verbose_name="Creado por",
    )
    enviado_en = models.DateTimeField("Enviado en", null=True, blank=True)
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)
    actualizado_en = models.DateTimeField("Actualizado en", auto_now=True)

    class Meta:
        verbose_name = "Consolidado semanal"
        verbose_name_plural = "Consolidados semanales"
        ordering = ["-anio", "-semana", "tipo"]
        constraints = [
            models.UniqueConstraint(
                fields=["organizacion", "anio", "semana", "tipo"],
                name="uq_consolidado_semanal",
            )
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.anio}-S{self.semana:02d} @ {self.organizacion}"

    def clean(self):
        super().clean()
        if not (1 <= self.semana <= 53):
            raise ValidationError({"semana": "La semana debe estar entre 1 y 53."})


class FilaConsolidado(models.Model):
    """Matriz eventos × grupos de edad × sexo, 1:1 con la fila del formulario.

    Regla oficial: cuando la edad es ignorada el conteo se anota en la columna
    Hombres (campo `edad_ignorada_h`); `edad_ignorada_m` queda reservado (0).
    """

    consolidado = models.ForeignKey(
        ConsolidadoSemanal, on_delete=models.CASCADE, related_name="filas"
    )
    evento = models.ForeignKey(EventoENO, on_delete=models.PROTECT, related_name="filas_consolidado")
    menor_1_h = models.PositiveIntegerField("<1 H", default=0)
    menor_1_m = models.PositiveIntegerField("<1 M", default=0)
    de_1_4_h = models.PositiveIntegerField("1-4 H", default=0)
    de_1_4_m = models.PositiveIntegerField("1-4 M", default=0)
    de_5_6_h = models.PositiveIntegerField("5-6 H", default=0)
    de_5_6_m = models.PositiveIntegerField("5-6 M", default=0)
    de_7_9_h = models.PositiveIntegerField("7-9 H", default=0)
    de_7_9_m = models.PositiveIntegerField("7-9 M", default=0)
    de_10_11_h = models.PositiveIntegerField("10-11 H", default=0)
    de_10_11_m = models.PositiveIntegerField("10-11 M", default=0)
    de_12_14_h = models.PositiveIntegerField("12-14 H", default=0)
    de_12_14_m = models.PositiveIntegerField("12-14 M", default=0)
    de_15_19_h = models.PositiveIntegerField("15-19 H", default=0)
    de_15_19_m = models.PositiveIntegerField("15-19 M", default=0)
    de_20_24_h = models.PositiveIntegerField("20-24 H", default=0)
    de_20_24_m = models.PositiveIntegerField("20-24 M", default=0)
    de_25_44_h = models.PositiveIntegerField("25-44 H", default=0)
    de_25_44_m = models.PositiveIntegerField("25-44 M", default=0)
    de_45_59_h = models.PositiveIntegerField("45-59 H", default=0)
    de_45_59_m = models.PositiveIntegerField("45-59 M", default=0)
    de_60_64_h = models.PositiveIntegerField("60-64 H", default=0)
    de_60_64_m = models.PositiveIntegerField("60-64 M", default=0)
    de_65_h = models.PositiveIntegerField("65+ H", default=0)
    de_65_m = models.PositiveIntegerField("65+ M", default=0)
    edad_ignorada_h = models.PositiveIntegerField("Edad ignorada (Hombres)", default=0)
    edad_ignorada_m = models.PositiveIntegerField("Edad ignorada (Mujeres)", default=0)

    class Meta:
        verbose_name = "Fila del consolidado"
        verbose_name_plural = "Filas del consolidado"
        ordering = ["evento__orden_epi12", "evento__orden_epi14"]
        constraints = [
            models.UniqueConstraint(
                fields=["consolidado", "evento"], name="uq_fila_consolidado_evento"
            )
        ]

    def __str__(self):
        return f"{self.consolidado} — {self.evento.nombre}"

    def total_hombres(self):
        return sum(getattr(self, f"{g[0]}_h") for g in GRUPOS_ETARIOS)

    total_hombres.short_description = "Total hombres"

    def total_mujeres(self):
        return sum(getattr(self, f"{g[0]}_m") for g in GRUPOS_ETARIOS)

    total_mujeres.short_description = "Total mujeres"

    @property
    def total(self):
        return self.total_hombres() + self.total_mujeres()


class SituacionEspecial(models.Model):
    TIPO_CHOICES = [
        ("QUIMICO", "Químico"),
        ("RADIONUCLEAR", "Radionuclear"),
        ("EN_ANIMALES", "En animales"),
        ("DESASTRE_NATURAL", "Desastre natural"),
        ("ALIMENTARIO", "Alimentario"),
        ("INFECCIOSO", "Infeccioso"),
        ("INDETERMINADO", "Indeterminado"),
    ]

    consolidado = models.ForeignKey(
        ConsolidadoSemanal, on_delete=models.CASCADE, related_name="situaciones_especiales"
    )
    tipo_evento = models.CharField("Tipo de evento", max_length=18, choices=TIPO_CHOICES)
    comunidad = models.CharField("Comunidad", max_length=200, blank=True)
    casos = models.PositiveIntegerField("Casos", default=0)
    muertes = models.PositiveIntegerField("Muertes", default=0)
    descripcion = models.TextField("Descripción del evento", blank=True)
    medidas_tomadas = models.TextField("Medidas tomadas", blank=True)

    class Meta:
        verbose_name = "Situación especial"
        verbose_name_plural = "Situaciones especiales"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.get_tipo_evento_display()} @ {self.consolidado}"


class AlertaEpidemia(models.Model):
    CLASE_ALERTA = "ALERTA"
    CLASE_EPIDEMIA = "EPIDEMIA"
    CLASE_CHOICES = [
        (CLASE_ALERTA, "Situación de alerta"),
        (CLASE_EPIDEMIA, "Situación de epidemia"),
    ]

    consolidado = models.ForeignKey(
        ConsolidadoSemanal, on_delete=models.CASCADE, related_name="alertas_epidemias"
    )
    clase = models.CharField("Clase", max_length=10, choices=CLASE_CHOICES)
    evento = models.ForeignKey(
        EventoENO, null=True, blank=True, on_delete=models.SET_NULL, related_name="alertas_epidemias"
    )
    enfermedad = models.CharField("Enfermedad", max_length=200, blank=True)
    casos = models.PositiveIntegerField("Casos", default=0)
    muertes = models.PositiveIntegerField("Muertes", default=0)
    grave = models.BooleanField("Grave", default=False)
    inusitado = models.BooleanField("Inusitado", default=False)
    impacto_nacional = models.BooleanField("Impacto nacional", default=False)
    fecha_inicio = models.DateField("Fecha de inicio", null=True, blank=True)
    fecha_fin = models.DateField("Fecha fin", null=True, blank=True)
    unidad_geografica = models.CharField("Unidad geográfica", max_length=200, blank=True)
    unidad_sanitaria = models.CharField("Unidad sanitaria", max_length=200, blank=True)

    class Meta:
        verbose_name = "Alerta / epidemia"
        verbose_name_plural = "Alertas / epidemias"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.get_clase_display()}: {self.enfermedad or self.evento} @ {self.consolidado}"