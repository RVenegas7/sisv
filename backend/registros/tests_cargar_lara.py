"""Pruebas del comando ``cargar_lara_2019_2020`` (§27.8.1).

El archivo ``lara_2019_2020.xlsx`` trae el EV-14 con varias columnas mal
rotuladas y la hora en reloj de 12 h con el marcador a.m./p.m. inservible. Aquí
se fija el parseo puro (sin Excel ni BD): es donde estaba el riesgo de cargar
datos inventados.
"""
import datetime

from django.test import SimpleTestCase

from registros.management.commands.cargar_lara_2019_2020 import (
    Command,
    _causa,
    _clave_nombre,
    _clave_numero,
    _fecha,
    _lugar,
    _misma_persona,
    _planilla,
    _primer_entero,
    _resolver_cie10,
)


class FechaTests(SimpleTestCase):
    def test_iso_y_dma(self):
        self.assertEqual(_fecha("2019-05-17 00:00:00"), datetime.date(2019, 5, 17))
        self.assertEqual(_fecha("23/9/1889"), datetime.date(1889, 9, 23))
        self.assertEqual(_fecha("03/02/19"), datetime.date(2019, 2, 3))
        self.assertEqual(_fecha("03/02/1996"), datetime.date(1996, 2, 3))

    def test_invalidas(self):
        self.assertIsNone(_fecha(""))
        self.assertIsNone(_fecha(None))
        self.assertIsNone(_fecha("SIN FECHA"))
        self.assertIsNone(_fecha("2019-13-45"))


class CausaTests(SimpleTestCase):
    def test_codigo_al_inicio(self):
        self.assertEqual(
            _causa("O622 Otra inercia uterina"), ("O62.2", "Otra inercia uterina")
        )
        self.assertEqual(_causa("I500 Insuficiencia cardíaca"), ("I50.0", "Insuficiencia cardíaca"))
        self.assertEqual(_causa("A09.0 Otras gastroenteritis"), ("A09.0", "Otras gastroenteritis"))
        self.assertEqual(_causa("U071 COVID-19"), ("U07.1", "COVID-19"))

    def test_codigo_con_signo(self):
        # «C61+» es una causa con signo: el código no lleva el «+».
        self.assertEqual(
            _causa("C61+ or maligno de la próstata (C61)"),
            ("C61", "or maligno de la próstata (C61)"),
        )

    def test_sin_codigo(self):
        self.assertEqual(_causa("SIN INFORMACION"), ("", "SIN INFORMACION"))
        self.assertEqual(_causa(None), ("", ""))

    def test_resolver_con_fallbacks(self):
        mapa = {"I50.0": 1, "I50": 2, "C61": 3}
        self.assertEqual(_resolver_cie10("I50.0", mapa), 1)
        self.assertEqual(_resolver_cie10("I50.9", mapa), 2)   # sin subcategoría
        self.assertEqual(_resolver_cie10("C61.X", mapa), 3)   # .X → sin «.X»
        self.assertIsNone(_resolver_cie10("Z99.9", mapa))
        self.assertIsNone(_resolver_cie10("", mapa))


class LugarTests(SimpleTestCase):
    def test_hospital_y_residencia(self):
        self.assertEqual(
            _lugar("478 - BARQUISIMETO En IRIBARREN, LARA"),
            ("Barquisimeto", "Iribarren", "Lara"),
        )
        self.assertEqual(
            _lugar("PIO TAMAYO En ANDRES ELOY BLANCO, LARA"),
            ("Pio Tamayo", "Andres Eloy Blanco", "Lara"),
        )

    def test_sin_formato(self):
        self.assertEqual(_lugar(""), ("", "", ""))
        self.assertEqual(_lugar("BARQUISIMETO"), ("", "", ""))


