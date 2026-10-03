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
    # El certificado de nacimiento EV-25 ofrece cuatro opciones de sexo: masculino,
    # femenino, hermafrodita y sin información. El histórico solo tenía tres códigos
    # (M/F/I) y hay 115 filas con 'I' que venía de 'NAC_RNACIDO.HSEXO' 0/3, es decir
    # «indeterminado» del catálogo legacy. No se reinterpretan: 'I' conserva el código y
    # ahora se rotula como lo rotula el certificado, y 'N' es el código nuevo para
    # «sin información», que antes no tenía dónde guardarse.
    SEXO = [
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("I", "Hermafrodita"),
        ("N", "Sin información"),
    ]
    NACIONALIDAD = [
        ("V", "Venezolana"),
        ("E", "Extranjera"),
        ("P", "Pasaporte"),
        ("I", "Sin información"),
        ("O", "Otra identificación"),
    ]
    RESIDENCIA = [
        ("V", "Venezuela"),
        ("E", "Exterior"),
        ("I", "Sin información"),
    ]
    TIPO_NUMERO_CERTIFICADO = [
        ("COMPLETO", "Completo"),
        ("HISTORICO", "Histórico"),
    ]
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

    # --- Sección I: datos del recién nacido ---
    nino_nombres = models.CharField("Nombres del recién nacido", max_length=150, blank=True)
    nino_apellidos = models.CharField("Apellidos del recién nacido", max_length=150, blank=True)
    numero_historia_clinica = models.CharField("Nº de historia clínica", max_length=30, blank=True)

    # --- Sección II: datos de la madre ---
    madre_nombres = models.CharField("Nombres de la madre", max_length=150)
    madre_apellidos = models.CharField("Apellidos de la madre", max_length=150)
    madre_cedula = models.CharField("Cédula de la madre", max_length=20)
    madre_edad = models.PositiveSmallIntegerField("Edad de la madre")
    madre_estado_civil = models.CharField("Estado civil", max_length=15, choices=ESTADO_CIVIL, default="SOLTERA")
    madre_nacionalidad = models.CharField(
        "Nacionalidad de la madre", max_length=1, choices=NACIONALIDAD, blank=True
    )
    madre_pasaporte = models.CharField(
        "Nº de pasaporte u otra identificación de la madre", max_length=20, blank=True
    )
    # La residencia habitual es el territorio de la madre, que no es el del establecimiento.
    madre_residencia = models.CharField(
        "Residencia habitual de la madre", max_length=1, choices=RESIDENCIA, blank=True
    )
    madre_residencia_pais = models.CharField("País de residencia de la madre", max_length=80, blank=True)
    madre_residencia_direccion = models.CharField(
        "Dirección de residencia de la madre", max_length=250, blank=True
    )
    madre_residencia_parroquia = models.ForeignKey(
        "territorio.DivisionTerritorial", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="nacimientos_madre_parroquia", verbose_name="Parroquia de residencia de la madre",
        help_text="Nivel PARROQUIA. Es el territorio de la madre, no el del establecimiento.",
    )
    madre_residencia_comunidad = models.ForeignKey(
        "territorio.DivisionTerritorial", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="nacimientos_madre_comunidad", verbose_name="Comunidad de residencia de la madre",
        help_text="Nivel COMUNIDAD. Es el territorio de la madre, no el del establecimiento.",
    )

    # --- Sección III: datos del padre ---
    padre_nombres = models.CharField("Nombres del padre", max_length=150, blank=True)
    padre_apellidos = models.CharField("Apellidos del padre", max_length=150, blank=True)
    padre_cedula = models.CharField("Cédula del padre", max_length=20, blank=True)
    padre_nacionalidad = models.CharField(
        "Nacionalidad del padre", max_length=1, choices=NACIONALIDAD, blank=True
    )
    padre_pasaporte = models.CharField(
        "Nº de pasaporte u otra identificación del padre", max_length=20, blank=True
    )
    padre_residencia = models.CharField(
        "Residencia habitual del padre", max_length=1, choices=RESIDENCIA, blank=True
    )
    padre_residencia_pais = models.CharField("País de residencia del padre", max_length=80, blank=True)
    padre_residencia_direccion = models.CharField(
        "Dirección de residencia del padre", max_length=250, blank=True
    )
    padre_residencia_parroquia = models.ForeignKey(
        "territorio.DivisionTerritorial", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="nacimientos_padre_parroquia", verbose_name="Parroquia de residencia del padre",
    )
    padre_residencia_comunidad = models.ForeignKey(
        "territorio.DivisionTerritorial", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="nacimientos_padre_comunidad", verbose_name="Comunidad de residencia del padre",
    )

    # --- Cabecera del certificado ---
    fecha_emision = models.DateField("Fecha de emisión", null=True, blank=True)
    numero_planilla = models.CharField("Nº de la planilla impresa", max_length=30, blank=True)
    tipo_numero_certificado = models.CharField(
        "Tipo del nº en el certificado", max_length=10, choices=TIPO_NUMERO_CERTIFICADO, blank=True,
        help_text="El formulario ofrece un número Completo u Histórico en el certificado impreso.",
    )

    # --- Responsable de la certificación ---
    certificador_nombres = models.CharField(
        "Nombre del responsable de la certificación", max_length=200, blank=True
    )
    certificador_cedula = models.CharField("Cédula del responsable de la certificación", max_length=20, blank=True)
    certificador_matricula_mpps = models.CharField("Nº MSDS del responsable", max_length=30, blank=True)
    director_establecimiento = models.CharField("Director del establecimiento", max_length=200, blank=True)

    # --- Sección IV: registro civil ---
    libro = models.CharField("Libro de registro civil", max_length=20, blank=True)
    folio = models.PositiveIntegerField("Folio", null=True, blank=True)
    acta = models.PositiveIntegerField("Acta", null=True, blank=True)

    class Meta:
        verbose_name = "Nacimiento"
        verbose_name_plural = "Nacimientos"
        ordering = ["-fecha_evento"]

    def clean(self):
        super().clean()
        for campo, nivel in (
            ("madre_residencia_parroquia", "PARROQUIA"),
            ("madre_residencia_comunidad", "COMUNIDAD"),
            ("padre_residencia_parroquia", "PARROQUIA"),
            ("padre_residencia_comunidad", "COMUNIDAD"),
        ):
            nodo = getattr(self, f"{campo}_id", None) and getattr(self, campo)
            if nodo is not None and nodo.nivel != nivel:
                raise ValidationError({campo: f"La residencia debe registrar una {nivel.lower()}."})

    def residencia_ubicacion(self, quien):
        """Territorio de residencia habitual de la madre o del padre, de arriba hacia abajo.

        Devuelve los cuatro niveles con nombre, que es lo que la cascada del formulario
        necesita para dejarse precargar; el nivel más fino informado es el que se guardó.
        """
        comunidad = getattr(self, f"{quien}_residencia_comunidad", None)
        parroquia = getattr(self, f"{quien}_residencia_parroquia", None)
        if comunidad is not None:
            return {
                "estado": comunidad.subir_hasta("ESTADO"),
                "municipio": comunidad.subir_hasta("MUNICIPIO"),
                "parroquia": comunidad.subir_hasta("PARROQUIA"),
                "comunidad": comunidad,
            }
        if parroquia is None:
            return {"estado": None, "municipio": None, "parroquia": None, "comunidad": None}
        return {
            "estado": parroquia.subir_hasta("ESTADO"),
            "municipio": parroquia.subir_hasta("MUNICIPIO"),
            "parroquia": parroquia,
            "comunidad": None,
        }


