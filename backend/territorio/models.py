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