class EdadTests(SimpleTestCase):
    """El archivo rotula mal las columnas: la unidad y el valor están cruzados."""

    def _g(self, datos):
        return lambda clave: datos.get(clave)

    def test_menor_de_un_anio(self):
        cmd = Command()
        # Los valores reales del archivo no llevan código delante.
        g = self._g({"c18a": "Días", "c_18_tipo_edad_cuantos": "7"})
        self.assertEqual(cmd._edad("2", g), (7, "DIAS", False))
        g = self._g({"c18a": "Meses", "c_18_tipo_edad_cuantos": "3"})
        self.assertEqual(cmd._edad("2", g), (3, "MESES", False))
        # Murió en las primeras horas: menos de un día.
        g = self._g({"c18a": "Horas", "c_18_tipo_edad_cuantos": "5"})
        self.assertEqual(cmd._edad("2", g), (0, "DIAS", False))

    def test_fetal_sin_edad(self):
        cmd = Command()
        g = self._g({"c18a": "Fetal", "c_18_tipo_edad_cuantos": "0"})
        self.assertEqual(cmd._edad("1", g), (None, "", False))

    def test_mayor_de_un_anio(self):
        cmd = Command()
        # «39. tipo EDAD» trae la edad; «C39V» el tipo.
        g = self._g({"c39v": "Años", "c_39_tipo_edad": "39"})
        self.assertEqual(cmd._edad("3", g), (39, "ANIOS", False))
        g = self._g({"c39v": "100 y", "c_39_tipo_edad": ""})
        self.assertEqual(cmd._edad("3", g), (100, "ANIOS", False))
        g = self._g({"c39v": "Ignorado", "c_39_tipo_edad": ""})
        self.assertEqual(cmd._edad("3", g), (None, "", True))


class NumeroTests(SimpleTestCase):
    def test_planilla(self):
        self.assertEqual(_planilla(" 00123 "), "00123")
        self.assertEqual(_planilla("0"), "")     # «0» es sin dato
        self.assertEqual(_planilla(""), "")
        self.assertEqual(_planilla("ABC"), "")

    def test_clave_numero(self):
        self.assertEqual(_clave_numero("00123"), "123")
        self.assertEqual(_clave_numero("913101410"), "913101410")
        self.assertEqual(_clave_numero(""), "")

    def test_clave_nombre_ignora_rellenos(self):
        # Mismo nombre en otro orden → misma clave.
        self.assertEqual(
            _clave_nombre("PEREZ", "GOMEZ", "ANA", "MARIA"),
            _clave_nombre("Gomez", "Perez", "Maria", "Ana"),
        )
        # Los nombres de relleno no identifican a nadie.
        self.assertEqual(_clave_nombre("XXX", "", "XXX", ""), "")
        self.assertEqual(_clave_nombre("FETO", None, "DESCONOCIDO", None), "")
        self.assertNotEqual(
            _clave_nombre("PEREZ", None, "ANA", None),
            _clave_nombre("GOMEZ", None, "ANA", None),
        )

    def test_primer_entero(self):
        self.assertEqual(_primer_entero("38 SEMANAS"), 38)
        self.assertEqual(_primer_entero(""), None)


class MismaPersonaTests(SimpleTestCase):
    """El número impreso se reutiliza: la identidad la deciden cédula/nombre/fecha."""

    def test_cedula(self):
        self.assertTrue(
            _misma_persona("", datetime.date(2019, 1, 1), "123", "", datetime.date(2018, 1, 1), "123")
        )

    def test_nombre(self):
        self.assertTrue(
            _misma_persona("ANA PEREZ", datetime.date(2019, 1, 1), "", "ANA PEREZ", datetime.date(2020, 1, 1), "")
        )

    def test_fecha_con_nombre_parecido(self):
        self.assertTrue(
            _misma_persona(
                "ANTO COLMENAREZ YOXON", datetime.date(2019, 5, 17), "",
                "COLMENAREZ YIXON ANTONIO", datetime.date(2019, 5, 17), "",
            )
        )

    def test_misma_fecha_sin_nombre_parecido(self):
        self.assertFalse(
            _misma_persona(
                "ROMULO PIÑA PERAZA", datetime.date(2019, 5, 24), "5949570",
                "FELIX ANTONIO MARQUEZ", datetime.date(2019, 5, 24), "3089402",
            )
        )

    def test_fecha_distinta_sin_otra_coincidencia(self):
        self.assertFalse(
            _misma_persona("ANA PEREZ", datetime.date(2019, 1, 1), "1", "LUZ GOMEZ", datetime.date(2018, 1, 1), "2")
        )

    def test_cedula_distinta_no_impide_reconocer_al_mismo_certificado(self):
        # Mismo número, mismo día y mismo apellido con la cédula tecleada
        # distinto: es el certificado repetido, no otra persona.
        self.assertTrue(
            _misma_persona(
                "ANTO COLMENAREZ YOXON", datetime.date(2019, 5, 17), "5949570",
                "COLMENAREZ YIXON ANTONIO", datetime.date(2019, 5, 17), "3089402",
            )
        )

    def test_sin_nombre_en_una_de_las_dos(self):
        # Sin nombre no hay con qué distinguir: misma fecha ⇒ mismo certificado.
        self.assertTrue(
            _misma_persona("", datetime.date(2019, 1, 1), "", "", datetime.date(2019, 1, 1), "")
        )


