from django.db import models


class DivisionTerritorial(models.Model):
    NIVEL_ESTADO = "ESTADO"
    NIVEL_MUNICIPIO = "MUNICIPIO"
    NIVEL_PARROQUIA = "PARROQUIA"
    NIVEL_COMUNIDAD = "COMUNIDAD"
    NIVEL_CHOICES = [
        (NIVEL_ESTADO, "Estado"),
        (NIVEL_MUNICIPIO, "Municipio"),
        (NIVEL_PARROQUIA, "Parroquia"),
        (NIVEL_COMUNIDAD, "Comunidad"),
    ]
    NIVEL_ANTERIOR = {
        NIVEL_MUNICIPIO: NIVEL_ESTADO,
        NIVEL_PARROQUIA: NIVEL_MUNICIPIO,
        NIVEL_COMUNIDAD: NIVEL_PARROQUIA,
    }

    nombre = models.CharField("Nombre", max_length=120, db_index=True)
    codigo = models.CharField("Código", max_length=20, blank=True)
    nivel = models.CharField("Nivel", max_length=12, choices=NIVEL_CHOICES, db_index=True)
    padre = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hijos",
        verbose_name="Depende de",
    )
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "División territorial"
        verbose_name_plural = "División territorial"
        ordering = ["nivel", "nombre"]
        constraints = [
            models.UniqueConstraint(fields=["nivel", "nombre", "padre"], name="territorio_unico_por_padre")
        ]

    def __str__(self):
        return f"[{self.get_nivel_display()}] {self.nombre}"

    @property
    def ruta(self):
        camino = []
        x = self
        while x is not None:
            camino.append({"nivel": x.nivel, "nombre": x.nombre})
            x = x.padre
        camino.reverse()
        return camino

    def subir_hasta(self, nivel):
        x = self
        while x is not None and x.nivel != nivel:
            x = x.padre
        return x


class ASIC(models.Model):
    nombre = models.CharField("Nombre del ASIC", max_length=200)
    codigo = models.CharField("Código", max_length=30, unique=True)
    parroquia = models.ForeignKey(
        DivisionTerritorial,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="asics",
        verbose_name="Parroquia sede",
        help_text="Parroquia donde se ubica la sede del área de salud.",
    )
    direccion = models.CharField("Dirección de la sede", max_length=300, blank=True)
    responsable = models.CharField("Responsable", max_length=200, blank=True)
    telefono = models.CharField("Teléfono", max_length=40, blank=True)
    email = models.EmailField("Correo", blank=True)
    establecimientos_adscritos = models.PositiveSmallIntegerField(
        "Establecimientos adscritos", default=0,
        help_text="Consultorios populares, ambulatorios, CDI/CRI y otros de la red del ASIC.",
    )
    comunidades = models.ManyToManyField(
        DivisionTerritorial,
        blank=True,
        related_name="asics_territoriales",
        verbose_name="Comunidades del territorio",
        help_text="Comunidades (nivel COMUNIDAD) que integran el área de salud integral.",
    )
    observaciones = models.TextField("Observaciones", blank=True)
    activo = models.BooleanField("Activo", default=True)
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        verbose_name = "ASIC"
        verbose_name_plural = "ASIC"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.parroquia_id and self.parroquia.nivel != DivisionTerritorial.NIVEL_PARROQUIA:
            raise ValidationError({"parroquia": "La sede debe ser una parroquia (nivel PARROQUIA)."})

    def ubicacion(self):
        p = self.parroquia
        if p is None:
            return {"estado": "", "municipio": "", "parroquia": ""}
        municipio = p.subir_hasta(DivisionTerritorial.NIVEL_MUNICIPIO)
        estado = p.subir_hasta(DivisionTerritorial.NIVEL_ESTADO)
        return {
            "estado": estado.nombre if estado else "",
            "municipio": municipio.nombre if municipio else "",
            "parroquia": p.nombre,
        }