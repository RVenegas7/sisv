from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from catalogos.models import CIE10, CIE11
from registros.services import version_cie_por_fecha


class RegistroConCIE(models.Model):
    VERSIONES = [("CIE10", "CIE-10"), ("CIE11", "CIE-11")]

    fecha_evento = models.DateField("Fecha del evento", db_index=True)
    version_cie = models.CharField(
        "Versión CIE", max_length=6, choices=VERSIONES, default="CIE11", db_index=True
    )
    cie10 = models.ForeignKey(
        CIE10, null=True, blank=True, on_delete=models.PROTECT, related_name="%(class)s_registros"
    )
    cie11 = models.ForeignKey(
        CIE11, null=True, blank=True, on_delete=models.PROTECT, related_name="%(class)s_registros"
    )
    organizacion = models.ForeignKey(
        "seguridad.Organizacion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_registros",
        verbose_name="Organización",
    )
    legacy_tabla = models.CharField("Tabla legacy de origen", max_length=40, blank=True, db_index=True)
    legacy_id = models.CharField("ID legacy de origen", max_length=40, blank=True, db_index=True)
    cie10_legacy = models.CharField(
        "Código CIE-10 original (legacy)", max_length=20, blank=True,
        help_text="Código tal como estaba codificado en el sistema anterior; no se pierde.",
    )
    codificacion_pendiente = models.BooleanField(
        "Pendiente de codificación CIE-11", default=False, db_index=True,
        help_text="El evento requiere CIE-11 y aún no tiene código resuelto: lo revisa el codificador.",
    )
    cie11_sugerido = models.ForeignKey(
        CIE11, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        verbose_name="CIE-11 sugerido (cross-walk)",
    )
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.cie10_id or self.cie11_id:
            self.codificacion_pendiente = False
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.fecha_evento:
            version_esperada = version_cie_por_fecha(self.fecha_evento)
            if self.version_cie != version_esperada:
                raise ValidationError(
                    {"version_cie": f"La fecha del evento exige la versión {version_esperada}."}
                )
            if version_esperada == "CIE10":
                if not self.cie10:
                    raise ValidationError({"cie10": "Código CIE-10 obligatorio para este evento."})
                if self.cie11:
                    raise ValidationError({"cie11": "No usar CIE-11 en eventos históricos."})
            else:
                if not self.cie11:
                    raise ValidationError({"cie11": "Código CIE-11 obligatorio."})


class Nacimiento(RegistroConCIE):
    SEXO = [("M", "Masculino"), ("F", "Femenino"), ("I", "Indeterminado")]
    TIPO_PARTO = [
        ("VAGINAL", "Vaginal"),
        ("CESAREA", "Cesárea"),
        ("INSTRUMENTAL", "Instrumental"),
        ("OTRO", "Otro"),
    ]
    TIPO_EMBARAZO = [
        ("UNICO", "Único"),
        ("GEMELAR", "Gemelar"),
        ("TRIPLE", "Triple"),
        ("MULTIPLE", "Múltiple"),
    ]
    SITIO_NACIMIENTO = [
        ("ESTABLECIMIENTO", "Establecimiento de salud"),
        ("DOMICILIO", "Domicilio"),
        ("VIA_PUBLICA", "Vía pública"),
        ("OTRO", "Otro"),
    ]
    ESTADO_CIVIL = [
        ("SOLTERA", "Soltera"),
        ("CASADA", "Casada"),
        ("DIVORCIADA", "Divorciada"),
        ("VIUDA", "Viuda"),
        ("UNION_LIBRE", "Unión libre"),
    ]

    registro_numero = models.CharField("Nº de registro", max_length=30, unique=True)
    lote_id = models.CharField("Lote de carga masiva", max_length=40, blank=True, db_index=True)
    hora_nacimiento = models.TimeField("Hora de nacimiento", null=True, blank=True)
    sexo = models.CharField("Sexo", max_length=1, choices=SEXO, default="F")
    peso_gramos = models.PositiveIntegerField("Peso al nacer (g)", null=True, blank=True)
    talla_cm = models.DecimalField("Talla (cm)", max_digits=4, decimal_places=1, null=True, blank=True)
    edad_gestacional_semanas = models.PositiveSmallIntegerField(
        "Edad gestacional (semanas)", null=True, blank=True
    )
    tipo_parto = models.CharField("Tipo de parto", max_length=15, choices=TIPO_PARTO, default="VAGINAL")
    tipo_embarazo = models.CharField("Tipo de embarazo", max_length=10, choices=TIPO_EMBARAZO, default="UNICO")
    numero_gemelar = models.PositiveSmallIntegerField("Nº gemelar", null=True, blank=True)
    sitio_nacimiento = models.CharField("Sitio", max_length=15, choices=SITIO_NACIMIENTO, default="ESTABLECIMIENTO")
    establecimiento = models.CharField("Establecimiento de salud", max_length=200, blank=True)
    estado = models.CharField("Estado", max_length=60, blank=True)
    municipio = models.CharField("Municipio", max_length=100, blank=True)
    parroquia = models.CharField("Parroquia", max_length=100, blank=True)
    nacido_vivo = models.BooleanField("Nacido vivo", default=True)
    apgar_1m = models.PositiveSmallIntegerField("Apgar 1 min", null=True, blank=True)
    apgar_5m = models.PositiveSmallIntegerField("Apgar 5 min", null=True, blank=True)

    madre_nombres = models.CharField("Nombres de la madre", max_length=150)
    madre_apellidos = models.CharField("Apellidos de la madre", max_length=150)
    madre_cedula = models.CharField("Cédula de la madre", max_length=20)
    madre_edad = models.PositiveSmallIntegerField("Edad de la madre")
    madre_estado_civil = models.CharField("Estado civil", max_length=15, choices=ESTADO_CIVIL, default="SOLTERA")

    padre_nombres = models.CharField("Nombres del padre", max_length=150, blank=True)
    padre_apellidos = models.CharField("Apellidos del padre", max_length=150, blank=True)
    padre_cedula = models.CharField("Cédula del padre", max_length=20, blank=True)

    libro = models.CharField("Libro de registro civil", max_length=20, blank=True)
    folio = models.PositiveIntegerField("Folio", null=True, blank=True)
    acta = models.PositiveIntegerField("Acta", null=True, blank=True)

    class Meta:
        verbose_name = "Nacimiento"
        verbose_name_plural = "Nacimientos"
        ordering = ["-fecha_evento"]