def _contadores():
    return {k: 0 for k in (
        "leidas", "sin_fecha", "ya_cargadas", "ya_existen", "duplicadas",
        "sin_numero_ya_existe", "insertadas", "pendientes_cie", "sin_numero",
        "numero_repetido",
    )}


def _persona(apellido="PEREZ", nombre="ANA", cedula="1234567", fecha="2019-05-17"):
    return {
        "c_8_defuncion": fecha,
        "planilla": "3546212",
        "c_1_primer_apellido": apellido,
        "c_3_primer_nombre": nombre,
        "c_5_cedula_de_identidad": cedula,
        "tipo_de_defuncion": "3 Un Año o más",
        "c_39_tipo_edad": "40",
        "c39v": "Años",
        "c_54_causa_de_muerte": "I500 Insuficiencia cardíaca",
        "c_46_lugar_de_residencia_h": "478 - BARQUISIMETO En IRIBARREN, LARA",
        "c_6_sexo": "2 Femenino",
    }


class DedupTests(SimpleTestCase):
    """El número impreso se reutiliza: el dedup tiene que mirar a la persona."""

    def _fila(self, datos, *, existentes=None, vistos=None, contadores=None):
        cmd = Command()
        g = lambda clave, datos=datos: datos.get(clave)  # noqa: E731
        return cmd._fila(
            "2019", 3, g, datos.get("planilla"), "2019-3",
            mapa_cie={"I50.0": 1},
            existentes_num=existentes or {},
            existentes_nombre=set(),
            cargadas=set(),
            vistos={} if vistos is None else vistos,
            contadores=contadores if contadores is not None else _contadores(),
        )

    def test_numero_repetido_con_otra_persona_se_carga(self):
        existentes = {"3546212": [("MARIA SANCHEZ", datetime.date(2019, 1, 2), "7654321")]}
        resultado, obj = self._fila(_persona(), existentes=existentes)
        self.assertEqual(resultado, "insertada_numero_repetido")
        self.assertEqual(obj.numero_certificado, "3546212")
        self.assertEqual(obj.fallecido_apellidos, "PEREZ")

    def test_misma_cedula_aunque_cambie_la_fecha_ya_existe(self):
        # Misma cédula: es la misma persona con la fecha tecleada distinto.
        existentes = {"3546212": [("", datetime.date(2018, 1, 1), "1234567")]}
        resultado, _ = self._fila(_persona(), existentes=existentes)
        self.assertEqual(resultado, "ya_existe")

    def test_mismo_numero_y_fecha_con_otra_persona_se_carga(self):
        # Dos personas pueden morir el mismo día con el serial reutilizado.
        existentes = {"3546212": [("MARIA SANCHEZ", datetime.date(2019, 5, 17), "7654321")]}
        resultado, _ = self._fila(_persona(), existentes=existentes)
        self.assertEqual(resultado, "insertada_numero_repetido")

    def test_mismo_numero_y_fecha_con_nombre_parecido_ya_existe(self):
        # Misma fecha y una palabra del nombre en común (apellido): es la misma
        # persona con el nombre mal tecleado, no se carga dos veces.
        existentes = {"3546212": [("PEREZ GOMEZ", datetime.date(2019, 5, 17), "")]}
        resultado, _ = self._fila(_persona(), existentes=existentes)
        self.assertEqual(resultado, "ya_existe")

    def test_mismo_numero_y_fecha_con_cedulas_distintas_ya_existe(self):
        # Mismo día, mismo apellido y la cédula tecleada distinto: certificado
        # repetido (no se carga dos veces).
        existentes = {"3546212": [("PEREZ GOMEZ", datetime.date(2019, 5, 17), "7654321")]}
        resultado, _ = self._fila(_persona(), existentes=existentes)
        self.assertEqual(resultado, "ya_existe")

    def test_numero_y_fecha_iguales_ya_existe(self):
        existentes = {"3546212": [("", datetime.date(2019, 5, 17), "")]}
        resultado, obj = self._fila(_persona(), existentes=existentes)
        self.assertEqual(resultado, "ya_existe")
        self.assertIsNone(obj)

    def test_numero_y_cedula_iguales_ya_existe(self):
        existentes = {"3546212": [("", datetime.date(2010, 1, 1), "1234567")]}
        resultado, _ = self._fila(_persona(), existentes=existentes)
        self.assertEqual(resultado, "ya_existe")

    def test_duplicado_dentro_del_archivo(self):
        vistos = {"3546212": [("ANA PEREZ", datetime.date(2019, 5, 17), "1234567")]}
        resultado, obj = self._fila(_persona(), vistos=vistos)
        self.assertEqual(resultado, "duplicada_en_archivo")
        self.assertIsNone(obj)

    def test_misma_planilla_distinta_persona_en_el_archivo(self):
        vistos = {"3546212": [("OTRA GENTE", datetime.date(2019, 5, 17), "999")]}
        resultado, obj = self._fila(_persona(), vistos=vistos)
        self.assertEqual(resultado, "insertada_numero_repetido")
        self.assertIsNotNone(obj)

    def test_fila_cargada_por_legacy_id(self):
        cmd = Command()
        datos = _persona()
        g = lambda clave, datos=datos: datos.get(clave)  # noqa: E731
        resultado, obj = cmd._fila(
            "2019", 3, g, datos.get("planilla"), "2019-3",
            mapa_cie={}, existentes_num={}, existentes_nombre=set(),
            cargadas={"2019-3"}, vistos={}, contadores=_contadores(),
        )
        self.assertEqual(resultado, "ya_cargada")
        self.assertIsNone(obj)

    def test_mapeo_del_certificado(self):
        resultado, obj = self._fila(_persona())
        self.assertEqual(resultado, "insertada")
        self.assertEqual(obj.fecha_evento, datetime.date(2019, 5, 17))
        self.assertEqual(obj.edad, 40)
        self.assertEqual(obj.edad_unidad, "ANIOS")
        self.assertEqual(obj.sexo, "F")
        self.assertEqual(obj.cie10_legacy, "I50.0")
        self.assertEqual(obj.cie10_id, 1)
        self.assertFalse(obj.codificacion_pendiente)
        self.assertEqual(obj.version_cie, "CIE10")
        self.assertEqual(obj.estado, "Lara")
        self.assertEqual(obj.municipio, "Iribarren")
        self.assertEqual(obj.parroquia, "Barquisimeto")
        self.assertEqual(obj.organizacion_id, None)   # el xlsx no trae centro
        self.assertEqual(obj.legacy_id, "2019-3")
        self.assertEqual(obj.lote_id, "LARA-2019-2020")

    def test_sin_causa_queda_pendiente(self):
        datos = _persona()
        datos["c_54_causa_de_muerte"] = None
        resultado, obj = self._fila(datos)
        self.assertEqual(resultado, "insertada")
        self.assertTrue(obj.codificacion_pendiente)
        self.assertIsNone(obj.cie10_id)

    def test_sin_fecha_no_se_carga(self):
        datos = _persona()
        datos["c_8_defuncion"] = "SIN FECHA"
        contadores = _contadores()
        resultado, obj = self._fila(datos, contadores=contadores)
        self.assertEqual(resultado, "sin_fecha")
        self.assertIsNone(obj)
        self.assertEqual(contadores["sin_fecha"], 1)
