"""Control de registradores civiles con historial de vigencias (§24.2).

El legacy guardaba el nombre y la cédula del registrador en cada certificado de
defunción (`SISMAI.CERTIFICADO.NOMREGISTRADOR`/`CIREGISTRADOR`, 167.447 de
173.533), pero **nunca** modeló el cargo ni la vigencia. Por eso SISV construye un
catálogo propio: `RegistroCivil` (la oficina, opcionalmente ligada a un centro),
`RegistradorCivil` (la persona, que **no** tiene por qué ser usuario del sistema) y
`DesignacionRegistrador` (el vínculo con `desde`/`hasta`).

Así se puede responder de forma retroactiva «¿quién firmaba en esta fecha?»:
basta con buscar la designación cuya vigencia cubre la fecha del hecho.

Regla de diseño: el historial se modela como filas con vigencia, **no** como un
campo suelto en la organización ni con un `ForeignKey` a `auth.User`.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class RegistroCivil(models.Model):
    """Oficina de registro civil (puede pertenecer a un centro de salud)."""

    nombre = models.CharField("Nombre del registro civil", max_length=200, unique=True)
    organizacion = models.ForeignKey(
        "seguridad.Organizacion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="registros_civiles",
        verbose_name="Centro / organización",
        help_text="Centro de salud al que está adscrito el registro civil, si aplica.",
    )
    estado = models.CharField("Estado", max_length=60, blank=True, default="")
    municipio = models.CharField("Municipio", max_length=100, blank=True, default="")
    parroquia = models.CharField("Parroquia", max_length=100, blank=True, default="")
    activo = models.BooleanField("Activo", default=True)
    observaciones = models.TextField("Observaciones", blank=True, default="")
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        verbose_name = "Registro civil"
        verbose_name_plural = "Registros civiles"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class RegistradorCivil(models.Model):
    """Persona que ejerce como registrador civil; no es necesariamente usuario."""

    NACIONALIDAD_V = "V"
    NACIONALIDAD_E = "E"
    NACIONALIDAD_P = "P"
    NACIONALIDAD_I = "I"
    NACIONALIDAD_O = "O"
    NACIONALIDAD_CHOICES = [
        (NACIONALIDAD_V, "Venezolano"),
        (NACIONALIDAD_E, "Extranjero"),
        (NACIONALIDAD_P, "Pasaporte"),
        (NACIONALIDAD_I, "Indocumentado"),
        (NACIONALIDAD_O, "Otro"),
    ]

    nacionalidad = models.CharField(
        "Nacionalidad", max_length=1, choices=NACIONALIDAD_CHOICES, default=NACIONALIDAD_V
    )
    cedula = models.CharField("Cédula", max_length=20)
    nombres = models.CharField("Nombres", max_length=150)
    apellidos = models.CharField("Apellidos", max_length=150, blank=True, default="")
    telefono = models.CharField("Teléfono", max_length=30, blank=True, default="")
    email = models.EmailField("Correo electrónico", blank=True, default="")
    activo = models.BooleanField("Activo", default=True)
    observaciones = models.TextField("Observaciones", blank=True, default="")
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        verbose_name = "Registrador civil"
        verbose_name_plural = "Registradores civiles"
        ordering = ["apellidos", "nombres"]
        constraints = [
            models.UniqueConstraint(
                fields=["nacionalidad", "cedula"], name="registrador_unico_por_cedula"
            ),
        ]

    def __str__(self):
        return f"{self.cedula_completa} {self.nombre_completo}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    @property
    def cedula_completa(self):
        return f"{self.nacionalidad}-{self.cedula}"


class DesignacionRegistrador(models.Model):
    """Vigencia de un registrador al frente de un registro civil.

    `hasta=None` significa que sigue vigente. Varias designaciones pueden
    solaparse (titular y suplente a la vez), por eso no se prohíbe el solape.
    """

    CARGO_TITULAR = "TITULAR"
    CARGO_SUPLENTE = "SUPLENTE"
    CARGO_ENCARGADO = "ENCARGADO"
    CARGO_CHOICES = [
        (CARGO_TITULAR, "Titular"),
        (CARGO_SUPLENTE, "Suplente"),
        (CARGO_ENCARGADO, "Encargado"),
    ]

    registro_civil = models.ForeignKey(
        RegistroCivil,
        on_delete=models.PROTECT,
        related_name="designaciones",
        verbose_name="Registro civil",
    )
    registrador = models.ForeignKey(
        RegistradorCivil,
        on_delete=models.PROTECT,
        related_name="designaciones",
        verbose_name="Registrador civil",
    )
    cargo = models.CharField("Cargo", max_length=15, choices=CARGO_CHOICES, default=CARGO_TITULAR)
    desde = models.DateField("Vigente desde")
    hasta = models.DateField("Vigente hasta", null=True, blank=True)
    fecha_toma_posesion = models.DateField("Fecha de toma de posesión", null=True, blank=True)
    acta_nombramiento = models.CharField("Acta / nombramiento", max_length=100, blank=True, default="")
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
        verbose_name = "Designación de registrador"
        verbose_name_plural = "Designaciones de registradores"
        ordering = ["-desde", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["registro_civil", "registrador", "desde"],
                name="designacion_unica_por_inicio",
            ),
            models.CheckConstraint(
                condition=models.Q(hasta__isnull=True) | models.Q(hasta__gte=models.F("desde")),
                name="designacion_vigencia_valida",
            ),
        ]

    def __str__(self):
        fin = self.hasta.isoformat() if self.hasta else "vigente"
        return f"{self.registrador} en {self.registro_civil} ({self.desde} → {fin})"

    @property
    def vigente(self):
        return self.hasta is None

    def clean(self):
        if self.hasta and self.desde and self.hasta < self.desde:
            raise ValidationError(
                {"hasta": "La fecha «hasta» no puede ser anterior a la fecha «desde»."}
            )

    def cubre(self, fecha):
        """True si la designación estaba vigente en `fecha`."""
        if fecha is None:
            return False
        if self.desde and fecha < self.desde:
            return False
        if self.hasta and fecha > self.hasta:
            return False
        return True