class Defuncion(RegistroConCIE):
    SEXO = [("M", "Masculino"), ("F", "Femenino"), ("I", "Indeterminado")]

    registro_numero = models.CharField("Nº de certificado", max_length=30, unique=True)
    lote_id = models.CharField("Lote de carga masiva", max_length=40, blank=True, db_index=True)
    hora_defuncion = models.TimeField("Hora de defunción", null=True, blank=True)
    fallecido_nombres = models.CharField("Nombres del fallecido", max_length=150)
    fallecido_apellidos = models.CharField("Apellidos del fallecido", max_length=150)
    fallecido_cedula = models.CharField("Cédula del fallecido", max_length=20, blank=True)
    sexo = models.CharField("Sexo", max_length=1, choices=SEXO, default="F")
    fecha_nacimiento = models.DateField("Fecha de nacimiento", null=True, blank=True)
    lugar_defuncion = models.CharField("Lugar de defunción", max_length=15, choices=[("ESTABLECIMIENTO", "Establecimiento de salud"), ("DOMICILIO", "Domicilio"), ("VIA_PUBLICA", "Vía pública"), ("OTRO", "Otro")], default="ESTABLECIMIENTO")
    establecimiento = models.CharField("Establecimiento", max_length=200, blank=True)
    estado = models.CharField("Estado", max_length=60, blank=True)
    municipio = models.CharField("Municipio", max_length=100, blank=True)
    parroquia = models.CharField("Parroquia", max_length=100, blank=True)
    causa_directa = models.CharField("Causa inmediata (texto)", max_length=300, blank=True)
    embarazo_o_puerperio = models.BooleanField("Defunción materna (embarazo/puerperio)", default=False)
    autopsia = models.BooleanField("Se realizó autopsia", default=False)
    embalsamado = models.BooleanField("Embalsamado", default=False)
    certificador_nombres = models.CharField("Médico certificador", max_length=150, blank=True)
    certificador_cedula = models.CharField("C.I. certificador", max_length=20, blank=True)

    class Meta:
        verbose_name = "Defunción"
        verbose_name_plural = "Defunciones"
        ordering = ["-fecha_evento"]


class FichaVigilancia(RegistroConCIE):
    SEXO = [("M", "Masculino"), ("F", "Femenino"), ("I", "Indeterminado")]
    CLASIFICACION = [
        ("SOSPECHOSO", "Sospechoso"),
        ("PROBABLE", "Probable"),
        ("CONFIRMADO", "Confirmado"),
        ("DESCARTADO", "Descartado"),
    ]

    codigo_notificacion = models.CharField("Código de notificación", max_length=30, unique=True)
    lote_id = models.CharField("Lote de carga masiva", max_length=40, blank=True, db_index=True)
    nombre_evento = models.CharField("Evento de salud", max_length=200)
    fecha_notificacion = models.DateField("Fecha de notificación")
    fecha_inicio_sintomas = models.DateField("Fecha de inicio de síntomas", null=True, blank=True)
    clasificacion = models.CharField("Clasificación", max_length=12, choices=CLASIFICACION, default="SOSPECHOSO")
    establecimiento = models.CharField("Establecimiento", max_length=200, blank=True)
    estado = models.CharField("Estado", max_length=60, blank=True)
    municipio = models.CharField("Municipio", max_length=100, blank=True)
    parroquia = models.CharField("Parroquia", max_length=100, blank=True)
    paciente_nombres = models.CharField("Nombres", max_length=150)
    paciente_apellidos = models.CharField("Apellidos", max_length=150)
    paciente_cedula = models.CharField("Cédula", max_length=20, blank=True)
    sexo = models.CharField("Sexo", max_length=1, choices=SEXO, default="F")
    edad = models.PositiveSmallIntegerField("Edad", null=True, blank=True)
    sintomas = models.TextField("Síntomas", blank=True)
    nota = models.TextField("Observaciones", blank=True)

    class Meta:
        verbose_name = "Ficha de vigilancia"
        verbose_name_plural = "Fichas de vigilancia"
        ordering = ["-fecha_evento"]

class ConfiguracionGeneral(models.Model):
    estado = models.CharField("Estado por defecto", max_length=60, blank=True)
    municipio = models.CharField("Municipio por defecto", max_length=100, blank=True)
    parroquia = models.CharField("Parroquia por defecto", max_length=100, blank=True)
    establecimiento = models.CharField("Establecimiento por defecto", max_length=200, blank=True)
    fecha_corte_cie11 = models.DateField("Fecha de corte CIE-11")
    organizacion_activa = models.ForeignKey(
        "seguridad.Organizacion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Organización activa",
    )
    actualizado_en = models.DateTimeField("Actualizado en", auto_now=True)

    class Meta:
        verbose_name = "Configuración general"
        verbose_name_plural = "Configuración general"

    @classmethod
    def obtener(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create(fecha_corte_cie11=getattr(settings, "FECHA_CORTE_CIE11", None) or date.today())
        return obj
