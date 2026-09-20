from django.conf import settings
from django.db import models


class Organizacion(models.Model):
    NIVEL_MINISTERIO = "MINISTERIO"
    NIVEL_GOBERNACION = "GOBERNACION"
    NIVEL_REGIONAL = "REGIONAL"
    NIVEL_CENTRO = "CENTRO"
    NIVEL_CHOICES = [
        (NIVEL_MINISTERIO, "Ministerio de Salud"),
        (NIVEL_GOBERNACION, "Gobernación"),
        (NIVEL_REGIONAL, "Dirección Regional"),
        (NIVEL_CENTRO, "Centro de salud"),
    ]

    nombre = models.CharField("Nombre", max_length=200)
    codigo = models.CharField("Código", max_length=30, unique=True)
    nivel = models.CharField("Nivel", max_length=15, choices=NIVEL_CHOICES, default=NIVEL_CENTRO)
    estado = models.CharField("Estado", max_length=60, blank=True)
    municipio = models.CharField("Municipio", max_length=100, blank=True)
    parroquia = models.CharField("Parroquia", max_length=100, blank=True)
    asic = models.ForeignKey(
        "territorio.ASIC",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizaciones",
        verbose_name="ASIC asociado",
        help_text="Área de Salud Integral Comunitaria a la que pertenece el centro de salud.",
    )
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
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ["nivel", "nombre"]

    def __str__(self):
        return f"[{self.get_nivel_display()}] {self.nombre}"


class Perfil(models.Model):
    ROL_TRANSCRIPTOR = "TRANSCRIPTOR"
    ROL_CODIFICADOR = "CODIFICADOR"
    ROL_EPIDEMIOLOGO = "EPIDEMIOLOGO"
    ROL_DIRECTOR = "DIRECTOR"
    ROL_CHOICES = [
        (ROL_TRANSCRIPTOR, "Transcriptor"),
        (ROL_CODIFICADOR, "Codificador"),
        (ROL_EPIDEMIOLOGO, "Epidemiólogo"),
        (ROL_DIRECTOR, "Director"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField("Rol", max_length=15, choices=ROL_CHOICES, default=ROL_TRANSCRIPTOR)
    organizacion = models.ForeignKey(
        Organizacion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="integrantes",
        verbose_name="Organización asociada",
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

    def __str__(self):
        org = self.organizacion.nombre if self.organizacion else "Sin organización"
        return f"{self.user.get_full_name()} ({self.get_rol_display()}) @ {org}"