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


class ConciliacionNeonatal(models.Model):
    """Muerte neonatal (0 a 27 días) del registro MMI de la oficina contra SISV.

    El grano es **(año, semana, organización)**. La semana se calcula **en cada lado
    desde la fecha real del evento** con la misma función epidemiológica, y **no**
    desde `DOCUMENTO."PERIODO"`: en el legacy ese campo no es una semana, es un
    número de formulario del centro, con rangos que se solapan (en 2019 el periodo
    29 va del 2 de enero al 12 de septiembre). Comparar `PERIODO` contra la semana
    de SISV mediría un número de formulario, no una diferencia de captura.

    El lado legacy es `sismai."CASOS_MMI"` (el registro materno-infantil), que trae
    nombre, edad **con su unidad**, sexo y fecha de ocurrencia. Los neonatos son las
    filas con edad en horas o en días de 0 a 27.

    ⚠ Esta tabla **no** concilia la muerte materna: aquí se cuentan los neonatos de
    `CASOS_MMI`, que mezcla materna, infantil y otras sin marcarlas. La MM se concilia
    aparte contra `RENGLON_CASOSMM` en `ConciliacionMaterna`. Ver PENDIENTES.md §20 y §21.
    """

    ESTADO_CHOICES = [
        ("CUADRA", "Cuadra"),
        ("DIFERENCIA", "Diferencia"),
        ("SOLO_CRUDO", "Solo en el registro de la oficina"),
        ("SOLO_SISV", "Solo en SISV"),
    ]
    RESOLUCION_CHOICES = [
        ("CONCILIADO", "Conciliado"),
        ("CENTRO_SIN_ORG", "Centro sin organización"),
    ]

    anio = models.SmallIntegerField("Año", db_index=True)
    semana = models.SmallIntegerField("Semana epidemiológica", db_index=True)

    organizacion = models.ForeignKey(
        "seguridad.Organizacion",
        on_delete=models.CASCADE,
        related_name="conciliaciones_neonatal",
        verbose_name="Organización",
        help_text="A NULL cuando el establecimiento legacy no tiene organización propia; "
                  "esos casos caen en el agregado regional, no se pierden.",
    )
    es_agregado_sin_org = models.BooleanField(
        "Pertenece al agregado regional",
        default=False,
        help_text="El establecimiento legacy no resolvió a una organización y se sumó al "
                  "agregado 'Legacy regional (histórico)'.",
    )

    cantidad_centros_legacy = models.PositiveIntegerField("Centros legacy", default=1)

    legado = models.IntegerField("Neonatos en el registro MMI", default=0)
    sisv = models.IntegerField("Neonatos en SISV", default=0)
    diferencia = models.IntegerField("Diferencia", default=0)

    estado = models.CharField("Estado", max_length=12, choices=ESTADO_CHOICES, db_index=True)
    resolucion = models.CharField("Resolución", max_length=20, choices=RESOLUCION_CHOICES)
    calculado_en = models.DateTimeField("Calculado en", default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Conciliación neonatal"
        verbose_name_plural = "Conciliaciones neonatales"
        unique_together = ("anio", "semana", "organizacion")
        ordering = ("anio", "semana", "organizacion_id")
        indexes = [models.Index(fields=["anio", "estado"])]

    def __str__(self):
        return f"{self.anio} S{self.semana:02d} org={self.organizacion_id} " \
               f"legacy={self.legado} sisv={self.sisv}"


class ConciliacionMaterna(models.Model):
    """Muerte materna del registro de investigación de la oficina contra SISV.

    El grano es **(año, semana, organización)**, igual que `ConciliacionNeonatal`.

    El lado de la oficina es `sismai."RENGLON_CASOSMM"` enlazado a
    `sismai."CASOS_MMI"`: **749 renglones, uno por persona, 748 de los 748 enlazan**
    con `CASOS_MMI."ID"` y traen `FECHAOCURRENCIA`. ⚠ `HCASOSMMI` es el **ID de la
    persona, no un conteo** — por eso `SUM(HCASOSMMI)` da 658.439.440.845 y no 749
    (§17.18 lo sospechó como bug de mapeo: no lo es, era la lectura equivocada).
    `PERIODOOCURRENCIA` viene `NULL` en las 749 porque **no es la fecha**: la fecha
    real de la muerte está en `CASOS_MMI."FECHAOCURRENCIA"`.

    El lado SISV es `Defuncion.embarazo_o_puerperio` (`CERTIFICADO.HPRESENCIAEMBARAZO`),
    que **se queda como el indicador de los certificados**, no como el total. Ese
    campo es un aviso opcional del certificador y solo lo diligencia 7 de 18 veces en
    2026, así que contarlo como MM subestima el indicador real. La diferencia entre
    ambos lados es precisamente el hallazgo: no es una pérdida de datos sino que el
    certificado rarely marca el embarazo, y el registro de investigación sí.
    """

    ESTADO_CHOICES = [
        ("CUADRA", "Cuadra"),
        ("DIFERENCIA", "Diferencia"),
        ("SOLO_CRUDO", "Solo en el registro de la oficina"),
        ("SOLO_SISV", "Solo en SISV"),
    ]
    RESOLUCION_CHOICES = [
        ("CONCILIADO", "Conciliado"),
        ("CENTRO_SIN_ORG", "Centro sin organización"),
    ]

    anio = models.SmallIntegerField("Año", db_index=True)
    semana = models.SmallIntegerField("Semana epidemiológica", db_index=True)

    organizacion = models.ForeignKey(
        "seguridad.Organizacion",
        on_delete=models.CASCADE,
        related_name="conciliaciones_materna",
        verbose_name="Organización",
        help_text="A NULL cuando el establecimiento legacy no tiene organización propia; "
                  "esos casos caen en el agregado regional, no se pierden.",
    )
    es_agregado_sin_org = models.BooleanField(
        "Pertenece al agregado regional",
        default=False,
        help_text="El establecimiento legacy no resolvió a una organización y se sumó al "
        "agregado 'Legacy regional (histórico)'.",
    )

    cantidad_centros_legacy = models.PositiveIntegerField("Centros legacy", default=1)

    legado = models.IntegerField("Muertes maternas en el registro de la oficina", default=0)
    sisv = models.IntegerField("Muertes maternas marcadas en el certificado", default=0)
    diferencia = models.IntegerField("Diferencia", default=0)

    estado = models.CharField("Estado", max_length=12, choices=ESTADO_CHOICES, db_index=True)
    resolucion = models.CharField("Resolución", max_length=20, choices=RESOLUCION_CHOICES)
    calculado_en = models.DateTimeField("Calculado en", default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Conciliación materna"
        verbose_name_plural = "Conciliaciones maternas"
        unique_together = ("anio", "semana", "organizacion")
        ordering = ("anio", "semana", "organizacion_id")
        indexes = [models.Index(fields=["anio", "estado"])]

    def __str__(self):
        return f"{self.anio} S{self.semana:02d} org={self.organizacion_id} " \
               f"legacy={self.legado} sisv={self.sisv}"


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
