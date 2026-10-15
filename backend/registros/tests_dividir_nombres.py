"""Pruebas del comando que separa el nombre compuesto (§35).

El legacy guarda «apellidos + nombres» en un solo campo; el comando lo reparte en
``*_apellidos`` y ``*_nombres`` cuando los apellidos están vacíos. Se fija que sea
idempotente, que respete lo ya escrito y que el dry-run no toque nada.
"""
from django.core.management import call_command
from django.test import TestCase

from registros.models import Nacimiento
from registros.services import dividir_nombre_compuesto


class DividirNombreCompuestoUnitTests(TestCase):
    def test_cuatro_palabras_dos_apellidos_dos_nombres(self):
        # El caso del usuario: «BARCOS SILVA DEYARLIN DANIELA».
        self.assertEqual(
            dividir_nombre_compuesto("BARCOS SILVA DEYARLIN DANIELA"),
            ("DEYARLIN DANIELA", "BARCOS SILVA"),
        )

    def test_con_coma_es_inequivoco(self):
        self.assertEqual(dividir_nombre_compuesto("PEREZ GOMEZ, JUAN CARLOS"),
                         ("JUAN CARLOS", "PEREZ GOMEZ"))

    def test_dos_o_tres_palabras_un_apellido(self):
        self.assertEqual(dividir_nombre_compuesto("PEREZ JUAN"), ("JUAN", "PEREZ"))
        self.assertEqual(dividir_nombre_compuesto("PEREZ JUAN CARLOS"),
                         ("JUAN CARLOS", "PEREZ"))

    def test_una_palabra_no_se_toca(self):
        self.assertEqual(dividir_nombre_compuesto("JUAN"), ("JUAN", ""))

    def test_vacio(self):
        self.assertEqual(dividir_nombre_compuesto(""), ("", ""))
        self.assertEqual(dividir_nombre_compuesto(None), ("", ""))


class DividirNombresNacimientoTests(TestCase):
    def setUp(self):
        self.madre = Nacimiento.objects.create(
            registro_numero="LEG-RN-1", legacy_id="1", legacy_tabla="NAC_RNACIDO",
            fecha_evento="2010-05-01", madre_edad=20,
            madre_nombres="BARCOS SILVA DEYARLIN DANIELA", madre_apellidos="",
        )
        self.nino = Nacimiento.objects.create(
            registro_numero="LEG-RN-2", legacy_id="2", legacy_tabla="NAC_RNACIDO",
            fecha_evento="2010-05-02", madre_edad=22,
            madre_nombres="Ana", madre_apellidos="LOPEZ",
            nino_nombres="GOMEZ PEREZ LUIS", nino_apellidos="",
        )
        self.simple = Nacimiento.objects.create(
            registro_numero="LEG-RN-3", legacy_id="3", legacy_tabla="NAC_RNACIDO",
            fecha_evento="2010-05-03", madre_edad=24,
            madre_nombres="JUAN", madre_apellidos="",
        )

    def test_dry_run_no_modifica(self):
        call_command("dividir_nombres_nacimiento", stdout=None)
        self.madre.refresh_from_db()
        self.assertEqual(self.madre.madre_apellidos, "")
        self.assertEqual(self.madre.madre_nombres, "BARCOS SILVA DEYARLIN DANIELA")

    def test_ejecutar_reparte_apellidos_y_nombres(self):
        call_command("dividir_nombres_nacimiento", "--ejecutar", stdout=None)
        self.madre.refresh_from_db()
        self.assertEqual(self.madre.madre_apellidos, "BARCOS SILVA")
        self.assertEqual(self.madre.madre_nombres, "DEYARLIN DANIELA")
        self.nino.refresh_from_db()
        self.assertEqual(self.nino.nino_apellidos, "GOMEZ")
        self.assertEqual(self.nino.nino_nombres, "PEREZ LUIS")
        # Los apellidos ya escritos no se tocan.
        self.assertEqual(self.nino.madre_apellidos, "LOPEZ")

    def test_una_sola_palabra_no_se_selecciona(self):
        call_command("dividir_nombres_nacimiento", "--ejecutar", stdout=None)
        self.simple.refresh_from_db()
        self.assertEqual(self.simple.madre_apellidos, "")
        self.assertEqual(self.simple.madre_nombres, "JUAN")

    def test_es_idempotente(self):
        call_command("dividir_nombres_nacimiento", "--ejecutar", stdout=None)
        call_command("dividir_nombres_nacimiento", "--ejecutar", stdout=None)
        self.madre.refresh_from_db()
        self.assertEqual(self.madre.madre_apellidos, "BARCOS SILVA")
        self.assertEqual(self.madre.madre_nombres, "DEYARLIN DANIELA")

    def test_solo_madre(self):
        call_command("dividir_nombres_nacimiento", "--ejecutar", "--solo", "madre",
                     stdout=None)
        self.nino.refresh_from_db()
        self.assertEqual(self.nino.nino_apellidos, "")
