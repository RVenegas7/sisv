from django.db import models


class CIE10(models.Model):
    ORIGEN_OMS = "OMS"
    ORIGEN_LEGACY = "LEGACY"
    ORIGEN_CHOICES = [
        (ORIGEN_OMS, "OMS/OPS"),
        (ORIGEN_LEGACY, "Legacy (SISMAI)"),
    ]

    codigo = models.CharField("Código", max_length=10, unique=True)
    descripcion = models.CharField("Descripción", max_length=500)
    capitulo = models.CharField("Capítulo", max_length=300, blank=True)
    origen = models.CharField("Origen", max_length=10, choices=ORIGEN_CHOICES, default=ORIGEN_OMS)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "CIE-10"
        verbose_name_plural = "CIE-10"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class CIE11(models.Model):
    NIVEL_CAPITULO = 1
    NIVEL_BLOQUE = 2
    NIVEL_CATEGORIA = 3
    NIVEL_SUBGRUPO = 4
    NIVEL_CHOICES = [
        (NIVEL_CAPITULO, "Capítulo"),
        (NIVEL_BLOQUE, "Bloque"),
        (NIVEL_CATEGORIA, "Categoría"),
        (NIVEL_SUBGRUPO, "Subgrupo"),
    ]

    codigo = models.CharField("Código", max_length=64)
    titulo = models.CharField("Título", max_length=500)
    padre = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="hijos",
        verbose_name="Nodo padre",
    )
    capitulo = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="items",
        limit_choices_to={"nivel": NIVEL_CAPITULO},
        verbose_name="Capítulo",
    )
    nivel = models.PositiveSmallIntegerField("Nivel", choices=NIVEL_CHOICES, db_index=True)
    requiere_subgrupo = models.BooleanField("Requiere subgrupo obligatorio", default=False)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "CIE-11"
        verbose_name_plural = "CIE-11"
        ordering = ["nivel", "codigo"]
        constraints = [
            models.UniqueConstraint(fields=["codigo", "padre"], name="uq_cie11_codigo_padre"),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"


class MapeoCIE(models.Model):
    TIPO_EXACTO = "EXA"
    TIPO_PARCIAL = "PAR"
    TIPO_INEXACTO = "INE"
    TIPO_CHOICES = [
        (TIPO_EXACTO, "Exacto"),
        (TIPO_PARCIAL, "Parcial"),
        (TIPO_INEXACTO, "Inexacto"),
    ]

    cie10 = models.ForeignKey(CIE10, on_delete=models.CASCADE, related_name="mapeos")
    cie11 = models.ForeignKey(CIE11, on_delete=models.CASCADE, related_name="mapeos")
    tipo = models.CharField("Tipo de equivalencia", max_length=3, choices=TIPO_CHOICES, default=TIPO_EXACTO)
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        verbose_name = "Equivalencia CIE-10 <-> CIE-11"
        verbose_name_plural = "Equivalencias CIE-10 <-> CIE-11"
        constraints = [
            models.UniqueConstraint(fields=["cie10", "cie11"], name="uq_mapeo_cie10_cie11"),
        ]

    def __str__(self):
        return f"{self.cie10} <-> {self.cie11} ({self.get_tipo_display()})"