class Defuncion(RegistroConCIE):
    SEXO = [("M", "Masculino"), ("F", "Femenino"), ("I", "Indeterminado")]
    NACIONALIDAD = [
        ("V", "Venezolana"),
        ("E", "Extranjera"),
        ("P", "Pasaporte"),
        ("I", "Ignorado"),
        ("O", "Otra"),
    ]
    ESTADO_CIVIL = [
        ("SOLTERO", "Soltero(a)"),
        ("CASADO", "Casado(a)"),
        ("VIUDO", "Viudo(a)"),
        ("DIVORCIADO", "Divorciado(a)"),
        ("UNIDO", "Unido(a)"),
        ("SEPARADO", "Separado(a)"),
    ]
    MANERA_DE_MORIR = [
        ("ENFERMEDAD", "Enfermedad"),
        ("ACCIDENTE", "Accidente"),
        ("AGRESION", "Agresión"),
        ("AUTOINFLIGIDA", "Autoinfligida"),
        ("NO_DETERMINADA", "No determinada"),
        ("ESTUDIO_FORENSE", "Estudio forense"),
    ]
    SI_NO_IGNORADO = [
        ("SI", "Sí"),
        ("NO", "No"),
        ("IGNORADO", "Ignorado"),
    ]
    TIPO_EMBARAZO = [
        ("UNICO", "Único"),
        ("MULTIPLE", "Múltiple"),
    ]
    TIPO_PARTO = [
        ("VAGINAL", "Vaginal"),
        ("CESAREA", "Cesárea"),
        ("INSTRUMENTAL", "Instrumental"),
        ("OTRO", "Otro"),
    ]
    PERIODO_PUERPERIO = [
        ("NIUNA", "No corresponde"),
        ("DENTRO42D", "Dentro de 42 días"),
        ("DENTRO12M", "Dentro de 12 meses"),
        ("IGNORADO", "Ignorado"),
    ]

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

    # --- EV-14 (formulario oficial de defunción, Venezuela) ---------------
    # Sección I — Identificación del fallecido(a)
    nacionalidad = models.CharField("Nacionalidad", max_length=1, choices=NACIONALIDAD, blank=True, default="")
    segundo_apellido = models.CharField("Segundo apellido", max_length=150, blank=True, default="")
    segundo_nombre = models.CharField("Segundo nombre", max_length=150, blank=True, default="")
    edad_ignorada = models.BooleanField("Edad ignorada", default=False)
    lugar_nacimiento = models.CharField("Lugar de nacimiento", max_length=200, blank=True, default="")
    nacimiento_exterior = models.BooleanField("Nacimiento en el exterior", default=False)
    estado_civil = models.CharField("Estado civil", max_length=15, choices=ESTADO_CIVIL, blank=True, default="")
    profesion = models.CharField("Profesión", max_length=100, blank=True, default="")
    ocupacion_lugar_trabajo = models.CharField("Ocupación y lugar de trabajo", max_length=200, blank=True, default="")
    sabe_leer_escribir = models.CharField("Sabe leer y escribir", max_length=10, choices=SI_NO_IGNORADO, blank=True, default="")
    residencia_habitual = models.CharField("Dirección de residencia habitual", max_length=300, blank=True, default="")
    asistencia_medica = models.CharField("Asistencia médica", max_length=10, choices=SI_NO_IGNORADO, blank=True, default="")

    # Sección II — Menores de un año / muerte fetal y datos de la madre
    es_muerte_fetal = models.BooleanField("Es muerte fetal", default=False)
    peso_nacer_gramos = models.PositiveIntegerField("Peso al nacer (g)", null=True, blank=True)
    edad_gestacional_semanas = models.PositiveSmallIntegerField("Semanas de gestación", null=True, blank=True)
    tipo_embarazo = models.CharField("Tipo de embarazo", max_length=10, choices=TIPO_EMBARAZO, blank=True, default="")
    tipo_parto = models.CharField("Tipo de parto", max_length=12, choices=TIPO_PARTO, blank=True, default="")
    asistencia_parto = models.CharField("Asistencia del parto", max_length=100, blank=True, default="")
    madre_apellidos = models.CharField("Apellidos de la madre", max_length=150, blank=True, default="")
    madre_nombres = models.CharField("Nombres de la madre", max_length=150, blank=True, default="")
    madre_cedula = models.CharField("Cédula de la madre", max_length=20, blank=True, default="")
    madre_numero_gestas = models.PositiveSmallIntegerField("Número de gestas (madre)", null=True, blank=True)
    madre_fecha_ultima_gesta = models.DateField("Fecha de la última gesta", null=True, blank=True)
    madre_embarazada = models.CharField("Estaba embarazada", max_length=10, choices=SI_NO_IGNORADO, blank=True, default="")
    madre_puerperio = models.CharField("En puerperio de", max_length=12, choices=PERIODO_PUERPERIO, blank=True, default="")

    # Sección V — Muerte violenta
    manera_de_morir = models.CharField("Manera de morir", max_length=15, choices=MANERA_DE_MORIR, blank=True, default="")
    fecha_hecho_violento = models.DateField("Fecha del hecho violento", null=True, blank=True)
    hora_hecho_violento = models.TimeField("Hora del hecho violento", null=True, blank=True)
    descripcion_hecho_violento = models.CharField("Descripción del hecho violento", max_length=300, blank=True, default="")

    # Sección VI — Certificación médica
    causa_antecedentes = models.CharField("Causas antecedentes (texto)", max_length=300, blank=True, default="")
    otros_estados_patologicos = models.CharField("Otros estados patológicos (texto)", max_length=300, blank=True, default="")
    diagnostico_examen_cadaver = models.BooleanField("Diagnóstico: examen del cadáver", default=False)
    diagnostico_examen_laboratorio = models.BooleanField("Diagnóstico: examen de laboratorio", default=False)
    diagnostico_historia_clinica = models.BooleanField("Diagnóstico: historia clínica", default=False)
    diagnostico_interrogatorio_familiar = models.BooleanField("Diagnóstico: interrogatorio familiar o testigo", default=False)
    cirugia = models.BooleanField("Tuvo alguna cirugía", default=False)
    fecha_ultima_cirugia = models.DateField("Fecha de la última cirugía", null=True, blank=True)
    descripcion_cirugia = models.CharField("Breve descripción de la cirugía", max_length=300, blank=True, default="")
    intervalo_enf_muerte = models.CharField("Intervalo entre inicio y muerte", max_length=200, blank=True, default="")
    correo_contacto = models.EmailField("Correo electrónico de contacto", max_length=150, blank=True, default="")
    matricula_mpps = models.CharField("Matrícula MPPS del médico", max_length=30, blank=True, default="")

    # Sección VII — Registro civil
    registro_civil_nombre = models.CharField("Nombre del registro civil", max_length=150, blank=True, default="")
    folio_defuncion = models.CharField("Folio del acta", max_length=20, blank=True, default="")
    numero_acta_defuncion = models.CharField("Número del acta de defunción", max_length=30, blank=True, default="")
    fecha_registro = models.DateField("Fecha de registro", null=True, blank=True)
    declarante_nombres = models.CharField("Apellidos y nombres del declarante", max_length=200, blank=True, default="")
    declarante_cedula = models.CharField("Cédula del declarante", max_length=20, blank=True, default="")
    registrador_civil_nombres = models.CharField("Apellidos y nombres del registrador civil", max_length=200, blank=True, default="")
    registrador_civil_cedula = models.CharField("Cédula del registrador civil", max_length=20, blank=True, default="")
    gaceta = models.CharField("Gaceta", max_length=30, blank=True, default="")
    resolucion = models.CharField("Resolución", max_length=30, blank=True, default="")

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
    detectar_meses_degradados = models.BooleanField(
        "Detectar meses degradados", default=True,
        help_text="Avisa cuando un mes tiene muchos menos registros de lo normal.",
    )
    factor_mes_degradado = models.FloatField(
        "Factor de mes degradado", default=0.40,
        help_text="Cuánto del nivel normal puede bajar un mes antes de avisar (0 a 1).",
    )
    min_meses_historia = models.PositiveSmallIntegerField(
        "Meses de historia para la mediana", default=12,
        help_text="Meses normales que se usan como referencia para comparar.",
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
