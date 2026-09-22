# -*- coding: utf-8 -*-
# GENERADO AUTOMÁTICAMENTE por `manage.py mapear_legacy` (no editar a mano).
#
# Mapa de modelos del sistema legacy SISMAI (Oracle 10g → PostgreSQL).
# Modelos de SOLO LECTURA (managed=False): no crean migraciones ni alteran
# tablas. db_table va calificado por esquema (ej. "sismai"."ESTABLECIMIENTO").
# Esquemas documentados: sismai / legacy / inbdlar1 / historico.
from django.db import models


class Errores(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"ERRORES\""


class Erroresb(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"ERRORESB\""


class Erroresc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"ERRORESC\""


class ErroresLabo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"ERRORES_LABO\""


class ErroresResi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"ERRORES_RESI\""


class ErroresSinc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"ERRORES_SINC\""


class Evento2(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"EVENTO2\""


class Eventos(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"EVENTOS\""


class EventosDblink(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"historico\".\"EVENTOS_DBLINK\""


class TAccilabo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    accidente = models.FloatField(blank=True, null=True, db_column='ACCIDENTE')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    hora = models.CharField(blank=True, null=True, db_column='HORA', max_length=20)
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    tratamiento = models.CharField(blank=True, null=True, db_column='TRATAMIENTO', max_length=1)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=1)
    fechatra = models.DateTimeField(blank=True, null=True, db_column='FECHATRA')
    horatratamiento = models.CharField(blank=True, null=True, db_column='HORATRATAMIENTO', max_length=20)
    fuente = models.CharField(blank=True, null=True, db_column='FUENTE', max_length=1)
    desconoce = models.FloatField(blank=True, null=True, db_column='DESCONOCE')
    fuentedesconoce = models.FloatField(blank=True, null=True, db_column='FUENTEDESCONOCE')
    serologia = models.CharField(blank=True, null=True, db_column='SEROLOGIA', max_length=1)
    resultadosero = models.CharField(blank=True, null=True, db_column='RESULTADOSERO', max_length=30)
    fecharesultadosero = models.DateTimeField(blank=True, null=True, db_column='FECHARESULTADOSERO')
    hexposicion = models.FloatField(blank=True, null=True, db_column='HEXPOSICION')
    hobjeto = models.FloatField(blank=True, null=True, db_column='HOBJETO')
    hliquido = models.FloatField(blank=True, null=True, db_column='HLIQUIDO')
    hsituacion = models.FloatField(blank=True, null=True, db_column='HSITUACION')
    abusosexual = models.FloatField(blank=True, null=True, db_column='ABUSOSEXUAL')
    hlocalidadabuso = models.FloatField(blank=True, null=True, db_column='HLOCALIDADABUSO')
    fechaabuso = models.DateTimeField(blank=True, null=True, db_column='FECHAABUSO')
    horaabuso = models.CharField(blank=True, null=True, db_column='HORAABUSO', max_length=20)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_ACCILABO\""


class TAcctrans(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha = models.FloatField(blank=True, null=True, db_column='HFICHA')
    htipo_accidente = models.FloatField(blank=True, null=True, db_column='HTIPO_ACCIDENTE')
    htipo_vehiculo = models.FloatField(blank=True, null=True, db_column='HTIPO_VEHICULO')
    hcondicion = models.FloatField(blank=True, null=True, db_column='HCONDICION')
    hsitio_accidente = models.FloatField(blank=True, null=True, db_column='HSITIO_ACCIDENTE')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    hsitio_auto = models.FloatField(blank=True, null=True, db_column='HSITIO_AUTO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    causa = models.FloatField(blank=True, null=True, db_column='CAUSA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_ACCTRANS\""


class TAlabcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_analisis = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANALISIS')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fecha_analisis = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANALISIS')
    resultado = models.CharField(blank=True, null=True, db_column='RESULTADO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_ALABCARD\""


class TAnalabor(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_analisis = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANALISIS')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fecha_analisis = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANALISIS')
    resultado = models.CharField(blank=True, null=True, db_column='RESULTADO', max_length=50)
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_ANALABOR\""


class TAntefact(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_anteced = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANTECED')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_ANTEFACT\""


class TAuditoria(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombreforma = models.CharField(blank=True, null=True, db_column='NOMBREFORMA', max_length=60)
    nombretabla = models.CharField(blank=True, null=True, db_column='NOMBRETABLA', max_length=30)
    evento = models.FloatField(blank=True, null=True, db_column='EVENTO')
    nombreregistro = models.CharField(blank=True, null=True, db_column='NOMBREREGISTRO', max_length=200)
    idregistro = models.FloatField(blank=True, null=True, db_column='IDREGISTRO')
    pc = models.CharField(blank=True, null=True, db_column='PC', max_length=20)
    husuario = models.FloatField(blank=True, null=True, db_column='HUSUARIO')
    fecha_ope = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPE')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_AUDITORIA\""


class TBiopseg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_BIOPSEG\""


class TBiopsiat(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    aspectoclinico = models.FloatField(blank=True, null=True, db_column='ASPECTOCLINICO')
    biopsiaanterior = models.FloatField(blank=True, null=True, db_column='BIOPSIAANTERIOR')
    ceneoplasicas = models.FloatField(blank=True, null=True, db_column='CENEOPLASICAS')
    cereactivas = models.FloatField(blank=True, null=True, db_column='CEREACTIVAS')
    cgneoplasicas = models.FloatField(blank=True, null=True, db_column='CGNEOPLASICAS')
    cgreactivas = models.FloatField(blank=True, null=True, db_column='CGREACTIVAS')
    citanormal = models.FloatField(blank=True, null=True, db_column='CITANORMAL')
    citologiaant = models.FloatField(blank=True, null=True, db_column='CITOLOGIAANT')
    citologianeoplasia = models.FloatField(blank=True, null=True, db_column='CITOLOGIANEOPLASIA')
    codigomuestrasas = models.CharField(blank=True, null=True, db_column='CODIGOMUESTRASAS', max_length=8)
    crinfecciosos = models.FloatField(blank=True, null=True, db_column='CRINFECCIOSOS')
    crinflamatorios = models.FloatField(blank=True, null=True, db_column='CRINFLAMATORIOS')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    embarazada = models.FloatField(blank=True, null=True, db_column='EMBARAZADA')
    fechacriocirugia = models.DateTimeField(blank=True, null=True, db_column='FECHACRIOCIRUGIA')
    fechaconizacion = models.DateTimeField(blank=True, null=True, db_column='FECHACONIZACION')
    fechadoc = models.DateTimeField(blank=True, null=True, db_column='FECHADOC')
    fechahistradical = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTRADICAL')
    fechahisttotal = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTTOTAL')
    fechalectura = models.DateTimeField(blank=True, null=True, db_column='FECHALECTURA')
    fechamuestra = models.DateTimeField(blank=True, null=True, db_column='FECHAMUESTRA')
    fecharadioterapia = models.DateTimeField(blank=True, null=True, db_column='FECHARADIOTERAPIA')
    fecharesultado = models.DateTimeField(blank=True, null=True, db_column='FECHARESULTADO')
    fechaultregla = models.DateTimeField(blank=True, null=True, db_column='FECHAULTREGLA')
    hlaboratorio = models.FloatField(blank=True, null=True, db_column='HLABORATORIO')
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hpatologo = models.FloatField(blank=True, null=True, db_column='HPATOLOGO')
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    mesbiopsia = models.DateTimeField(blank=True, null=True, db_column='MESBIOPSIA')
    mescitologia = models.DateTimeField(blank=True, null=True, db_column='MESCITOLOGIA')
    muestracitologica = models.FloatField(blank=True, null=True, db_column='MUESTRACITOLOGICA')
    nroparto = models.FloatField(blank=True, null=True, db_column='NROPARTO')
    nroaborto = models.FloatField(blank=True, null=True, db_column='NROABORTO')
    nrolamina = models.CharField(blank=True, null=True, db_column='NROLAMINA', max_length=20)
    numero = models.FloatField(blank=True, null=True, db_column='NUMERO')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=600)
    resultadoasociado = models.FloatField(blank=True, null=True, db_column='RESULTADOASOCIADO')
    hresultadob = models.FloatField(blank=True, null=True, db_column='HRESULTADOB')
    hresultadoc = models.FloatField(blank=True, null=True, db_column='HRESULTADOC')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    tipoexamen = models.FloatField(blank=True, null=True, db_column='TIPOEXAMEN')
    tipomuestra1 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA1')
    tipomuestra2 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA2')
    tratamientoprevio = models.FloatField(blank=True, null=True, db_column='TRATAMIENTOPREVIO')
    valorlectura = models.FloatField(blank=True, null=True, db_column='VALORLECTURA')
    vph = models.FloatField(blank=True, null=True, db_column='VPH')
    usuario_amb = models.CharField(blank=True, null=True, db_column='USUARIO_AMB', max_length=10)
    usuario_lab = models.CharField(blank=True, null=True, db_column='USUARIO_LAB', max_length=10)
    hcentromuestra = models.FloatField(blank=True, null=True, db_column='HCENTROMUESTRA')
    observacionesmacro = models.CharField(blank=True, null=True, db_column='OBSERVACIONESMACRO', max_length=4000)
    muestrautero = models.CharField(blank=True, null=True, db_column='MUESTRAUTERO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_BIOPSIAT\""


class TCasosmm(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    num_partos = models.FloatField(blank=True, null=True, db_column='NUM_PARTOS')
    hijos_nacvivos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACVIVOS')
    hijos_nacmuertos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACMUERTOS')
    hijos_nacabortos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACABORTOS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=25)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_CASOSMM\""


class TCasosmmi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=25)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=25)
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    hsexo = models.FloatField(blank=True, null=True, db_column='HSEXO')
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    fechaocurrencia = models.DateTimeField(blank=True, null=True, db_column='FECHAOCURRENCIA')
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=25)
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    hresidencia_pais = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAIS')
    nacionalidad = models.CharField(blank=True, null=True, db_column='NACIONALIDAD', max_length=1)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    numeromsds = models.CharField(blank=True, null=True, db_column='NUMEROMSDS', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_CASOSMMI\""


class TCaummedi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    causa1 = models.CharField(blank=True, null=True, db_column='CAUSA1', max_length=120)
    causa2 = models.CharField(blank=True, null=True, db_column='CAUSA2', max_length=120)
    causa3 = models.CharField(blank=True, null=True, db_column='CAUSA3', max_length=120)
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_CAUMMEDI\""


class TCertmort(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    numeropartida = models.CharField(blank=True, null=True, db_column='NUMEROPARTIDA', max_length=10)
    numeromsds = models.CharField(blank=True, null=True, db_column='NUMEROMSDS', max_length=10)
    certificado = models.CharField(blank=True, null=True, db_column='CERTIFICADO', max_length=10)
    annocertificado = models.FloatField(blank=True, null=True, db_column='ANNOCERTIFICADO')
    mfetal = models.FloatField(blank=True, null=True, db_column='MFETAL')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=100)
    nacionalidad = models.FloatField(blank=True, null=True, db_column='NACIONALIDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=15)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    fecha_m = models.DateTimeField(blank=True, null=True, db_column='FECHA_M')
    fecha_n = models.DateTimeField(blank=True, null=True, db_column='FECHA_N')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    tipoedad = models.CharField(blank=True, null=True, db_column='TIPOEDAD', max_length=1)
    hestadocivil = models.FloatField(blank=True, null=True, db_column='HESTADOCIVIL')
    annocursado = models.FloatField(blank=True, null=True, db_column='ANNOCURSADO')
    annoterminado = models.FloatField(blank=True, null=True, db_column='ANNOTERMINADO')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    hprofesion = models.FloatField(blank=True, null=True, db_column='HPROFESION')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    hpais = models.FloatField(blank=True, null=True, db_column='HPAIS')
    hsitio_m = models.FloatField(blank=True, null=True, db_column='HSITIO_M')
    nombreclinica = models.CharField(blank=True, null=True, db_column='NOMBRECLINICA', max_length=100)
    hlocaocurrencia = models.FloatField(blank=True, null=True, db_column='HLOCAOCURRENCIA')
    direcocurrencia = models.CharField(blank=True, null=True, db_column='DIRECOCURRENCIA', max_length=250)
    hlocaresidencia = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIA')
    direcresidencia = models.CharField(blank=True, null=True, db_column='DIRECRESIDENCIA', max_length=200)
    hpresenciaembarazo = models.FloatField(blank=True, null=True, db_column='HPRESENCIAEMBARAZO')
    hcausabasica = models.FloatField(blank=True, null=True, db_column='HCAUSABASICA')
    otrosestados = models.CharField(blank=True, null=True, db_column='OTROSESTADOS', max_length=400)
    autopsia = models.FloatField(blank=True, null=True, db_column='AUTOPSIA')
    examencuerpo = models.FloatField(blank=True, null=True, db_column='EXAMENCUERPO')
    examenlab = models.FloatField(blank=True, null=True, db_column='EXAMENLAB')
    interrogatorio = models.FloatField(blank=True, null=True, db_column='INTERROGATORIO')
    historiaclinica = models.FloatField(blank=True, null=True, db_column='HISTORIACLINICA')
    numerodiagnostico = models.CharField(blank=True, null=True, db_column='NUMERODIAGNOSTICO', max_length=10)
    hmedicofirmante = models.FloatField(blank=True, null=True, db_column='HMEDICOFIRMANTE')
    otromedfirmante = models.CharField(blank=True, null=True, db_column='OTROMEDFIRMANTE', max_length=100)
    asistenciamedica = models.FloatField(blank=True, null=True, db_column='ASISTENCIAMEDICA')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    firmamedico = models.FloatField(blank=True, null=True, db_column='FIRMAMEDICO')
    direcservicio_m = models.CharField(blank=True, null=True, db_column='DIRECSERVICIO_M', max_length=200)
    descernomedica = models.CharField(blank=True, null=True, db_column='DESCERNOMEDICA', max_length=250)
    hdestinocuerpo = models.FloatField(blank=True, null=True, db_column='HDESTINOCUERPO')
    numeropermiso = models.CharField(blank=True, null=True, db_column='NUMEROPERMISO', max_length=10)
    hregionpermiso = models.FloatField(blank=True, null=True, db_column='HREGIONPERMISO')
    lugarpermiso = models.CharField(blank=True, null=True, db_column='LUGARPERMISO', max_length=200)
    fechapermiso = models.DateTimeField(blank=True, null=True, db_column='FECHAPERMISO')
    hregionexpe = models.FloatField(blank=True, null=True, db_column='HREGIONEXPE')
    lugarexpedicion = models.CharField(blank=True, null=True, db_column='LUGAREXPEDICION', max_length=200)
    fechaexpe = models.DateTimeField(blank=True, null=True, db_column='FECHAEXPE')
    firmaautoridad = models.FloatField(blank=True, null=True, db_column='FIRMAAUTORIDAD')
    sello = models.FloatField(blank=True, null=True, db_column='SELLO')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    hmadre = models.FloatField(blank=True, null=True, db_column='HMADRE')
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    edad2 = models.FloatField(blank=True, null=True, db_column='EDAD2')
    tipoedad2 = models.CharField(blank=True, null=True, db_column='TIPOEDAD2', max_length=1)
    transresi = models.FloatField(blank=True, null=True, db_column='TRANSRESI')
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    sabeleer = models.CharField(blank=True, null=True, db_column='SABELEER', max_length=1)
    hijosnac_v = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_V')
    hijosnac_av = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_AV')
    hijosnac_m = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_M')
    hijosnac_mf = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_MF')
    tomo = models.CharField(blank=True, null=True, db_column='TOMO', max_length=50)
    folio = models.CharField(blank=True, null=True, db_column='FOLIO', max_length=50)
    libro = models.CharField(blank=True, null=True, db_column='LIBRO', max_length=50)
    acta = models.CharField(blank=True, null=True, db_column='ACTA', max_length=50)
    nacmadrefallecido = models.FloatField(blank=True, null=True, db_column='NACMADREFALLECIDO')
    cimadrefallecido = models.CharField(blank=True, null=True, db_column='CIMADREFALLECIDO', max_length=15)
    nommadrefallecido = models.CharField(blank=True, null=True, db_column='NOMMADREFALLECIDO', max_length=50)
    nacpadrefallecido = models.FloatField(blank=True, null=True, db_column='NACPADREFALLECIDO')
    cipadrefallecido = models.CharField(blank=True, null=True, db_column='CIPADREFALLECIDO', max_length=15)
    nompadrefallecido = models.CharField(blank=True, null=True, db_column='NOMPADREFALLECIDO', max_length=50)
    nacregistrador = models.FloatField(blank=True, null=True, db_column='NACREGISTRADOR')
    ciregistrador = models.CharField(blank=True, null=True, db_column='CIREGISTRADOR', max_length=10)
    nomregistrador = models.CharField(blank=True, null=True, db_column='NOMREGISTRADOR', max_length=50)
    tomopartidanac = models.CharField(blank=True, null=True, db_column='TOMOPARTIDANAC', max_length=50)
    foliopartidanac = models.CharField(blank=True, null=True, db_column='FOLIOPARTIDANAC', max_length=50)
    libropartidanac = models.CharField(blank=True, null=True, db_column='LIBROPARTIDANAC', max_length=50)
    actapartidanac = models.CharField(blank=True, null=True, db_column='ACTAPARTIDANAC', max_length=50)
    horamuerte = models.CharField(blank=True, null=True, db_column='HORAMUERTE', max_length=20)
    hestado = models.FloatField(blank=True, null=True, db_column='HESTADO')
    hlocaresidenciafp = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIAFP')
    hestablecimiento_ocur = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO_OCUR')
    especial = models.FloatField(blank=True, null=True, db_column='ESPECIAL')
    otrodiagnostico = models.FloatField(blank=True, null=True, db_column='OTRODIAGNOSTICO')
    otrodiagnosticocert = models.CharField(blank=True, null=True, db_column='OTRODIAGNOSTICOCERT', max_length=50)
    fechaelaboracion = models.DateTimeField(blank=True, null=True, db_column='FECHAELABORACION')
    numeroautopsia = models.CharField(blank=True, null=True, db_column='NUMEROAUTOPSIA', max_length=20)
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=500)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_CERTMORT\""


class TCertnaci(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    fechacertificado = models.DateTimeField(blank=True, null=True, db_column='FECHACERTIFICADO')
    htipoderegistro = models.FloatField(blank=True, null=True, db_column='HTIPODEREGISTRO')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    codigosas = models.CharField(blank=True, null=True, db_column='CODIGOSAS', max_length=10)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    hlocalidadoc = models.FloatField(blank=True, null=True, db_column='HLOCALIDADOC')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    nombredirector = models.CharField(blank=True, null=True, db_column='NOMBREDIRECTOR', max_length=100)
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    actadenacimento = models.CharField(blank=True, null=True, db_column='ACTADENACIMENTO', max_length=50)
    tomo = models.CharField(blank=True, null=True, db_column='TOMO', max_length=50)
    folio = models.CharField(blank=True, null=True, db_column='FOLIO', max_length=50)
    libro = models.CharField(blank=True, null=True, db_column='LIBRO', max_length=50)
    testigo1 = models.CharField(blank=True, null=True, db_column='TESTIGO1', max_length=40)
    testigoci1 = models.CharField(blank=True, null=True, db_column='TESTIGOCI1', max_length=10)
    testigoedad1 = models.FloatField(blank=True, null=True, db_column='TESTIGOEDAD1')
    testigo2 = models.CharField(blank=True, null=True, db_column='TESTIGO2', max_length=40)
    testigoci2 = models.CharField(blank=True, null=True, db_column='TESTIGOCI2', max_length=10)
    testigoedad2 = models.FloatField(blank=True, null=True, db_column='TESTIGOEDAD2')
    jefecivil = models.CharField(blank=True, null=True, db_column='JEFECIVIL', max_length=40)
    jefecivilci = models.CharField(blank=True, null=True, db_column='JEFECIVILCI', max_length=10)
    fecharegcivil = models.DateTimeField(blank=True, null=True, db_column='FECHAREGCIVIL')
    especial = models.FloatField(blank=True, null=True, db_column='ESPECIAL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_CERTNACI\""


class TComaguda(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_COMAGUDA\""


class TComcroni(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_COMCRONI\""


class TComdisca(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_COMDISCA\""


class TCompcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    tipo = models.CharField(blank=True, null=True, db_column='TIPO', max_length=1)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_COMPCARD\""


class TComplica(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_COMPLICA\""


class TComquir(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hcomplicacion = models.FloatField(blank=True, null=True, db_column='HCOMPLICACION')
    htipocomplicacion = models.FloatField(blank=True, null=True, db_column='HTIPOCOMPLICACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_COMQUIR\""


class TComsegim(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_COMSEGIM\""


class TDiagasoc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcie10 = models.BigIntegerField(blank=True, null=True, db_column='HCIE10')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_DIAGASOC\""


class TDocudeng(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    c_fiebre = models.FloatField(blank=True, null=True, db_column='C_FIEBRE')
    c_hemorragico = models.FloatField(blank=True, null=True, db_column='C_HEMORRAGICO')
    c_hospitalizado = models.FloatField(blank=True, null=True, db_column='C_HOSPITALIZADO')
    c_muestra = models.FloatField(blank=True, null=True, db_column='C_MUESTRA')
    c_positivo = models.FloatField(blank=True, null=True, db_column='C_POSITIVO')
    c_negativo = models.FloatField(blank=True, null=True, db_column='C_NEGATIVO')
    c_pendiente = models.FloatField(blank=True, null=True, db_column='C_PENDIENTE')
    c_epidemiologico = models.FloatField(blank=True, null=True, db_column='C_EPIDEMIOLOGICO')
    c_laboratorio = models.FloatField(blank=True, null=True, db_column='C_LABORATORIO')
    nro_semana = models.FloatField(blank=True, null=True, db_column='NRO_SEMANA')
    casos_semana = models.FloatField(blank=True, null=True, db_column='CASOS_SEMANA')
    htipodengue = models.FloatField(blank=True, null=True, db_column='HTIPODENGUE')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    totaldengue = models.FloatField(blank=True, null=True, db_column='TOTALDENGUE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_DOCUDENG\""


class TDocument(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    tipo = models.FloatField(blank=True, null=True, db_column='TIPO')
    horigen = models.FloatField(blank=True, null=True, db_column='HORIGEN')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=500)
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=20)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_DOCUMENT\""


class TDocusosp(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    c_estudio = models.FloatField(blank=True, null=True, db_column='C_ESTUDIO')
    c_descartado = models.FloatField(blank=True, null=True, db_column='C_DESCARTADO')
    c_confirmado = models.FloatField(blank=True, null=True, db_column='C_CONFIRMADO')
    c_compartido = models.FloatField(blank=True, null=True, db_column='C_COMPARTIDO')
    c_notificado = models.FloatField(blank=True, null=True, db_column='C_NOTIFICADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_DOCUSOSP\""


class TEstable(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    htipo = models.FloatField(blank=True, null=True, db_column='HTIPO')
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=250)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefono = models.CharField(blank=True, null=True, db_column='TELEFONO', max_length=50)
    status = models.CharField(blank=True, null=True, db_column='STATUS', max_length=1)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    domiciliado = models.CharField(blank=True, null=True, db_column='DOMICILIADO', max_length=1)
    rif = models.CharField(blank=True, null=True, db_column='RIF', max_length=20)
    tipoestablec = models.FloatField(blank=True, null=True, db_column='TIPOESTABLEC')
    cuentadante = models.FloatField(blank=True, null=True, db_column='CUENTADANTE')
    hnivel = models.FloatField(blank=True, null=True, db_column='HNIVEL')
    x_utm = models.DecimalField(blank=True, null=True, db_column='X_UTM', max_digits=24, decimal_places=6)
    y_utm = models.DecimalField(blank=True, null=True, db_column='Y_UTM', max_digits=24, decimal_places=6)
    altitud = models.DecimalField(blank=True, null=True, db_column='ALTITUD', max_digits=10, decimal_places=2)
    funcionamiento = models.CharField(blank=True, null=True, db_column='FUNCIONAMIENTO', max_length=1)
    hdependencia_adm = models.FloatField(blank=True, null=True, db_column='HDEPENDENCIA_ADM')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_ESTABLE\""


class TEventos(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_EVENTOS\""


class TFdolorto(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_programa = models.FloatField(blank=True, null=True, db_column='HFICHA_PROGRAMA')
    hfichadeldolor = models.FloatField(blank=True, null=True, db_column='HFICHADELDOLOR')
    si = models.FloatField(blank=True, null=True, db_column='SI')
    no = models.FloatField(blank=True, null=True, db_column='NO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_FDOLORTO\""


class TFichaacc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=15)
    fecha_oc = models.DateTimeField(blank=True, null=True, db_column='FECHA_OC')
    hora_oc = models.CharField(blank=True, null=True, db_column='HORA_OC', max_length=20)
    hlocalidad_oc = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_OC')
    sitio_oc = models.CharField(blank=True, null=True, db_column='SITIO_OC', max_length=150)
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    fallecio = models.FloatField(blank=True, null=True, db_column='FALLECIO')
    hora_muerte = models.CharField(blank=True, null=True, db_column='HORA_MUERTE', max_length=20)
    hsitio_muerte = models.FloatField(blank=True, null=True, db_column='HSITIO_MUERTE')
    influencia_alcohol = models.FloatField(blank=True, null=True, db_column='INFLUENCIA_ALCOHOL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_FICHAACC\""


class TFichasep(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    hlocalidad_ficha = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIDAD_FICHA')
    nro_caso = models.CharField(blank=True, null=True, db_column='NRO_CASO', max_length=20)
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    ano_fecha_reg = models.IntegerField(blank=True, null=True, db_column='ANO_FECHA_REG')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=254)
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_FICHASEP\""


class THechosvi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha = models.FloatField(blank=True, null=True, db_column='HFICHA')
    htipo_hecho = models.FloatField(blank=True, null=True, db_column='HTIPO_HECHO')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hefectuo_hecho = models.FloatField(blank=True, null=True, db_column='HEFECTUO_HECHO')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hubic_diagnostico = models.FloatField(blank=True, null=True, db_column='HUBIC_DIAGNOSTICO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_HECHOSVI\""


class TIntquir(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hintervencion = models.FloatField(blank=True, null=True, db_column='HINTERVENCION')
    hanatomia = models.FloatField(blank=True, null=True, db_column='HANATOMIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=1000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_INTQUIR\""


class TLugarvis(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    lugar = models.CharField(blank=True, null=True, db_column='LUGAR', max_length=200)
    tiempo_perm = models.IntegerField(blank=True, null=True, db_column='TIEMPO_PERM')
    unid_tiemperm = models.CharField(blank=True, null=True, db_column='UNID_TIEMPERM', max_length=10)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_LUGARVIS\""


class TMadrnaci(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    apellidos = models.CharField(blank=True, null=True, db_column='APELLIDOS', max_length=100)
    pasaporte = models.CharField(blank=True, null=True, db_column='PASAPORTE', max_length=20)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=20)
    phistoriaclinica = models.CharField(blank=True, null=True, db_column='PHISTORIACLINICA', max_length=20)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edadm = models.FloatField(blank=True, null=True, db_column='EDADM')
    edadp = models.FloatField(blank=True, null=True, db_column='EDADP')
    estadocivil = models.FloatField(blank=True, null=True, db_column='ESTADOCIVIL')
    annosmatrimonio = models.FloatField(blank=True, null=True, db_column='ANNOSMATRIMONIO')
    nacvivos = models.FloatField(blank=True, null=True, db_column='NACVIVOS')
    nacionm = models.FloatField(blank=True, null=True, db_column='NACIONM')
    nacionp = models.FloatField(blank=True, null=True, db_column='NACIONP')
    hentidam = models.FloatField(blank=True, null=True, db_column='HENTIDAM')
    hentidap = models.FloatField(blank=True, null=True, db_column='HENTIDAP')
    hpaism = models.FloatField(blank=True, null=True, db_column='HPAISM')
    hpaisp = models.FloatField(blank=True, null=True, db_column='HPAISP')
    actualvivos = models.FloatField(blank=True, null=True, db_column='ACTUALVIVOS')
    leerescribir = models.FloatField(blank=True, null=True, db_column='LEERESCRIBIR')
    nacvivosfallec = models.FloatField(blank=True, null=True, db_column='NACVIVOSFALLEC')
    muertesfetales = models.FloatField(blank=True, null=True, db_column='MUERTESFETALES')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    profesion = models.FloatField(blank=True, null=True, db_column='PROFESION')
    controlprenatal = models.FloatField(blank=True, null=True, db_column='CONTROLPRENATAL')
    telefonom = models.CharField(blank=True, null=True, db_column='TELEFONOM', max_length=20)
    ptelefono = models.CharField(blank=True, null=True, db_column='PTELEFONO', max_length=20)
    ocupacion = models.FloatField(blank=True, null=True, db_column='OCUPACION')
    pcedula = models.CharField(blank=True, null=True, db_column='PCEDULA', max_length=10)
    pnombres = models.CharField(blank=True, null=True, db_column='PNOMBRES', max_length=100)
    ppasaporte = models.CharField(blank=True, null=True, db_column='PPASAPORTE', max_length=20)
    pdireccion = models.CharField(blank=True, null=True, db_column='PDIRECCION', max_length=100)
    hpresidencia = models.FloatField(blank=True, null=True, db_column='HPRESIDENCIA')
    pfechanacimiento = models.DateTimeField(blank=True, null=True, db_column='PFECHANACIMIENTO')
    pestadocivil = models.FloatField(blank=True, null=True, db_column='PESTADOCIVIL')
    pleerescribir = models.FloatField(blank=True, null=True, db_column='PLEERESCRIBIR')
    hpultimogrado = models.FloatField(blank=True, null=True, db_column='HPULTIMOGRADO')
    pprofesion = models.FloatField(blank=True, null=True, db_column='PPROFESION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=100)
    pocupacion = models.FloatField(blank=True, null=True, db_column='POCUPACION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    nacionalidap = models.FloatField(blank=True, null=True, db_column='NACIONALIDAP')
    nacionalidam = models.FloatField(blank=True, null=True, db_column='NACIONALIDAM')
    unionmat = models.FloatField(blank=True, null=True, db_column='UNIONMAT')
    nroconsultaspre = models.FloatField(blank=True, null=True, db_column='NROCONSULTASPRE')
    hetniam = models.FloatField(blank=True, null=True, db_column='HETNIAM')
    hetniap = models.FloatField(blank=True, null=True, db_column='HETNIAP')
    hablaetniam = models.FloatField(blank=True, null=True, db_column='HABLAETNIAM')
    hablaetniap = models.FloatField(blank=True, null=True, db_column='HABLAETNIAP')
    ultimogradom = models.FloatField(blank=True, null=True, db_column='ULTIMOGRADOM')
    ultimogradop = models.FloatField(blank=True, null=True, db_column='ULTIMOGRADOP')
    residenciam = models.IntegerField(blank=True, null=True, db_column='RESIDENCIAM')
    hresidencia_paism = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAISM')
    residenciap = models.IntegerField(blank=True, null=True, db_column='RESIDENCIAP')
    hresidencia_paisp = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAISP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MADRNACI\""


class TMbased(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    sid = models.CharField(blank=True, null=True, db_column='SID', max_length=10)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    texto_fecha = models.CharField(blank=True, null=True, db_column='TEXTO_FECHA', max_length=20)
    nombre_tablespace = models.CharField(blank=True, null=True, db_column='NOMBRE_TABLESPACE', max_length=50)
    ts_size_mb = models.DecimalField(blank=True, null=True, db_column='TS_SIZE_MB', max_digits=11, decimal_places=2)
    ts_usado_mb = models.DecimalField(blank=True, null=True, db_column='TS_USADO_MB', max_digits=11, decimal_places=2)
    ts_usado_pc = models.DecimalField(blank=True, null=True, db_column='TS_USADO_PC', max_digits=11, decimal_places=2)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MBASED\""


class TMcaumorb(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MCAUMORB\""


class TMcausmre(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    desenfermedad = models.CharField(blank=True, null=True, db_column='DESENFERMEDAD', max_length=200)
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MCAUSMRE\""


class TMhojarep(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    reparapor = models.FloatField(blank=True, null=True, db_column='REPARAPOR')
    atravesde = models.FloatField(blank=True, null=True, db_column='ATRAVESDE')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=10)
    fecharepara = models.DateTimeField(blank=True, null=True, db_column='FECHAREPARA')
    otrosmedios = models.CharField(blank=True, null=True, db_column='OTROSMEDIOS', max_length=100)
    nombreclinico = models.CharField(blank=True, null=True, db_column='NOMBRECLINICO', max_length=100)
    nacmedico = models.FloatField(blank=True, null=True, db_column='NACMEDICO')
    cedulaclinico = models.CharField(blank=True, null=True, db_column='CEDULACLINICO', max_length=15)
    nombreepidem = models.CharField(blank=True, null=True, db_column='NOMBREEPIDEM', max_length=100)
    nacepidem = models.FloatField(blank=True, null=True, db_column='NACEPIDEM')
    cedulaepidem = models.CharField(blank=True, null=True, db_column='CEDULAEPIDEM', max_length=15)
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MHOJAREP\""


class TMortanul(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausaanulado = models.FloatField(blank=True, null=True, db_column='HCAUSAANULADO')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    fecha_anulado = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANULADO')
    causa_anulado = models.CharField(blank=True, null=True, db_column='CAUSA_ANULADO', max_length=200)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fecha_operacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MORTANUL\""


class TMortcaus(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    desenfermedad = models.CharField(blank=True, null=True, db_column='DESENFERMEDAD', max_length=200)
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MORTCAUS\""


class TMortfeta(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hmadre = models.FloatField(blank=True, null=True, db_column='HMADRE')
    hduracionemba = models.FloatField(blank=True, null=True, db_column='HDURACIONEMBA')
    hnactipoemba = models.FloatField(blank=True, null=True, db_column='HNACTIPOEMBA')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    hm_relaparto = models.FloatField(blank=True, null=True, db_column='HM_RELAPARTO')
    pesofeto = models.FloatField(blank=True, null=True, db_column='PESOFETO')
    ignoradopeso = models.FloatField(blank=True, null=True, db_column='IGNORADOPESO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    hasistenteparto = models.FloatField(blank=True, null=True, db_column='HASISTENTEPARTO')
    otroasistparto = models.CharField(blank=True, null=True, db_column='OTROASISTPARTO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MORTFETA\""


class TMortmadr(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=100)
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    nacionalidad = models.FloatField(blank=True, null=True, db_column='NACIONALIDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=15)
    hprofesion = models.FloatField(blank=True, null=True, db_column='HPROFESION')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    annocursado = models.FloatField(blank=True, null=True, db_column='ANNOCURSADO')
    annoterminado = models.FloatField(blank=True, null=True, db_column='ANNOTERMINADO')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    hijosnac_v = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_V')
    hijosnac_m = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_M')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    sabeleer = models.CharField(blank=True, null=True, db_column='SABELEER', max_length=1)
    hestadocivil = models.FloatField(blank=True, null=True, db_column='HESTADOCIVIL')
    hijosnac_av = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_AV')
    hijosnac_mf = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_MF')
    hlocaresidencia = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIA')
    direcresidencia = models.CharField(blank=True, null=True, db_column='DIRECRESIDENCIA', max_length=200)
    hlocaresidenciafp = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIAFP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MORTMADR\""


class TMortviol(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    htipo_m = models.FloatField(blank=True, null=True, db_column='HTIPO_M')
    hora_mv = models.CharField(blank=True, null=True, db_column='HORA_MV', max_length=20)
    fecha_mv = models.DateTimeField(blank=True, null=True, db_column='FECHA_MV')
    descripcionsuceso = models.CharField(blank=True, null=True, db_column='DESCRIPCIONSUCESO', max_length=400)
    hlugarsuceso = models.FloatField(blank=True, null=True, db_column='HLUGARSUCESO')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MORTVIOL\""


class TMrespa(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    sid = models.CharField(blank=True, null=True, db_column='SID', max_length=10)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    texto_fecha = models.CharField(blank=True, null=True, db_column='TEXTO_FECHA', max_length=20)
    hdd_bd_usado = models.CharField(blank=True, null=True, db_column='HDD_BD_USADO', max_length=10)
    hdd_bd_size = models.CharField(blank=True, null=True, db_column='HDD_BD_SIZE', max_length=10)
    hdd_bk_usado = models.CharField(blank=True, null=True, db_column='HDD_BK_USADO', max_length=10)
    hdd_bk_size = models.CharField(blank=True, null=True, db_column='HDD_BK_SIZE', max_length=10)
    hdd_opt_usado = models.CharField(blank=True, null=True, db_column='HDD_OPT_USADO', max_length=10)
    hdd_opt_size = models.CharField(blank=True, null=True, db_column='HDD_OPT_SIZE', max_length=10)
    tam_respaldo_dmp = models.CharField(blank=True, null=True, db_column='TAM_RESPALDO_DMP', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_MRESPA\""


class TNotdsp04(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    nota = models.CharField(blank=True, null=True, db_column='NOTA', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_NOTDSP04\""


class TOrggeog(models.Model):
    num_region = models.BigIntegerField(blank=True, null=True, primary_key=True, db_column='NUM_REGION')
    cod_categoria = models.IntegerField(blank=True, null=True, db_column='COD_CATEGORIA')
    region_precedente = models.BigIntegerField(blank=True, null=True, db_column='REGION_PRECEDENTE')
    des_region = models.CharField(blank=True, null=True, db_column='DES_REGION', max_length=150)
    cod_ocei = models.CharField(blank=True, null=True, db_column='COD_OCEI', max_length=30)
    can_casas = models.IntegerField(blank=True, null=True, db_column='CAN_CASAS')
    poblacion_estimada = models.IntegerField(blank=True, null=True, db_column='POBLACION_ESTIMADA')
    gac_gis_lat = models.CharField(blank=True, null=True, db_column='GAC_GIS_LAT', max_length=18)
    gac_gis_long = models.CharField(blank=True, null=True, db_column='GAC_GIS_LONG', max_length=18)
    gac_gis_proj = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_PROJ')
    gac_gis_tagx = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGX', max_digits=14, decimal_places=4)
    gac_gis_tagy = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGY', max_digits=14, decimal_places=4)
    gac_gis_tagf = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_TAGF')
    gac_gis_tagt = models.CharField(blank=True, null=True, db_column='GAC_GIS_TAGT', max_length=1)
    gac_gis_tagh = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGH', max_digits=8, decimal_places=2)
    gac_gis_tagc = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_TAGC')
    gac_gis_tagr = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGR', max_digits=8, decimal_places=3)
    gac_gis_pcol = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_PCOL')
    gac_gis_lib = models.CharField(blank=True, null=True, db_column='GAC_GIS_LIB', max_length=50)
    gac_clav_loc = models.CharField(blank=True, null=True, db_column='GAC_CLAV_LOC', max_length=9)
    gac_cla_ocei = models.CharField(blank=True, null=True, db_column='GAC_CLA_OCEI', max_length=10)
    gac_nombre = models.CharField(blank=True, null=True, db_column='GAC_NOMBRE', max_length=40)
    gac_generico = models.CharField(blank=True, null=True, db_column='GAC_GENERICO', max_length=4)
    gac_latitud = models.CharField(blank=True, null=True, db_column='GAC_LATITUD', max_length=6)
    gac_longitud = models.CharField(blank=True, null=True, db_column='GAC_LONGITUD', max_length=6)
    gac_ubic_polit = models.CharField(blank=True, null=True, db_column='GAC_UBIC_POLIT', max_length=6)
    gac_estado = models.CharField(blank=True, null=True, db_column='GAC_ESTADO', max_length=2)
    gac_mun_dis = models.CharField(blank=True, null=True, db_column='GAC_MUN_DIS', max_length=2)
    gac_for_par = models.CharField(blank=True, null=True, db_column='GAC_FOR_PAR', max_length=2)
    gac_localidad = models.CharField(blank=True, null=True, db_column='GAC_LOCALIDAD', max_length=3)
    gac_carta = models.CharField(blank=True, null=True, db_column='GAC_CARTA', max_length=4)
    gac_cuadricula = models.CharField(blank=True, null=True, db_column='GAC_CUADRICULA', max_length=6)
    cod_estado = models.CharField(blank=True, null=True, db_column='COD_ESTADO', max_length=20)
    obs_region = models.CharField(blank=True, null=True, db_column='OBS_REGION', max_length=250)
    clave_ctrl = models.BigIntegerField(blank=True, null=True, db_column='CLAVE_CTRL')
    edo_ctrl = models.BigIntegerField(blank=True, null=True, db_column='EDO_CTRL')
    codigointerno = models.CharField(blank=True, null=True, db_column='CODIGOINTERNO', max_length=25)
    nombrelargo = models.CharField(blank=True, null=True, db_column='NOMBRELARGO', max_length=500)
    cod_ine = models.CharField(blank=True, null=True, db_column='COD_INE', max_length=14)
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_ORGGEOG\""


class TOtrotrat(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    tratamiento = models.CharField(blank=True, null=True, db_column='TRATAMIENTO', max_length=100)
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    indicaciones = models.CharField(blank=True, null=True, db_column='INDICACIONES', max_length=100)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_OTROTRAT\""


class TPacconde(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hcondicionespecial = models.FloatField(blank=True, null=True, db_column='HCONDICIONESPECIAL')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PACCONDE\""


class TPaciend(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=15)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    tipoedad = models.FloatField(blank=True, null=True, db_column='TIPOEDAD')
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=254)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    origen = models.FloatField(blank=True, null=True, db_column='ORIGEN')
    semana = models.FloatField(blank=True, null=True, db_column='SEMANA')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    tipodengue = models.FloatField(blank=True, null=True, db_column='TIPODENGUE')
    asistencia = models.FloatField(blank=True, null=True, db_column='ASISTENCIA')
    muerte = models.FloatField(blank=True, null=True, db_column='MUERTE')
    fechacreacion = models.DateTimeField(blank=True, null=True, db_column='FECHACREACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PACIEND\""


class TPacienfe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=25)
    apellidopaciente = models.CharField(blank=True, null=True, db_column='APELLIDOPACIENTE', max_length=25)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    lugar_nac = models.CharField(blank=True, null=True, db_column='LUGAR_NAC', max_length=50)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=254)
    hubicacion = models.BigIntegerField(blank=True, null=True, db_column='HUBICACION')
    tiempo_residencia = models.CharField(blank=True, null=True, db_column='TIEMPO_RESIDENCIA', max_length=10)
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    hlocalizacion = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIZACION')
    otro_tiempo_res = models.CharField(blank=True, null=True, db_column='OTRO_TIEMPO_RES', max_length=10)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    hconyugal = models.FloatField(blank=True, null=True, db_column='HCONYUGAL')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    analfabeta = models.CharField(blank=True, null=True, db_column='ANALFABETA', max_length=2)
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    anos_aprobados = models.IntegerField(blank=True, null=True, db_column='ANOS_APROBADOS')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    nomrepresentante = models.CharField(blank=True, null=True, db_column='NOMREPRESENTANTE', max_length=40)
    numero_hijo = models.CharField(blank=True, null=True, db_column='NUMERO_HIJO', max_length=2)
    fechadefuncion = models.DateTimeField(blank=True, null=True, db_column='FECHADEFUNCION')
    nacionalidad = models.CharField(blank=True, null=True, db_column='NACIONALIDAD', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PACIENFE\""


class TPacientt(models.Model):
    usuario = models.CharField(blank=True, null=True, primary_key=True, db_column='USUARIO', max_length=10)
    id = models.FloatField(blank=True, null=True, db_column='ID')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=50)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PACIENTT\""


class TPacimisi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hmision = models.FloatField(blank=True, null=True, db_column='HMISION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PACIMISI\""


class TPerquir(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hrolmedico = models.FloatField(blank=True, null=True, db_column='HROLMEDICO')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PERQUIR\""


class TPersmedi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=8)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    codigosas = models.CharField(blank=True, null=True, db_column='CODIGOSAS', max_length=12)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefonos = models.CharField(blank=True, null=True, db_column='TELEFONOS', max_length=35)
    cargo = models.CharField(blank=True, null=True, db_column='CARGO', max_length=50)
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PERSMEDI\""


class TPobesta(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    pob_total = models.FloatField(blank=True, null=True, db_column='POB_TOTAL')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    cobertura = models.FloatField(blank=True, null=True, db_column='COBERTURA')
    distribucion = models.FloatField(blank=True, null=True, db_column='DISTRIBUCION')
    pobcobertura = models.FloatField(blank=True, null=True, db_column='POBCOBERTURA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_POBESTA\""


class TProdiabe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    anoinicio = models.FloatField(blank=True, null=True, db_column='ANOINICIO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    hprediabetico = models.FloatField(blank=True, null=True, db_column='HPREDIABETICO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PRODIABE\""


class TProgcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    anoinicio = models.FloatField(blank=True, null=True, db_column='ANOINICIO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    infartado = models.FloatField(blank=True, null=True, db_column='INFARTADO')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PROGCARD\""


class TProgmche(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_epidemiologica = models.FloatField(blank=True, null=True, db_column='HFICHA_EPIDEMIOLOGICA')
    otras_bases_diag = models.CharField(blank=True, null=True, db_column='OTRAS_BASES_DIAG', max_length=100)
    nro_muestra = models.CharField(blank=True, null=True, db_column='NRO_MUESTRA', max_length=20)
    fecha_toma = models.DateTimeField(blank=True, null=True, db_column='FECHA_TOMA')
    lugar_toma = models.CharField(blank=True, null=True, db_column='LUGAR_TOMA', max_length=100)
    fech_init_fiebre = models.DateTimeField(blank=True, null=True, db_column='FECH_INIT_FIEBRE')
    lugar_inicio_fiebre = models.CharField(blank=True, null=True, db_column='LUGAR_INICIO_FIEBRE', max_length=50)
    permanencia_lug_fiebre = models.CharField(blank=True, null=True, db_column='PERMANENCIA_LUG_FIEBRE', max_length=20)
    hcondicion_ingreso_malaria = models.FloatField(blank=True, null=True, db_column='HCONDICION_INGRESO_MALARIA')
    otros_tratamientos = models.CharField(blank=True, null=True, db_column='OTROS_TRATAMIENTOS', max_length=250)
    hubicacion_infeccion = models.BigIntegerField(blank=True, null=True, db_column='HUBICACION_INFECCION')
    hpais = models.FloatField(blank=True, null=True, db_column='HPAIS')
    tranf_sangre = models.CharField(blank=True, null=True, db_column='TRANF_SANGRE', max_length=1)
    tratam_endovenoso = models.CharField(blank=True, null=True, db_column='TRATAM_ENDOVENOSO', max_length=1)
    fecha_tranf = models.DateTimeField(blank=True, null=True, db_column='FECHA_TRANF')
    hestab_tranf = models.FloatField(blank=True, null=True, db_column='HESTAB_TRANF')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    fecha_result = models.DateTimeField(blank=True, null=True, db_column='FECHA_RESULT')
    hresultados_prog = models.FloatField(blank=True, null=True, db_column='HRESULTADOS_PROG')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    complicaciones = models.CharField(blank=True, null=True, db_column='COMPLICACIONES', max_length=250)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PROGMCHE\""


class TProgtube(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    serie = models.CharField(blank=True, null=True, db_column='SERIE', max_length=2)
    casonumero = models.CharField(blank=True, null=True, db_column='CASONUMERO', max_length=9)
    cohorte = models.CharField(blank=True, null=True, db_column='COHORTE', max_length=1)
    fechanotificacion = models.DateTimeField(blank=True, null=True, db_column='FECHANOTIFICACION')
    hcondicioncaso = models.FloatField(blank=True, null=True, db_column='HCONDICIONCASO')
    serologiavih = models.FloatField(blank=True, null=True, db_column='SEROLOGIAVIH')
    bacteriologia = models.FloatField(blank=True, null=True, db_column='BACTERIOLOGIA')
    clinica = models.FloatField(blank=True, null=True, db_column='CLINICA')
    radiologia = models.FloatField(blank=True, null=True, db_column='RADIOLOGIA')
    resradiologia = models.FloatField(blank=True, null=True, db_column='RESRADIOLOGIA')
    caverna = models.FloatField(blank=True, null=True, db_column='CAVERNA')
    histologia = models.FloatField(blank=True, null=True, db_column='HISTOLOGIA')
    tuberculina = models.FloatField(blank=True, null=True, db_column='TUBERCULINA')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    localizacion = models.FloatField(blank=True, null=True, db_column='LOCALIZACION')
    reslocalizacion = models.FloatField(blank=True, null=True, db_column='RESLOCALIZACION')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    hmedicocoord = models.FloatField(blank=True, null=True, db_column='HMEDICOCOORD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PROGTUBE\""


class TProttrom(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_programa = models.FloatField(blank=True, null=True, db_column='HFICHA_PROGRAMA')
    infartoprevio = models.FloatField(blank=True, null=True, db_column='INFARTOPREVIO')
    tiempoutil = models.CharField(blank=True, null=True, db_column='TIEMPOUTIL', max_length=2)
    tratamientotrombo = models.FloatField(blank=True, null=True, db_column='TRATAMIENTOTROMBO')
    li_pre_trombo = models.FloatField(blank=True, null=True, db_column='LI_PRE_TROMBO')
    li_post_trombo = models.FloatField(blank=True, null=True, db_column='LI_POST_TROMBO')
    li_enzima_pre_t = models.FloatField(blank=True, null=True, db_column='LI_ENZIMA_PRE_T')
    li_post_t = models.FloatField(blank=True, null=True, db_column='LI_POST_T')
    estancia = models.FloatField(blank=True, null=True, db_column='ESTANCIA')
    estudionoinvasivo = models.FloatField(blank=True, null=True, db_column='ESTUDIONOINVASIVO')
    hemodinamia = models.FloatField(blank=True, null=True, db_column='HEMODINAMIA')
    cirugia = models.FloatField(blank=True, null=True, db_column='CIRUGIA')
    ucc = models.FloatField(blank=True, null=True, db_column='UCC')
    uti = models.FloatField(blank=True, null=True, db_column='UTI')
    hospitalizacion = models.FloatField(blank=True, null=True, db_column='HOSPITALIZACION')
    d_egreso = models.FloatField(blank=True, null=True, db_column='D_EGRESO')
    d_morge = models.FloatField(blank=True, null=True, db_column='D_MORGE')
    d_otroservicio = models.FloatField(blank=True, null=True, db_column='D_OTROSERVICIO')
    sistolica = models.FloatField(blank=True, null=True, db_column='SISTOLICA')
    diastolica = models.FloatField(blank=True, null=True, db_column='DIASTOLICA')
    hora_iniciadolor = models.CharField(blank=True, null=True, db_column='HORA_INICIADOLOR', max_length=10)
    hora_asistencia = models.CharField(blank=True, null=True, db_column='HORA_ASISTENCIA', max_length=10)
    hora_ingresohosp = models.CharField(blank=True, null=True, db_column='HORA_INGRESOHOSP', max_length=10)
    evaltratamiento = models.FloatField(blank=True, null=True, db_column='EVALTRATAMIENTO')
    cualcomplicacion = models.CharField(blank=True, null=True, db_column='CUALCOMPLICACION', max_length=50)
    dondehospitalizacion = models.CharField(blank=True, null=True, db_column='DONDEHOSPITALIZACION', max_length=50)
    hcentroreferencia = models.FloatField(blank=True, null=True, db_column='HCENTROREFERENCIA')
    localizainfarto = models.FloatField(blank=True, null=True, db_column='LOCALIZAINFARTO')
    referidootroservicio = models.CharField(blank=True, null=True, db_column='REFERIDOOTROSERVICIO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PROTTROM\""


class TPrvihsid(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    nro_hijos = models.FloatField(blank=True, null=True, db_column='NRO_HIJOS')
    edad_ult_hijo = models.FloatField(blank=True, null=True, db_column='EDAD_ULT_HIJO')
    htransmision_por = models.FloatField(blank=True, null=True, db_column='HTRANSMISION_POR')
    hmedio_transmision = models.FloatField(blank=True, null=True, db_column='HMEDIO_TRANSMISION')
    otras_bases_diag = models.CharField(blank=True, null=True, db_column='OTRAS_BASES_DIAG', max_length=100)
    hcondicion_ingreso = models.FloatField(blank=True, null=True, db_column='HCONDICION_INGRESO')
    hactividad_osp = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD_OSP')
    otros_tratamientos = models.CharField(blank=True, null=True, db_column='OTROS_TRATAMIENTOS', max_length=250)
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    complicaciones = models.CharField(blank=True, null=True, db_column='COMPLICACIONES', max_length=4000)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_PRVIHSID\""


class TRcasosmi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcasosmmi = models.FloatField(blank=True, null=True, db_column='HCASOSMMI')
    hocurrencia = models.FloatField(blank=True, null=True, db_column='HOCURRENCIA')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausa_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSA_CIE10')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    control_prenatal = models.FloatField(blank=True, null=True, db_column='CONTROL_PRENATAL')
    peso = models.FloatField(blank=True, null=True, db_column='PESO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=50)
    hcausabas_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSABAS_CIE10')
    hnutricion = models.FloatField(blank=True, null=True, db_column='HNUTRICION')
    estanciahosp = models.FloatField(blank=True, null=True, db_column='ESTANCIAHOSP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RCASOSMI\""


class TRcasosmm(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcasosmmi = models.FloatField(blank=True, null=True, db_column='HCASOSMMI')
    hocurrencia = models.FloatField(blank=True, null=True, db_column='HOCURRENCIA')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausa_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSA_CIE10')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    control_prenatal = models.FloatField(blank=True, null=True, db_column='CONTROL_PRENATAL')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    hanexosperiodo = models.FloatField(blank=True, null=True, db_column='HANEXOSPERIODO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=50)
    periodoocurrencia = models.FloatField(blank=True, null=True, db_column='PERIODOOCURRENCIA')
    hcausabas_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSABAS_CIE10')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RCASOSMM\""


class TRegciru(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    interv_hosp_amb = models.FloatField(blank=True, null=True, db_column='INTERV_HOSP_AMB')
    fecha_interv = models.DateTimeField(blank=True, null=True, db_column='FECHA_INTERV')
    fecha_ingreso = models.DateTimeField(blank=True, null=True, db_column='FECHA_INGRESO')
    fecha_salida = models.DateTimeField(blank=True, null=True, db_column='FECHA_SALIDA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    numero_historia = models.CharField(blank=True, null=True, db_column='NUMERO_HISTORIA', max_length=20)
    hospital_elect_emerg = models.FloatField(blank=True, null=True, db_column='HOSPITAL_ELECT_EMERG')
    referido_centro = models.FloatField(blank=True, null=True, db_column='REFERIDO_CENTRO')
    referido_servicio = models.FloatField(blank=True, null=True, db_column='REFERIDO_SERVICIO')
    quirofano = models.FloatField(blank=True, null=True, db_column='QUIROFANO')
    toma_muestra = models.CharField(blank=True, null=True, db_column='TOMA_MUESTRA', max_length=200)
    intervencion_omitida = models.FloatField(blank=True, null=True, db_column='INTERVENCION_OMITIDA')
    otraintervencion_omitida = models.CharField(blank=True, null=True, db_column='OTRAINTERVENCION_OMITIDA', max_length=100)
    causa_egreso = models.FloatField(blank=True, null=True, db_column='CAUSA_EGRESO')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_REGCIRU\""


class TRegvacu(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hactividad = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hpacientemision = models.FloatField(blank=True, null=True, db_column='HPACIENTEMISION')
    embarazada = models.FloatField(blank=True, null=True, db_column='EMBARAZADA')
    lote = models.CharField(blank=True, null=True, db_column='LOTE', max_length=30)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    tipoedad2 = models.CharField(blank=True, null=True, db_column='TIPOEDAD2', max_length=1)
    edad2 = models.FloatField(blank=True, null=True, db_column='EDAD2')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    hpac_cond_espe = models.FloatField(blank=True, null=True, db_column='HPAC_COND_ESPE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_REGVACU\""


class TRendsp04(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    realizado = models.FloatField(blank=True, null=True, db_column='REALIZADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RENDSP04\""


class TRenepi15(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    casosx = models.FloatField(blank=True, null=True, db_column='CASOSX')
    casosp = models.FloatField(blank=True, null=True, db_column='CASOSP')
    casoss = models.FloatField(blank=True, null=True, db_column='CASOSS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RENEPI15\""


class TRengres(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    htipoestable = models.FloatField(blank=True, null=True, db_column='HTIPOESTABLE')
    cant_estable = models.FloatField(blank=True, null=True, db_column='CANT_ESTABLE')
    cant_documento = models.FloatField(blank=True, null=True, db_column='CANT_DOCUMENTO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RENGRES\""


class TRengsit(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    hcodificador = models.FloatField(blank=True, null=True, db_column='HCODIFICADOR')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    cant_casos = models.FloatField(blank=True, null=True, db_column='CANT_CASOS')
    cant_muertes = models.FloatField(blank=True, null=True, db_column='CANT_MUERTES')
    tiposituacion = models.FloatField(blank=True, null=True, db_column='TIPOSITUACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    grave = models.FloatField(blank=True, null=True, db_column='GRAVE')
    inusitado = models.FloatField(blank=True, null=True, db_column='INUSITADO')
    nacional = models.FloatField(blank=True, null=True, db_column='NACIONAL')
    internac = models.FloatField(blank=True, null=True, db_column='INTERNAC')
    fechainicio = models.DateTimeField(blank=True, null=True, db_column='FECHAINICIO')
    fechafin = models.DateTimeField(blank=True, null=True, db_column='FECHAFIN')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RENGSIT\""


class TRengtele(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    casos = models.FloatField(blank=True, null=True, db_column='CASOS')
    muertes = models.FloatField(blank=True, null=True, db_column='MUERTES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    casoshom = models.FloatField(blank=True, null=True, db_column='CASOSHOM')
    casosmuj = models.FloatField(blank=True, null=True, db_column='CASOSMUJ')
    muerteshom = models.FloatField(blank=True, null=True, db_column='MUERTESHOM')
    muertesmuj = models.FloatField(blank=True, null=True, db_column='MUERTESMUJ')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RENGTELE\""


class TResumen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    situacion_especial = models.CharField(blank=True, null=True, db_column='SITUACION_ESPECIAL', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RESUMEN\""


class TRnacanul(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    fecha_anulado = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANULADO')
    causa_anulado = models.CharField(blank=True, null=True, db_column='CAUSA_ANULADO', max_length=200)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    hcausaanulado = models.FloatField(blank=True, null=True, db_column='HCAUSAANULADO')
    fecha_operacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RNACANUL\""


class TRnacnaci(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=20)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    hora = models.CharField(blank=True, null=True, db_column='HORA', max_length=10)
    peso = models.FloatField(blank=True, null=True, db_column='PESO')
    talla = models.FloatField(blank=True, null=True, db_column='TALLA')
    hsexo = models.FloatField(blank=True, null=True, db_column='HSEXO')
    htipoparto = models.FloatField(blank=True, null=True, db_column='HTIPOPARTO')
    hasistencia = models.FloatField(blank=True, null=True, db_column='HASISTENCIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    hsitioparto = models.FloatField(blank=True, null=True, db_column='HSITIOPARTO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    semanagestacion = models.FloatField(blank=True, null=True, db_column='SEMANAGESTACION')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    vivo_muerto = models.IntegerField(blank=True, null=True, db_column='VIVO_MUERTO')
    ocurrepartootro = models.CharField(blank=True, null=True, db_column='OCURREPARTOOTRO', max_length=60)
    atendiopartootro = models.CharField(blank=True, null=True, db_column='ATENDIOPARTOOTRO', max_length=60)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_RNACNACI\""


class TSegdiabe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    fechaevolucion = models.DateTimeField(blank=True, null=True, db_column='FECHAEVOLUCION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    numsecciones = models.FloatField(blank=True, null=True, db_column='NUMSECCIONES')
    imc = models.FloatField(blank=True, null=True, db_column='IMC')
    glicemia = models.FloatField(blank=True, null=True, db_column='GLICEMIA')
    tensionarterial_alta = models.FloatField(blank=True, null=True, db_column='TENSIONARTERIAL_ALTA')
    tensionarterial_baja = models.FloatField(blank=True, null=True, db_column='TENSIONARTERIAL_BAJA')
    glicosilada = models.FloatField(blank=True, null=True, db_column='GLICOSILADA')
    colesterol = models.FloatField(blank=True, null=True, db_column='COLESTEROL')
    microalbum = models.FloatField(blank=True, null=True, db_column='MICROALBUM')
    creatinina = models.FloatField(blank=True, null=True, db_column='CREATININA')
    triglicerido = models.FloatField(blank=True, null=True, db_column='TRIGLICERIDO')
    ldl = models.FloatField(blank=True, null=True, db_column='LDL')
    hdl = models.FloatField(blank=True, null=True, db_column='HDL')
    depcreatinina = models.FloatField(blank=True, null=True, db_column='DEPCREATININA')
    fondodeojo = models.FloatField(blank=True, null=True, db_column='FONDODEOJO')
    causashospitalarias = models.CharField(blank=True, null=True, db_column='CAUSASHOSPITALARIAS', max_length=250)
    sesioneducativa = models.CharField(blank=True, null=True, db_column='SESIONEDUCATIVA', max_length=100)
    secciones = models.FloatField(blank=True, null=True, db_column='SECCIONES')
    egreso = models.FloatField(blank=True, null=True, db_column='EGRESO')
    condicionegreso = models.FloatField(blank=True, null=True, db_column='CONDICIONEGRESO')
    hlocalidad_tranf = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_TRANF')
    hlocalidad_seg = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    fechatransferencia = models.DateTimeField(blank=True, null=True, db_column='FECHATRANSFERENCIA')
    causademuerte = models.CharField(blank=True, null=True, db_column='CAUSADEMUERTE', max_length=1)
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    fluoro = models.FloatField(blank=True, null=True, db_column='FLUORO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    evaluacion = models.CharField(blank=True, null=True, db_column='EVALUACION', max_length=4000)
    hespecialidad = models.FloatField(blank=True, null=True, db_column='HESPECIALIDAD')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_SEGDIABE\""


class TSegevolp(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    fecha_seg = models.DateTimeField(blank=True, null=True, db_column='FECHA_SEG')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hlocalidad_seg = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    fecha_result_seg = models.DateTimeField(blank=True, null=True, db_column='FECHA_RESULT_SEG')
    otros_tratam_seg = models.CharField(blank=True, null=True, db_column='OTROS_TRATAM_SEG', max_length=250)
    complicacion_seg = models.CharField(blank=True, null=True, db_column='COMPLICACION_SEG', max_length=250)
    observacion_seg = models.CharField(blank=True, null=True, db_column='OBSERVACION_SEG', max_length=4000)
    hevolucion = models.FloatField(blank=True, null=True, db_column='HEVOLUCION')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hresultados_prog = models.FloatField(blank=True, null=True, db_column='HRESULTADOS_PROG')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_SEGEVOLP\""


class TSegucard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    hlocalidad_seg = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    evaluacion = models.CharField(blank=True, null=True, db_column='EVALUACION', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaevolucion = models.DateTimeField(blank=True, null=True, db_column='FECHAEVOLUCION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_SEGUCARD\""


class TSignsint(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_basesd = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_BASESD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_SIGNSINT\""


class TSigsinse(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_basesd = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_BASESD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_SIGSINSE\""


class TSituespe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    htipoevento = models.FloatField(blank=True, null=True, db_column='HTIPOEVENTO')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    cant_casos = models.FloatField(blank=True, null=True, db_column='CANT_CASOS')
    cant_muertes = models.FloatField(blank=True, null=True, db_column='CANT_MUERTES')
    medidatomada = models.CharField(blank=True, null=True, db_column='MEDIDATOMADA', max_length=200)
    descripcionevento = models.CharField(blank=True, null=True, db_column='DESCRIPCIONEVENTO', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_SITUESPE\""


class TTrasegim(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_TRASEGIM\""


class TTratamie(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_TRATAMIE\""


class TTratuber(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    iniciotra = models.FloatField(blank=True, null=True, db_column='INICIOTRA')
    fechainiciotra = models.DateTimeField(blank=True, null=True, db_column='FECHAINICIOTRA')
    mesestrat_i = models.FloatField(blank=True, null=True, db_column='MESESTRAT_I')
    mesestrat_m = models.FloatField(blank=True, null=True, db_column='MESESTRAT_M')
    administraciontra = models.FloatField(blank=True, null=True, db_column='ADMINISTRACIONTRA')
    notaes = models.CharField(blank=True, null=True, db_column='NOTAES', max_length=100)
    resultadobact_1 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_1')
    resultadobact_2 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_2')
    resultadobact_3 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_3')
    resultadobact_4 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_4')
    resultadobact_5 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_5')
    resultadobact_6 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_6')
    resultadobact_f = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_F')
    egreso = models.FloatField(blank=True, null=True, db_column='EGRESO')
    reingreso = models.FloatField(blank=True, null=True, db_column='REINGRESO')
    fechaegreso = models.DateTimeField(blank=True, null=True, db_column='FECHAEGRESO')
    fechareingreso = models.DateTimeField(blank=True, null=True, db_column='FECHAREINGRESO')
    hcondicionfinalegreso = models.FloatField(blank=True, null=True, db_column='HCONDICIONFINALEGRESO')
    hcondicionfinalreingreso = models.IntegerField(blank=True, null=True, db_column='HCONDICIONFINALREINGRESO')
    muertetb = models.FloatField(blank=True, null=True, db_column='MUERTETB')
    muerteotracausa = models.FloatField(blank=True, null=True, db_column='MUERTEOTRACAUSA')
    semana_abandono = models.FloatField(blank=True, null=True, db_column='SEMANA_ABANDONO')
    lugartransferencia = models.FloatField(blank=True, null=True, db_column='LUGARTRANSFERENCIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    tomasprogramadas = models.FloatField(blank=True, null=True, db_column='TOMASPROGRAMADAS')
    tomascumplidas = models.FloatField(blank=True, null=True, db_column='TOMASCUMPLIDAS')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_TRATUBER\""


class TTsegcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_TSEGCARD\""


class TUsuarios(models.Model):
    login = models.CharField(blank=True, null=True, primary_key=True, db_column='LOGIN', max_length=10)
    password = models.CharField(blank=True, null=True, db_column='PASSWORD', max_length=12)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=40)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    cargo = models.CharField(blank=True, null=True, db_column='CARGO', max_length=150)
    jerarquia = models.CharField(blank=True, null=True, db_column='JERARQUIA', max_length=2)
    creado = models.CharField(blank=True, null=True, db_column='CREADO', max_length=10)
    fec_crea = models.DateTimeField(blank=True, null=True, db_column='FEC_CREA')
    fec_ent = models.DateTimeField(blank=True, null=True, db_column='FEC_ENT')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    morbilidad = models.FloatField(blank=True, null=True, db_column='MORBILIDAD')
    natalidad = models.FloatField(blank=True, null=True, db_column='NATALIDAD')
    mortalidad = models.FloatField(blank=True, null=True, db_column='MORTALIDAD')
    oncologia = models.FloatField(blank=True, null=True, db_column='ONCOLOGIA')
    fichas = models.FloatField(blank=True, null=True, db_column='FICHAS')
    accidente = models.FloatField(blank=True, null=True, db_column='ACCIDENTE')
    cirugia = models.FloatField(blank=True, null=True, db_column='CIRUGIA')
    vacunacion = models.FloatField(blank=True, null=True, db_column='VACUNACION')
    transferencia = models.FloatField(blank=True, null=True, db_column='TRANSFERENCIA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"inbdlar1\".\"T_USUARIOS\""


class LegacyTAccilabo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    accidente = models.FloatField(blank=True, null=True, db_column='ACCIDENTE')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    hora = models.CharField(blank=True, null=True, db_column='HORA', max_length=20)
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    tratamiento = models.CharField(blank=True, null=True, db_column='TRATAMIENTO', max_length=1)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=1)
    fechatra = models.DateTimeField(blank=True, null=True, db_column='FECHATRA')
    horatratamiento = models.CharField(blank=True, null=True, db_column='HORATRATAMIENTO', max_length=20)
    fuente = models.CharField(blank=True, null=True, db_column='FUENTE', max_length=1)
    desconoce = models.FloatField(blank=True, null=True, db_column='DESCONOCE')
    fuentedesconoce = models.FloatField(blank=True, null=True, db_column='FUENTEDESCONOCE')
    serologia = models.CharField(blank=True, null=True, db_column='SEROLOGIA', max_length=1)
    resultadosero = models.CharField(blank=True, null=True, db_column='RESULTADOSERO', max_length=30)
    fecharesultadosero = models.DateTimeField(blank=True, null=True, db_column='FECHARESULTADOSERO')
    hexposicion = models.FloatField(blank=True, null=True, db_column='HEXPOSICION')
    hobjeto = models.FloatField(blank=True, null=True, db_column='HOBJETO')
    hliquido = models.FloatField(blank=True, null=True, db_column='HLIQUIDO')
    hsituacion = models.FloatField(blank=True, null=True, db_column='HSITUACION')
    abusosexual = models.FloatField(blank=True, null=True, db_column='ABUSOSEXUAL')
    hlocalidadabuso = models.FloatField(blank=True, null=True, db_column='HLOCALIDADABUSO')
    fechaabuso = models.DateTimeField(blank=True, null=True, db_column='FECHAABUSO')
    horaabuso = models.CharField(blank=True, null=True, db_column='HORAABUSO', max_length=20)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_ACCILABO\""


class LegacyTAcctrans(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha = models.FloatField(blank=True, null=True, db_column='HFICHA')
    htipo_accidente = models.FloatField(blank=True, null=True, db_column='HTIPO_ACCIDENTE')
    htipo_vehiculo = models.FloatField(blank=True, null=True, db_column='HTIPO_VEHICULO')
    hcondicion = models.FloatField(blank=True, null=True, db_column='HCONDICION')
    hsitio_accidente = models.FloatField(blank=True, null=True, db_column='HSITIO_ACCIDENTE')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    hsitio_auto = models.FloatField(blank=True, null=True, db_column='HSITIO_AUTO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    causa = models.FloatField(blank=True, null=True, db_column='CAUSA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_ACCTRANS\""


class LegacyTAlabcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_analisis = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANALISIS')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fecha_analisis = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANALISIS')
    resultado = models.CharField(blank=True, null=True, db_column='RESULTADO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_ALABCARD\""


class LegacyTAnalabor(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_analisis = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANALISIS')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fecha_analisis = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANALISIS')
    resultado = models.CharField(blank=True, null=True, db_column='RESULTADO', max_length=50)
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_ANALABOR\""


class LegacyTAntefact(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_anteced = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANTECED')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_ANTEFACT\""


class LegacyTAuditoria(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombreforma = models.CharField(blank=True, null=True, db_column='NOMBREFORMA', max_length=60)
    nombretabla = models.CharField(blank=True, null=True, db_column='NOMBRETABLA', max_length=30)
    evento = models.FloatField(blank=True, null=True, db_column='EVENTO')
    nombreregistro = models.CharField(blank=True, null=True, db_column='NOMBREREGISTRO', max_length=200)
    idregistro = models.FloatField(blank=True, null=True, db_column='IDREGISTRO')
    pc = models.CharField(blank=True, null=True, db_column='PC', max_length=20)
    husuario = models.FloatField(blank=True, null=True, db_column='HUSUARIO')
    fecha_ope = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPE')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_AUDITORIA\""


class LegacyTBiopseg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_BIOPSEG\""


class LegacyTBiopsiat(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    aspectoclinico = models.FloatField(blank=True, null=True, db_column='ASPECTOCLINICO')
    biopsiaanterior = models.FloatField(blank=True, null=True, db_column='BIOPSIAANTERIOR')
    ceneoplasicas = models.FloatField(blank=True, null=True, db_column='CENEOPLASICAS')
    cereactivas = models.FloatField(blank=True, null=True, db_column='CEREACTIVAS')
    cgneoplasicas = models.FloatField(blank=True, null=True, db_column='CGNEOPLASICAS')
    cgreactivas = models.FloatField(blank=True, null=True, db_column='CGREACTIVAS')
    citanormal = models.FloatField(blank=True, null=True, db_column='CITANORMAL')
    citologiaant = models.FloatField(blank=True, null=True, db_column='CITOLOGIAANT')
    citologianeoplasia = models.FloatField(blank=True, null=True, db_column='CITOLOGIANEOPLASIA')
    codigomuestrasas = models.CharField(blank=True, null=True, db_column='CODIGOMUESTRASAS', max_length=8)
    crinfecciosos = models.FloatField(blank=True, null=True, db_column='CRINFECCIOSOS')
    crinflamatorios = models.FloatField(blank=True, null=True, db_column='CRINFLAMATORIOS')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    embarazada = models.FloatField(blank=True, null=True, db_column='EMBARAZADA')
    fechacriocirugia = models.DateTimeField(blank=True, null=True, db_column='FECHACRIOCIRUGIA')
    fechaconizacion = models.DateTimeField(blank=True, null=True, db_column='FECHACONIZACION')
    fechadoc = models.DateTimeField(blank=True, null=True, db_column='FECHADOC')
    fechahistradical = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTRADICAL')
    fechahisttotal = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTTOTAL')
    fechalectura = models.DateTimeField(blank=True, null=True, db_column='FECHALECTURA')
    fechamuestra = models.DateTimeField(blank=True, null=True, db_column='FECHAMUESTRA')
    fecharadioterapia = models.DateTimeField(blank=True, null=True, db_column='FECHARADIOTERAPIA')
    fecharesultado = models.DateTimeField(blank=True, null=True, db_column='FECHARESULTADO')
    fechaultregla = models.DateTimeField(blank=True, null=True, db_column='FECHAULTREGLA')
    hlaboratorio = models.FloatField(blank=True, null=True, db_column='HLABORATORIO')
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hpatologo = models.FloatField(blank=True, null=True, db_column='HPATOLOGO')
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    mesbiopsia = models.DateTimeField(blank=True, null=True, db_column='MESBIOPSIA')
    mescitologia = models.DateTimeField(blank=True, null=True, db_column='MESCITOLOGIA')
    muestracitologica = models.FloatField(blank=True, null=True, db_column='MUESTRACITOLOGICA')
    nroparto = models.FloatField(blank=True, null=True, db_column='NROPARTO')
    nroaborto = models.FloatField(blank=True, null=True, db_column='NROABORTO')
    nrolamina = models.CharField(blank=True, null=True, db_column='NROLAMINA', max_length=20)
    numero = models.FloatField(blank=True, null=True, db_column='NUMERO')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=600)
    resultadoasociado = models.FloatField(blank=True, null=True, db_column='RESULTADOASOCIADO')
    hresultadob = models.FloatField(blank=True, null=True, db_column='HRESULTADOB')
    hresultadoc = models.FloatField(blank=True, null=True, db_column='HRESULTADOC')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    tipoexamen = models.FloatField(blank=True, null=True, db_column='TIPOEXAMEN')
    tipomuestra1 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA1')
    tipomuestra2 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA2')
    tratamientoprevio = models.FloatField(blank=True, null=True, db_column='TRATAMIENTOPREVIO')
    valorlectura = models.FloatField(blank=True, null=True, db_column='VALORLECTURA')
    vph = models.FloatField(blank=True, null=True, db_column='VPH')
    usuario_amb = models.CharField(blank=True, null=True, db_column='USUARIO_AMB', max_length=10)
    usuario_lab = models.CharField(blank=True, null=True, db_column='USUARIO_LAB', max_length=10)
    hcentromuestra = models.FloatField(blank=True, null=True, db_column='HCENTROMUESTRA')
    observacionesmacro = models.CharField(blank=True, null=True, db_column='OBSERVACIONESMACRO', max_length=4000)
    muestrautero = models.CharField(blank=True, null=True, db_column='MUESTRAUTERO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_BIOPSIAT\""


class LegacyTCasosmm(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    num_partos = models.FloatField(blank=True, null=True, db_column='NUM_PARTOS')
    hijos_nacvivos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACVIVOS')
    hijos_nacmuertos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACMUERTOS')
    hijos_nacabortos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACABORTOS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=25)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_CASOSMM\""


class LegacyTCasosmmi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=25)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=25)
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    hsexo = models.FloatField(blank=True, null=True, db_column='HSEXO')
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    fechaocurrencia = models.DateTimeField(blank=True, null=True, db_column='FECHAOCURRENCIA')
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=25)
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    hresidencia_pais = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAIS')
    nacionalidad = models.CharField(blank=True, null=True, db_column='NACIONALIDAD', max_length=1)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    numeromsds = models.CharField(blank=True, null=True, db_column='NUMEROMSDS', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_CASOSMMI\""


class LegacyTCaummedi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    causa1 = models.CharField(blank=True, null=True, db_column='CAUSA1', max_length=120)
    causa2 = models.CharField(blank=True, null=True, db_column='CAUSA2', max_length=120)
    causa3 = models.CharField(blank=True, null=True, db_column='CAUSA3', max_length=120)
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_CAUMMEDI\""


class LegacyTCertmort(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    numeropartida = models.CharField(blank=True, null=True, db_column='NUMEROPARTIDA', max_length=10)
    numeromsds = models.CharField(blank=True, null=True, db_column='NUMEROMSDS', max_length=10)
    certificado = models.CharField(blank=True, null=True, db_column='CERTIFICADO', max_length=10)
    annocertificado = models.FloatField(blank=True, null=True, db_column='ANNOCERTIFICADO')
    mfetal = models.FloatField(blank=True, null=True, db_column='MFETAL')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=100)
    nacionalidad = models.FloatField(blank=True, null=True, db_column='NACIONALIDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=15)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    fecha_m = models.DateTimeField(blank=True, null=True, db_column='FECHA_M')
    fecha_n = models.DateTimeField(blank=True, null=True, db_column='FECHA_N')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    tipoedad = models.CharField(blank=True, null=True, db_column='TIPOEDAD', max_length=1)
    hestadocivil = models.FloatField(blank=True, null=True, db_column='HESTADOCIVIL')
    annocursado = models.FloatField(blank=True, null=True, db_column='ANNOCURSADO')
    annoterminado = models.FloatField(blank=True, null=True, db_column='ANNOTERMINADO')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    hprofesion = models.FloatField(blank=True, null=True, db_column='HPROFESION')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    hpais = models.FloatField(blank=True, null=True, db_column='HPAIS')
    hsitio_m = models.FloatField(blank=True, null=True, db_column='HSITIO_M')
    nombreclinica = models.CharField(blank=True, null=True, db_column='NOMBRECLINICA', max_length=100)
    hlocaocurrencia = models.FloatField(blank=True, null=True, db_column='HLOCAOCURRENCIA')
    direcocurrencia = models.CharField(blank=True, null=True, db_column='DIRECOCURRENCIA', max_length=250)
    hlocaresidencia = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIA')
    direcresidencia = models.CharField(blank=True, null=True, db_column='DIRECRESIDENCIA', max_length=200)
    hpresenciaembarazo = models.FloatField(blank=True, null=True, db_column='HPRESENCIAEMBARAZO')
    hcausabasica = models.FloatField(blank=True, null=True, db_column='HCAUSABASICA')
    otrosestados = models.CharField(blank=True, null=True, db_column='OTROSESTADOS', max_length=400)
    autopsia = models.FloatField(blank=True, null=True, db_column='AUTOPSIA')
    examencuerpo = models.FloatField(blank=True, null=True, db_column='EXAMENCUERPO')
    examenlab = models.FloatField(blank=True, null=True, db_column='EXAMENLAB')
    interrogatorio = models.FloatField(blank=True, null=True, db_column='INTERROGATORIO')
    historiaclinica = models.FloatField(blank=True, null=True, db_column='HISTORIACLINICA')
    numerodiagnostico = models.CharField(blank=True, null=True, db_column='NUMERODIAGNOSTICO', max_length=10)
    hmedicofirmante = models.FloatField(blank=True, null=True, db_column='HMEDICOFIRMANTE')
    otromedfirmante = models.CharField(blank=True, null=True, db_column='OTROMEDFIRMANTE', max_length=100)
    asistenciamedica = models.FloatField(blank=True, null=True, db_column='ASISTENCIAMEDICA')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    firmamedico = models.FloatField(blank=True, null=True, db_column='FIRMAMEDICO')
    direcservicio_m = models.CharField(blank=True, null=True, db_column='DIRECSERVICIO_M', max_length=200)
    descernomedica = models.CharField(blank=True, null=True, db_column='DESCERNOMEDICA', max_length=250)
    hdestinocuerpo = models.FloatField(blank=True, null=True, db_column='HDESTINOCUERPO')
    numeropermiso = models.CharField(blank=True, null=True, db_column='NUMEROPERMISO', max_length=10)
    hregionpermiso = models.FloatField(blank=True, null=True, db_column='HREGIONPERMISO')
    lugarpermiso = models.CharField(blank=True, null=True, db_column='LUGARPERMISO', max_length=200)
    fechapermiso = models.DateTimeField(blank=True, null=True, db_column='FECHAPERMISO')
    hregionexpe = models.FloatField(blank=True, null=True, db_column='HREGIONEXPE')
    lugarexpedicion = models.CharField(blank=True, null=True, db_column='LUGAREXPEDICION', max_length=200)
    fechaexpe = models.DateTimeField(blank=True, null=True, db_column='FECHAEXPE')
    firmaautoridad = models.FloatField(blank=True, null=True, db_column='FIRMAAUTORIDAD')
    sello = models.FloatField(blank=True, null=True, db_column='SELLO')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    hmadre = models.FloatField(blank=True, null=True, db_column='HMADRE')
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    edad2 = models.FloatField(blank=True, null=True, db_column='EDAD2')
    tipoedad2 = models.CharField(blank=True, null=True, db_column='TIPOEDAD2', max_length=1)
    transresi = models.FloatField(blank=True, null=True, db_column='TRANSRESI')
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    sabeleer = models.CharField(blank=True, null=True, db_column='SABELEER', max_length=1)
    hijosnac_v = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_V')
    hijosnac_av = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_AV')
    hijosnac_m = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_M')
    hijosnac_mf = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_MF')
    tomo = models.CharField(blank=True, null=True, db_column='TOMO', max_length=50)
    folio = models.CharField(blank=True, null=True, db_column='FOLIO', max_length=50)
    libro = models.CharField(blank=True, null=True, db_column='LIBRO', max_length=50)
    acta = models.CharField(blank=True, null=True, db_column='ACTA', max_length=50)
    nacmadrefallecido = models.FloatField(blank=True, null=True, db_column='NACMADREFALLECIDO')
    cimadrefallecido = models.CharField(blank=True, null=True, db_column='CIMADREFALLECIDO', max_length=15)
    nommadrefallecido = models.CharField(blank=True, null=True, db_column='NOMMADREFALLECIDO', max_length=50)
    nacpadrefallecido = models.FloatField(blank=True, null=True, db_column='NACPADREFALLECIDO')
    cipadrefallecido = models.CharField(blank=True, null=True, db_column='CIPADREFALLECIDO', max_length=15)
    nompadrefallecido = models.CharField(blank=True, null=True, db_column='NOMPADREFALLECIDO', max_length=50)
    nacregistrador = models.FloatField(blank=True, null=True, db_column='NACREGISTRADOR')
    ciregistrador = models.CharField(blank=True, null=True, db_column='CIREGISTRADOR', max_length=10)
    nomregistrador = models.CharField(blank=True, null=True, db_column='NOMREGISTRADOR', max_length=50)
    tomopartidanac = models.CharField(blank=True, null=True, db_column='TOMOPARTIDANAC', max_length=50)
    foliopartidanac = models.CharField(blank=True, null=True, db_column='FOLIOPARTIDANAC', max_length=50)
    libropartidanac = models.CharField(blank=True, null=True, db_column='LIBROPARTIDANAC', max_length=50)
    actapartidanac = models.CharField(blank=True, null=True, db_column='ACTAPARTIDANAC', max_length=50)
    horamuerte = models.CharField(blank=True, null=True, db_column='HORAMUERTE', max_length=20)
    hestado = models.FloatField(blank=True, null=True, db_column='HESTADO')
    hlocaresidenciafp = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIAFP')
    hestablecimiento_ocur = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO_OCUR')
    especial = models.FloatField(blank=True, null=True, db_column='ESPECIAL')
    otrodiagnostico = models.FloatField(blank=True, null=True, db_column='OTRODIAGNOSTICO')
    otrodiagnosticocert = models.CharField(blank=True, null=True, db_column='OTRODIAGNOSTICOCERT', max_length=50)
    fechaelaboracion = models.DateTimeField(blank=True, null=True, db_column='FECHAELABORACION')
    numeroautopsia = models.CharField(blank=True, null=True, db_column='NUMEROAUTOPSIA', max_length=20)
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=500)
    valsexo = models.IntegerField(blank=True, null=True, db_column='VALSEXO')
    valcausabasica = models.IntegerField(blank=True, null=True, db_column='VALCAUSABASICA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_CERTMORT\""


class LegacyTComaguda(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_COMAGUDA\""


class LegacyTComcroni(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_COMCRONI\""


class LegacyTComdisca(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_COMDISCA\""


class LegacyTCompcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    tipo = models.CharField(blank=True, null=True, db_column='TIPO', max_length=1)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_COMPCARD\""


class LegacyTComplica(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_COMPLICA\""


class LegacyTComquir(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hcomplicacion = models.FloatField(blank=True, null=True, db_column='HCOMPLICACION')
    htipocomplicacion = models.FloatField(blank=True, null=True, db_column='HTIPOCOMPLICACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_COMQUIR\""


class LegacyTComsegim(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_COMSEGIM\""


class LegacyTDiagasoc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcie10 = models.BigIntegerField(blank=True, null=True, db_column='HCIE10')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_DIAGASOC\""


class LegacyTDocudeng(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    c_fiebre = models.FloatField(blank=True, null=True, db_column='C_FIEBRE')
    c_hemorragico = models.FloatField(blank=True, null=True, db_column='C_HEMORRAGICO')
    c_hospitalizado = models.FloatField(blank=True, null=True, db_column='C_HOSPITALIZADO')
    c_muestra = models.FloatField(blank=True, null=True, db_column='C_MUESTRA')
    c_positivo = models.FloatField(blank=True, null=True, db_column='C_POSITIVO')
    c_negativo = models.FloatField(blank=True, null=True, db_column='C_NEGATIVO')
    c_pendiente = models.FloatField(blank=True, null=True, db_column='C_PENDIENTE')
    c_epidemiologico = models.FloatField(blank=True, null=True, db_column='C_EPIDEMIOLOGICO')
    c_laboratorio = models.FloatField(blank=True, null=True, db_column='C_LABORATORIO')
    nro_semana = models.FloatField(blank=True, null=True, db_column='NRO_SEMANA')
    casos_semana = models.FloatField(blank=True, null=True, db_column='CASOS_SEMANA')
    htipodengue = models.FloatField(blank=True, null=True, db_column='HTIPODENGUE')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    totaldengue = models.FloatField(blank=True, null=True, db_column='TOTALDENGUE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_DOCUDENG\""


class LegacyTDocument(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    tipo = models.FloatField(blank=True, null=True, db_column='TIPO')
    horigen = models.FloatField(blank=True, null=True, db_column='HORIGEN')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=500)
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=20)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_DOCUMENT\""


class LegacyTDocusosp(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    c_estudio = models.FloatField(blank=True, null=True, db_column='C_ESTUDIO')
    c_descartado = models.FloatField(blank=True, null=True, db_column='C_DESCARTADO')
    c_confirmado = models.FloatField(blank=True, null=True, db_column='C_CONFIRMADO')
    c_compartido = models.FloatField(blank=True, null=True, db_column='C_COMPARTIDO')
    c_notificado = models.FloatField(blank=True, null=True, db_column='C_NOTIFICADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_DOCUSOSP\""


class LegacyTEstable(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    htipo = models.FloatField(blank=True, null=True, db_column='HTIPO')
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=250)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefono = models.CharField(blank=True, null=True, db_column='TELEFONO', max_length=50)
    status = models.CharField(blank=True, null=True, db_column='STATUS', max_length=1)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    domiciliado = models.CharField(blank=True, null=True, db_column='DOMICILIADO', max_length=1)
    rif = models.CharField(blank=True, null=True, db_column='RIF', max_length=20)
    tipoestablec = models.FloatField(blank=True, null=True, db_column='TIPOESTABLEC')
    cuentadante = models.FloatField(blank=True, null=True, db_column='CUENTADANTE')
    hnivel = models.FloatField(blank=True, null=True, db_column='HNIVEL')
    x_utm = models.DecimalField(blank=True, null=True, db_column='X_UTM', max_digits=24, decimal_places=6)
    y_utm = models.DecimalField(blank=True, null=True, db_column='Y_UTM', max_digits=24, decimal_places=6)
    altitud = models.DecimalField(blank=True, null=True, db_column='ALTITUD', max_digits=10, decimal_places=2)
    funcionamiento = models.CharField(blank=True, null=True, db_column='FUNCIONAMIENTO', max_length=1)
    hdependencia_adm = models.FloatField(blank=True, null=True, db_column='HDEPENDENCIA_ADM')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_ESTABLE\""


class LegacyTEventos(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_EVENTOS\""


class LegacyTFdolorto(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_programa = models.FloatField(blank=True, null=True, db_column='HFICHA_PROGRAMA')
    hfichadeldolor = models.FloatField(blank=True, null=True, db_column='HFICHADELDOLOR')
    si = models.FloatField(blank=True, null=True, db_column='SI')
    no = models.FloatField(blank=True, null=True, db_column='NO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_FDOLORTO\""


class LegacyTFichaacc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=15)
    fecha_oc = models.DateTimeField(blank=True, null=True, db_column='FECHA_OC')
    hora_oc = models.CharField(blank=True, null=True, db_column='HORA_OC', max_length=20)
    hlocalidad_oc = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_OC')
    sitio_oc = models.CharField(blank=True, null=True, db_column='SITIO_OC', max_length=150)
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    fallecio = models.FloatField(blank=True, null=True, db_column='FALLECIO')
    hora_muerte = models.CharField(blank=True, null=True, db_column='HORA_MUERTE', max_length=20)
    hsitio_muerte = models.FloatField(blank=True, null=True, db_column='HSITIO_MUERTE')
    influencia_alcohol = models.FloatField(blank=True, null=True, db_column='INFLUENCIA_ALCOHOL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_FICHAACC\""


class LegacyTFichasep(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    hlocalidad_ficha = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIDAD_FICHA')
    nro_caso = models.CharField(blank=True, null=True, db_column='NRO_CASO', max_length=20)
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    ano_fecha_reg = models.IntegerField(blank=True, null=True, db_column='ANO_FECHA_REG')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=254)
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_FICHASEP\""


class LegacyTHechosvi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha = models.FloatField(blank=True, null=True, db_column='HFICHA')
    htipo_hecho = models.FloatField(blank=True, null=True, db_column='HTIPO_HECHO')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hefectuo_hecho = models.FloatField(blank=True, null=True, db_column='HEFECTUO_HECHO')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hubic_diagnostico = models.FloatField(blank=True, null=True, db_column='HUBIC_DIAGNOSTICO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_HECHOSVI\""


class LegacyTIntquir(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hintervencion = models.FloatField(blank=True, null=True, db_column='HINTERVENCION')
    hanatomia = models.FloatField(blank=True, null=True, db_column='HANATOMIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=1000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_INTQUIR\""


class LegacyTLugarvis(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    lugar = models.CharField(blank=True, null=True, db_column='LUGAR', max_length=200)
    tiempo_perm = models.IntegerField(blank=True, null=True, db_column='TIEMPO_PERM')
    unid_tiemperm = models.CharField(blank=True, null=True, db_column='UNID_TIEMPERM', max_length=10)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_LUGARVIS\""


class LegacyTMadrnaci(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    apellidos = models.CharField(blank=True, null=True, db_column='APELLIDOS', max_length=100)
    pasaporte = models.CharField(blank=True, null=True, db_column='PASAPORTE', max_length=20)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=20)
    phistoriaclinica = models.CharField(blank=True, null=True, db_column='PHISTORIACLINICA', max_length=20)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edadm = models.FloatField(blank=True, null=True, db_column='EDADM')
    edadp = models.FloatField(blank=True, null=True, db_column='EDADP')
    estadocivil = models.FloatField(blank=True, null=True, db_column='ESTADOCIVIL')
    annosmatrimonio = models.FloatField(blank=True, null=True, db_column='ANNOSMATRIMONIO')
    nacvivos = models.FloatField(blank=True, null=True, db_column='NACVIVOS')
    nacionm = models.FloatField(blank=True, null=True, db_column='NACIONM')
    nacionp = models.FloatField(blank=True, null=True, db_column='NACIONP')
    hentidam = models.FloatField(blank=True, null=True, db_column='HENTIDAM')
    hentidap = models.FloatField(blank=True, null=True, db_column='HENTIDAP')
    hpaism = models.FloatField(blank=True, null=True, db_column='HPAISM')
    hpaisp = models.FloatField(blank=True, null=True, db_column='HPAISP')
    actualvivos = models.FloatField(blank=True, null=True, db_column='ACTUALVIVOS')
    leerescribir = models.FloatField(blank=True, null=True, db_column='LEERESCRIBIR')
    nacvivosfallec = models.FloatField(blank=True, null=True, db_column='NACVIVOSFALLEC')
    muertesfetales = models.FloatField(blank=True, null=True, db_column='MUERTESFETALES')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    profesion = models.FloatField(blank=True, null=True, db_column='PROFESION')
    controlprenatal = models.FloatField(blank=True, null=True, db_column='CONTROLPRENATAL')
    telefonom = models.CharField(blank=True, null=True, db_column='TELEFONOM', max_length=20)
    ptelefono = models.CharField(blank=True, null=True, db_column='PTELEFONO', max_length=20)
    ocupacion = models.FloatField(blank=True, null=True, db_column='OCUPACION')
    pcedula = models.CharField(blank=True, null=True, db_column='PCEDULA', max_length=10)
    pnombres = models.CharField(blank=True, null=True, db_column='PNOMBRES', max_length=100)
    ppasaporte = models.CharField(blank=True, null=True, db_column='PPASAPORTE', max_length=20)
    pdireccion = models.CharField(blank=True, null=True, db_column='PDIRECCION', max_length=100)
    hpresidencia = models.FloatField(blank=True, null=True, db_column='HPRESIDENCIA')
    pfechanacimiento = models.DateTimeField(blank=True, null=True, db_column='PFECHANACIMIENTO')
    pestadocivil = models.FloatField(blank=True, null=True, db_column='PESTADOCIVIL')
    pleerescribir = models.FloatField(blank=True, null=True, db_column='PLEERESCRIBIR')
    hpultimogrado = models.FloatField(blank=True, null=True, db_column='HPULTIMOGRADO')
    pprofesion = models.FloatField(blank=True, null=True, db_column='PPROFESION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=100)
    pocupacion = models.FloatField(blank=True, null=True, db_column='POCUPACION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    nacionalidap = models.FloatField(blank=True, null=True, db_column='NACIONALIDAP')
    nacionalidam = models.FloatField(blank=True, null=True, db_column='NACIONALIDAM')
    unionmat = models.FloatField(blank=True, null=True, db_column='UNIONMAT')
    nroconsultaspre = models.FloatField(blank=True, null=True, db_column='NROCONSULTASPRE')
    hetniam = models.FloatField(blank=True, null=True, db_column='HETNIAM')
    hetniap = models.FloatField(blank=True, null=True, db_column='HETNIAP')
    hablaetniam = models.FloatField(blank=True, null=True, db_column='HABLAETNIAM')
    hablaetniap = models.FloatField(blank=True, null=True, db_column='HABLAETNIAP')
    ultimogradom = models.FloatField(blank=True, null=True, db_column='ULTIMOGRADOM')
    ultimogradop = models.FloatField(blank=True, null=True, db_column='ULTIMOGRADOP')
    residenciam = models.IntegerField(blank=True, null=True, db_column='RESIDENCIAM')
    hresidencia_paism = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAISM')
    residenciap = models.IntegerField(blank=True, null=True, db_column='RESIDENCIAP')
    hresidencia_paisp = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAISP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MADRNACI\""


class LegacyTMbased(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    sid = models.CharField(blank=True, null=True, db_column='SID', max_length=10)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    texto_fecha = models.CharField(blank=True, null=True, db_column='TEXTO_FECHA', max_length=20)
    nombre_tablespace = models.CharField(blank=True, null=True, db_column='NOMBRE_TABLESPACE', max_length=50)
    ts_size_mb = models.DecimalField(blank=True, null=True, db_column='TS_SIZE_MB', max_digits=11, decimal_places=2)
    ts_usado_mb = models.DecimalField(blank=True, null=True, db_column='TS_USADO_MB', max_digits=11, decimal_places=2)
    ts_usado_pc = models.DecimalField(blank=True, null=True, db_column='TS_USADO_PC', max_digits=11, decimal_places=2)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MBASED\""


class LegacyTMcaumorb(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MCAUMORB\""


class LegacyTMcausmre(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    desenfermedad = models.CharField(blank=True, null=True, db_column='DESENFERMEDAD', max_length=200)
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MCAUSMRE\""


class LegacyTMhojarep(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    reparapor = models.FloatField(blank=True, null=True, db_column='REPARAPOR')
    atravesde = models.FloatField(blank=True, null=True, db_column='ATRAVESDE')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=10)
    fecharepara = models.DateTimeField(blank=True, null=True, db_column='FECHAREPARA')
    otrosmedios = models.CharField(blank=True, null=True, db_column='OTROSMEDIOS', max_length=100)
    nombreclinico = models.CharField(blank=True, null=True, db_column='NOMBRECLINICO', max_length=100)
    nacmedico = models.FloatField(blank=True, null=True, db_column='NACMEDICO')
    cedulaclinico = models.CharField(blank=True, null=True, db_column='CEDULACLINICO', max_length=15)
    nombreepidem = models.CharField(blank=True, null=True, db_column='NOMBREEPIDEM', max_length=100)
    nacepidem = models.FloatField(blank=True, null=True, db_column='NACEPIDEM')
    cedulaepidem = models.CharField(blank=True, null=True, db_column='CEDULAEPIDEM', max_length=15)
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MHOJAREP\""


class LegacyTMortanul(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausaanulado = models.FloatField(blank=True, null=True, db_column='HCAUSAANULADO')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    fecha_anulado = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANULADO')
    causa_anulado = models.CharField(blank=True, null=True, db_column='CAUSA_ANULADO', max_length=200)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fecha_operacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MORTANUL\""


class LegacyTMortcaus(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    desenfermedad = models.CharField(blank=True, null=True, db_column='DESENFERMEDAD', max_length=200)
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MORTCAUS\""


class LegacyTMortfeta(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hmadre = models.FloatField(blank=True, null=True, db_column='HMADRE')
    hduracionemba = models.FloatField(blank=True, null=True, db_column='HDURACIONEMBA')
    hnactipoemba = models.FloatField(blank=True, null=True, db_column='HNACTIPOEMBA')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    hm_relaparto = models.FloatField(blank=True, null=True, db_column='HM_RELAPARTO')
    pesofeto = models.FloatField(blank=True, null=True, db_column='PESOFETO')
    ignoradopeso = models.FloatField(blank=True, null=True, db_column='IGNORADOPESO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    hasistenteparto = models.FloatField(blank=True, null=True, db_column='HASISTENTEPARTO')
    otroasistparto = models.CharField(blank=True, null=True, db_column='OTROASISTPARTO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MORTFETA\""


class LegacyTMortmadr(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=100)
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    nacionalidad = models.FloatField(blank=True, null=True, db_column='NACIONALIDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=15)
    hprofesion = models.FloatField(blank=True, null=True, db_column='HPROFESION')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    annocursado = models.FloatField(blank=True, null=True, db_column='ANNOCURSADO')
    annoterminado = models.FloatField(blank=True, null=True, db_column='ANNOTERMINADO')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    hijosnac_v = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_V')
    hijosnac_m = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_M')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    sabeleer = models.CharField(blank=True, null=True, db_column='SABELEER', max_length=1)
    hestadocivil = models.FloatField(blank=True, null=True, db_column='HESTADOCIVIL')
    hijosnac_av = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_AV')
    hijosnac_mf = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_MF')
    hlocaresidencia = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIA')
    direcresidencia = models.CharField(blank=True, null=True, db_column='DIRECRESIDENCIA', max_length=200)
    hlocaresidenciafp = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIAFP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MORTMADR\""


class LegacyTMortviol(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    htipo_m = models.FloatField(blank=True, null=True, db_column='HTIPO_M')
    hora_mv = models.CharField(blank=True, null=True, db_column='HORA_MV', max_length=20)
    fecha_mv = models.DateTimeField(blank=True, null=True, db_column='FECHA_MV')
    descripcionsuceso = models.CharField(blank=True, null=True, db_column='DESCRIPCIONSUCESO', max_length=400)
    hlugarsuceso = models.FloatField(blank=True, null=True, db_column='HLUGARSUCESO')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MORTVIOL\""


class LegacyTMrespa(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    sid = models.CharField(blank=True, null=True, db_column='SID', max_length=10)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    texto_fecha = models.CharField(blank=True, null=True, db_column='TEXTO_FECHA', max_length=20)
    hdd_bd_usado = models.CharField(blank=True, null=True, db_column='HDD_BD_USADO', max_length=10)
    hdd_bd_size = models.CharField(blank=True, null=True, db_column='HDD_BD_SIZE', max_length=10)
    hdd_bk_usado = models.CharField(blank=True, null=True, db_column='HDD_BK_USADO', max_length=10)
    hdd_bk_size = models.CharField(blank=True, null=True, db_column='HDD_BK_SIZE', max_length=10)
    hdd_opt_usado = models.CharField(blank=True, null=True, db_column='HDD_OPT_USADO', max_length=10)
    hdd_opt_size = models.CharField(blank=True, null=True, db_column='HDD_OPT_SIZE', max_length=10)
    tam_respaldo_dmp = models.CharField(blank=True, null=True, db_column='TAM_RESPALDO_DMP', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_MRESPA\""


class LegacyTNotdsp04(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    nota = models.CharField(blank=True, null=True, db_column='NOTA', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_NOTDSP04\""


class LegacyTOrggeog(models.Model):
    num_region = models.BigIntegerField(blank=True, null=True, primary_key=True, db_column='NUM_REGION')
    cod_categoria = models.IntegerField(blank=True, null=True, db_column='COD_CATEGORIA')
    region_precedente = models.BigIntegerField(blank=True, null=True, db_column='REGION_PRECEDENTE')
    des_region = models.CharField(blank=True, null=True, db_column='DES_REGION', max_length=150)
    cod_ocei = models.CharField(blank=True, null=True, db_column='COD_OCEI', max_length=30)
    can_casas = models.IntegerField(blank=True, null=True, db_column='CAN_CASAS')
    poblacion_estimada = models.IntegerField(blank=True, null=True, db_column='POBLACION_ESTIMADA')
    gac_gis_lat = models.CharField(blank=True, null=True, db_column='GAC_GIS_LAT', max_length=18)
    gac_gis_long = models.CharField(blank=True, null=True, db_column='GAC_GIS_LONG', max_length=18)
    gac_gis_proj = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_PROJ')
    gac_gis_tagx = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGX', max_digits=14, decimal_places=4)
    gac_gis_tagy = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGY', max_digits=14, decimal_places=4)
    gac_gis_tagf = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_TAGF')
    gac_gis_tagt = models.CharField(blank=True, null=True, db_column='GAC_GIS_TAGT', max_length=1)
    gac_gis_tagh = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGH', max_digits=8, decimal_places=2)
    gac_gis_tagc = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_TAGC')
    gac_gis_tagr = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGR', max_digits=8, decimal_places=3)
    gac_gis_pcol = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_PCOL')
    gac_gis_lib = models.CharField(blank=True, null=True, db_column='GAC_GIS_LIB', max_length=50)
    gac_clav_loc = models.CharField(blank=True, null=True, db_column='GAC_CLAV_LOC', max_length=9)
    gac_cla_ocei = models.CharField(blank=True, null=True, db_column='GAC_CLA_OCEI', max_length=10)
    gac_nombre = models.CharField(blank=True, null=True, db_column='GAC_NOMBRE', max_length=40)
    gac_generico = models.CharField(blank=True, null=True, db_column='GAC_GENERICO', max_length=4)
    gac_latitud = models.CharField(blank=True, null=True, db_column='GAC_LATITUD', max_length=6)
    gac_longitud = models.CharField(blank=True, null=True, db_column='GAC_LONGITUD', max_length=6)
    gac_ubic_polit = models.CharField(blank=True, null=True, db_column='GAC_UBIC_POLIT', max_length=6)
    gac_estado = models.CharField(blank=True, null=True, db_column='GAC_ESTADO', max_length=2)
    gac_mun_dis = models.CharField(blank=True, null=True, db_column='GAC_MUN_DIS', max_length=2)
    gac_for_par = models.CharField(blank=True, null=True, db_column='GAC_FOR_PAR', max_length=2)
    gac_localidad = models.CharField(blank=True, null=True, db_column='GAC_LOCALIDAD', max_length=3)
    gac_carta = models.CharField(blank=True, null=True, db_column='GAC_CARTA', max_length=4)
    gac_cuadricula = models.CharField(blank=True, null=True, db_column='GAC_CUADRICULA', max_length=6)
    cod_estado = models.CharField(blank=True, null=True, db_column='COD_ESTADO', max_length=20)
    obs_region = models.CharField(blank=True, null=True, db_column='OBS_REGION', max_length=250)
    clave_ctrl = models.BigIntegerField(blank=True, null=True, db_column='CLAVE_CTRL')
    edo_ctrl = models.BigIntegerField(blank=True, null=True, db_column='EDO_CTRL')
    codigointerno = models.CharField(blank=True, null=True, db_column='CODIGOINTERNO', max_length=25)
    nombrelargo = models.CharField(blank=True, null=True, db_column='NOMBRELARGO', max_length=500)
    cod_ine = models.CharField(blank=True, null=True, db_column='COD_INE', max_length=14)
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_ORGGEOG\""


class LegacyTOtrotrat(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    tratamiento = models.CharField(blank=True, null=True, db_column='TRATAMIENTO', max_length=100)
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    indicaciones = models.CharField(blank=True, null=True, db_column='INDICACIONES', max_length=100)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_OTROTRAT\""


class LegacyTPacconde(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hcondicionespecial = models.FloatField(blank=True, null=True, db_column='HCONDICIONESPECIAL')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PACCONDE\""


class LegacyTPaciend(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=15)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    tipoedad = models.FloatField(blank=True, null=True, db_column='TIPOEDAD')
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=254)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    origen = models.FloatField(blank=True, null=True, db_column='ORIGEN')
    semana = models.FloatField(blank=True, null=True, db_column='SEMANA')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    tipodengue = models.FloatField(blank=True, null=True, db_column='TIPODENGUE')
    asistencia = models.FloatField(blank=True, null=True, db_column='ASISTENCIA')
    muerte = models.FloatField(blank=True, null=True, db_column='MUERTE')
    fechacreacion = models.DateTimeField(blank=True, null=True, db_column='FECHACREACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PACIEND\""


class LegacyTPacienfe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=25)
    apellidopaciente = models.CharField(blank=True, null=True, db_column='APELLIDOPACIENTE', max_length=25)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    lugar_nac = models.CharField(blank=True, null=True, db_column='LUGAR_NAC', max_length=50)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=254)
    hubicacion = models.BigIntegerField(blank=True, null=True, db_column='HUBICACION')
    tiempo_residencia = models.CharField(blank=True, null=True, db_column='TIEMPO_RESIDENCIA', max_length=10)
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    hlocalizacion = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIZACION')
    otro_tiempo_res = models.CharField(blank=True, null=True, db_column='OTRO_TIEMPO_RES', max_length=10)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    hconyugal = models.FloatField(blank=True, null=True, db_column='HCONYUGAL')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    analfabeta = models.CharField(blank=True, null=True, db_column='ANALFABETA', max_length=2)
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    anos_aprobados = models.IntegerField(blank=True, null=True, db_column='ANOS_APROBADOS')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    nomrepresentante = models.CharField(blank=True, null=True, db_column='NOMREPRESENTANTE', max_length=40)
    numero_hijo = models.CharField(blank=True, null=True, db_column='NUMERO_HIJO', max_length=2)
    fechadefuncion = models.DateTimeField(blank=True, null=True, db_column='FECHADEFUNCION')
    nacionalidad = models.CharField(blank=True, null=True, db_column='NACIONALIDAD', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PACIENFE\""


class LegacyTPacientt(models.Model):
    usuario = models.CharField(blank=True, null=True, primary_key=True, db_column='USUARIO', max_length=10)
    id = models.FloatField(blank=True, null=True, db_column='ID')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=50)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PACIENTT\""


class LegacyTPacimisi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hmision = models.FloatField(blank=True, null=True, db_column='HMISION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PACIMISI\""


class LegacyTPerquir(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hrolmedico = models.FloatField(blank=True, null=True, db_column='HROLMEDICO')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PERQUIR\""


class LegacyTPersmedi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=8)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    codigosas = models.CharField(blank=True, null=True, db_column='CODIGOSAS', max_length=12)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefonos = models.CharField(blank=True, null=True, db_column='TELEFONOS', max_length=35)
    cargo = models.CharField(blank=True, null=True, db_column='CARGO', max_length=50)
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PERSMEDI\""


class LegacyTPobesta(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    pob_total = models.FloatField(blank=True, null=True, db_column='POB_TOTAL')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    cobertura = models.FloatField(blank=True, null=True, db_column='COBERTURA')
    distribucion = models.FloatField(blank=True, null=True, db_column='DISTRIBUCION')
    pobcobertura = models.FloatField(blank=True, null=True, db_column='POBCOBERTURA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_POBESTA\""


class LegacyTProdiabe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    anoinicio = models.FloatField(blank=True, null=True, db_column='ANOINICIO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    hprediabetico = models.FloatField(blank=True, null=True, db_column='HPREDIABETICO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PRODIABE\""


class LegacyTProgcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    anoinicio = models.FloatField(blank=True, null=True, db_column='ANOINICIO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    infartado = models.FloatField(blank=True, null=True, db_column='INFARTADO')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PROGCARD\""


class LegacyTProgmche(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_epidemiologica = models.FloatField(blank=True, null=True, db_column='HFICHA_EPIDEMIOLOGICA')
    otras_bases_diag = models.CharField(blank=True, null=True, db_column='OTRAS_BASES_DIAG', max_length=100)
    nro_muestra = models.CharField(blank=True, null=True, db_column='NRO_MUESTRA', max_length=20)
    fecha_toma = models.DateTimeField(blank=True, null=True, db_column='FECHA_TOMA')
    lugar_toma = models.CharField(blank=True, null=True, db_column='LUGAR_TOMA', max_length=100)
    fech_init_fiebre = models.DateTimeField(blank=True, null=True, db_column='FECH_INIT_FIEBRE')
    lugar_inicio_fiebre = models.CharField(blank=True, null=True, db_column='LUGAR_INICIO_FIEBRE', max_length=50)
    permanencia_lug_fiebre = models.CharField(blank=True, null=True, db_column='PERMANENCIA_LUG_FIEBRE', max_length=20)
    hcondicion_ingreso_malaria = models.FloatField(blank=True, null=True, db_column='HCONDICION_INGRESO_MALARIA')
    otros_tratamientos = models.CharField(blank=True, null=True, db_column='OTROS_TRATAMIENTOS', max_length=250)
    hubicacion_infeccion = models.BigIntegerField(blank=True, null=True, db_column='HUBICACION_INFECCION')
    hpais = models.FloatField(blank=True, null=True, db_column='HPAIS')
    tranf_sangre = models.CharField(blank=True, null=True, db_column='TRANF_SANGRE', max_length=1)
    tratam_endovenoso = models.CharField(blank=True, null=True, db_column='TRATAM_ENDOVENOSO', max_length=1)
    fecha_tranf = models.DateTimeField(blank=True, null=True, db_column='FECHA_TRANF')
    hestab_tranf = models.FloatField(blank=True, null=True, db_column='HESTAB_TRANF')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    fecha_result = models.DateTimeField(blank=True, null=True, db_column='FECHA_RESULT')
    hresultados_prog = models.FloatField(blank=True, null=True, db_column='HRESULTADOS_PROG')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    complicaciones = models.CharField(blank=True, null=True, db_column='COMPLICACIONES', max_length=250)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PROGMCHE\""


class LegacyTProgtube(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    serie = models.CharField(blank=True, null=True, db_column='SERIE', max_length=1)
    casonumero = models.CharField(blank=True, null=True, db_column='CASONUMERO', max_length=9)
    cohorte = models.CharField(blank=True, null=True, db_column='COHORTE', max_length=1)
    fechanotificacion = models.DateTimeField(blank=True, null=True, db_column='FECHANOTIFICACION')
    hcondicioncaso = models.FloatField(blank=True, null=True, db_column='HCONDICIONCASO')
    serologiavih = models.FloatField(blank=True, null=True, db_column='SEROLOGIAVIH')
    bacteriologia = models.FloatField(blank=True, null=True, db_column='BACTERIOLOGIA')
    clinica = models.FloatField(blank=True, null=True, db_column='CLINICA')
    radiologia = models.FloatField(blank=True, null=True, db_column='RADIOLOGIA')
    resradiologia = models.FloatField(blank=True, null=True, db_column='RESRADIOLOGIA')
    caverna = models.FloatField(blank=True, null=True, db_column='CAVERNA')
    histologia = models.FloatField(blank=True, null=True, db_column='HISTOLOGIA')
    tuberculina = models.FloatField(blank=True, null=True, db_column='TUBERCULINA')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    localizacion = models.FloatField(blank=True, null=True, db_column='LOCALIZACION')
    reslocalizacion = models.FloatField(blank=True, null=True, db_column='RESLOCALIZACION')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    hmedicocoord = models.FloatField(blank=True, null=True, db_column='HMEDICOCOORD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PROGTUBE\""


class LegacyTProttrom(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_programa = models.FloatField(blank=True, null=True, db_column='HFICHA_PROGRAMA')
    infartoprevio = models.FloatField(blank=True, null=True, db_column='INFARTOPREVIO')
    tiempoutil = models.CharField(blank=True, null=True, db_column='TIEMPOUTIL', max_length=2)
    tratamientotrombo = models.FloatField(blank=True, null=True, db_column='TRATAMIENTOTROMBO')
    li_pre_trombo = models.FloatField(blank=True, null=True, db_column='LI_PRE_TROMBO')
    li_post_trombo = models.FloatField(blank=True, null=True, db_column='LI_POST_TROMBO')
    li_enzima_pre_t = models.FloatField(blank=True, null=True, db_column='LI_ENZIMA_PRE_T')
    li_post_t = models.FloatField(blank=True, null=True, db_column='LI_POST_T')
    estancia = models.FloatField(blank=True, null=True, db_column='ESTANCIA')
    estudionoinvasivo = models.FloatField(blank=True, null=True, db_column='ESTUDIONOINVASIVO')
    hemodinamia = models.FloatField(blank=True, null=True, db_column='HEMODINAMIA')
    cirugia = models.FloatField(blank=True, null=True, db_column='CIRUGIA')
    ucc = models.FloatField(blank=True, null=True, db_column='UCC')
    uti = models.FloatField(blank=True, null=True, db_column='UTI')
    hospitalizacion = models.FloatField(blank=True, null=True, db_column='HOSPITALIZACION')
    d_egreso = models.FloatField(blank=True, null=True, db_column='D_EGRESO')
    d_morge = models.FloatField(blank=True, null=True, db_column='D_MORGE')
    d_otroservicio = models.FloatField(blank=True, null=True, db_column='D_OTROSERVICIO')
    sistolica = models.FloatField(blank=True, null=True, db_column='SISTOLICA')
    diastolica = models.FloatField(blank=True, null=True, db_column='DIASTOLICA')
    hora_iniciadolor = models.CharField(blank=True, null=True, db_column='HORA_INICIADOLOR', max_length=10)
    hora_asistencia = models.CharField(blank=True, null=True, db_column='HORA_ASISTENCIA', max_length=10)
    hora_ingresohosp = models.CharField(blank=True, null=True, db_column='HORA_INGRESOHOSP', max_length=10)
    evaltratamiento = models.FloatField(blank=True, null=True, db_column='EVALTRATAMIENTO')
    cualcomplicacion = models.CharField(blank=True, null=True, db_column='CUALCOMPLICACION', max_length=50)
    dondehospitalizacion = models.CharField(blank=True, null=True, db_column='DONDEHOSPITALIZACION', max_length=50)
    hcentroreferencia = models.FloatField(blank=True, null=True, db_column='HCENTROREFERENCIA')
    localizainfarto = models.FloatField(blank=True, null=True, db_column='LOCALIZAINFARTO')
    referidootroservicio = models.CharField(blank=True, null=True, db_column='REFERIDOOTROSERVICIO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PROTTROM\""


class LegacyTPrvihsid(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    nro_hijos = models.FloatField(blank=True, null=True, db_column='NRO_HIJOS')
    edad_ult_hijo = models.FloatField(blank=True, null=True, db_column='EDAD_ULT_HIJO')
    htransmision_por = models.FloatField(blank=True, null=True, db_column='HTRANSMISION_POR')
    hmedio_transmision = models.FloatField(blank=True, null=True, db_column='HMEDIO_TRANSMISION')
    otras_bases_diag = models.CharField(blank=True, null=True, db_column='OTRAS_BASES_DIAG', max_length=100)
    hcondicion_ingreso = models.FloatField(blank=True, null=True, db_column='HCONDICION_INGRESO')
    hactividad_osp = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD_OSP')
    otros_tratamientos = models.CharField(blank=True, null=True, db_column='OTROS_TRATAMIENTOS', max_length=250)
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    complicaciones = models.CharField(blank=True, null=True, db_column='COMPLICACIONES', max_length=4000)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_PRVIHSID\""


class LegacyTRcasosmi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcasosmmi = models.FloatField(blank=True, null=True, db_column='HCASOSMMI')
    hocurrencia = models.FloatField(blank=True, null=True, db_column='HOCURRENCIA')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausa_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSA_CIE10')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    control_prenatal = models.FloatField(blank=True, null=True, db_column='CONTROL_PRENATAL')
    peso = models.FloatField(blank=True, null=True, db_column='PESO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    hcausabas_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSABAS_CIE10')
    hnutricion = models.FloatField(blank=True, null=True, db_column='HNUTRICION')
    estanciahosp = models.FloatField(blank=True, null=True, db_column='ESTANCIAHOSP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RCASOSMI\""


class LegacyTRcasosmm(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcasosmmi = models.FloatField(blank=True, null=True, db_column='HCASOSMMI')
    hocurrencia = models.FloatField(blank=True, null=True, db_column='HOCURRENCIA')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausa_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSA_CIE10')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    control_prenatal = models.FloatField(blank=True, null=True, db_column='CONTROL_PRENATAL')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    hanexosperiodo = models.FloatField(blank=True, null=True, db_column='HANEXOSPERIODO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    periodoocurrencia = models.FloatField(blank=True, null=True, db_column='PERIODOOCURRENCIA')
    hcausabas_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSABAS_CIE10')
    num_partos = models.FloatField(blank=True, null=True, db_column='NUM_PARTOS')
    hijos_nacvivos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACVIVOS')
    hijos_nacmuertos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACMUERTOS')
    hijos_nacabortos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACABORTOS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RCASOSMM\""


class LegacyTRegciru(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    interv_hosp_amb = models.FloatField(blank=True, null=True, db_column='INTERV_HOSP_AMB')
    fecha_interv = models.DateTimeField(blank=True, null=True, db_column='FECHA_INTERV')
    fecha_ingreso = models.DateTimeField(blank=True, null=True, db_column='FECHA_INGRESO')
    fecha_salida = models.DateTimeField(blank=True, null=True, db_column='FECHA_SALIDA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    numero_historia = models.CharField(blank=True, null=True, db_column='NUMERO_HISTORIA', max_length=20)
    hospital_elect_emerg = models.FloatField(blank=True, null=True, db_column='HOSPITAL_ELECT_EMERG')
    referido_centro = models.FloatField(blank=True, null=True, db_column='REFERIDO_CENTRO')
    referido_servicio = models.FloatField(blank=True, null=True, db_column='REFERIDO_SERVICIO')
    quirofano = models.FloatField(blank=True, null=True, db_column='QUIROFANO')
    toma_muestra = models.CharField(blank=True, null=True, db_column='TOMA_MUESTRA', max_length=200)
    intervencion_omitida = models.FloatField(blank=True, null=True, db_column='INTERVENCION_OMITIDA')
    otraintervencion_omitida = models.CharField(blank=True, null=True, db_column='OTRAINTERVENCION_OMITIDA', max_length=100)
    causa_egreso = models.FloatField(blank=True, null=True, db_column='CAUSA_EGRESO')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_REGCIRU\""


class LegacyTRegvacu(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hactividad = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hpacientemision = models.FloatField(blank=True, null=True, db_column='HPACIENTEMISION')
    embarazada = models.FloatField(blank=True, null=True, db_column='EMBARAZADA')
    lote = models.CharField(blank=True, null=True, db_column='LOTE', max_length=30)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    tipoedad2 = models.CharField(blank=True, null=True, db_column='TIPOEDAD2', max_length=1)
    edad2 = models.FloatField(blank=True, null=True, db_column='EDAD2')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    hpac_cond_espe = models.FloatField(blank=True, null=True, db_column='HPAC_COND_ESPE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_REGVACU\""


class LegacyTRendsp04(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    realizado = models.FloatField(blank=True, null=True, db_column='REALIZADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RENDSP04\""


class LegacyTRenepi15(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    casosx = models.FloatField(blank=True, null=True, db_column='CASOSX')
    casosp = models.FloatField(blank=True, null=True, db_column='CASOSP')
    casoss = models.FloatField(blank=True, null=True, db_column='CASOSS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RENEPI15\""


class LegacyTRengres(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    htipoestable = models.FloatField(blank=True, null=True, db_column='HTIPOESTABLE')
    cant_estable = models.FloatField(blank=True, null=True, db_column='CANT_ESTABLE')
    cant_documento = models.FloatField(blank=True, null=True, db_column='CANT_DOCUMENTO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RENGRES\""


class LegacyTRengsit(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    hcodificador = models.FloatField(blank=True, null=True, db_column='HCODIFICADOR')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    cant_casos = models.FloatField(blank=True, null=True, db_column='CANT_CASOS')
    cant_muertes = models.FloatField(blank=True, null=True, db_column='CANT_MUERTES')
    tiposituacion = models.FloatField(blank=True, null=True, db_column='TIPOSITUACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    grave = models.FloatField(blank=True, null=True, db_column='GRAVE')
    inusitado = models.FloatField(blank=True, null=True, db_column='INUSITADO')
    nacional = models.FloatField(blank=True, null=True, db_column='NACIONAL')
    internac = models.FloatField(blank=True, null=True, db_column='INTERNAC')
    fechainicio = models.DateTimeField(blank=True, null=True, db_column='FECHAINICIO')
    fechafin = models.DateTimeField(blank=True, null=True, db_column='FECHAFIN')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RENGSIT\""


class LegacyTRengtele(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    casos = models.FloatField(blank=True, null=True, db_column='CASOS')
    muertes = models.FloatField(blank=True, null=True, db_column='MUERTES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    casoshom = models.FloatField(blank=True, null=True, db_column='CASOSHOM')
    casosmuj = models.FloatField(blank=True, null=True, db_column='CASOSMUJ')
    muerteshom = models.FloatField(blank=True, null=True, db_column='MUERTESHOM')
    muertesmuj = models.FloatField(blank=True, null=True, db_column='MUERTESMUJ')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RENGTELE\""


class LegacyTResumen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    situacion_especial = models.CharField(blank=True, null=True, db_column='SITUACION_ESPECIAL', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RESUMEN\""


class LegacyTRnacanul(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    fecha_anulado = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANULADO')
    causa_anulado = models.CharField(blank=True, null=True, db_column='CAUSA_ANULADO', max_length=200)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    hcausaanulado = models.FloatField(blank=True, null=True, db_column='HCAUSAANULADO')
    fecha_operacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RNACANUL\""


class LegacyTRnacnaci(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=20)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    hora = models.CharField(blank=True, null=True, db_column='HORA', max_length=10)
    peso = models.FloatField(blank=True, null=True, db_column='PESO')
    talla = models.FloatField(blank=True, null=True, db_column='TALLA')
    hsexo = models.FloatField(blank=True, null=True, db_column='HSEXO')
    htipoparto = models.FloatField(blank=True, null=True, db_column='HTIPOPARTO')
    hasistencia = models.FloatField(blank=True, null=True, db_column='HASISTENCIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    hsitioparto = models.FloatField(blank=True, null=True, db_column='HSITIOPARTO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    semanagestacion = models.FloatField(blank=True, null=True, db_column='SEMANAGESTACION')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    vivo_muerto = models.IntegerField(blank=True, null=True, db_column='VIVO_MUERTO')
    ocurrepartootro = models.CharField(blank=True, null=True, db_column='OCURREPARTOOTRO', max_length=60)
    atendiopartootro = models.CharField(blank=True, null=True, db_column='ATENDIOPARTOOTRO', max_length=60)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_RNACNACI\""


class LegacyTSegdiabe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    fechaevolucion = models.DateTimeField(blank=True, null=True, db_column='FECHAEVOLUCION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    numsecciones = models.FloatField(blank=True, null=True, db_column='NUMSECCIONES')
    imc = models.FloatField(blank=True, null=True, db_column='IMC')
    glicemia = models.FloatField(blank=True, null=True, db_column='GLICEMIA')
    tensionarterial_alta = models.FloatField(blank=True, null=True, db_column='TENSIONARTERIAL_ALTA')
    tensionarterial_baja = models.FloatField(blank=True, null=True, db_column='TENSIONARTERIAL_BAJA')
    glicosilada = models.FloatField(blank=True, null=True, db_column='GLICOSILADA')
    colesterol = models.FloatField(blank=True, null=True, db_column='COLESTEROL')
    microalbum = models.FloatField(blank=True, null=True, db_column='MICROALBUM')
    creatinina = models.FloatField(blank=True, null=True, db_column='CREATININA')
    triglicerido = models.FloatField(blank=True, null=True, db_column='TRIGLICERIDO')
    ldl = models.FloatField(blank=True, null=True, db_column='LDL')
    hdl = models.FloatField(blank=True, null=True, db_column='HDL')
    depcreatinina = models.FloatField(blank=True, null=True, db_column='DEPCREATININA')
    fondodeojo = models.FloatField(blank=True, null=True, db_column='FONDODEOJO')
    causashospitalarias = models.CharField(blank=True, null=True, db_column='CAUSASHOSPITALARIAS', max_length=250)
    sesioneducativa = models.CharField(blank=True, null=True, db_column='SESIONEDUCATIVA', max_length=100)
    secciones = models.FloatField(blank=True, null=True, db_column='SECCIONES')
    egreso = models.FloatField(blank=True, null=True, db_column='EGRESO')
    condicionegreso = models.FloatField(blank=True, null=True, db_column='CONDICIONEGRESO')
    hlocalidad_tranf = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_TRANF')
    hlocalidad_seg = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    fechatransferencia = models.DateTimeField(blank=True, null=True, db_column='FECHATRANSFERENCIA')
    causademuerte = models.CharField(blank=True, null=True, db_column='CAUSADEMUERTE', max_length=1)
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fluoro = models.FloatField(blank=True, null=True, db_column='FLUORO')
    evaluacion = models.CharField(blank=True, null=True, db_column='EVALUACION', max_length=4000)
    hespecialidad = models.FloatField(blank=True, null=True, db_column='HESPECIALIDAD')
    evaluacion2 = models.CharField(blank=True, null=True, db_column='EVALUACION2', max_length=4000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_SEGDIABE\""


class LegacyTSegevolp(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    fecha_seg = models.DateTimeField(blank=True, null=True, db_column='FECHA_SEG')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hlocalidad_seg = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    fecha_result_seg = models.DateTimeField(blank=True, null=True, db_column='FECHA_RESULT_SEG')
    otros_tratam_seg = models.CharField(blank=True, null=True, db_column='OTROS_TRATAM_SEG', max_length=250)
    complicacion_seg = models.CharField(blank=True, null=True, db_column='COMPLICACION_SEG', max_length=250)
    observacion_seg = models.CharField(blank=True, null=True, db_column='OBSERVACION_SEG', max_length=4000)
    hevolucion = models.FloatField(blank=True, null=True, db_column='HEVOLUCION')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hresultados_prog = models.FloatField(blank=True, null=True, db_column='HRESULTADOS_PROG')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_SEGEVOLP\""


class LegacyTSegucard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    hlocalidad_seg = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    evaluacion = models.CharField(blank=True, null=True, db_column='EVALUACION', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaevolucion = models.DateTimeField(blank=True, null=True, db_column='FECHAEVOLUCION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_SEGUCARD\""


class LegacyTSignsint(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_basesd = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_BASESD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_SIGNSINT\""


class LegacyTSigsinse(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_basesd = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_BASESD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_SIGSINSE\""


class LegacyTSituespe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    htipoevento = models.FloatField(blank=True, null=True, db_column='HTIPOEVENTO')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    cant_casos = models.FloatField(blank=True, null=True, db_column='CANT_CASOS')
    cant_muertes = models.FloatField(blank=True, null=True, db_column='CANT_MUERTES')
    medidatomada = models.CharField(blank=True, null=True, db_column='MEDIDATOMADA', max_length=200)
    descripcionevento = models.CharField(blank=True, null=True, db_column='DESCRIPCIONEVENTO', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_SITUESPE\""


class LegacyTTrasegim(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_TRASEGIM\""


class LegacyTTratamie(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_TRATAMIE\""


class LegacyTTratuber(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    iniciotra = models.FloatField(blank=True, null=True, db_column='INICIOTRA')
    fechainiciotra = models.DateTimeField(blank=True, null=True, db_column='FECHAINICIOTRA')
    mesestrat_i = models.FloatField(blank=True, null=True, db_column='MESESTRAT_I')
    mesestrat_m = models.FloatField(blank=True, null=True, db_column='MESESTRAT_M')
    administraciontra = models.FloatField(blank=True, null=True, db_column='ADMINISTRACIONTRA')
    notaes = models.CharField(blank=True, null=True, db_column='NOTAES', max_length=100)
    resultadobact_1 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_1')
    resultadobact_2 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_2')
    resultadobact_3 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_3')
    resultadobact_4 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_4')
    resultadobact_5 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_5')
    resultadobact_6 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_6')
    resultadobact_f = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_F')
    egreso = models.FloatField(blank=True, null=True, db_column='EGRESO')
    reingreso = models.FloatField(blank=True, null=True, db_column='REINGRESO')
    fechaegreso = models.DateTimeField(blank=True, null=True, db_column='FECHAEGRESO')
    fechareingreso = models.DateTimeField(blank=True, null=True, db_column='FECHAREINGRESO')
    hcondicionfinalegreso = models.FloatField(blank=True, null=True, db_column='HCONDICIONFINALEGRESO')
    hcondicionfinalreingreso = models.IntegerField(blank=True, null=True, db_column='HCONDICIONFINALREINGRESO')
    muertetb = models.FloatField(blank=True, null=True, db_column='MUERTETB')
    muerteotracausa = models.FloatField(blank=True, null=True, db_column='MUERTEOTRACAUSA')
    semana_abandono = models.FloatField(blank=True, null=True, db_column='SEMANA_ABANDONO')
    lugartransferencia = models.FloatField(blank=True, null=True, db_column='LUGARTRANSFERENCIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    tomasprogramadas = models.FloatField(blank=True, null=True, db_column='TOMASPROGRAMADAS')
    tomascumplidas = models.FloatField(blank=True, null=True, db_column='TOMASCUMPLIDAS')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_TRATUBER\""


class LegacyTTsegcard(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_TSEGCARD\""


class LegacyTUsuarios(models.Model):
    login = models.CharField(blank=True, null=True, primary_key=True, db_column='LOGIN', max_length=10)
    password = models.CharField(blank=True, null=True, db_column='PASSWORD', max_length=12)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=40)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    cargo = models.CharField(blank=True, null=True, db_column='CARGO', max_length=150)
    jerarquia = models.CharField(blank=True, null=True, db_column='JERARQUIA', max_length=2)
    creado = models.CharField(blank=True, null=True, db_column='CREADO', max_length=10)
    fec_crea = models.DateTimeField(blank=True, null=True, db_column='FEC_CREA')
    fec_ent = models.DateTimeField(blank=True, null=True, db_column='FEC_ENT')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    morbilidad = models.FloatField(blank=True, null=True, db_column='MORBILIDAD')
    natalidad = models.FloatField(blank=True, null=True, db_column='NATALIDAD')
    mortalidad = models.FloatField(blank=True, null=True, db_column='MORTALIDAD')
    oncologia = models.FloatField(blank=True, null=True, db_column='ONCOLOGIA')
    fichas = models.FloatField(blank=True, null=True, db_column='FICHAS')
    accidente = models.FloatField(blank=True, null=True, db_column='ACCIDENTE')
    cirugia = models.FloatField(blank=True, null=True, db_column='CIRUGIA')
    vacunacion = models.FloatField(blank=True, null=True, db_column='VACUNACION')
    transferencia = models.FloatField(blank=True, null=True, db_column='TRANSFERENCIA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"legacy\".\"T_USUARIOS\""


class Accidentelaboral(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    accidente = models.FloatField(blank=True, null=True, db_column='ACCIDENTE')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    hora = models.CharField(blank=True, null=True, db_column='HORA', max_length=20)
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    tratamiento = models.CharField(blank=True, null=True, db_column='TRATAMIENTO', max_length=1)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=1)
    fechatra = models.DateTimeField(blank=True, null=True, db_column='FECHATRA')
    horatratamiento = models.CharField(blank=True, null=True, db_column='HORATRATAMIENTO', max_length=20)
    fuente = models.CharField(blank=True, null=True, db_column='FUENTE', max_length=1)
    desconoce = models.FloatField(blank=True, null=True, db_column='DESCONOCE')
    fuentedesconoce = models.FloatField(blank=True, null=True, db_column='FUENTEDESCONOCE')
    serologia = models.CharField(blank=True, null=True, db_column='SEROLOGIA', max_length=1)
    resultadosero = models.CharField(blank=True, null=True, db_column='RESULTADOSERO', max_length=30)
    fecharesultadosero = models.DateTimeField(blank=True, null=True, db_column='FECHARESULTADOSERO')
    hexposicion = models.FloatField(blank=True, null=True, db_column='HEXPOSICION')
    hobjeto = models.FloatField(blank=True, null=True, db_column='HOBJETO')
    hliquido = models.FloatField(blank=True, null=True, db_column='HLIQUIDO')
    hsituacion = models.FloatField(blank=True, null=True, db_column='HSITUACION')
    abusosexual = models.FloatField(blank=True, null=True, db_column='ABUSOSEXUAL')
    hlocalidadabuso = models.FloatField(blank=True, null=True, db_column='HLOCALIDADABUSO')
    fechaabuso = models.DateTimeField(blank=True, null=True, db_column='FECHAABUSO')
    horaabuso = models.CharField(blank=True, null=True, db_column='HORAABUSO', max_length=20)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ACCIDENTELABORAL\""


class AccTransito(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha = models.FloatField(blank=True, null=True, db_column='HFICHA')
    htipo_accidente = models.FloatField(blank=True, null=True, db_column='HTIPO_ACCIDENTE')
    htipo_vehiculo = models.FloatField(blank=True, null=True, db_column='HTIPO_VEHICULO')
    hcondicion = models.FloatField(blank=True, null=True, db_column='HCONDICION')
    hsitio_accidente = models.FloatField(blank=True, null=True, db_column='HSITIO_ACCIDENTE')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    hsitio_auto = models.FloatField(blank=True, null=True, db_column='HSITIO_AUTO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    causa = models.FloatField(blank=True, null=True, db_column='CAUSA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ACC_TRANSITO\""


class Actividad(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=20)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    descripcion = models.TextField(blank=True, null=True, db_column='DESCRIPCION')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    reporte = models.FloatField(blank=True, null=True, db_column='REPORTE')
    ficha_epi = models.CharField(blank=True, null=True, db_column='FICHA_EPI', max_length=1)
    nombrelargo = models.CharField(blank=True, null=True, db_column='NOMBRELARGO', max_length=300)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ACTIVIDAD\""


class Actividadcomun(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=250)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=29)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ACTIVIDADCOMUN\""


class ActividadOsp(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    rendimiento = models.FloatField(blank=True, null=True, db_column='RENDIMIENTO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=250)
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=80)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ACTIVIDAD_OSP\""


class ActividadOsplan(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hactividad_osp = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD_OSP')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    rendimiento = models.FloatField(blank=True, null=True, db_column='RENDIMIENTO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ACTIVIDAD_OSPLAN\""


class Albergue(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    tipouso = models.IntegerField(blank=True, null=True, db_column='TIPOUSO')
    totalfamilia = models.FloatField(blank=True, null=True, db_column='TOTALFAMILIA')
    totalpersonas = models.FloatField(blank=True, null=True, db_column='TOTALPERSONAS')
    contacto = models.CharField(blank=True, null=True, db_column='CONTACTO', max_length=100)
    telefcontacto = models.CharField(blank=True, null=True, db_column='TELEFCONTACTO', max_length=50)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ALBERGUE\""


class AnalisisLaboratorio(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_analisis = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANALISIS')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fecha_analisis = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANALISIS')
    resultado = models.CharField(blank=True, null=True, db_column='RESULTADO', max_length=50)
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANALISIS_LABORATORIO\""


class AnalisisLaboratorioCardio(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_analisis = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANALISIS')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fecha_analisis = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANALISIS')
    resultado = models.CharField(blank=True, null=True, db_column='RESULTADO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANALISIS_LABORATORIO_CARDIO\""


class AnalisisLabProg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=30)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANALISIS_LAB_PROG\""


class Anatomia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANATOMIA\""


class AnexosPeriodo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=6)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=20)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANEXOS_PERIODO\""


class AntecedentesProg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=30)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANTECEDENTES_PROG\""


class AntecedFactRiesgo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_anteced = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_ANTECED')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANTECED_FACT_RIESGO\""


class Anuario01(models.Model):
    anno = models.IntegerField(blank=True, null=True, primary_key=True, db_column='ANNO')
    seq_id_actual = models.BigIntegerField(blank=True, null=True, db_column='SEQ_ID_ACTUAL')
    hedades = models.FloatField(blank=True, null=True, db_column='HEDADES')
    sexo = models.IntegerField(blank=True, null=True, db_column='SEXO')
    region_ocurrencia = models.BigIntegerField(blank=True, null=True, db_column='REGION_OCURRENCIA')
    total = models.BigIntegerField(blank=True, null=True, db_column='TOTAL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANUARIO_01\""


class Anuario02(models.Model):
    anno = models.IntegerField(blank=True, null=True, primary_key=True, db_column='ANNO')
    seq_id_actual = models.BigIntegerField(blank=True, null=True, db_column='SEQ_ID_ACTUAL')
    hedades = models.FloatField(blank=True, null=True, db_column='HEDADES')
    sexo = models.IntegerField(blank=True, null=True, db_column='SEXO')
    region_residencia = models.BigIntegerField(blank=True, null=True, db_column='REGION_RESIDENCIA')
    total = models.BigIntegerField(blank=True, null=True, db_column='TOTAL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANUARIO_02\""


class Anuario03(models.Model):
    anno = models.IntegerField(blank=True, null=True, primary_key=True, db_column='ANNO')
    hedades = models.FloatField(blank=True, null=True, db_column='HEDADES')
    sexo = models.IntegerField(blank=True, null=True, db_column='SEXO')
    region_ocurrencia = models.BigIntegerField(blank=True, null=True, db_column='REGION_OCURRENCIA')
    total = models.BigIntegerField(blank=True, null=True, db_column='TOTAL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANUARIO_03\""


class Anuario04(models.Model):
    anno = models.IntegerField(blank=True, null=True, primary_key=True, db_column='ANNO')
    hedades = models.FloatField(blank=True, null=True, db_column='HEDADES')
    sexo = models.IntegerField(blank=True, null=True, db_column='SEXO')
    region_residencia = models.BigIntegerField(blank=True, null=True, db_column='REGION_RESIDENCIA')
    total = models.BigIntegerField(blank=True, null=True, db_column='TOTAL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANUARIO_04\""


class Anuario05(models.Model):
    anno = models.IntegerField(blank=True, null=True, primary_key=True, db_column='ANNO')
    seq_id_actual = models.BigIntegerField(blank=True, null=True, db_column='SEQ_ID_ACTUAL')
    sexo = models.IntegerField(blank=True, null=True, db_column='SEXO')
    mes = models.IntegerField(blank=True, null=True, db_column='MES')
    region_ocurrencia = models.BigIntegerField(blank=True, null=True, db_column='REGION_OCURRENCIA')
    total = models.BigIntegerField(blank=True, null=True, db_column='TOTAL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANUARIO_05\""


class Anuario06(models.Model):
    anno = models.IntegerField(blank=True, null=True, primary_key=True, db_column='ANNO')
    seq_id_actual = models.BigIntegerField(blank=True, null=True, db_column='SEQ_ID_ACTUAL')
    sexo = models.IntegerField(blank=True, null=True, db_column='SEXO')
    mes = models.IntegerField(blank=True, null=True, db_column='MES')
    region_residencia = models.BigIntegerField(blank=True, null=True, db_column='REGION_RESIDENCIA')
    total = models.BigIntegerField(blank=True, null=True, db_column='TOTAL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ANUARIO_06\""


class Asic(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ASIC\""


class Bacteriologia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"BACTERIOLOGIA\""


class BasesDiagProg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=20)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"BASES_DIAG_PROG\""


class Biopsiaspaciente(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    aspectoclinico = models.FloatField(blank=True, null=True, db_column='ASPECTOCLINICO')
    biopsiaanterior = models.FloatField(blank=True, null=True, db_column='BIOPSIAANTERIOR')
    ceneoplasicas = models.FloatField(blank=True, null=True, db_column='CENEOPLASICAS')
    cereactivas = models.FloatField(blank=True, null=True, db_column='CEREACTIVAS')
    cgneoplasicas = models.FloatField(blank=True, null=True, db_column='CGNEOPLASICAS')
    cgreactivas = models.FloatField(blank=True, null=True, db_column='CGREACTIVAS')
    citanormal = models.FloatField(blank=True, null=True, db_column='CITANORMAL')
    citologiaant = models.FloatField(blank=True, null=True, db_column='CITOLOGIAANT')
    citologianeoplasia = models.FloatField(blank=True, null=True, db_column='CITOLOGIANEOPLASIA')
    codigomuestrasas = models.CharField(blank=True, null=True, db_column='CODIGOMUESTRASAS', max_length=8)
    crinfecciosos = models.FloatField(blank=True, null=True, db_column='CRINFECCIOSOS')
    crinflamatorios = models.FloatField(blank=True, null=True, db_column='CRINFLAMATORIOS')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    embarazada = models.FloatField(blank=True, null=True, db_column='EMBARAZADA')
    fechacriocirugia = models.DateTimeField(blank=True, null=True, db_column='FECHACRIOCIRUGIA')
    fechaconizacion = models.DateTimeField(blank=True, null=True, db_column='FECHACONIZACION')
    fechadoc = models.DateTimeField(blank=True, null=True, db_column='FECHADOC')
    fechahistradical = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTRADICAL')
    fechahisttotal = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTTOTAL')
    fechalectura = models.DateTimeField(blank=True, null=True, db_column='FECHALECTURA')
    fechamuestra = models.DateTimeField(blank=True, null=True, db_column='FECHAMUESTRA')
    fecharadioterapia = models.DateTimeField(blank=True, null=True, db_column='FECHARADIOTERAPIA')
    fecharesultado = models.DateTimeField(blank=True, null=True, db_column='FECHARESULTADO')
    fechaultregla = models.DateTimeField(blank=True, null=True, db_column='FECHAULTREGLA')
    hlaboratorio = models.FloatField(blank=True, null=True, db_column='HLABORATORIO')
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hpatologo = models.FloatField(blank=True, null=True, db_column='HPATOLOGO')
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    mesbiopsia = models.DateTimeField(blank=True, null=True, db_column='MESBIOPSIA')
    mescitologia = models.DateTimeField(blank=True, null=True, db_column='MESCITOLOGIA')
    muestracitologica = models.FloatField(blank=True, null=True, db_column='MUESTRACITOLOGICA')
    nroparto = models.FloatField(blank=True, null=True, db_column='NROPARTO')
    nroaborto = models.FloatField(blank=True, null=True, db_column='NROABORTO')
    nrolamina = models.CharField(blank=True, null=True, db_column='NROLAMINA', max_length=20)
    numero = models.FloatField(blank=True, null=True, db_column='NUMERO')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=600)
    resultadoasociado = models.FloatField(blank=True, null=True, db_column='RESULTADOASOCIADO')
    hresultadob = models.FloatField(blank=True, null=True, db_column='HRESULTADOB')
    hresultadoc = models.FloatField(blank=True, null=True, db_column='HRESULTADOC')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    tipoexamen = models.FloatField(blank=True, null=True, db_column='TIPOEXAMEN')
    tipomuestra1 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA1')
    tipomuestra2 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA2')
    tratamientoprevio = models.FloatField(blank=True, null=True, db_column='TRATAMIENTOPREVIO')
    valorlectura = models.FloatField(blank=True, null=True, db_column='VALORLECTURA')
    vph = models.FloatField(blank=True, null=True, db_column='VPH')
    usuario_amb = models.CharField(blank=True, null=True, db_column='USUARIO_AMB', max_length=10)
    usuario_lab = models.CharField(blank=True, null=True, db_column='USUARIO_LAB', max_length=10)
    hcentromuestra = models.FloatField(blank=True, null=True, db_column='HCENTROMUESTRA')
    observacionesmacro = models.CharField(blank=True, null=True, db_column='OBSERVACIONESMACRO', max_length=4000)
    muestrautero = models.CharField(blank=True, null=True, db_column='MUESTRAUTERO', max_length=50)
    transresi = models.FloatField(blank=True, null=True, db_column='TRANSRESI')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"BIOPSIASPACIENTE\""


class Biopsiaspacienteseg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"BIOPSIASPACIENTESEG\""


class BiopsiasError(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hlaboratorio = models.FloatField(blank=True, null=True, db_column='HLABORATORIO')
    tipoexamen = models.FloatField(blank=True, null=True, db_column='TIPOEXAMEN')
    fechamuestra = models.DateTimeField(blank=True, null=True, db_column='FECHAMUESTRA')
    hcentromuestra = models.FloatField(blank=True, null=True, db_column='HCENTROMUESTRA')
    citanormal = models.FloatField(blank=True, null=True, db_column='CITANORMAL')
    fechalectura = models.DateTimeField(blank=True, null=True, db_column='FECHALECTURA')
    ceneoplasicas = models.FloatField(blank=True, null=True, db_column='CENEOPLASICAS')
    valorlectura = models.FloatField(blank=True, null=True, db_column='VALORLECTURA')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    hpatologo = models.FloatField(blank=True, null=True, db_column='HPATOLOGO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"BIOPSIAS_ERROR\""


class Biopsiatra(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    aspectoclinico = models.FloatField(blank=True, null=True, db_column='ASPECTOCLINICO')
    biopsiaanterior = models.FloatField(blank=True, null=True, db_column='BIOPSIAANTERIOR')
    ceneoplasicas = models.FloatField(blank=True, null=True, db_column='CENEOPLASICAS')
    cereactivas = models.FloatField(blank=True, null=True, db_column='CEREACTIVAS')
    cgneoplasicas = models.FloatField(blank=True, null=True, db_column='CGNEOPLASICAS')
    cgreactivas = models.FloatField(blank=True, null=True, db_column='CGREACTIVAS')
    citanormal = models.FloatField(blank=True, null=True, db_column='CITANORMAL')
    citologiaant = models.FloatField(blank=True, null=True, db_column='CITOLOGIAANT')
    citologianeoplasia = models.FloatField(blank=True, null=True, db_column='CITOLOGIANEOPLASIA')
    codigomuestrasas = models.CharField(blank=True, null=True, db_column='CODIGOMUESTRASAS', max_length=8)
    crinfecciosos = models.FloatField(blank=True, null=True, db_column='CRINFECCIOSOS')
    crinflamatorios = models.FloatField(blank=True, null=True, db_column='CRINFLAMATORIOS')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    embarazada = models.FloatField(blank=True, null=True, db_column='EMBARAZADA')
    fechacriocirugia = models.DateTimeField(blank=True, null=True, db_column='FECHACRIOCIRUGIA')
    fechaconizacion = models.DateTimeField(blank=True, null=True, db_column='FECHACONIZACION')
    fechadoc = models.DateTimeField(blank=True, null=True, db_column='FECHADOC')
    fechahistradical = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTRADICAL')
    fechahisttotal = models.DateTimeField(blank=True, null=True, db_column='FECHAHISTTOTAL')
    fechalectura = models.DateTimeField(blank=True, null=True, db_column='FECHALECTURA')
    fechamuestra = models.DateTimeField(blank=True, null=True, db_column='FECHAMUESTRA')
    fecharadioterapia = models.DateTimeField(blank=True, null=True, db_column='FECHARADIOTERAPIA')
    fecharesultado = models.DateTimeField(blank=True, null=True, db_column='FECHARESULTADO')
    fechaultregla = models.DateTimeField(blank=True, null=True, db_column='FECHAULTREGLA')
    hlaboratorio = models.FloatField(blank=True, null=True, db_column='HLABORATORIO')
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hpatologo = models.FloatField(blank=True, null=True, db_column='HPATOLOGO')
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    mesbiopsia = models.DateTimeField(blank=True, null=True, db_column='MESBIOPSIA')
    mescitologia = models.DateTimeField(blank=True, null=True, db_column='MESCITOLOGIA')
    muestracitologica = models.FloatField(blank=True, null=True, db_column='MUESTRACITOLOGICA')
    nroparto = models.FloatField(blank=True, null=True, db_column='NROPARTO')
    nroaborto = models.FloatField(blank=True, null=True, db_column='NROABORTO')
    nrolamina = models.CharField(blank=True, null=True, db_column='NROLAMINA', max_length=20)
    numero = models.FloatField(blank=True, null=True, db_column='NUMERO')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=254)
    resultadoasociado = models.FloatField(blank=True, null=True, db_column='RESULTADOASOCIADO')
    hresultadob = models.FloatField(blank=True, null=True, db_column='HRESULTADOB')
    hresultadoc = models.FloatField(blank=True, null=True, db_column='HRESULTADOC')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    tipoexamen = models.FloatField(blank=True, null=True, db_column='TIPOEXAMEN')
    tipomuestra1 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA1')
    tipomuestra2 = models.FloatField(blank=True, null=True, db_column='TIPOMUESTRA2')
    tratamientoprevio = models.FloatField(blank=True, null=True, db_column='TRATAMIENTOPREVIO')
    valorlectura = models.FloatField(blank=True, null=True, db_column='VALORLECTURA')
    vph = models.FloatField(blank=True, null=True, db_column='VPH')
    usuario_amb = models.CharField(blank=True, null=True, db_column='USUARIO_AMB', max_length=10)
    usuario_lab = models.CharField(blank=True, null=True, db_column='USUARIO_LAB', max_length=10)
    hcentromuestra = models.FloatField(blank=True, null=True, db_column='HCENTROMUESTRA')
    muestrautero = models.CharField(blank=True, null=True, db_column='MUESTRAUTERO', max_length=50)
    observacionesmacro = models.CharField(blank=True, null=True, db_column='OBSERVACIONESMACRO', max_length=4000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"BIOPSIATRA\""


class Cambios(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAMBIOS\""


class Cambioscirugia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAMBIOSCIRUGIA\""


class Cargo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CARGO\""


class Casosmm(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    num_partos = models.FloatField(blank=True, null=True, db_column='NUM_PARTOS')
    hijos_nacvivos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACVIVOS')
    hijos_nacmuertos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACMUERTOS')
    hijos_nacabortos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACABORTOS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=25)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CASOSMM\""


class CasosMmi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=25)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=25)
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    hsexo = models.FloatField(blank=True, null=True, db_column='HSEXO')
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    fechaocurrencia = models.DateTimeField(blank=True, null=True, db_column='FECHAOCURRENCIA')
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=25)
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    hresidencia_pais = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAIS')
    nacionalidad = models.CharField(blank=True, null=True, db_column='NACIONALIDAD', max_length=1)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    numeromsds = models.CharField(blank=True, null=True, db_column='NUMEROMSDS', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CASOS_MMI\""


class Categoria(models.Model):
    cod_categoria = models.IntegerField(blank=True, null=True, primary_key=True, db_column='COD_CATEGORIA')
    des_categoria = models.CharField(blank=True, null=True, db_column='DES_CATEGORIA', max_length=30)
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CATEGORIA\""


class CategoriaCie10(models.Model):
    cod_categoria = models.IntegerField(blank=True, null=True, primary_key=True, db_column='COD_CATEGORIA')
    des_categoria = models.CharField(blank=True, null=True, db_column='DES_CATEGORIA', max_length=30)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CATEGORIA_CIE10\""


class CategoriaDoc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    hgrupo = models.FloatField(blank=True, null=True, db_column='HGRUPO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CATEGORIA_DOC\""


class Causa(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAUSA\""


class Causaanulacion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=6)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=254)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAUSAANULACION\""


class CausaM(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    desenfermedad = models.CharField(blank=True, null=True, db_column='DESENFERMEDAD', max_length=200)
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAUSA_M\""


class CausaMmedico(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    causa1 = models.CharField(blank=True, null=True, db_column='CAUSA1', max_length=120)
    causa2 = models.CharField(blank=True, null=True, db_column='CAUSA2', max_length=120)
    causa3 = models.CharField(blank=True, null=True, db_column='CAUSA3', max_length=120)
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAUSA_MMEDICO\""


class CausaMorbosas(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAUSA_MORBOSAS\""


class CausaMRepa(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    intervalo = models.CharField(blank=True, null=True, db_column='INTERVALO', max_length=30)
    desenfermedad = models.CharField(blank=True, null=True, db_column='DESENFERMEDAD', max_length=200)
    ordenlista = models.CharField(blank=True, null=True, db_column='ORDENLISTA', max_length=1)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CAUSA_M_REPA\""


class Certificado(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    numeropartida = models.CharField(blank=True, null=True, db_column='NUMEROPARTIDA', max_length=10)
    numeromsds = models.CharField(blank=True, null=True, db_column='NUMEROMSDS', max_length=10)
    certificado = models.CharField(blank=True, null=True, db_column='CERTIFICADO', max_length=10)
    annocertificado = models.FloatField(blank=True, null=True, db_column='ANNOCERTIFICADO')
    mfetal = models.FloatField(blank=True, null=True, db_column='MFETAL')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=100)
    nacionalidad = models.FloatField(blank=True, null=True, db_column='NACIONALIDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=15)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    fecha_m = models.DateTimeField(blank=True, null=True, db_column='FECHA_M')
    fecha_n = models.DateTimeField(blank=True, null=True, db_column='FECHA_N')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    tipoedad = models.CharField(blank=True, null=True, db_column='TIPOEDAD', max_length=1)
    hestadocivil = models.FloatField(blank=True, null=True, db_column='HESTADOCIVIL')
    annocursado = models.FloatField(blank=True, null=True, db_column='ANNOCURSADO')
    annoterminado = models.FloatField(blank=True, null=True, db_column='ANNOTERMINADO')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    hprofesion = models.FloatField(blank=True, null=True, db_column='HPROFESION')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    hpais = models.FloatField(blank=True, null=True, db_column='HPAIS')
    hsitio_m = models.FloatField(blank=True, null=True, db_column='HSITIO_M')
    nombreclinica = models.CharField(blank=True, null=True, db_column='NOMBRECLINICA', max_length=100)
    hlocaocurrencia = models.FloatField(blank=True, null=True, db_column='HLOCAOCURRENCIA')
    direcocurrencia = models.CharField(blank=True, null=True, db_column='DIRECOCURRENCIA', max_length=250)
    hlocaresidencia = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIA')
    direcresidencia = models.CharField(blank=True, null=True, db_column='DIRECRESIDENCIA', max_length=200)
    hpresenciaembarazo = models.FloatField(blank=True, null=True, db_column='HPRESENCIAEMBARAZO')
    hcausabasica = models.FloatField(blank=True, null=True, db_column='HCAUSABASICA')
    otrosestados = models.CharField(blank=True, null=True, db_column='OTROSESTADOS', max_length=400)
    autopsia = models.FloatField(blank=True, null=True, db_column='AUTOPSIA')
    examencuerpo = models.FloatField(blank=True, null=True, db_column='EXAMENCUERPO')
    examenlab = models.FloatField(blank=True, null=True, db_column='EXAMENLAB')
    interrogatorio = models.FloatField(blank=True, null=True, db_column='INTERROGATORIO')
    historiaclinica = models.FloatField(blank=True, null=True, db_column='HISTORIACLINICA')
    numerodiagnostico = models.CharField(blank=True, null=True, db_column='NUMERODIAGNOSTICO', max_length=10)
    hmedicofirmante = models.FloatField(blank=True, null=True, db_column='HMEDICOFIRMANTE')
    otromedfirmante = models.CharField(blank=True, null=True, db_column='OTROMEDFIRMANTE', max_length=100)
    asistenciamedica = models.FloatField(blank=True, null=True, db_column='ASISTENCIAMEDICA')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    firmamedico = models.FloatField(blank=True, null=True, db_column='FIRMAMEDICO')
    direcservicio_m = models.CharField(blank=True, null=True, db_column='DIRECSERVICIO_M', max_length=200)
    descernomedica = models.CharField(blank=True, null=True, db_column='DESCERNOMEDICA', max_length=250)
    hdestinocuerpo = models.FloatField(blank=True, null=True, db_column='HDESTINOCUERPO')
    numeropermiso = models.CharField(blank=True, null=True, db_column='NUMEROPERMISO', max_length=10)
    hregionpermiso = models.FloatField(blank=True, null=True, db_column='HREGIONPERMISO')
    lugarpermiso = models.CharField(blank=True, null=True, db_column='LUGARPERMISO', max_length=200)
    fechapermiso = models.DateTimeField(blank=True, null=True, db_column='FECHAPERMISO')
    hregionexpe = models.FloatField(blank=True, null=True, db_column='HREGIONEXPE')
    lugarexpedicion = models.CharField(blank=True, null=True, db_column='LUGAREXPEDICION', max_length=200)
    fechaexpe = models.DateTimeField(blank=True, null=True, db_column='FECHAEXPE')
    firmaautoridad = models.FloatField(blank=True, null=True, db_column='FIRMAAUTORIDAD')
    sello = models.FloatField(blank=True, null=True, db_column='SELLO')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    hmadre = models.FloatField(blank=True, null=True, db_column='HMADRE')
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    edad2 = models.FloatField(blank=True, null=True, db_column='EDAD2')
    tipoedad2 = models.CharField(blank=True, null=True, db_column='TIPOEDAD2', max_length=1)
    transresi = models.FloatField(blank=True, null=True, db_column='TRANSRESI')
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    sabeleer = models.CharField(blank=True, null=True, db_column='SABELEER', max_length=1)
    hijosnac_v = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_V')
    hijosnac_av = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_AV')
    hijosnac_m = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_M')
    hijosnac_mf = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_MF')
    tomo = models.CharField(blank=True, null=True, db_column='TOMO', max_length=50)
    folio = models.CharField(blank=True, null=True, db_column='FOLIO', max_length=50)
    libro = models.CharField(blank=True, null=True, db_column='LIBRO', max_length=50)
    acta = models.CharField(blank=True, null=True, db_column='ACTA', max_length=50)
    nacmadrefallecido = models.FloatField(blank=True, null=True, db_column='NACMADREFALLECIDO')
    cimadrefallecido = models.CharField(blank=True, null=True, db_column='CIMADREFALLECIDO', max_length=15)
    nommadrefallecido = models.CharField(blank=True, null=True, db_column='NOMMADREFALLECIDO', max_length=50)
    nacpadrefallecido = models.FloatField(blank=True, null=True, db_column='NACPADREFALLECIDO')
    cipadrefallecido = models.CharField(blank=True, null=True, db_column='CIPADREFALLECIDO', max_length=15)
    nompadrefallecido = models.CharField(blank=True, null=True, db_column='NOMPADREFALLECIDO', max_length=50)
    nacregistrador = models.FloatField(blank=True, null=True, db_column='NACREGISTRADOR')
    ciregistrador = models.CharField(blank=True, null=True, db_column='CIREGISTRADOR', max_length=10)
    nomregistrador = models.CharField(blank=True, null=True, db_column='NOMREGISTRADOR', max_length=50)
    tomopartidanac = models.CharField(blank=True, null=True, db_column='TOMOPARTIDANAC', max_length=50)
    foliopartidanac = models.CharField(blank=True, null=True, db_column='FOLIOPARTIDANAC', max_length=50)
    libropartidanac = models.CharField(blank=True, null=True, db_column='LIBROPARTIDANAC', max_length=50)
    actapartidanac = models.CharField(blank=True, null=True, db_column='ACTAPARTIDANAC', max_length=50)
    horamuerte = models.CharField(blank=True, null=True, db_column='HORAMUERTE', max_length=20)
    hestado = models.FloatField(blank=True, null=True, db_column='HESTADO')
    hlocaresidenciafp = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIAFP')
    hestablecimiento_ocur = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO_OCUR')
    especial = models.FloatField(blank=True, null=True, db_column='ESPECIAL')
    otrodiagnostico = models.FloatField(blank=True, null=True, db_column='OTRODIAGNOSTICO')
    otrodiagnosticocert = models.CharField(blank=True, null=True, db_column='OTRODIAGNOSTICOCERT', max_length=50)
    fechaelaboracion = models.DateTimeField(blank=True, null=True, db_column='FECHAELABORACION')
    numeroautopsia = models.CharField(blank=True, null=True, db_column='NUMEROAUTOPSIA', max_length=20)
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=500)
    valsexo = models.IntegerField(blank=True, null=True, db_column='VALSEXO')
    valcausabasica = models.IntegerField(blank=True, null=True, db_column='VALCAUSABASICA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CERTIFICADO\""


class CertiMadreM(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hmadre = models.FloatField(blank=True, null=True, db_column='HMADRE')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CERTI_MADRE_M\""


class Certnacimiento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    fechacertificado = models.DateTimeField(blank=True, null=True, db_column='FECHACERTIFICADO')
    htipoderegistro = models.FloatField(blank=True, null=True, db_column='HTIPODEREGISTRO')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    codigosas = models.CharField(blank=True, null=True, db_column='CODIGOSAS', max_length=10)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    hlocalidadoc = models.FloatField(blank=True, null=True, db_column='HLOCALIDADOC')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    nombredirector = models.CharField(blank=True, null=True, db_column='NOMBREDIRECTOR', max_length=100)
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    actadenacimento = models.CharField(blank=True, null=True, db_column='ACTADENACIMENTO', max_length=50)
    tomo = models.CharField(blank=True, null=True, db_column='TOMO', max_length=50)
    folio = models.CharField(blank=True, null=True, db_column='FOLIO', max_length=50)
    libro = models.CharField(blank=True, null=True, db_column='LIBRO', max_length=50)
    testigo1 = models.CharField(blank=True, null=True, db_column='TESTIGO1', max_length=40)
    testigoci1 = models.CharField(blank=True, null=True, db_column='TESTIGOCI1', max_length=10)
    testigoedad1 = models.FloatField(blank=True, null=True, db_column='TESTIGOEDAD1')
    testigo2 = models.CharField(blank=True, null=True, db_column='TESTIGO2', max_length=40)
    testigoci2 = models.CharField(blank=True, null=True, db_column='TESTIGOCI2', max_length=10)
    testigoedad2 = models.FloatField(blank=True, null=True, db_column='TESTIGOEDAD2')
    jefecivil = models.CharField(blank=True, null=True, db_column='JEFECIVIL', max_length=40)
    jefecivilci = models.CharField(blank=True, null=True, db_column='JEFECIVILCI', max_length=10)
    fecharegcivil = models.DateTimeField(blank=True, null=True, db_column='FECHAREGCIVIL')
    especial = models.FloatField(blank=True, null=True, db_column='ESPECIAL')
    validado = models.IntegerField(blank=True, null=True, db_column='VALIDADO')
    cambio_id = models.FloatField(blank=True, null=True, db_column='CAMBIO_ID')
    id_old = models.FloatField(blank=True, null=True, db_column='ID_OLD')
    anno_idold = models.CharField(blank=True, null=True, db_column='ANNO_IDOLD', max_length=4)
    bd_sid = models.CharField(blank=True, null=True, db_column='BD_SID', max_length=4)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CERTNACIMIENTO\""


class Cheqesquema(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    ubicacion = models.CharField(blank=True, null=True, db_column='UBICACION', max_length=6)
    sidbd = models.CharField(blank=True, null=True, db_column='SIDBD', max_length=6)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CHEQESQUEMA\""


class Cie10(models.Model):
    seq_id_actual = models.BigIntegerField(blank=True, null=True, primary_key=True, db_column='SEQ_ID_ACTUAL')
    cod_categoria = models.IntegerField(blank=True, null=True, db_column='COD_CATEGORIA')
    cod_clasificacion = models.CharField(blank=True, null=True, db_column='COD_CLASIFICACION', max_length=7)
    des_clasificacio1 = models.CharField(blank=True, null=True, db_column='DES_CLASIFICACIO1', max_length=200)
    des_clasificacio2 = models.CharField(blank=True, null=True, db_column='DES_CLASIFICACIO2', max_length=200)
    causa_basica = models.CharField(blank=True, null=True, db_column='CAUSA_BASICA', max_length=1)
    sexo_afectado = models.IntegerField(blank=True, null=True, db_column='SEXO_AFECTADO')
    frecuencia = models.CharField(blank=True, null=True, db_column='FRECUENCIA', max_length=1)
    criterio_frecuenci = models.CharField(blank=True, null=True, db_column='CRITERIO_FRECUENCI', max_length=2)
    edad_minima = models.IntegerField(blank=True, null=True, db_column='EDAD_MINIMA')
    unidad_minima = models.CharField(blank=True, null=True, db_column='UNIDAD_MINIMA', max_length=1)
    edad_maxima = models.IntegerField(blank=True, null=True, db_column='EDAD_MAXIMA')
    unidad_maxima = models.CharField(blank=True, null=True, db_column='UNIDAD_MAXIMA', max_length=1)
    no_puede_ser = models.CharField(blank=True, null=True, db_column='NO_PUEDE_SER', max_length=2)
    validacion_categor = models.CharField(blank=True, null=True, db_column='VALIDACION_CATEGOR', max_length=15)
    rango = models.CharField(blank=True, null=True, db_column='RANGO', max_length=15)
    id_precedente = models.BigIntegerField(blank=True, null=True, db_column='ID_PRECEDENTE')
    orden_clasificacio = models.CharField(blank=True, null=True, db_column='ORDEN_CLASIFICACIO', max_length=1)
    clave_ctrl = models.BigIntegerField(blank=True, null=True, db_column='CLAVE_CTRL')
    edo_ctrl = models.BigIntegerField(blank=True, null=True, db_column='EDO_CTRL')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CIE10\""


class Citologiasaexamen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcitologiaa = models.FloatField(blank=True, null=True, db_column='HCITOLOGIAA')
    htipoexamen = models.FloatField(blank=True, null=True, db_column='HTIPOEXAMEN')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CITOLOGIASAEXAMEN\""


class Citologiasanormal(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    hpadre = models.FloatField(blank=True, null=True, db_column='HPADRE')
    tipo = models.FloatField(blank=True, null=True, db_column='TIPO')
    tipocelula = models.FloatField(blank=True, null=True, db_column='TIPOCELULA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CITOLOGIASANORMAL\""


class Clasificador(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CLASIFICADOR\""


class ClasifConsultanteProg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=80)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CLASIF_CONSULTANTE_PROG\""


class Codificador(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    reportaepi = models.FloatField(blank=True, null=True, db_column='REPORTAEPI')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    epi = models.FloatField(blank=True, null=True, db_column='EPI')
    tele = models.FloatField(blank=True, null=True, db_column='TELE')
    hgrupo = models.FloatField(blank=True, null=True, db_column='HGRUPO')
    reportatele = models.FloatField(blank=True, null=True, db_column='REPORTATELE')
    orden = models.FloatField(blank=True, null=True, db_column='ORDEN')
    ordenepi = models.FloatField(blank=True, null=True, db_column='ORDENEPI')
    evento_especial = models.FloatField(blank=True, null=True, db_column='EVENTO_ESPECIAL')
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CODIFICADOR\""


class CodificadorEdad(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    henfermedad = models.FloatField(blank=True, null=True, db_column='HENFERMEDAD')
    hedad = models.FloatField(blank=True, null=True, db_column='HEDAD')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CODIFICADOR_EDAD\""


class CodifCie10(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    hcodificador = models.FloatField(blank=True, null=True, db_column='HCODIFICADOR')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CODIF_CIE10\""


class Complicacionaguda(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACIONAGUDA\""


class Complicacioncardiovascular(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    tipo = models.CharField(blank=True, null=True, db_column='TIPO', max_length=1)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACIONCARDIOVASCULAR\""


class Complicacioncronica(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACIONCRONICA\""


class Complicaciondisca(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACIONDISCA\""


class Complicaciones(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACIONES\""


class ComplicacionesSeg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_complica = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_COMPLICA')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACIONES_SEG\""


class Complicacionquirurgica(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hcomplicacion = models.FloatField(blank=True, null=True, db_column='HCOMPLICACION')
    htipocomplicacion = models.FloatField(blank=True, null=True, db_column='HTIPOCOMPLICACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACIONQUIRURGICA\""


class ComplicacionProg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    status = models.CharField(blank=True, null=True, db_column='STATUS', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"COMPLICACION_PROG\""


class Condicion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CONDICION\""


class Condicioncaso(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CONDICIONCASO\""


class Condicionespecial(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=4)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=100)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CONDICIONESPECIAL\""


class CondicionIngresoMalaria(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=20)
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CONDICION_INGRESO_MALARIA\""


class Configuracion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdependencia = models.FloatField(blank=True, null=True, db_column='HDEPENDENCIA')
    hdependencia2 = models.FloatField(blank=True, null=True, db_column='HDEPENDENCIA2')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    nivelrecepcion = models.FloatField(blank=True, null=True, db_column='NIVELRECEPCION')
    niveltransmision = models.FloatField(blank=True, null=True, db_column='NIVELTRANSMISION')
    hestado = models.FloatField(blank=True, null=True, db_column='HESTADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CONFIGURACION\""


class Conyugal(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"CONYUGAL\""


class DependenciaAdm(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=250)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    hnivel = models.FloatField(blank=True, null=True, db_column='HNIVEL')
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DEPENDENCIA_ADM\""


class Destinocuerpo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DESTINOCUERPO\""


class Diagnostico(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DIAGNOSTICO\""


class DiagnosticosAsoc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcie10 = models.BigIntegerField(blank=True, null=True, db_column='HCIE10')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DIAGNOSTICOS_ASOC\""


class Documento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    tipo = models.FloatField(blank=True, null=True, db_column='TIPO')
    horigen = models.FloatField(blank=True, null=True, db_column='HORIGEN')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=500)
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=20)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DOCUMENTO\""


class Documentocons(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    tipo = models.FloatField(blank=True, null=True, db_column='TIPO')
    horigen = models.FloatField(blank=True, null=True, db_column='HORIGEN')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=250)
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=20)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DOCUMENTOCONS\""


class DocumentoDengue(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    c_fiebre = models.FloatField(blank=True, null=True, db_column='C_FIEBRE')
    c_hemorragico = models.FloatField(blank=True, null=True, db_column='C_HEMORRAGICO')
    c_hospitalizado = models.FloatField(blank=True, null=True, db_column='C_HOSPITALIZADO')
    c_muestra = models.FloatField(blank=True, null=True, db_column='C_MUESTRA')
    c_positivo = models.FloatField(blank=True, null=True, db_column='C_POSITIVO')
    c_negativo = models.FloatField(blank=True, null=True, db_column='C_NEGATIVO')
    c_pendiente = models.FloatField(blank=True, null=True, db_column='C_PENDIENTE')
    c_epidemiologico = models.FloatField(blank=True, null=True, db_column='C_EPIDEMIOLOGICO')
    c_laboratorio = models.FloatField(blank=True, null=True, db_column='C_LABORATORIO')
    nro_semana = models.FloatField(blank=True, null=True, db_column='NRO_SEMANA')
    casos_semana = models.FloatField(blank=True, null=True, db_column='CASOS_SEMANA')
    htipodengue = models.FloatField(blank=True, null=True, db_column='HTIPODENGUE')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    totaldengue = models.FloatField(blank=True, null=True, db_column='TOTALDENGUE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DOCUMENTO_DENGUE\""


class DocControl(models.Model):
    documento = models.FloatField(blank=True, null=True, primary_key=True, db_column='DOCUMENTO')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=20)
    origen = models.FloatField(blank=True, null=True, db_column='ORIGEN')
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DOC_CONTROL\""


class DocSospecha(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    c_estudio = models.FloatField(blank=True, null=True, db_column='C_ESTUDIO')
    c_descartado = models.FloatField(blank=True, null=True, db_column='C_DESCARTADO')
    c_confirmado = models.FloatField(blank=True, null=True, db_column='C_CONFIRMADO')
    c_compartido = models.FloatField(blank=True, null=True, db_column='C_COMPARTIDO')
    c_notificado = models.FloatField(blank=True, null=True, db_column='C_NOTIFICADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DOC_SOSPECHA\""


class DondeRealizoPai(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=250)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DONDE_REALIZO_PAI\""


class Duracionembarazo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hedades = models.FloatField(blank=True, null=True, db_column='HEDADES')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"DURACIONEMBARAZO\""


class Edades(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    formula = models.CharField(blank=True, null=True, db_column='FORMULA', max_length=100)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    htipoedad1 = models.CharField(blank=True, null=True, db_column='HTIPOEDAD1', max_length=1)
    edad1 = models.FloatField(blank=True, null=True, db_column='EDAD1')
    htipoedad2 = models.CharField(blank=True, null=True, db_column='HTIPOEDAD2', max_length=1)
    edad2 = models.FloatField(blank=True, null=True, db_column='EDAD2')
    hgp1 = models.FloatField(blank=True, null=True, db_column='HGP1')
    hgp2 = models.FloatField(blank=True, null=True, db_column='HGP2')
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    orden = models.FloatField(blank=True, null=True, db_column='ORDEN')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"EDADES\""


class EfectuoHecho(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"EFECTUO_HECHO\""


class Egresos(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"EGRESOS\""


class SismaiErrores(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ERRORES\""


class ErroresAnuario(models.Model):
    codigo = models.FloatField(blank=True, null=True, primary_key=True, db_column='CODIGO')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=200)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    id_certif = models.FloatField(blank=True, null=True, db_column='ID_CERTIF')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ERRORES_ANUARIO\""


class SismaiErroresLabo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ERRORES_LABO\""


class SismaiErroresResi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ERRORES_RESI\""


class SismaiErroresSinc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tabla = models.CharField(blank=True, null=True, db_column='TABLA', max_length=100)
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    sqlcodigo = models.FloatField(blank=True, null=True, db_column='SQLCODIGO')
    sqlerror = models.CharField(blank=True, null=True, db_column='SQLERROR', max_length=200)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ERRORES_SINC\""


class Especialidad(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ESPECIALIDAD\""


class Establecimiento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    htipo = models.FloatField(blank=True, null=True, db_column='HTIPO')
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=250)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefono = models.CharField(blank=True, null=True, db_column='TELEFONO', max_length=50)
    status = models.CharField(blank=True, null=True, db_column='STATUS', max_length=1)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    domiciliado = models.CharField(blank=True, null=True, db_column='DOMICILIADO', max_length=1)
    rif = models.CharField(blank=True, null=True, db_column='RIF', max_length=20)
    tipoestablec = models.FloatField(blank=True, null=True, db_column='TIPOESTABLEC')
    cuentadante = models.FloatField(blank=True, null=True, db_column='CUENTADANTE')
    hnivel = models.FloatField(blank=True, null=True, db_column='HNIVEL')
    descripcion = models.TextField(blank=True, null=True, db_column='DESCRIPCION')
    x_utm = models.DecimalField(blank=True, null=True, db_column='X_UTM', max_digits=24, decimal_places=6)
    y_utm = models.DecimalField(blank=True, null=True, db_column='Y_UTM', max_digits=24, decimal_places=6)
    altitud = models.DecimalField(blank=True, null=True, db_column='ALTITUD', max_digits=10, decimal_places=2)
    hasic = models.FloatField(blank=True, null=True, db_column='HASIC')
    funcionamiento = models.CharField(blank=True, null=True, db_column='FUNCIONAMIENTO', max_length=1)
    hdependencia_adm = models.FloatField(blank=True, null=True, db_column='HDEPENDENCIA_ADM')
    htipo2 = models.FloatField(blank=True, null=True, db_column='HTIPO2')
    horario = models.FloatField(blank=True, null=True, db_column='HORARIO')
    nombrelargo_comu = models.CharField(blank=True, null=True, db_column='NOMBRELARGO_COMU', max_length=500)
    nombrelargo_trad = models.CharField(blank=True, null=True, db_column='NOMBRELARGO_TRAD', max_length=500)
    nombre2 = models.CharField(blank=True, null=True, db_column='NOMBRE2', max_length=150)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ESTABLECIMIENTO\""


class EstablecimientoMaestra(models.Model):
    hnivel = models.FloatField(blank=True, null=True, primary_key=True, db_column='HNIVEL')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    htipo = models.FloatField(blank=True, null=True, db_column='HTIPO')
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=250)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefono = models.CharField(blank=True, null=True, db_column='TELEFONO', max_length=50)
    status = models.CharField(blank=True, null=True, db_column='STATUS', max_length=1)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    cuentadante = models.FloatField(blank=True, null=True, db_column='CUENTADANTE')
    funcionamiento = models.CharField(blank=True, null=True, db_column='FUNCIONAMIENTO', max_length=1)
    hdependencia_adm = models.FloatField(blank=True, null=True, db_column='HDEPENDENCIA_ADM')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ESTABLECIMIENTO_MAESTRA\""


class Estadisticas(models.Model):
    tipoestab = models.CharField(blank=True, null=True, primary_key=True, db_column='TIPOESTAB', max_length=1)
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    archivo = models.CharField(blank=True, null=True, db_column='ARCHIVO', max_length=50)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    tipo = models.CharField(blank=True, null=True, db_column='TIPO', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ESTADISTICAS\""


class Etnia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=40)
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    hubic_geo_etnia = models.BigIntegerField(blank=True, null=True, db_column='HUBIC_GEO_ETNIA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hregistro = models.FloatField(blank=True, null=True, db_column='HREGISTRO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ETNIA\""


class SismaiEventos(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"EVENTOS\""


class EventosLabo(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"EVENTOS_LABO\""


class EventosResi(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=100)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=1)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    status = models.IntegerField(blank=True, null=True, db_column='STATUS')
    esquema = models.CharField(blank=True, null=True, db_column='ESQUEMA', max_length=20)
    ams = models.CharField(blank=True, null=True, db_column='AMS', max_length=12)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"EVENTOS_RESI\""


class Evolucion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=80)
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"EVOLUCION\""


class Fallalectura(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FALLALECTURA\""


class Fichadeldolor(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FICHADELDOLOR\""


class Fichadolortoracico(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_programa = models.FloatField(blank=True, null=True, db_column='HFICHA_PROGRAMA')
    hfichadeldolor = models.FloatField(blank=True, null=True, db_column='HFICHADELDOLOR')
    si = models.FloatField(blank=True, null=True, db_column='SI')
    no = models.FloatField(blank=True, null=True, db_column='NO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FICHADOLORTORACICO\""


class Fichaepi13(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hestablecimientoasignado = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTOASIGNADO')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    muerte = models.FloatField(blank=True, null=True, db_column='MUERTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FICHAEPI13\""


class FichasEpidemiologicas(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    hlocalidad_ficha = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIDAD_FICHA')
    nro_caso = models.CharField(blank=True, null=True, db_column='NRO_CASO', max_length=20)
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    ano_fecha_reg = models.IntegerField(blank=True, null=True, db_column='ANO_FECHA_REG')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=254)
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FICHAS_EPIDEMIOLOGICAS\""


class FichaAccidente(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=15)
    fecha_oc = models.DateTimeField(blank=True, null=True, db_column='FECHA_OC')
    hora_oc = models.CharField(blank=True, null=True, db_column='HORA_OC', max_length=20)
    hlocalidad_oc = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_OC')
    sitio_oc = models.CharField(blank=True, null=True, db_column='SITIO_OC', max_length=150)
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    fallecio = models.FloatField(blank=True, null=True, db_column='FALLECIO')
    hora_muerte = models.CharField(blank=True, null=True, db_column='HORA_MUERTE', max_length=20)
    hsitio_muerte = models.FloatField(blank=True, null=True, db_column='HSITIO_MUERTE')
    influencia_alcohol = models.FloatField(blank=True, null=True, db_column='INFLUENCIA_ALCOHOL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FICHA_ACCIDENTE\""


class FinalTratamiento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FINAL_TRATAMIENTO\""


class Formaparto(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"FORMAPARTO\""


class Gaprivilegies(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    grupo = models.FloatField(blank=True, null=True, db_column='GRUPO')
    toplevel = models.CharField(blank=True, null=True, db_column='TOPLEVEL', max_length=32)
    childwindow = models.CharField(blank=True, null=True, db_column='CHILDWINDOW', max_length=32)
    hvisible = models.FloatField(blank=True, null=True, db_column='HVISIBLE')
    heditable = models.FloatField(blank=True, null=True, db_column='HEDITABLE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"GAPRIVILEGIES\""


class GrPoblacional(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    porc_masc = models.FloatField(blank=True, null=True, db_column='PORC_MASC')
    porc_fem = models.FloatField(blank=True, null=True, db_column='PORC_FEM')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"GR_POBLACIONAL\""


class HechosViolentos(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha = models.FloatField(blank=True, null=True, db_column='HFICHA')
    htipo_hecho = models.FloatField(blank=True, null=True, db_column='HTIPO_HECHO')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hefectuo_hecho = models.FloatField(blank=True, null=True, db_column='HEFECTUO_HECHO')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hubic_diagnostico = models.FloatField(blank=True, null=True, db_column='HUBIC_DIAGNOSTICO')
    hcie10 = models.FloatField(blank=True, null=True, db_column='HCIE10')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"HECHOS_VIOLENTOS\""


class Histdoc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    instancia = models.CharField(blank=True, null=True, db_column='INSTANCIA', max_length=30)
    evento = models.CharField(blank=True, null=True, db_column='EVENTO', max_length=100)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=20)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"HISTDOC\""


class HistoricoIds(models.Model):
    idregistro = models.FloatField(blank=True, null=True, primary_key=True, db_column='IDREGISTRO')
    nombre_tabla = models.CharField(blank=True, null=True, db_column='NOMBRE_TABLA', max_length=50)
    bd = models.CharField(blank=True, null=True, db_column='BD', max_length=8)
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=25)
    nroplanilla_numeromsds = models.CharField(blank=True, null=True, db_column='NROPLANILLA_NUMEROMSDS', max_length=25)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"HISTORICO_IDS\""


class HistCodificador(models.Model):
    codigo = models.CharField(blank=True, null=True, primary_key=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    accion = models.CharField(blank=True, null=True, db_column='ACCION', max_length=1)
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"HIST_CODIFICADOR\""


class Hojareparo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    reparapor = models.FloatField(blank=True, null=True, db_column='REPARAPOR')
    atravesde = models.FloatField(blank=True, null=True, db_column='ATRAVESDE')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=10)
    fecharepara = models.DateTimeField(blank=True, null=True, db_column='FECHAREPARA')
    otrosmedios = models.CharField(blank=True, null=True, db_column='OTROSMEDIOS', max_length=100)
    nombreclinico = models.CharField(blank=True, null=True, db_column='NOMBRECLINICO', max_length=100)
    nacmedico = models.FloatField(blank=True, null=True, db_column='NACMEDICO')
    cedulaclinico = models.CharField(blank=True, null=True, db_column='CEDULACLINICO', max_length=15)
    nombreepidem = models.CharField(blank=True, null=True, db_column='NOMBREEPIDEM', max_length=100)
    nacepidem = models.FloatField(blank=True, null=True, db_column='NACEPIDEM')
    cedulaepidem = models.CharField(blank=True, null=True, db_column='CEDULAEPIDEM', max_length=15)
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"HOJAREPARO\""


class HorAmbulat(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hactividad_osp = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD_OSP')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    horas = models.FloatField(blank=True, null=True, db_column='HORAS')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"HOR_AMBULAT\""


class InformeEpi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    casosp = models.FloatField(blank=True, null=True, db_column='CASOSP')
    casoss = models.FloatField(blank=True, null=True, db_column='CASOSS')
    casosx = models.FloatField(blank=True, null=True, db_column='CASOSX')
    acummes = models.FloatField(blank=True, null=True, db_column='ACUMMES')
    acumanno = models.FloatField(blank=True, null=True, db_column='ACUMANNO')
    orden = models.FloatField(blank=True, null=True, db_column='ORDEN')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"INFORME_EPI\""


class InstitucionFormadora(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=200)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=250)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    husuario = models.FloatField(blank=True, null=True, db_column='HUSUARIO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"INSTITUCION_FORMADORA\""


class Intervencion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"INTERVENCION\""


class Intervencionquirurgica(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    hintervencion = models.FloatField(blank=True, null=True, db_column='HINTERVENCION')
    hanatomia = models.FloatField(blank=True, null=True, db_column='HANATOMIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=1000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"INTERVENCIONQUIRURGICA\""


class IntervencionOmitida(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"INTERVENCION_OMITIDA\""


class Laboratorios(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=8)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    encargado = models.CharField(blank=True, null=True, db_column='ENCARGADO', max_length=30)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefonos = models.CharField(blank=True, null=True, db_column='TELEFONOS', max_length=30)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"LABORATORIOS\""


class LiquidoConta(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"LIQUIDO_CONTA\""


class Localidadestab(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"LOCALIDADESTAB\""


class Localizacionpulmon(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"LOCALIZACIONPULMON\""


class LugaresVisitados(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    lugar = models.CharField(blank=True, null=True, db_column='LUGAR', max_length=200)
    tiempo_perm = models.IntegerField(blank=True, null=True, db_column='TIEMPO_PERM')
    unid_tiemperm = models.CharField(blank=True, null=True, db_column='UNID_TIEMPERM', max_length=10)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"LUGARES_VISITADOS\""


class Lugarsuceso(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"LUGARSUCESO\""


class Medicofirmante(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"MEDICOFIRMANTE\""


class Mision(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=4)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=30)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"MISION\""


class MonitorBasededatos(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    sid = models.CharField(blank=True, null=True, db_column='SID', max_length=10)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    texto_fecha = models.CharField(blank=True, null=True, db_column='TEXTO_FECHA', max_length=20)
    nombre_tablespace = models.CharField(blank=True, null=True, db_column='NOMBRE_TABLESPACE', max_length=50)
    ts_size_mb = models.DecimalField(blank=True, null=True, db_column='TS_SIZE_MB', max_digits=11, decimal_places=2)
    ts_usado_mb = models.DecimalField(blank=True, null=True, db_column='TS_USADO_MB', max_digits=11, decimal_places=2)
    ts_usado_pc = models.DecimalField(blank=True, null=True, db_column='TS_USADO_PC', max_digits=11, decimal_places=2)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"MONITOR_BASEDEDATOS\""


class MonitorRespaldo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    sid = models.CharField(blank=True, null=True, db_column='SID', max_length=10)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    texto_fecha = models.CharField(blank=True, null=True, db_column='TEXTO_FECHA', max_length=20)
    hdd_bd_usado = models.CharField(blank=True, null=True, db_column='HDD_BD_USADO', max_length=10)
    hdd_bd_size = models.CharField(blank=True, null=True, db_column='HDD_BD_SIZE', max_length=10)
    hdd_bk_usado = models.CharField(blank=True, null=True, db_column='HDD_BK_USADO', max_length=10)
    hdd_bk_size = models.CharField(blank=True, null=True, db_column='HDD_BK_SIZE', max_length=10)
    hdd_opt_usado = models.CharField(blank=True, null=True, db_column='HDD_OPT_USADO', max_length=10)
    hdd_opt_size = models.CharField(blank=True, null=True, db_column='HDD_OPT_SIZE', max_length=10)
    tam_respaldo_dmp = models.CharField(blank=True, null=True, db_column='TAM_RESPALDO_DMP', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"MONITOR_RESPALDO\""


class MorAnulados(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausaanulado = models.FloatField(blank=True, null=True, db_column='HCAUSAANULADO')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    fecha_anulado = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANULADO')
    causa_anulado = models.CharField(blank=True, null=True, db_column='CAUSA_ANULADO', max_length=200)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fecha_operacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"MOR_ANULADOS\""


class MFetal(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    hmadre = models.FloatField(blank=True, null=True, db_column='HMADRE')
    hduracionemba = models.FloatField(blank=True, null=True, db_column='HDURACIONEMBA')
    hnactipoemba = models.FloatField(blank=True, null=True, db_column='HNACTIPOEMBA')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    hm_relaparto = models.FloatField(blank=True, null=True, db_column='HM_RELAPARTO')
    pesofeto = models.FloatField(blank=True, null=True, db_column='PESOFETO')
    ignoradopeso = models.FloatField(blank=True, null=True, db_column='IGNORADOPESO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    hasistenteparto = models.FloatField(blank=True, null=True, db_column='HASISTENTEPARTO')
    otroasistparto = models.CharField(blank=True, null=True, db_column='OTROASISTPARTO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"M_FETAL\""


class MMadre(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    apellido = models.CharField(blank=True, null=True, db_column='APELLIDO', max_length=100)
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    nacionalidad = models.FloatField(blank=True, null=True, db_column='NACIONALIDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=15)
    hprofesion = models.FloatField(blank=True, null=True, db_column='HPROFESION')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    annocursado = models.FloatField(blank=True, null=True, db_column='ANNOCURSADO')
    annoterminado = models.FloatField(blank=True, null=True, db_column='ANNOTERMINADO')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    hijosnac_v = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_V')
    hijosnac_m = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_M')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    sabeleer = models.CharField(blank=True, null=True, db_column='SABELEER', max_length=1)
    hestadocivil = models.FloatField(blank=True, null=True, db_column='HESTADOCIVIL')
    hijosnac_av = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_AV')
    hijosnac_mf = models.FloatField(blank=True, null=True, db_column='HIJOSNAC_MF')
    hlocaresidencia = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIA')
    direcresidencia = models.CharField(blank=True, null=True, db_column='DIRECRESIDENCIA', max_length=200)
    hlocaresidenciafp = models.FloatField(blank=True, null=True, db_column='HLOCARESIDENCIAFP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"M_MADRE\""


class MRelaparto(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"M_RELAPARTO\""


class MViolenta(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    htipo_m = models.FloatField(blank=True, null=True, db_column='HTIPO_M')
    hora_mv = models.CharField(blank=True, null=True, db_column='HORA_MV', max_length=20)
    fecha_mv = models.DateTimeField(blank=True, null=True, db_column='FECHA_MV')
    descripcionsuceso = models.CharField(blank=True, null=True, db_column='DESCRIPCIONSUCESO', max_length=400)
    hlugarsuceso = models.FloatField(blank=True, null=True, db_column='HLUGARSUCESO')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"M_VIOLENTA\""


class NacAnulados(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    nroplanilla = models.CharField(blank=True, null=True, db_column='NROPLANILLA', max_length=20)
    consecutivo = models.CharField(blank=True, null=True, db_column='CONSECUTIVO', max_length=20)
    ano_certif = models.FloatField(blank=True, null=True, db_column='ANO_CERTIF')
    fecha_anulado = models.DateTimeField(blank=True, null=True, db_column='FECHA_ANULADO')
    causa_anulado = models.CharField(blank=True, null=True, db_column='CAUSA_ANULADO', max_length=200)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    hcausaanulado = models.FloatField(blank=True, null=True, db_column='HCAUSAANULADO')
    fecha_operacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NAC_ANULADOS\""


class NacAsistencia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NAC_ASISTENCIA\""


class NacMadre(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    apellidos = models.CharField(blank=True, null=True, db_column='APELLIDOS', max_length=100)
    pasaporte = models.CharField(blank=True, null=True, db_column='PASAPORTE', max_length=20)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=20)
    phistoriaclinica = models.CharField(blank=True, null=True, db_column='PHISTORIACLINICA', max_length=20)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edadm = models.FloatField(blank=True, null=True, db_column='EDADM')
    edadp = models.FloatField(blank=True, null=True, db_column='EDADP')
    estadocivil = models.FloatField(blank=True, null=True, db_column='ESTADOCIVIL')
    annosmatrimonio = models.FloatField(blank=True, null=True, db_column='ANNOSMATRIMONIO')
    nacvivos = models.FloatField(blank=True, null=True, db_column='NACVIVOS')
    nacionm = models.FloatField(blank=True, null=True, db_column='NACIONM')
    nacionp = models.FloatField(blank=True, null=True, db_column='NACIONP')
    hentidam = models.FloatField(blank=True, null=True, db_column='HENTIDAM')
    hentidap = models.FloatField(blank=True, null=True, db_column='HENTIDAP')
    hpaism = models.FloatField(blank=True, null=True, db_column='HPAISM')
    hpaisp = models.FloatField(blank=True, null=True, db_column='HPAISP')
    actualvivos = models.FloatField(blank=True, null=True, db_column='ACTUALVIVOS')
    leerescribir = models.FloatField(blank=True, null=True, db_column='LEERESCRIBIR')
    nacvivosfallec = models.FloatField(blank=True, null=True, db_column='NACVIVOSFALLEC')
    muertesfetales = models.FloatField(blank=True, null=True, db_column='MUERTESFETALES')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    profesion = models.FloatField(blank=True, null=True, db_column='PROFESION')
    controlprenatal = models.FloatField(blank=True, null=True, db_column='CONTROLPRENATAL')
    telefonom = models.CharField(blank=True, null=True, db_column='TELEFONOM', max_length=20)
    ptelefono = models.CharField(blank=True, null=True, db_column='PTELEFONO', max_length=20)
    ocupacion = models.FloatField(blank=True, null=True, db_column='OCUPACION')
    pcedula = models.CharField(blank=True, null=True, db_column='PCEDULA', max_length=10)
    pnombres = models.CharField(blank=True, null=True, db_column='PNOMBRES', max_length=100)
    ppasaporte = models.CharField(blank=True, null=True, db_column='PPASAPORTE', max_length=20)
    pdireccion = models.CharField(blank=True, null=True, db_column='PDIRECCION', max_length=100)
    hpresidencia = models.FloatField(blank=True, null=True, db_column='HPRESIDENCIA')
    pfechanacimiento = models.DateTimeField(blank=True, null=True, db_column='PFECHANACIMIENTO')
    pestadocivil = models.FloatField(blank=True, null=True, db_column='PESTADOCIVIL')
    pleerescribir = models.FloatField(blank=True, null=True, db_column='PLEERESCRIBIR')
    hpultimogrado = models.FloatField(blank=True, null=True, db_column='HPULTIMOGRADO')
    pprofesion = models.FloatField(blank=True, null=True, db_column='PPROFESION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=100)
    pocupacion = models.FloatField(blank=True, null=True, db_column='POCUPACION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    nacionalidap = models.FloatField(blank=True, null=True, db_column='NACIONALIDAP')
    nacionalidam = models.FloatField(blank=True, null=True, db_column='NACIONALIDAM')
    unionmat = models.FloatField(blank=True, null=True, db_column='UNIONMAT')
    nroconsultaspre = models.FloatField(blank=True, null=True, db_column='NROCONSULTASPRE')
    hetniam = models.FloatField(blank=True, null=True, db_column='HETNIAM')
    hetniap = models.FloatField(blank=True, null=True, db_column='HETNIAP')
    hablaetniam = models.FloatField(blank=True, null=True, db_column='HABLAETNIAM')
    hablaetniap = models.FloatField(blank=True, null=True, db_column='HABLAETNIAP')
    ultimogradom = models.FloatField(blank=True, null=True, db_column='ULTIMOGRADOM')
    ultimogradop = models.FloatField(blank=True, null=True, db_column='ULTIMOGRADOP')
    residenciam = models.IntegerField(blank=True, null=True, db_column='RESIDENCIAM')
    hresidencia_paism = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAISM')
    residenciap = models.IntegerField(blank=True, null=True, db_column='RESIDENCIAP')
    hresidencia_paisp = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA_PAISP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NAC_MADRE\""


class NacRnacido(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=20)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    hora = models.CharField(blank=True, null=True, db_column='HORA', max_length=10)
    peso = models.FloatField(blank=True, null=True, db_column='PESO')
    talla = models.FloatField(blank=True, null=True, db_column='TALLA')
    hsexo = models.FloatField(blank=True, null=True, db_column='HSEXO')
    htipoparto = models.FloatField(blank=True, null=True, db_column='HTIPOPARTO')
    hasistencia = models.FloatField(blank=True, null=True, db_column='HASISTENCIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    hsitioparto = models.FloatField(blank=True, null=True, db_column='HSITIOPARTO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    semanagestacion = models.FloatField(blank=True, null=True, db_column='SEMANAGESTACION')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    vivo_muerto = models.IntegerField(blank=True, null=True, db_column='VIVO_MUERTO')
    ocurrepartootro = models.CharField(blank=True, null=True, db_column='OCURREPARTOOTRO', max_length=60)
    atendiopartootro = models.CharField(blank=True, null=True, db_column='ATENDIOPARTOOTRO', max_length=60)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NAC_RNACIDO\""


class NacTipoparto(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NAC_TIPOPARTO\""


class NacTiporeg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NAC_TIPOREG\""


class Nivel(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=30)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NIVEL\""


class NotasDsp04(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    nota = models.CharField(blank=True, null=True, db_column='NOTA', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NOTAS_DSP04\""


class Notificantes(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    hestablecnot = models.FloatField(blank=True, null=True, db_column='HESTABLECNOT')
    htipoestablec = models.FloatField(blank=True, null=True, db_column='HTIPOESTABLEC')
    cant_estable = models.FloatField(blank=True, null=True, db_column='CANT_ESTABLE')
    cant_documento = models.FloatField(blank=True, null=True, db_column='CANT_DOCUMENTO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NOTIFICANTES\""


class NumeroBd(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=4)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=6)
    servicio = models.CharField(blank=True, null=True, db_column='SERVICIO', max_length=6)
    sid = models.CharField(blank=True, null=True, db_column='SID', max_length=4)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=60)
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=6)
    idestable = models.FloatField(blank=True, null=True, db_column='IDESTABLE')
    nata_ids = models.CharField(blank=True, null=True, db_column='NATA_IDS', max_length=8)
    mort_ids = models.CharField(blank=True, null=True, db_column='MORT_IDS', max_length=8)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NUMERO_BD\""


class Nutricion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=6)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=20)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"NUTRICION\""


class Ocupacion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"OCUPACION\""


class Ocupasivigila(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=6)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=60)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"OCUPASIVIGILA\""


class OpcionCertnacimiento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    tema = models.IntegerField(blank=True, null=True, db_column='TEMA')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=200)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"OPCION_CERTNACIMIENTO\""


class OrgGeografica(models.Model):
    num_region = models.BigIntegerField(blank=True, null=True, primary_key=True, db_column='NUM_REGION')
    cod_categoria = models.IntegerField(blank=True, null=True, db_column='COD_CATEGORIA')
    region_precedente = models.BigIntegerField(blank=True, null=True, db_column='REGION_PRECEDENTE')
    des_region = models.CharField(blank=True, null=True, db_column='DES_REGION', max_length=150)
    cod_ocei = models.CharField(blank=True, null=True, db_column='COD_OCEI', max_length=30)
    can_casas = models.IntegerField(blank=True, null=True, db_column='CAN_CASAS')
    poblacion_estimada = models.IntegerField(blank=True, null=True, db_column='POBLACION_ESTIMADA')
    gac_gis_lat = models.CharField(blank=True, null=True, db_column='GAC_GIS_LAT', max_length=18)
    gac_gis_long = models.CharField(blank=True, null=True, db_column='GAC_GIS_LONG', max_length=18)
    gac_gis_proj = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_PROJ')
    gac_gis_tagx = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGX', max_digits=14, decimal_places=4)
    gac_gis_tagy = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGY', max_digits=14, decimal_places=4)
    gac_gis_tagf = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_TAGF')
    gac_gis_tagt = models.CharField(blank=True, null=True, db_column='GAC_GIS_TAGT', max_length=1)
    gac_gis_tagh = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGH', max_digits=8, decimal_places=2)
    gac_gis_tagc = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_TAGC')
    gac_gis_tagr = models.DecimalField(blank=True, null=True, db_column='GAC_GIS_TAGR', max_digits=8, decimal_places=3)
    gac_gis_pcol = models.IntegerField(blank=True, null=True, db_column='GAC_GIS_PCOL')
    gac_gis_lib = models.CharField(blank=True, null=True, db_column='GAC_GIS_LIB', max_length=50)
    gac_clav_loc = models.CharField(blank=True, null=True, db_column='GAC_CLAV_LOC', max_length=9)
    gac_cla_ocei = models.CharField(blank=True, null=True, db_column='GAC_CLA_OCEI', max_length=10)
    gac_nombre = models.CharField(blank=True, null=True, db_column='GAC_NOMBRE', max_length=40)
    gac_generico = models.CharField(blank=True, null=True, db_column='GAC_GENERICO', max_length=4)
    gac_latitud = models.CharField(blank=True, null=True, db_column='GAC_LATITUD', max_length=6)
    gac_longitud = models.CharField(blank=True, null=True, db_column='GAC_LONGITUD', max_length=6)
    gac_ubic_polit = models.CharField(blank=True, null=True, db_column='GAC_UBIC_POLIT', max_length=6)
    gac_estado = models.CharField(blank=True, null=True, db_column='GAC_ESTADO', max_length=2)
    gac_mun_dis = models.CharField(blank=True, null=True, db_column='GAC_MUN_DIS', max_length=2)
    gac_for_par = models.CharField(blank=True, null=True, db_column='GAC_FOR_PAR', max_length=2)
    gac_localidad = models.CharField(blank=True, null=True, db_column='GAC_LOCALIDAD', max_length=3)
    gac_carta = models.CharField(blank=True, null=True, db_column='GAC_CARTA', max_length=4)
    gac_cuadricula = models.CharField(blank=True, null=True, db_column='GAC_CUADRICULA', max_length=6)
    cod_estado = models.CharField(blank=True, null=True, db_column='COD_ESTADO', max_length=20)
    obs_region = models.CharField(blank=True, null=True, db_column='OBS_REGION', max_length=250)
    clave_ctrl = models.BigIntegerField(blank=True, null=True, db_column='CLAVE_CTRL')
    edo_ctrl = models.BigIntegerField(blank=True, null=True, db_column='EDO_CTRL')
    codigointerno = models.CharField(blank=True, null=True, db_column='CODIGOINTERNO', max_length=25)
    nombrelargo = models.CharField(blank=True, null=True, db_column='NOMBRELARGO', max_length=500)
    cod_ine = models.CharField(blank=True, null=True, db_column='COD_INE', max_length=14)
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ORG_GEOGRAFICA\""


class Otrostratamientos(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    tratamiento = models.CharField(blank=True, null=True, db_column='TRATAMIENTO', max_length=100)
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    indicaciones = models.CharField(blank=True, null=True, db_column='INDICACIONES', max_length=100)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"OTROSTRATAMIENTOS\""


class Paciente(models.Model):
    usuario = models.CharField(blank=True, null=True, primary_key=True, db_column='USUARIO', max_length=10)
    id = models.FloatField(blank=True, null=True, db_column='ID')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=50)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    hlocalizacion = models.FloatField(blank=True, null=True, db_column='HLOCALIZACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE\""


class Pacientesinexamen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTESINEXAMEN\""


class PacienteCondEspe(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hcondicionespecial = models.FloatField(blank=True, null=True, db_column='HCONDICIONESPECIAL')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE_COND_ESPE\""


class PacienteD(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=15)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    tipoedad = models.FloatField(blank=True, null=True, db_column='TIPOEDAD')
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=254)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    origen = models.FloatField(blank=True, null=True, db_column='ORIGEN')
    semana = models.FloatField(blank=True, null=True, db_column='SEMANA')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    tipodengue = models.FloatField(blank=True, null=True, db_column='TIPODENGUE')
    asistencia = models.FloatField(blank=True, null=True, db_column='ASISTENCIA')
    muerte = models.FloatField(blank=True, null=True, db_column='MUERTE')
    fechacreacion = models.DateTimeField(blank=True, null=True, db_column='FECHACREACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE_D\""


class PacienteDiabetes(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=25)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=254)
    hubicacion = models.BigIntegerField(blank=True, null=True, db_column='HUBICACION')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    fechaevolucion = models.DateTimeField(blank=True, null=True, db_column='FECHAEVOLUCION')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    ficha = models.FloatField(blank=True, null=True, db_column='FICHA')
    nro_caso = models.CharField(blank=True, null=True, db_column='NRO_CASO', max_length=20)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE_DIABETES\""


class PacienteError(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE_ERROR\""


class PacienteExamen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    fecharegistro = models.DateTimeField(blank=True, null=True, db_column='FECHAREGISTRO')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=50)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=100)
    hubicacion = models.FloatField(blank=True, null=True, db_column='HUBICACION')
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    citanormal = models.FloatField(blank=True, null=True, db_column='CITANORMAL')
    fechalectura = models.DateTimeField(blank=True, null=True, db_column='FECHALECTURA')
    fechamuestra = models.DateTimeField(blank=True, null=True, db_column='FECHAMUESTRA')
    hlaboratorio = models.FloatField(blank=True, null=True, db_column='HLABORATORIO')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    idexamen = models.FloatField(blank=True, null=True, db_column='IDEXAMEN')
    hpatologo = models.FloatField(blank=True, null=True, db_column='HPATOLOGO')
    nrolamina = models.CharField(blank=True, null=True, db_column='NROLAMINA', max_length=20)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=254)
    observacionesmacro = models.CharField(blank=True, null=True, db_column='OBSERVACIONESMACRO', max_length=4000)
    tipoexamen = models.FloatField(blank=True, null=True, db_column='TIPOEXAMEN')
    valorlectura = models.FloatField(blank=True, null=True, db_column='VALORLECTURA')
    ceneoplasicas = models.FloatField(blank=True, null=True, db_column='CENEOPLASICAS')
    hcentromuestra = models.FloatField(blank=True, null=True, db_column='HCENTROMUESTRA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE_EXAMEN\""


class PacienteFichaEpi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    nrohistoria = models.CharField(blank=True, null=True, db_column='NROHISTORIA', max_length=20)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    nombrepaciente = models.CharField(blank=True, null=True, db_column='NOMBREPACIENTE', max_length=25)
    apellidopaciente = models.CharField(blank=True, null=True, db_column='APELLIDOPACIENTE', max_length=25)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    lugar_nac = models.CharField(blank=True, null=True, db_column='LUGAR_NAC', max_length=50)
    sexo = models.FloatField(blank=True, null=True, db_column='SEXO')
    direccionhabitual = models.CharField(blank=True, null=True, db_column='DIRECCIONHABITUAL', max_length=254)
    hubicacion = models.BigIntegerField(blank=True, null=True, db_column='HUBICACION')
    tiempo_residencia = models.CharField(blank=True, null=True, db_column='TIEMPO_RESIDENCIA', max_length=10)
    telefonoh = models.CharField(blank=True, null=True, db_column='TELEFONOH', max_length=12)
    localizacion = models.CharField(blank=True, null=True, db_column='LOCALIZACION', max_length=254)
    hlocalizacion = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIZACION')
    otro_tiempo_res = models.CharField(blank=True, null=True, db_column='OTRO_TIEMPO_RES', max_length=10)
    telefonol = models.CharField(blank=True, null=True, db_column='TELEFONOL', max_length=12)
    hetnia = models.FloatField(blank=True, null=True, db_column='HETNIA')
    hconyugal = models.FloatField(blank=True, null=True, db_column='HCONYUGAL')
    hocupacion = models.FloatField(blank=True, null=True, db_column='HOCUPACION')
    analfabeta = models.CharField(blank=True, null=True, db_column='ANALFABETA', max_length=2)
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    anos_aprobados = models.IntegerField(blank=True, null=True, db_column='ANOS_APROBADOS')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    nomrepresentante = models.CharField(blank=True, null=True, db_column='NOMREPRESENTANTE', max_length=40)
    numero_hijo = models.CharField(blank=True, null=True, db_column='NUMERO_HIJO', max_length=2)
    fechadefuncion = models.DateTimeField(blank=True, null=True, db_column='FECHADEFUNCION')
    nacionalidad = models.CharField(blank=True, null=True, db_column='NACIONALIDAD', max_length=1)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE_FICHA_EPI\""


class PacienteMision(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hmision = models.FloatField(blank=True, null=True, db_column='HMISION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PACIENTE_MISION\""


class Pais(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PAIS\""


class Personalmedico(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=8)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    codigosas = models.CharField(blank=True, null=True, db_column='CODIGOSAS', max_length=12)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    telefonos = models.CharField(blank=True, null=True, db_column='TELEFONOS', max_length=35)
    cargo = models.CharField(blank=True, null=True, db_column='CARGO', max_length=50)
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PERSONALMEDICO\""


class Personalquirurgico(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hregistrocirugia = models.FloatField(blank=True, null=True, db_column='HREGISTROCIRUGIA')
    hrolmedico = models.FloatField(blank=True, null=True, db_column='HROLMEDICO')
    hmedico = models.FloatField(blank=True, null=True, db_column='HMEDICO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PERSONALQUIRURGICO\""


class Personalsalud(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=30)
    nacionalidad = models.CharField(blank=True, null=True, db_column='NACIONALIDAD', max_length=1)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=12)
    primer_nombre = models.CharField(blank=True, null=True, db_column='PRIMER_NOMBRE', max_length=40)
    segundo_nombre = models.CharField(blank=True, null=True, db_column='SEGUNDO_NOMBRE', max_length=40)
    primer_apellido = models.CharField(blank=True, null=True, db_column='PRIMER_APELLIDO', max_length=40)
    segundo_apellido = models.CharField(blank=True, null=True, db_column='SEGUNDO_APELLIDO', max_length=40)
    hsexo = models.FloatField(blank=True, null=True, db_column='HSEXO')
    fecha_nac = models.DateTimeField(blank=True, null=True, db_column='FECHA_NAC')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    unidad_edad = models.CharField(blank=True, null=True, db_column='UNIDAD_EDAD', max_length=1)
    telefono = models.CharField(blank=True, null=True, db_column='TELEFONO', max_length=35)
    correo = models.CharField(blank=True, null=True, db_column='CORREO', max_length=50)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=500)
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    hprofesion = models.FloatField(blank=True, null=True, db_column='HPROFESION')
    fecha_grado = models.DateTimeField(blank=True, null=True, db_column='FECHA_GRADO')
    hinstitucion = models.FloatField(blank=True, null=True, db_column='HINSTITUCION')
    fecha_registro = models.DateTimeField(blank=True, null=True, db_column='FECHA_REGISTRO')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=250)
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    fechadefuncion = models.DateTimeField(blank=True, null=True, db_column='FECHADEFUNCION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    husuario = models.FloatField(blank=True, null=True, db_column='HUSUARIO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PERSONALSALUD\""


class PesonalsaludPostgrados(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hpersonalsalud = models.FloatField(blank=True, null=True, db_column='HPERSONALSALUD')
    hinstitucion = models.FloatField(blank=True, null=True, db_column='HINSTITUCION')
    nombre_postgrado = models.CharField(blank=True, null=True, db_column='NOMBRE_POSTGRADO', max_length=250)
    fecha_postgrado = models.DateTimeField(blank=True, null=True, db_column='FECHA_POSTGRADO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    husuario = models.FloatField(blank=True, null=True, db_column='HUSUARIO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PESONALSALUD_POSTGRADOS\""


class PobEstab(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    pob_total = models.FloatField(blank=True, null=True, db_column='POB_TOTAL')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    cobertura = models.FloatField(blank=True, null=True, db_column='COBERTURA')
    distribucion = models.FloatField(blank=True, null=True, db_column='DISTRIBUCION')
    pobcobertura = models.FloatField(blank=True, null=True, db_column='POBCOBERTURA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"POB_ESTAB\""


class PosConfig(models.Model):
    objectcount = models.FloatField(blank=True, null=True, primary_key=True, db_column='OBJECTCOUNT')
    lamina = models.FloatField(blank=True, null=True, db_column='LAMINA')
    hestable = models.FloatField(blank=True, null=True, db_column='HESTABLE')
    tipoestab = models.CharField(blank=True, null=True, db_column='TIPOESTAB', max_length=1)
    sd = models.FloatField(blank=True, null=True, db_column='SD')
    hlaborat = models.FloatField(blank=True, null=True, db_column='HLABORAT')
    eruta = models.CharField(blank=True, null=True, db_column='ERUTA', max_length=100)
    iruta = models.CharField(blank=True, null=True, db_column='IRUTA', max_length=100)
    minobjectcount = models.FloatField(blank=True, null=True, db_column='MINOBJECTCOUNT')
    maxobjectcount = models.FloatField(blank=True, null=True, db_column='MAXOBJECTCOUNT')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    hdependencia2 = models.FloatField(blank=True, null=True, db_column='HDEPENDENCIA2')
    hestado = models.FloatField(blank=True, null=True, db_column='HESTADO')
    nivelrecepcion = models.FloatField(blank=True, null=True, db_column='NIVELRECEPCION')
    niveltransmision = models.FloatField(blank=True, null=True, db_column='NIVELTRANSMISION')
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    consulta = models.FloatField(blank=True, null=True, db_column='CONSULTA')
    nivelconsolidado = models.FloatField(blank=True, null=True, db_column='NIVELCONSOLIDADO')
    nivelcons_f = models.CharField(blank=True, null=True, db_column='NIVELCONS_F', max_length=3)
    ruta_archivo = models.CharField(blank=True, null=True, db_column='RUTA_ARCHIVO', max_length=80)
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    actualiza_org = models.FloatField(blank=True, null=True, db_column='ACTUALIZA_ORG')
    actualiza_dep = models.FloatField(blank=True, null=True, db_column='ACTUALIZA_DEP')
    actualiza_med = models.FloatField(blank=True, null=True, db_column='ACTUALIZA_MED')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"POS_CONFIG\""


class Presenciaembarazo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PRESENCIAEMBARAZO\""


class Profesion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=4)
    largo = models.FloatField(blank=True, null=True, db_column='LARGO')
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    codigoine = models.CharField(blank=True, null=True, db_column='CODIGOINE', max_length=8)
    nivel = models.CharField(blank=True, null=True, db_column='NIVEL', max_length=4)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROFESION\""


class Programaestablec(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hprogcomun = models.FloatField(blank=True, null=True, db_column='HPROGCOMUN')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROGRAMAESTABLEC\""


class ProgCardiovascular(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    anoinicio = models.FloatField(blank=True, null=True, db_column='ANOINICIO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    infartado = models.FloatField(blank=True, null=True, db_column='INFARTADO')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROG_CARDIOVASCULAR\""


class ProgComunitario(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=6)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    tipo = models.FloatField(blank=True, null=True, db_column='TIPO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROG_COMUNITARIO\""


class ProgDiabetes(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    anoinicio = models.FloatField(blank=True, null=True, db_column='ANOINICIO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    hprediabetico = models.FloatField(blank=True, null=True, db_column='HPREDIABETICO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROG_DIABETES\""


class ProgDiabeTemp(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    anoinicio = models.FloatField(blank=True, null=True, db_column='ANOINICIO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    hprediabetico = models.FloatField(blank=True, null=True, db_column='HPREDIABETICO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROG_DIABE_TEMP\""


class ProgMalChagEsq(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_epidemiologica = models.FloatField(blank=True, null=True, db_column='HFICHA_EPIDEMIOLOGICA')
    otras_bases_diag = models.CharField(blank=True, null=True, db_column='OTRAS_BASES_DIAG', max_length=100)
    nro_muestra = models.CharField(blank=True, null=True, db_column='NRO_MUESTRA', max_length=20)
    fecha_toma = models.DateTimeField(blank=True, null=True, db_column='FECHA_TOMA')
    lugar_toma = models.CharField(blank=True, null=True, db_column='LUGAR_TOMA', max_length=100)
    fech_init_fiebre = models.DateTimeField(blank=True, null=True, db_column='FECH_INIT_FIEBRE')
    lugar_inicio_fiebre = models.CharField(blank=True, null=True, db_column='LUGAR_INICIO_FIEBRE', max_length=50)
    permanencia_lug_fiebre = models.CharField(blank=True, null=True, db_column='PERMANENCIA_LUG_FIEBRE', max_length=20)
    hcondicion_ingreso_malaria = models.FloatField(blank=True, null=True, db_column='HCONDICION_INGRESO_MALARIA')
    otros_tratamientos = models.CharField(blank=True, null=True, db_column='OTROS_TRATAMIENTOS', max_length=250)
    hubicacion_infeccion = models.BigIntegerField(blank=True, null=True, db_column='HUBICACION_INFECCION')
    hpais = models.FloatField(blank=True, null=True, db_column='HPAIS')
    tranf_sangre = models.CharField(blank=True, null=True, db_column='TRANF_SANGRE', max_length=1)
    tratam_endovenoso = models.CharField(blank=True, null=True, db_column='TRATAM_ENDOVENOSO', max_length=1)
    fecha_tranf = models.DateTimeField(blank=True, null=True, db_column='FECHA_TRANF')
    hestab_tranf = models.FloatField(blank=True, null=True, db_column='HESTAB_TRANF')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    fecha_result = models.DateTimeField(blank=True, null=True, db_column='FECHA_RESULT')
    hresultados_prog = models.FloatField(blank=True, null=True, db_column='HRESULTADOS_PROG')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    complicaciones = models.CharField(blank=True, null=True, db_column='COMPLICACIONES', max_length=250)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROG_MAL_CHAG_ESQ\""


class ProgTuberculosis(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    serie = models.CharField(blank=True, null=True, db_column='SERIE', max_length=1)
    casonumero = models.CharField(blank=True, null=True, db_column='CASONUMERO', max_length=9)
    cohorte = models.CharField(blank=True, null=True, db_column='COHORTE', max_length=1)
    fechanotificacion = models.DateTimeField(blank=True, null=True, db_column='FECHANOTIFICACION')
    hcondicioncaso = models.FloatField(blank=True, null=True, db_column='HCONDICIONCASO')
    serologiavih = models.FloatField(blank=True, null=True, db_column='SEROLOGIAVIH')
    bacteriologia = models.FloatField(blank=True, null=True, db_column='BACTERIOLOGIA')
    clinica = models.FloatField(blank=True, null=True, db_column='CLINICA')
    radiologia = models.FloatField(blank=True, null=True, db_column='RADIOLOGIA')
    resradiologia = models.FloatField(blank=True, null=True, db_column='RESRADIOLOGIA')
    caverna = models.FloatField(blank=True, null=True, db_column='CAVERNA')
    histologia = models.FloatField(blank=True, null=True, db_column='HISTOLOGIA')
    tuberculina = models.FloatField(blank=True, null=True, db_column='TUBERCULINA')
    hdiagnostico = models.FloatField(blank=True, null=True, db_column='HDIAGNOSTICO')
    localizacion = models.FloatField(blank=True, null=True, db_column='LOCALIZACION')
    reslocalizacion = models.FloatField(blank=True, null=True, db_column='RESLOCALIZACION')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    hmedicocoord = models.FloatField(blank=True, null=True, db_column='HMEDICOCOORD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROG_TUBERCULOSIS\""


class ProgVihSida(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    nro_hijos = models.FloatField(blank=True, null=True, db_column='NRO_HIJOS')
    edad_ult_hijo = models.FloatField(blank=True, null=True, db_column='EDAD_ULT_HIJO')
    htransmision_por = models.FloatField(blank=True, null=True, db_column='HTRANSMISION_POR')
    hmedio_transmision = models.FloatField(blank=True, null=True, db_column='HMEDIO_TRANSMISION')
    otras_bases_diag = models.CharField(blank=True, null=True, db_column='OTRAS_BASES_DIAG', max_length=100)
    hcondicion_ingreso = models.FloatField(blank=True, null=True, db_column='HCONDICION_INGRESO')
    hactividad_osp = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD_OSP')
    otros_tratamientos = models.CharField(blank=True, null=True, db_column='OTROS_TRATAMIENTOS', max_length=250)
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    complicaciones = models.CharField(blank=True, null=True, db_column='COMPLICACIONES', max_length=4000)
    observaciones = models.CharField(blank=True, null=True, db_column='OBSERVACIONES', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROG_VIH_SIDA\""


class Protocolotrombolisis(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hficha_programa = models.FloatField(blank=True, null=True, db_column='HFICHA_PROGRAMA')
    infartoprevio = models.FloatField(blank=True, null=True, db_column='INFARTOPREVIO')
    tiempoutil = models.CharField(blank=True, null=True, db_column='TIEMPOUTIL', max_length=2)
    tratamientotrombo = models.FloatField(blank=True, null=True, db_column='TRATAMIENTOTROMBO')
    li_pre_trombo = models.FloatField(blank=True, null=True, db_column='LI_PRE_TROMBO')
    li_post_trombo = models.FloatField(blank=True, null=True, db_column='LI_POST_TROMBO')
    li_enzima_pre_t = models.FloatField(blank=True, null=True, db_column='LI_ENZIMA_PRE_T')
    li_post_t = models.FloatField(blank=True, null=True, db_column='LI_POST_T')
    estancia = models.FloatField(blank=True, null=True, db_column='ESTANCIA')
    estudionoinvasivo = models.FloatField(blank=True, null=True, db_column='ESTUDIONOINVASIVO')
    hemodinamia = models.FloatField(blank=True, null=True, db_column='HEMODINAMIA')
    cirugia = models.FloatField(blank=True, null=True, db_column='CIRUGIA')
    ucc = models.FloatField(blank=True, null=True, db_column='UCC')
    uti = models.FloatField(blank=True, null=True, db_column='UTI')
    hospitalizacion = models.FloatField(blank=True, null=True, db_column='HOSPITALIZACION')
    d_egreso = models.FloatField(blank=True, null=True, db_column='D_EGRESO')
    d_morge = models.FloatField(blank=True, null=True, db_column='D_MORGE')
    d_otroservicio = models.FloatField(blank=True, null=True, db_column='D_OTROSERVICIO')
    sistolica = models.FloatField(blank=True, null=True, db_column='SISTOLICA')
    diastolica = models.FloatField(blank=True, null=True, db_column='DIASTOLICA')
    hora_iniciadolor = models.CharField(blank=True, null=True, db_column='HORA_INICIADOLOR', max_length=10)
    hora_asistencia = models.CharField(blank=True, null=True, db_column='HORA_ASISTENCIA', max_length=10)
    hora_ingresohosp = models.CharField(blank=True, null=True, db_column='HORA_INGRESOHOSP', max_length=10)
    evaltratamiento = models.FloatField(blank=True, null=True, db_column='EVALTRATAMIENTO')
    cualcomplicacion = models.CharField(blank=True, null=True, db_column='CUALCOMPLICACION', max_length=50)
    dondehospitalizacion = models.CharField(blank=True, null=True, db_column='DONDEHOSPITALIZACION', max_length=50)
    hcentroreferencia = models.FloatField(blank=True, null=True, db_column='HCENTROREFERENCIA')
    localizainfarto = models.FloatField(blank=True, null=True, db_column='LOCALIZAINFARTO')
    referidootroservicio = models.CharField(blank=True, null=True, db_column='REFERIDOOTROSERVICIO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"PROTOCOLOTROMBOLISIS\""


class Quirofano(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"QUIROFANO\""


class Referencia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    categoria = models.FloatField(blank=True, null=True, db_column='CATEGORIA')
    referencia = models.FloatField(blank=True, null=True, db_column='REFERENCIA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=29)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"REFERENCIA\""


class Referenciaedad(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    edades = models.FloatField(blank=True, null=True, db_column='EDADES')
    referencia = models.FloatField(blank=True, null=True, db_column='REFERENCIA')
    categoria = models.FloatField(blank=True, null=True, db_column='CATEGORIA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=20)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"REFERENCIAEDAD\""


class Registrocirugia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    interv_hosp_amb = models.FloatField(blank=True, null=True, db_column='INTERV_HOSP_AMB')
    fecha_interv = models.DateTimeField(blank=True, null=True, db_column='FECHA_INTERV')
    fecha_ingreso = models.DateTimeField(blank=True, null=True, db_column='FECHA_INGRESO')
    fecha_salida = models.DateTimeField(blank=True, null=True, db_column='FECHA_SALIDA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=200)
    numero_historia = models.CharField(blank=True, null=True, db_column='NUMERO_HISTORIA', max_length=20)
    hospital_elect_emerg = models.FloatField(blank=True, null=True, db_column='HOSPITAL_ELECT_EMERG')
    referido_centro = models.FloatField(blank=True, null=True, db_column='REFERIDO_CENTRO')
    referido_servicio = models.FloatField(blank=True, null=True, db_column='REFERIDO_SERVICIO')
    quirofano = models.FloatField(blank=True, null=True, db_column='QUIROFANO')
    toma_muestra = models.CharField(blank=True, null=True, db_column='TOMA_MUESTRA', max_length=200)
    intervencion_omitida = models.FloatField(blank=True, null=True, db_column='INTERVENCION_OMITIDA')
    otraintervencion_omitida = models.CharField(blank=True, null=True, db_column='OTRAINTERVENCION_OMITIDA', max_length=100)
    causa_egreso = models.FloatField(blank=True, null=True, db_column='CAUSA_EGRESO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"REGISTROCIRUGIA\""


class SismaiRegistroCirugia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hintervencion = models.FloatField(blank=True, null=True, db_column='HINTERVENCION')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=250)
    hinterv_cie10 = models.FloatField(blank=True, null=True, db_column='HINTERV_CIE10')
    hcompli_cie10 = models.FloatField(blank=True, null=True, db_column='HCOMPLI_CIE10')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"REGISTRO_CIRUGIA\""


class RegVacunacion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hactividad = models.FloatField(blank=True, null=True, db_column='HACTIVIDAD')
    hpaciente = models.FloatField(blank=True, null=True, db_column='HPACIENTE')
    hpacientemision = models.FloatField(blank=True, null=True, db_column='HPACIENTEMISION')
    embarazada = models.FloatField(blank=True, null=True, db_column='EMBARAZADA')
    lote = models.CharField(blank=True, null=True, db_column='LOTE', max_length=30)
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    tipoedad2 = models.CharField(blank=True, null=True, db_column='TIPOEDAD2', max_length=1)
    edad2 = models.FloatField(blank=True, null=True, db_column='EDAD2')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    hpac_cond_espe = models.FloatField(blank=True, null=True, db_column='HPAC_COND_ESPE')
    fechavencimiento = models.DateTimeField(blank=True, null=True, db_column='FECHAVENCIMIENTO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"REG_VACUNACION\""


class RelacionComplica(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcomplicacion_prog = models.FloatField(blank=True, null=True, db_column='HCOMPLICACION_PROG')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RELACION_COMPLICA\""


class RelacionProgAnalisis(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hanalisis_lab_prog = models.FloatField(blank=True, null=True, db_column='HANALISIS_LAB_PROG')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RELACION_PROG_ANALISIS\""


class RelacionProgAnteced(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hantecedentes_prog = models.FloatField(blank=True, null=True, db_column='HANTECEDENTES_PROG')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RELACION_PROG_ANTECED\""


class RelacionProgBasesd(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    hbases_diag_prog = models.FloatField(blank=True, null=True, db_column='HBASES_DIAG_PROG')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RELACION_PROG_BASESD\""


class RelacionProgTratam(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    htratamiento_prog = models.FloatField(blank=True, null=True, db_column='HTRATAMIENTO_PROG')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RELACION_PROG_TRATAM\""


class Renglondspcon(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    realizado = models.FloatField(blank=True, null=True, db_column='REALIZADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLONDSPCON\""


class Renglonepi13(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichaepi13 = models.FloatField(blank=True, null=True, db_column='HFICHAEPI13')
    henfermedad = models.FloatField(blank=True, null=True, db_column='HENFERMEDAD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLONEPI13\""


class Renglonepicon(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    casosx = models.FloatField(blank=True, null=True, db_column='CASOSX')
    casosp = models.FloatField(blank=True, null=True, db_column='CASOSP')
    casoss = models.FloatField(blank=True, null=True, db_column='CASOSS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLONEPICON\""


class Renglontele(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    casos = models.FloatField(blank=True, null=True, db_column='CASOS')
    muertes = models.FloatField(blank=True, null=True, db_column='MUERTES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    casoshom = models.FloatField(blank=True, null=True, db_column='CASOSHOM')
    casosmuj = models.FloatField(blank=True, null=True, db_column='CASOSMUJ')
    muerteshom = models.FloatField(blank=True, null=True, db_column='MUERTESHOM')
    muertesmuj = models.FloatField(blank=True, null=True, db_column='MUERTESMUJ')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLONTELE\""


class Renglontelecon(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    edad = models.FloatField(blank=True, null=True, db_column='EDAD')
    casos = models.FloatField(blank=True, null=True, db_column='CASOS')
    muertes = models.FloatField(blank=True, null=True, db_column='MUERTES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    casoshom = models.FloatField(blank=True, null=True, db_column='CASOSHOM')
    casosmuj = models.FloatField(blank=True, null=True, db_column='CASOSMUJ')
    muerteshom = models.FloatField(blank=True, null=True, db_column='MUERTESHOM')
    muertesmuj = models.FloatField(blank=True, null=True, db_column='MUERTESMUJ')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLONTELECON\""


class RenglonCasosmi(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcasosmmi = models.FloatField(blank=True, null=True, db_column='HCASOSMMI')
    hocurrencia = models.FloatField(blank=True, null=True, db_column='HOCURRENCIA')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausa_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSA_CIE10')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    control_prenatal = models.FloatField(blank=True, null=True, db_column='CONTROL_PRENATAL')
    peso = models.FloatField(blank=True, null=True, db_column='PESO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    hcausabas_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSABAS_CIE10')
    hnutricion = models.FloatField(blank=True, null=True, db_column='HNUTRICION')
    estanciahosp = models.FloatField(blank=True, null=True, db_column='ESTANCIAHOSP')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLON_CASOSMI\""


class RenglonCasosmm(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcasosmmi = models.FloatField(blank=True, null=True, db_column='HCASOSMMI')
    hocurrencia = models.FloatField(blank=True, null=True, db_column='HOCURRENCIA')
    hsitio_ocurrencia = models.FloatField(blank=True, null=True, db_column='HSITIO_OCURRENCIA')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcausa_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSA_CIE10')
    edad_gestacional = models.FloatField(blank=True, null=True, db_column='EDAD_GESTACIONAL')
    control_prenatal = models.FloatField(blank=True, null=True, db_column='CONTROL_PRENATAL')
    hformaparto = models.FloatField(blank=True, null=True, db_column='HFORMAPARTO')
    hanexosperiodo = models.FloatField(blank=True, null=True, db_column='HANEXOSPERIODO')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    periodoocurrencia = models.FloatField(blank=True, null=True, db_column='PERIODOOCURRENCIA')
    hcausabas_cie10 = models.FloatField(blank=True, null=True, db_column='HCAUSABAS_CIE10')
    num_partos = models.FloatField(blank=True, null=True, db_column='NUM_PARTOS')
    hijos_nacvivos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACVIVOS')
    hijos_nacmuertos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACMUERTOS')
    hijos_nacabortos = models.FloatField(blank=True, null=True, db_column='HIJOS_NACABORTOS')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLON_CASOSMM\""


class RenglonDsp04(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    actividad = models.FloatField(blank=True, null=True, db_column='ACTIVIDAD')
    realizado = models.FloatField(blank=True, null=True, db_column='REALIZADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLON_DSP04\""


class RenglonEpi15(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    documento = models.FloatField(blank=True, null=True, db_column='DOCUMENTO')
    enfermedad = models.FloatField(blank=True, null=True, db_column='ENFERMEDAD')
    casosx = models.FloatField(blank=True, null=True, db_column='CASOSX')
    casosp = models.FloatField(blank=True, null=True, db_column='CASOSP')
    casoss = models.FloatField(blank=True, null=True, db_column='CASOSS')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLON_EPI15\""


class RenglonResumen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    htipoestable = models.FloatField(blank=True, null=True, db_column='HTIPOESTABLE')
    cant_estable = models.FloatField(blank=True, null=True, db_column='CANT_ESTABLE')
    cant_documento = models.FloatField(blank=True, null=True, db_column='CANT_DOCUMENTO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLON_RESUMEN\""


class RenglonSituacion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    hcodificador = models.FloatField(blank=True, null=True, db_column='HCODIFICADOR')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    cant_casos = models.FloatField(blank=True, null=True, db_column='CANT_CASOS')
    cant_muertes = models.FloatField(blank=True, null=True, db_column='CANT_MUERTES')
    tiposituacion = models.FloatField(blank=True, null=True, db_column='TIPOSITUACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    grave = models.FloatField(blank=True, null=True, db_column='GRAVE')
    inusitado = models.FloatField(blank=True, null=True, db_column='INUSITADO')
    nacional = models.FloatField(blank=True, null=True, db_column='NACIONAL')
    internac = models.FloatField(blank=True, null=True, db_column='INTERNAC')
    fechainicio = models.DateTimeField(blank=True, null=True, db_column='FECHAINICIO')
    fechafin = models.DateTimeField(blank=True, null=True, db_column='FECHAFIN')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RENGLON_SITUACION\""


class Reportesanuario(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.FloatField(blank=True, null=True, db_column='CODIGO')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=200)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"REPORTESANUARIO\""


class ResultadosProg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hprograma = models.FloatField(blank=True, null=True, db_column='HPROGRAMA')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=30)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RESULTADOS_PROG\""


class Resumen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hcategoria = models.FloatField(blank=True, null=True, db_column='HCATEGORIA')
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    situacion_especial = models.CharField(blank=True, null=True, db_column='SITUACION_ESPECIAL', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RESUMEN\""


class ResumenD(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    htipo = models.FloatField(blank=True, null=True, db_column='HTIPO')
    total = models.FloatField(blank=True, null=True, db_column='TOTAL')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=20)
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    archivo = models.CharField(blank=True, null=True, db_column='ARCHIVO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RESUMEN_D\""


class ResumenNegativa(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hdocumento = models.FloatField(blank=True, null=True, db_column='HDOCUMENTO')
    notifica = models.FloatField(blank=True, null=True, db_column='NOTIFICA')
    hcausanegativa = models.FloatField(blank=True, null=True, db_column='HCAUSANEGATIVA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fecha_operacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_OPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"RESUMEN_NEGATIVA\""


class Rolmedicointerv(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ROLMEDICOINTERV\""


class RTransferencia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    htipo = models.FloatField(blank=True, null=True, db_column='HTIPO')
    total = models.FloatField(blank=True, null=True, db_column='TOTAL')
    fecha = models.DateTimeField(blank=True, null=True, db_column='FECHA')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=20)
    status = models.FloatField(blank=True, null=True, db_column='STATUS')
    archivo = models.CharField(blank=True, null=True, db_column='ARCHIVO', max_length=20)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"R_TRANSFERENCIA\""


class SeguimientoCardiovascular(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    hlocalidad_seg = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    evaluacion = models.CharField(blank=True, null=True, db_column='EVALUACION', max_length=4000)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaevolucion = models.DateTimeField(blank=True, null=True, db_column='FECHAEVOLUCION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SEGUIMIENTO_CARDIOVASCULAR\""


class SeguimientoDiabetes(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hcentroasistencial = models.FloatField(blank=True, null=True, db_column='HCENTROASISTENCIAL')
    fechaevolucion = models.DateTimeField(blank=True, null=True, db_column='FECHAEVOLUCION')
    hclasif_consultante_prog = models.FloatField(blank=True, null=True, db_column='HCLASIF_CONSULTANTE_PROG')
    numsecciones = models.FloatField(blank=True, null=True, db_column='NUMSECCIONES')
    imc = models.FloatField(blank=True, null=True, db_column='IMC')
    glicemia = models.FloatField(blank=True, null=True, db_column='GLICEMIA')
    tensionarterial_alta = models.FloatField(blank=True, null=True, db_column='TENSIONARTERIAL_ALTA')
    tensionarterial_baja = models.FloatField(blank=True, null=True, db_column='TENSIONARTERIAL_BAJA')
    glicosilada = models.FloatField(blank=True, null=True, db_column='GLICOSILADA')
    colesterol = models.FloatField(blank=True, null=True, db_column='COLESTEROL')
    microalbum = models.FloatField(blank=True, null=True, db_column='MICROALBUM')
    creatinina = models.FloatField(blank=True, null=True, db_column='CREATININA')
    triglicerido = models.FloatField(blank=True, null=True, db_column='TRIGLICERIDO')
    ldl = models.FloatField(blank=True, null=True, db_column='LDL')
    hdl = models.FloatField(blank=True, null=True, db_column='HDL')
    depcreatinina = models.FloatField(blank=True, null=True, db_column='DEPCREATININA')
    fondodeojo = models.FloatField(blank=True, null=True, db_column='FONDODEOJO')
    causashospitalarias = models.CharField(blank=True, null=True, db_column='CAUSASHOSPITALARIAS', max_length=250)
    sesioneducativa = models.CharField(blank=True, null=True, db_column='SESIONEDUCATIVA', max_length=100)
    secciones = models.FloatField(blank=True, null=True, db_column='SECCIONES')
    egreso = models.FloatField(blank=True, null=True, db_column='EGRESO')
    condicionegreso = models.FloatField(blank=True, null=True, db_column='CONDICIONEGRESO')
    hlocalidad_tranf = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_TRANF')
    hlocalidad_seg = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    fechatransferencia = models.DateTimeField(blank=True, null=True, db_column='FECHATRANSFERENCIA')
    causademuerte = models.CharField(blank=True, null=True, db_column='CAUSADEMUERTE', max_length=1)
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    fluoro = models.FloatField(blank=True, null=True, db_column='FLUORO')
    evaluacion = models.CharField(blank=True, null=True, db_column='EVALUACION', max_length=4000)
    hespecialidad = models.FloatField(blank=True, null=True, db_column='HESPECIALIDAD')
    evaluacion2 = models.CharField(blank=True, null=True, db_column='EVALUACION2', max_length=4000)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SEGUIMIENTO_DIABETES\""


class SegEvolPaciente(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    fecha_seg = models.DateTimeField(blank=True, null=True, db_column='FECHA_SEG')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    hlocalidad_seg = models.BigIntegerField(blank=True, null=True, db_column='HLOCALIDAD_SEG')
    fecha_result_seg = models.DateTimeField(blank=True, null=True, db_column='FECHA_RESULT_SEG')
    otros_tratam_seg = models.CharField(blank=True, null=True, db_column='OTROS_TRATAM_SEG', max_length=250)
    complicacion_seg = models.CharField(blank=True, null=True, db_column='COMPLICACION_SEG', max_length=250)
    observacion_seg = models.CharField(blank=True, null=True, db_column='OBSERVACION_SEG', max_length=4000)
    hevolucion = models.FloatField(blank=True, null=True, db_column='HEVOLUCION')
    hpersonalmedico = models.FloatField(blank=True, null=True, db_column='HPERSONALMEDICO')
    hcargo = models.FloatField(blank=True, null=True, db_column='HCARGO')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hresultados_prog = models.FloatField(blank=True, null=True, db_column='HRESULTADOS_PROG')
    h_prog_m_ch_e = models.FloatField(blank=True, null=True, db_column='H_PROG_M_CH_E')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SEG_EVOL_PACIENTE\""


class Semanapesotalla(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    semanagestacion = models.FloatField(blank=True, null=True, db_column='SEMANAGESTACION')
    peso1 = models.FloatField(blank=True, null=True, db_column='PESO1')
    peso2 = models.FloatField(blank=True, null=True, db_column='PESO2')
    talla1 = models.FloatField(blank=True, null=True, db_column='TALLA1')
    talla2 = models.FloatField(blank=True, null=True, db_column='TALLA2')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SEMANAPESOTALLA\""


class Semanas(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    mes = models.FloatField(blank=True, null=True, db_column='MES')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    semana = models.FloatField(blank=True, null=True, db_column='SEMANA')
    fechainicial = models.DateTimeField(blank=True, null=True, db_column='FECHAINICIAL')
    fechafinal = models.DateTimeField(blank=True, null=True, db_column='FECHAFINAL')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SEMANAS\""


class Sexo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SEXO\""


class SignosSintomas(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_basesd = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_BASESD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SIGNOS_SINTOMAS\""


class SignosSintomasSeg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_basesd = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_BASESD')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SIGNOS_SINTOMAS_SEG\""


class Sitioparto(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SITIOPARTO\""


class SitioAccidente(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    hpadre = models.FloatField(blank=True, null=True, db_column='HPADRE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SITIO_ACCIDENTE\""


class SitioM(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SITIO_M\""


class SitioMuerte(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SITIO_MUERTE\""


class SitioOcurrencia(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SITIO_OCURRENCIA\""


class Situacionaccidente(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SITUACIONACCIDENTE\""


class SituacionEspecial(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hresumen = models.FloatField(blank=True, null=True, db_column='HRESUMEN')
    htipoevento = models.FloatField(blank=True, null=True, db_column='HTIPOEVENTO')
    hlocalidad = models.FloatField(blank=True, null=True, db_column='HLOCALIDAD')
    cant_casos = models.FloatField(blank=True, null=True, db_column='CANT_CASOS')
    cant_muertes = models.FloatField(blank=True, null=True, db_column='CANT_MUERTES')
    medidatomada = models.CharField(blank=True, null=True, db_column='MEDIDATOMADA', max_length=200)
    descripcionevento = models.CharField(blank=True, null=True, db_column='DESCRIPCIONEVENTO', max_length=200)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"SITUACION_ESPECIAL\""


class Tablasis(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    creator = models.CharField(blank=True, null=True, db_column='CREATOR', max_length=12)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=30)
    temporal = models.CharField(blank=True, null=True, db_column='TEMPORAL', max_length=30)
    tran = models.IntegerField(blank=True, null=True, db_column='TRAN')
    resi = models.IntegerField(blank=True, null=True, db_column='RESI')
    nata = models.IntegerField(blank=True, null=True, db_column='NATA')
    mort = models.IntegerField(blank=True, null=True, db_column='MORT')
    docu = models.IntegerField(blank=True, null=True, db_column='DOCU')
    onco = models.IntegerField(blank=True, null=True, db_column='ONCO')
    mala = models.IntegerField(blank=True, null=True, db_column='MALA')
    diab = models.IntegerField(blank=True, null=True, db_column='DIAB')
    card = models.IntegerField(blank=True, null=True, db_column='CARD')
    ciru = models.IntegerField(blank=True, null=True, db_column='CIRU')
    acci = models.IntegerField(blank=True, null=True, db_column='ACCI')
    vacu = models.IntegerField(blank=True, null=True, db_column='VACU')
    codi = models.IntegerField(blank=True, null=True, db_column='CODI')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TABLASIS\""


class TableConfig(models.Model):
    tabla = models.CharField(blank=True, null=True, primary_key=True, db_column='TABLA', max_length=33)
    objectcount = models.FloatField(blank=True, null=True, db_column='OBJECTCOUNT')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TABLE_CONFIG\""


class Temponombre(models.Model):
    nombre = models.CharField(blank=True, null=True, primary_key=True, db_column='NOMBRE', max_length=100)
    masculino = models.FloatField(blank=True, null=True, db_column='MASCULINO')
    femenino = models.FloatField(blank=True, null=True, db_column='FEMENINO')
    hermafrodita = models.FloatField(blank=True, null=True, db_column='HERMAFRODITA')
    ignorado = models.FloatField(blank=True, null=True, db_column='IGNORADO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TEMPONOMBRE\""


class Temporal(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TEMPORAL\""


class Tipocomplicacion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPOCOMPLICACION\""


class Tipodengue(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPODENGUE\""


class Tipodocumento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=100)
    padre = models.CharField(blank=True, null=True, db_column='PADRE', max_length=5)
    categoria = models.FloatField(blank=True, null=True, db_column='CATEGORIA')
    serializado = models.CharField(blank=True, null=True, db_column='SERIALIZADO', max_length=5)
    tipocontrolserial = models.CharField(blank=True, null=True, db_column='TIPOCONTROLSERIAL', max_length=5)
    ultimoserial = models.CharField(blank=True, null=True, db_column='ULTIMOSERIAL', max_length=15)
    tipoperiodo = models.FloatField(blank=True, null=True, db_column='TIPOPERIODO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPODOCUMENTO\""


class Tipoestable(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=15)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=250)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    hnivel = models.FloatField(blank=True, null=True, db_column='HNIVEL')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPOESTABLE\""


class Tipoevento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=100)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPOEVENTO\""


class Tipoexamen(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=25)
    autorizado = models.CharField(blank=True, null=True, db_column='AUTORIZADO', max_length=2)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPOEXAMEN\""


class Tipolocal(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    padre = models.FloatField(blank=True, null=True, db_column='PADRE')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=200)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPOLOCAL\""


class Tipoperiodo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=50)
    maxvalor = models.IntegerField(blank=True, null=True, db_column='MAXVALOR')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPOPERIODO\""


class Tiposituacion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=50)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPOSITUACION\""


class TipoAccidente(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPO_ACCIDENTE\""


class TipoExposicion(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPO_EXPOSICION\""


class TipoHecho(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPO_HECHO\""


class TipoM(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=250)
    login = models.CharField(blank=True, null=True, db_column='LOGIN', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPO_M\""


class TipoObjeto(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=3)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPO_OBJETO\""


class TipoVehiculo(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TIPO_VEHICULO\""


class Tpaciente(models.Model):
    paciente = models.FloatField(blank=True, null=True, primary_key=True, db_column='PACIENTE')
    fechamuestra = models.DateTimeField(blank=True, null=True, db_column='FECHAMUESTRA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TPACIENTE\""


class TransmisionSida(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=20)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    categoria = models.FloatField(blank=True, null=True, db_column='CATEGORIA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TRANSMISION_SIDA\""


class Tratamiento(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    hseg_evol_paciente = models.FloatField(blank=True, null=True, db_column='HSEG_EVOL_PACIENTE')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    hprog_m_ch_e = models.FloatField(blank=True, null=True, db_column='HPROG_M_CH_E')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TRATAMIENTO\""


class TratamientoProg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=10)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=40)
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TRATAMIENTO_PROG\""


class TratamientoSeg(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TRATAMIENTO_SEG\""


class TratamientoSegcardio(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    hrelacion_prog_tratam = models.FloatField(blank=True, null=True, db_column='HRELACION_PROG_TRATAM')
    nro_unidades = models.FloatField(blank=True, null=True, db_column='NRO_UNIDADES')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TRATAMIENTO_SEGCARDIO\""


class TratamientoTuberculosis(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hfichas_epidemiologicas = models.FloatField(blank=True, null=True, db_column='HFICHAS_EPIDEMIOLOGICAS')
    iniciotra = models.FloatField(blank=True, null=True, db_column='INICIOTRA')
    fechainiciotra = models.DateTimeField(blank=True, null=True, db_column='FECHAINICIOTRA')
    mesestrat_i = models.FloatField(blank=True, null=True, db_column='MESESTRAT_I')
    mesestrat_m = models.FloatField(blank=True, null=True, db_column='MESESTRAT_M')
    administraciontra = models.FloatField(blank=True, null=True, db_column='ADMINISTRACIONTRA')
    notaes = models.CharField(blank=True, null=True, db_column='NOTAES', max_length=100)
    resultadobact_1 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_1')
    resultadobact_2 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_2')
    resultadobact_3 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_3')
    resultadobact_4 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_4')
    resultadobact_5 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_5')
    resultadobact_6 = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_6')
    resultadobact_f = models.FloatField(blank=True, null=True, db_column='RESULTADOBACT_F')
    egreso = models.FloatField(blank=True, null=True, db_column='EGRESO')
    reingreso = models.FloatField(blank=True, null=True, db_column='REINGRESO')
    fechaegreso = models.DateTimeField(blank=True, null=True, db_column='FECHAEGRESO')
    fechareingreso = models.DateTimeField(blank=True, null=True, db_column='FECHAREINGRESO')
    hcondicionfinalegreso = models.FloatField(blank=True, null=True, db_column='HCONDICIONFINALEGRESO')
    hcondicionfinalreingreso = models.IntegerField(blank=True, null=True, db_column='HCONDICIONFINALREINGRESO')
    muertetb = models.FloatField(blank=True, null=True, db_column='MUERTETB')
    muerteotracausa = models.FloatField(blank=True, null=True, db_column='MUERTEOTRACAUSA')
    semana_abandono = models.FloatField(blank=True, null=True, db_column='SEMANA_ABANDONO')
    lugartransferencia = models.FloatField(blank=True, null=True, db_column='LUGARTRANSFERENCIA')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=2000)
    tomasprogramadas = models.FloatField(blank=True, null=True, db_column='TOMASPROGRAMADAS')
    tomascumplidas = models.FloatField(blank=True, null=True, db_column='TOMASCUMPLIDAS')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=10)
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TRATAMIENTO_TUBERCULOSIS\""


class Trnacidos(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    hcertificado = models.FloatField(blank=True, null=True, db_column='HCERTIFICADO')
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    nombres = models.CharField(blank=True, null=True, db_column='NOMBRES', max_length=100)
    apellidos = models.CharField(blank=True, null=True, db_column='APELLIDOS', max_length=100)
    pasaporte = models.CharField(blank=True, null=True, db_column='PASAPORTE', max_length=20)
    direccion = models.CharField(blank=True, null=True, db_column='DIRECCION', max_length=100)
    hresidencia = models.FloatField(blank=True, null=True, db_column='HRESIDENCIA')
    historiaclinica = models.CharField(blank=True, null=True, db_column='HISTORIACLINICA', max_length=20)
    phistoriaclinica = models.CharField(blank=True, null=True, db_column='PHISTORIACLINICA', max_length=20)
    fechanacimiento = models.DateTimeField(blank=True, null=True, db_column='FECHANACIMIENTO')
    edadm = models.FloatField(blank=True, null=True, db_column='EDADM')
    edadp = models.FloatField(blank=True, null=True, db_column='EDADP')
    estadocivil = models.FloatField(blank=True, null=True, db_column='ESTADOCIVIL')
    annosmatrimonio = models.FloatField(blank=True, null=True, db_column='ANNOSMATRIMONIO')
    nacvivos = models.FloatField(blank=True, null=True, db_column='NACVIVOS')
    nacionm = models.FloatField(blank=True, null=True, db_column='NACIONM')
    nacionp = models.FloatField(blank=True, null=True, db_column='NACIONP')
    hentidam = models.FloatField(blank=True, null=True, db_column='HENTIDAM')
    hentidap = models.FloatField(blank=True, null=True, db_column='HENTIDAP')
    hpaism = models.FloatField(blank=True, null=True, db_column='HPAISM')
    hpaisp = models.FloatField(blank=True, null=True, db_column='HPAISP')
    actualvivos = models.FloatField(blank=True, null=True, db_column='ACTUALVIVOS')
    leerescribir = models.FloatField(blank=True, null=True, db_column='LEERESCRIBIR')
    nacvivosfallec = models.FloatField(blank=True, null=True, db_column='NACVIVOSFALLEC')
    muertesfetales = models.FloatField(blank=True, null=True, db_column='MUERTESFETALES')
    hultimogrado = models.FloatField(blank=True, null=True, db_column='HULTIMOGRADO')
    profesion = models.FloatField(blank=True, null=True, db_column='PROFESION')
    controlprenatal = models.FloatField(blank=True, null=True, db_column='CONTROLPRENATAL')
    telefonom = models.CharField(blank=True, null=True, db_column='TELEFONOM', max_length=20)
    ptelefono = models.CharField(blank=True, null=True, db_column='PTELEFONO', max_length=20)
    ocupacion = models.FloatField(blank=True, null=True, db_column='OCUPACION')
    pcedula = models.CharField(blank=True, null=True, db_column='PCEDULA', max_length=10)
    pnombres = models.CharField(blank=True, null=True, db_column='PNOMBRES', max_length=100)
    ppasaporte = models.CharField(blank=True, null=True, db_column='PPASAPORTE', max_length=20)
    pdireccion = models.CharField(blank=True, null=True, db_column='PDIRECCION', max_length=100)
    hpresidencia = models.FloatField(blank=True, null=True, db_column='HPRESIDENCIA')
    pfechanacimiento = models.DateTimeField(blank=True, null=True, db_column='PFECHANACIMIENTO')
    pestadocivil = models.FloatField(blank=True, null=True, db_column='PESTADOCIVIL')
    pleerescribir = models.FloatField(blank=True, null=True, db_column='PLEERESCRIBIR')
    hpultimogrado = models.FloatField(blank=True, null=True, db_column='HPULTIMOGRADO')
    pprofesion = models.FloatField(blank=True, null=True, db_column='PPROFESION')
    observacion = models.CharField(blank=True, null=True, db_column='OBSERVACION', max_length=100)
    pocupacion = models.FloatField(blank=True, null=True, db_column='POCUPACION')
    fechaoperacion = models.DateTimeField(blank=True, null=True, db_column='FECHAOPERACION')
    usuario = models.CharField(blank=True, null=True, db_column='USUARIO', max_length=15)
    nacionalidap = models.FloatField(blank=True, null=True, db_column='NACIONALIDAP')
    nacionalidam = models.FloatField(blank=True, null=True, db_column='NACIONALIDAM')
    unionmat = models.FloatField(blank=True, null=True, db_column='UNIONMAT')
    nroconsultaspre = models.FloatField(blank=True, null=True, db_column='NROCONSULTASPRE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"TRNACIDOS\""


class TDoc(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    anno = models.FloatField(blank=True, null=True, db_column='ANNO')
    periodo = models.FloatField(blank=True, null=True, db_column='PERIODO')
    tipo = models.FloatField(blank=True, null=True, db_column='TIPO')
    horigen = models.FloatField(blank=True, null=True, db_column='HORIGEN')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"T_DOC\""


class UbicacionDiag(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=5)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"UBICACION_DIAG\""


class Ultimogrado(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=2)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=150)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"ULTIMOGRADO\""


class Usuarios(models.Model):
    login = models.CharField(blank=True, null=True, primary_key=True, db_column='LOGIN', max_length=10)
    password = models.CharField(blank=True, null=True, db_column='PASSWORD', max_length=12)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=40)
    cedula = models.CharField(blank=True, null=True, db_column='CEDULA', max_length=10)
    cargo = models.CharField(blank=True, null=True, db_column='CARGO', max_length=150)
    jerarquia = models.CharField(blank=True, null=True, db_column='JERARQUIA', max_length=2)
    creado = models.CharField(blank=True, null=True, db_column='CREADO', max_length=10)
    fec_crea = models.DateTimeField(blank=True, null=True, db_column='FEC_CREA')
    fec_ent = models.DateTimeField(blank=True, null=True, db_column='FEC_ENT')
    id = models.FloatField(blank=True, null=True, db_column='ID')
    estatus = models.FloatField(blank=True, null=True, db_column='ESTATUS')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    morbilidad = models.FloatField(blank=True, null=True, db_column='MORBILIDAD')
    natalidad = models.FloatField(blank=True, null=True, db_column='NATALIDAD')
    mortalidad = models.FloatField(blank=True, null=True, db_column='MORTALIDAD')
    oncologia = models.FloatField(blank=True, null=True, db_column='ONCOLOGIA')
    fichas = models.FloatField(blank=True, null=True, db_column='FICHAS')
    accidente = models.FloatField(blank=True, null=True, db_column='ACCIDENTE')
    cirugia = models.FloatField(blank=True, null=True, db_column='CIRUGIA')
    vacunacion = models.FloatField(blank=True, null=True, db_column='VACUNACION')
    transferencia = models.FloatField(blank=True, null=True, db_column='TRANSFERENCIA')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"USUARIOS\""


class UsuarioEstab(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    husuarioweb = models.FloatField(blank=True, null=True, db_column='HUSUARIOWEB')
    hestablecimiento = models.FloatField(blank=True, null=True, db_column='HESTABLECIMIENTO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"USUARIO_ESTAB\""


class Validarcie10(models.Model):
    id = models.BigIntegerField(blank=True, null=True, primary_key=True, db_column='ID')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=7)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=200)
    asterisco = models.CharField(blank=True, null=True, db_column='ASTERISCO', max_length=1)
    limitadasexo = models.CharField(blank=True, null=True, db_column='LIMITADASEXO', max_length=1)
    inferioredad = models.CharField(blank=True, null=True, db_column='INFERIOREDAD', max_length=5)
    superioredad = models.CharField(blank=True, null=True, db_column='SUPERIOREDAD', max_length=5)
    trivial = models.CharField(blank=True, null=True, db_column='TRIVIAL', max_length=1)
    nocausabasica = models.CharField(blank=True, null=True, db_column='NOCAUSABASICA', max_length=1)
    fetal = models.CharField(blank=True, null=True, db_column='FETAL', max_length=1)
    causaops = models.CharField(blank=True, null=True, db_column='CAUSAOPS', max_length=1)
    opciona = models.CharField(blank=True, null=True, db_column='OPCIONA', max_length=1)
    opcionb = models.CharField(blank=True, null=True, db_column='OPCIONB', max_length=1)
    opcionc = models.CharField(blank=True, null=True, db_column='OPCIONC', max_length=1)
    sos_materna = models.FloatField(blank=True, null=True, db_column='SOS_MATERNA')
    capitulo = models.CharField(blank=True, null=True, db_column='CAPITULO', max_length=2)
    lista1 = models.CharField(blank=True, null=True, db_column='LISTA1', max_length=4)
    lista2 = models.CharField(blank=True, null=True, db_column='LISTA2', max_length=4)
    lista3 = models.CharField(blank=True, null=True, db_column='LISTA3', max_length=4)
    lista4 = models.CharField(blank=True, null=True, db_column='LISTA4', max_length=4)
    listagbd = models.FloatField(blank=True, null=True, db_column='LISTAGBD')
    listabecker = models.FloatField(blank=True, null=True, db_column='LISTABECKER')
    lista667 = models.FloatField(blank=True, null=True, db_column='LISTA667')
    listagbdsis = models.CharField(blank=True, null=True, db_column='LISTAGBDSIS', max_length=5)
    morbilidad = models.CharField(blank=True, null=True, db_column='MORBILIDAD', max_length=1)
    c_fre = models.CharField(blank=True, null=True, db_column='C_FRE', max_length=2)
    c_edad = models.CharField(blank=True, null=True, db_column='C_EDAD', max_length=2)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"VALIDARCIE10\""


class VLista3(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    numero = models.CharField(blank=True, null=True, db_column='NUMERO', max_length=10)
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=200)
    codigocie10 = models.CharField(blank=True, null=True, db_column='CODIGOCIE10', max_length=150)
    hpadre = models.FloatField(blank=True, null=True, db_column='HPADRE')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"V_LISTA3\""


class VMuertematerna(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=110)
    codigocie10 = models.CharField(blank=True, null=True, db_column='CODIGOCIE10', max_length=60)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"V_MUERTEMATERNA\""


class VNacimiento(models.Model):
    id = models.BigIntegerField(blank=True, null=True, primary_key=True, db_column='ID')
    htipo = models.IntegerField(blank=True, null=True, db_column='HTIPO')
    codigo = models.CharField(blank=True, null=True, db_column='CODIGO', max_length=30)
    nombre = models.CharField(blank=True, null=True, db_column='NOMBRE', max_length=50)
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"V_NACIMIENTO\""


class XCantHab(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=50)
    numero = models.FloatField(blank=True, null=True, db_column='NUMERO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"X_CANT_HAB\""


class XCausasMuertes(models.Model):
    id = models.FloatField(blank=True, null=True, primary_key=True, db_column='ID')
    descripcion = models.CharField(blank=True, null=True, db_column='DESCRIPCION', max_length=50)
    numero = models.FloatField(blank=True, null=True, db_column='NUMERO')
    # EL LEGACY NO DEFINE PK en esta tabla: la primera columna es PK nominal (solo lectura).

    class Meta:
        app_label = "legacy"
        managed = False
        db_table = "\"sismai\".\"X_CAUSAS_MUERTES\""


__all__ = [
    "Errores",
    "Erroresb",
    "Erroresc",
    "ErroresLabo",
    "ErroresResi",
    "ErroresSinc",
    "Evento2",
    "Eventos",
    "EventosDblink",
    "TAccilabo",
    "TAcctrans",
    "TAlabcard",
    "TAnalabor",
    "TAntefact",
    "TAuditoria",
    "TBiopseg",
    "TBiopsiat",
    "TCasosmm",
    "TCasosmmi",
    "TCaummedi",
    "TCertmort",
    "TCertnaci",
    "TComaguda",
    "TComcroni",
    "TComdisca",
    "TCompcard",
    "TComplica",
    "TComquir",
    "TComsegim",
    "TDiagasoc",
    "TDocudeng",
    "TDocument",
    "TDocusosp",
    "TEstable",
    "TEventos",
    "TFdolorto",
    "TFichaacc",
    "TFichasep",
    "THechosvi",
    "TIntquir",
    "TLugarvis",
    "TMadrnaci",
    "TMbased",
    "TMcaumorb",
    "TMcausmre",
    "TMhojarep",
    "TMortanul",
    "TMortcaus",
    "TMortfeta",
    "TMortmadr",
    "TMortviol",
    "TMrespa",
    "TNotdsp04",
    "TOrggeog",
    "TOtrotrat",
    "TPacconde",
    "TPaciend",
    "TPacienfe",
    "TPacientt",
    "TPacimisi",
    "TPerquir",
    "TPersmedi",
    "TPobesta",
    "TProdiabe",
    "TProgcard",
    "TProgmche",
    "TProgtube",
    "TProttrom",
    "TPrvihsid",
    "TRcasosmi",
    "TRcasosmm",
    "TRegciru",
    "TRegvacu",
    "TRendsp04",
    "TRenepi15",
    "TRengres",
    "TRengsit",
    "TRengtele",
    "TResumen",
    "TRnacanul",
    "TRnacnaci",
    "TSegdiabe",
    "TSegevolp",
    "TSegucard",
    "TSignsint",
    "TSigsinse",
    "TSituespe",
    "TTrasegim",
    "TTratamie",
    "TTratuber",
    "TTsegcard",
    "TUsuarios",
    "LegacyTAccilabo",
    "LegacyTAcctrans",
    "LegacyTAlabcard",
    "LegacyTAnalabor",
    "LegacyTAntefact",
    "LegacyTAuditoria",
    "LegacyTBiopseg",
    "LegacyTBiopsiat",
    "LegacyTCasosmm",
    "LegacyTCasosmmi",
    "LegacyTCaummedi",
    "LegacyTCertmort",
    "LegacyTComaguda",
    "LegacyTComcroni",
    "LegacyTComdisca",
    "LegacyTCompcard",
    "LegacyTComplica",
    "LegacyTComquir",
    "LegacyTComsegim",
    "LegacyTDiagasoc",
    "LegacyTDocudeng",
    "LegacyTDocument",
    "LegacyTDocusosp",
    "LegacyTEstable",
    "LegacyTEventos",
    "LegacyTFdolorto",
    "LegacyTFichaacc",
    "LegacyTFichasep",
    "LegacyTHechosvi",
    "LegacyTIntquir",
    "LegacyTLugarvis",
    "LegacyTMadrnaci",
    "LegacyTMbased",
    "LegacyTMcaumorb",
    "LegacyTMcausmre",
    "LegacyTMhojarep",
    "LegacyTMortanul",
    "LegacyTMortcaus",
    "LegacyTMortfeta",
    "LegacyTMortmadr",
    "LegacyTMortviol",
    "LegacyTMrespa",
    "LegacyTNotdsp04",
    "LegacyTOrggeog",
    "LegacyTOtrotrat",
    "LegacyTPacconde",
    "LegacyTPaciend",
    "LegacyTPacienfe",
    "LegacyTPacientt",
    "LegacyTPacimisi",
    "LegacyTPerquir",
    "LegacyTPersmedi",
    "LegacyTPobesta",
    "LegacyTProdiabe",
    "LegacyTProgcard",
    "LegacyTProgmche",
    "LegacyTProgtube",
    "LegacyTProttrom",
    "LegacyTPrvihsid",
    "LegacyTRcasosmi",
    "LegacyTRcasosmm",
    "LegacyTRegciru",
    "LegacyTRegvacu",
    "LegacyTRendsp04",
    "LegacyTRenepi15",
    "LegacyTRengres",
    "LegacyTRengsit",
    "LegacyTRengtele",
    "LegacyTResumen",
    "LegacyTRnacanul",
    "LegacyTRnacnaci",
    "LegacyTSegdiabe",
    "LegacyTSegevolp",
    "LegacyTSegucard",
    "LegacyTSignsint",
    "LegacyTSigsinse",
    "LegacyTSituespe",
    "LegacyTTrasegim",
    "LegacyTTratamie",
    "LegacyTTratuber",
    "LegacyTTsegcard",
    "LegacyTUsuarios",
    "Accidentelaboral",
    "AccTransito",
    "Actividad",
    "Actividadcomun",
    "ActividadOsp",
    "ActividadOsplan",
    "Albergue",
    "AnalisisLaboratorio",
    "AnalisisLaboratorioCardio",
    "AnalisisLabProg",
    "Anatomia",
    "AnexosPeriodo",
    "AntecedentesProg",
    "AntecedFactRiesgo",
    "Anuario01",
    "Anuario02",
    "Anuario03",
    "Anuario04",
    "Anuario05",
    "Anuario06",
    "Asic",
    "Bacteriologia",
    "BasesDiagProg",
    "Biopsiaspaciente",
    "Biopsiaspacienteseg",
    "BiopsiasError",
    "Biopsiatra",
    "Cambios",
    "Cambioscirugia",
    "Cargo",
    "Casosmm",
    "CasosMmi",
    "Categoria",
    "CategoriaCie10",
    "CategoriaDoc",
    "Causa",
    "Causaanulacion",
    "CausaM",
    "CausaMmedico",
    "CausaMorbosas",
    "CausaMRepa",
    "Certificado",
    "CertiMadreM",
    "Certnacimiento",
    "Cheqesquema",
    "Cie10",
    "Citologiasaexamen",
    "Citologiasanormal",
    "Clasificador",
    "ClasifConsultanteProg",
    "Codificador",
    "CodificadorEdad",
    "CodifCie10",
    "Complicacionaguda",
    "Complicacioncardiovascular",
    "Complicacioncronica",
    "Complicaciondisca",
    "Complicaciones",
    "ComplicacionesSeg",
    "Complicacionquirurgica",
    "ComplicacionProg",
    "Condicion",
    "Condicioncaso",
    "Condicionespecial",
    "CondicionIngresoMalaria",
    "Configuracion",
    "Conyugal",
    "DependenciaAdm",
    "Destinocuerpo",
    "Diagnostico",
    "DiagnosticosAsoc",
    "Documento",
    "Documentocons",
    "DocumentoDengue",
    "DocControl",
    "DocSospecha",
    "DondeRealizoPai",
    "Duracionembarazo",
    "Edades",
    "EfectuoHecho",
    "Egresos",
    "SismaiErrores",
    "ErroresAnuario",
    "SismaiErroresLabo",
    "SismaiErroresResi",
    "SismaiErroresSinc",
    "Especialidad",
    "Establecimiento",
    "EstablecimientoMaestra",
    "Estadisticas",
    "Etnia",
    "SismaiEventos",
    "EventosLabo",
    "EventosResi",
    "Evolucion",
    "Fallalectura",
    "Fichadeldolor",
    "Fichadolortoracico",
    "Fichaepi13",
    "FichasEpidemiologicas",
    "FichaAccidente",
    "FinalTratamiento",
    "Formaparto",
    "Gaprivilegies",
    "GrPoblacional",
    "HechosViolentos",
    "Histdoc",
    "HistoricoIds",
    "HistCodificador",
    "Hojareparo",
    "HorAmbulat",
    "InformeEpi",
    "InstitucionFormadora",
    "Intervencion",
    "Intervencionquirurgica",
    "IntervencionOmitida",
    "Laboratorios",
    "LiquidoConta",
    "Localidadestab",
    "Localizacionpulmon",
    "LugaresVisitados",
    "Lugarsuceso",
    "Medicofirmante",
    "Mision",
    "MonitorBasededatos",
    "MonitorRespaldo",
    "MorAnulados",
    "MFetal",
    "MMadre",
    "MRelaparto",
    "MViolenta",
    "NacAnulados",
    "NacAsistencia",
    "NacMadre",
    "NacRnacido",
    "NacTipoparto",
    "NacTiporeg",
    "Nivel",
    "NotasDsp04",
    "Notificantes",
    "NumeroBd",
    "Nutricion",
    "Ocupacion",
    "Ocupasivigila",
    "OpcionCertnacimiento",
    "OrgGeografica",
    "Otrostratamientos",
    "Paciente",
    "Pacientesinexamen",
    "PacienteCondEspe",
    "PacienteD",
    "PacienteDiabetes",
    "PacienteError",
    "PacienteExamen",
    "PacienteFichaEpi",
    "PacienteMision",
    "Pais",
    "Personalmedico",
    "Personalquirurgico",
    "Personalsalud",
    "PesonalsaludPostgrados",
    "PobEstab",
    "PosConfig",
    "Presenciaembarazo",
    "Profesion",
    "Programaestablec",
    "ProgCardiovascular",
    "ProgComunitario",
    "ProgDiabetes",
    "ProgDiabeTemp",
    "ProgMalChagEsq",
    "ProgTuberculosis",
    "ProgVihSida",
    "Protocolotrombolisis",
    "Quirofano",
    "Referencia",
    "Referenciaedad",
    "Registrocirugia",
    "SismaiRegistroCirugia",
    "RegVacunacion",
    "RelacionComplica",
    "RelacionProgAnalisis",
    "RelacionProgAnteced",
    "RelacionProgBasesd",
    "RelacionProgTratam",
    "Renglondspcon",
    "Renglonepi13",
    "Renglonepicon",
    "Renglontele",
    "Renglontelecon",
    "RenglonCasosmi",
    "RenglonCasosmm",
    "RenglonDsp04",
    "RenglonEpi15",
    "RenglonResumen",
    "RenglonSituacion",
    "Reportesanuario",
    "ResultadosProg",
    "Resumen",
    "ResumenD",
    "ResumenNegativa",
    "Rolmedicointerv",
    "RTransferencia",
    "SeguimientoCardiovascular",
    "SeguimientoDiabetes",
    "SegEvolPaciente",
    "Semanapesotalla",
    "Semanas",
    "Sexo",
    "SignosSintomas",
    "SignosSintomasSeg",
    "Sitioparto",
    "SitioAccidente",
    "SitioM",
    "SitioMuerte",
    "SitioOcurrencia",
    "Situacionaccidente",
    "SituacionEspecial",
    "Tablasis",
    "TableConfig",
    "Temponombre",
    "Temporal",
    "Tipocomplicacion",
    "Tipodengue",
    "Tipodocumento",
    "Tipoestable",
    "Tipoevento",
    "Tipoexamen",
    "Tipolocal",
    "Tipoperiodo",
    "Tiposituacion",
    "TipoAccidente",
    "TipoExposicion",
    "TipoHecho",
    "TipoM",
    "TipoObjeto",
    "TipoVehiculo",
    "Tpaciente",
    "TransmisionSida",
    "Tratamiento",
    "TratamientoProg",
    "TratamientoSeg",
    "TratamientoSegcardio",
    "TratamientoTuberculosis",
    "Trnacidos",
    "TDoc",
    "UbicacionDiag",
    "Ultimogrado",
    "Usuarios",
    "UsuarioEstab",
    "Validarcie10",
    "VLista3",
    "VMuertematerna",
    "VNacimiento",
    "XCantHab",
    "XCausasMuertes",
]
